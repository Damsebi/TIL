# Softmax와 수치 안정성·Log Probability

> 학습일: 2026-09-10

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Logit을 확률로 바꾸는 Softmax

모델이 출력한 logit은 각 클래스에 부여한 원시 점수이며 아직 확률이 아니다. 다중 분류에서 Softmax를 적용하면 각 logit을 0과 1 사이의 값으로 바꾸고, 전체 합이 1인 확률 분포로 해석할 수 있다.

클래스 $i$의 logit을 $z_i$라고 할 때 Softmax는 다음과 같다.

\[
\operatorname{softmax}(z_i)
= \frac{e^{z_i}}{\sum_j e^{z_j}}
\]

여기서 $e$는 약 $2.71828$인 고정된 자연상수이고, $z_i$가 클래스마다 달라지는 logit이다. 모든 클래스는 지수값 전체의 합인 $\sum_j e^{z_j}$를 공통 분모로 사용하므로 Softmax 결과의 합은 1이 된다. 실제 컴퓨터 계산에서는 부동소수점 오차 때문에 1과 아주 조금 다르게 표시될 수 있다.

단순히 가장 큰 클래스를 찾는 것이 목적이라면 `argmax(logits)`만으로도 가능하다. 이번 실습에서는 클래스별 확률과 이후 Cross Entropy에 사용할 log probability가 필요하므로 Softmax를 계산한다.

### 최댓값을 빼서 Overflow를 줄인다

지수함수는 입력이 커지면 값이 매우 빠르게 증가한다. 큰 logit에 그대로 `exp()`를 적용하면 표현 가능한 수의 범위를 넘어 overflow가 발생할 수 있다.

이를 줄이기 위해 Softmax를 적용하기 전 각 logit에서 같은 최댓값 $m$을 뺀다.

\[
m = \max(z)
\]

\[
\operatorname{softmax}(z_i)
= \frac{e^{z_i-m}}{\sum_j e^{z_j-m}}
\]

분자와 분모에 공통으로 $e^{-m}$이 적용되어 약분되므로 최종 확률은 바뀌지 않는다.

```text
[1000, 999, 998]
→ 최댓값 1000을 각 원소에서 뺌
→ [0, -1, -2]
→ exp() 계산
```

즉 Softmax를 적용한 뒤의 확률에서 최댓값을 빼는 것이 아니다. **Softmax를 적용하기 전 logit에서 최댓값을 뺀 뒤** 지수함수를 계산한다.

### NumPy의 Vectorized Operation과 Broadcasting

NumPy에서는 반복문을 직접 작성하지 않아도 배열 전체에 연산을 적용할 수 있다. 이를 vectorized operation이라고 한다.

```python
import numpy as np

x = np.array([1000, 999, 998])
shifted = x - np.max(x)

print(shifted)  # [ 0 -1 -2]
```

`np.max(x)`의 결과는 스칼라 `1000`이다. 배열에서 이 스칼라를 빼면 NumPy가 값을 각 원소에 적용한다.

```text
[1000, 999, 998] - 1000
→ [0, -1, -2]
```

이처럼 크기가 다른 값을 연산할 수 있도록 스칼라를 배열의 각 위치에 맞춰 적용하는 동작이 broadcasting이다.

여러 문의를 batch로 처리하여 `logits`의 Shape가 `(B, C)`라면 각 행에서 최댓값을 하나씩 구해야 한다.

```python
shifted = logits - np.max(logits, axis=-1, keepdims=True)
```

`np.max(..., axis=-1, keepdims=True)`의 결과 Shape는 `(B, 1)`이고, 이 값이 `(B, C)`의 각 클래스 위치로 broadcasting된다.

### Log Probability를 안정적으로 계산한다

Softmax 확률 $p_i$는 다음과 같다.

\[
p_i = \frac{e^{s_i}}{\sum_j e^{s_j}}
\]

여기서 $s_i = z_i - m$은 최댓값을 뺀 logit이다. 양변에 로그를 적용하면 다음과 같이 정리된다.

\[
\begin{aligned}
\log(p_i)
&= \log\left(\frac{e^{s_i}}{\sum_j e^{s_j}}\right) \\
&= \log(e^{s_i}) - \log\left(\sum_j e^{s_j}\right) \\
&= s_i - \log\left(\sum_j e^{s_j}\right)
\end{aligned}
\]

따라서 Softmax 확률을 먼저 구한 뒤 `np.log()`를 적용하지 않고 다음과 같이 log probability를 직접 계산할 수 있다.

```python
shifted = logits - np.max(logits, axis=-1, keepdims=True)
exp_shifted = np.exp(shifted)
denominator = np.sum(exp_shifted, axis=-1, keepdims=True)

probabilities = exp_shifted / denominator
log_probabilities = shifted - np.log(denominator)
```

`np.log(probabilities)`도 수학적으로는 같은 값이다. 하지만 아주 작은 확률이 부동소수점 계산에서 0으로 내려가면 `log(0)` 문제가 생길 수 있으므로, 이번 실습에서는 `shifted - np.log(denominator)` 형태로 직접 계산한다.

Log probability 자체가 Cross Entropy는 아니다. 이후 정답 클래스의 log probability를 선택하고 음수를 취하면 한 샘플의 Cross Entropy 손실이 된다.

\[
L = -\log(p_{\text{정답}})
\]

정답 확률이 높으면 손실이 작아지고, 정답 확률이 0에 가까워지면 손실이 커진다.

### 부동소수점 오차는 Endianness와 다르다

컴퓨터는 많은 실수를 유한한 비트의 2진수로 정확하게 표현할 수 없어 가까운 값으로 저장한다. 이 때문에 계산 결과가 `1.0000000002`나 `0.999999999...`처럼 기대한 값과 미세하게 다를 수 있다.

```python
print(0.1 + 0.2)  # 0.30000000000000004
```

이 현상은 floating-point error다. Little endian과 big endian은 여러 byte를 메모리에 어떤 순서로 저장하는지에 관한 개념이므로 원인이 다르다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| `1.0000000002`, `0.999999999...` 같은 미세한 차이를 Little endian이나 Big endian과 관련된 현상으로 생각했다. | 실수를 2진수로 정확히 표현하지 못해 근삿값으로 저장하면서 발생하는 floating-point error다. Endianness는 byte 저장 순서에 관한 개념이다. |
| Softmax 값을 최댓값으로 뺀다고 이해했다. | Softmax 결과를 빼는 것이 아니라 Softmax 적용 전 각 문의의 logit에서 해당 문의의 최대 logit을 뺀다. |
| `log_probabilities`를 `np.log(probabilities)`로 계산하려고 했다. | 수학적으로는 같지만, 이번 실습에서는 더 안정적으로 계산하기 위해 `shifted - np.log(denominator)`를 사용한다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Softmax는 각 원시 점수에 지수함수를 적용하고 지수값들의 전체 합으로 각각을 나누는가?

맞다. 각 logit $z_i$에 $e^{z_i}$를 적용하고, 모든 클래스의 지수값을 더한 공통 분모로 각각을 나눈다.

\[
\operatorname{softmax}(z_i)
= \frac{e^{z_i}}{\sum_j e^{z_j}}
\]

---

### 질문: $e^2 + e^1 + e^0$ 같은 값이 Softmax의 분모인가?

맞다. Logit이 `[2, 1, 0]`이라면 $e^2 + e^1 + e^0$이 모든 클래스가 함께 사용하는 분모다.

---

### 질문: Softmax의 수치 안정성은 어떻게 확보하는가?

각 logit에서 최댓값을 뺀 뒤 지수함수를 적용한다. 모든 클래스에서 같은 값을 빼므로 최종 Softmax 결과는 바뀌지 않지만, 지수함수에 들어가는 값의 크기가 작아져 overflow 위험이 줄어든다.

---

### 질문: $e$는 무엇인가?

$e$는 변수가 아니라 약 $2.71828$인 자연상수다. $e^x$에서 $e$는 고정되어 있고 $x$가 변한다. Softmax에서는 $x$ 자리에 각 logit이 들어간다.

---

### 이해한 내용: 자연상수와 Logit의 관계

Softmax의 $e^z$에서 $e$는 고정된 자연상수이고 $z$는 모델이 출력한 원시 점수라고 이해했다.

---

### 질문: NumPy에서 반복문이 없는데 배열의 각 값에서 최댓값이 하나씩 빠지는가?

맞다. 배열에서 스칼라를 빼면 broadcasting을 통해 그 스칼라가 배열의 각 원소에 적용된다. 배열 전체를 한 번에 계산하는 것은 vectorized operation이고, 크기가 다른 값이 각 위치에 맞게 적용되는 동작은 broadcasting이다.

---

### 질문: 컴퓨터에서 계산 결과가 `1.0000000002`나 `0.999999999...`처럼 나오는 이유는 무엇인가?

많은 실수를 2진수로 정확히 표현할 수 없어 가까운 값으로 저장하기 때문이다. 이 근삿값을 사용한 연산에서 작은 차이가 나타나는 현상을 floating-point error라고 한다.

---

### 질문: 왜 Softmax를 적용하는가?

Logit은 모델이 각 클래스에 부여한 원시 점수라서 그대로는 확률로 해석할 수 없다. 이번 다중 분류 실습에서는 Softmax를 적용해 합이 1인 부서별 확률 분포로 바꾼다.

가장 큰 클래스만 찾으려면 `argmax(logits)`로도 충분하지만, 이후 확률과 log probability를 이용해 Cross Entropy를 계산하기 위해 Softmax가 필요하다.

---

### 질문: 왜 최댓값을 빼는가?

큰 logit에 `exp()`를 적용할 때 발생할 수 있는 overflow를 줄이기 위해서다. 각 문의의 모든 클래스에서 같은 최댓값을 빼면 계산할 숫자의 크기는 줄어들지만 Softmax의 최종 확률은 유지된다.

---

### 질문: 딥러닝에서 변수명은 정해져 있는가?

직접 선언하는 변수명은 자유롭게 정할 수 있다. 다만 `logits`, `probs`, `pred`, `target`, `loss`처럼 딥러닝 코드에서 관습적으로 사용하는 이름을 따르면 의미를 쉽게 파악할 수 있다.

반면 `np.max(..., axis=-1, keepdims=True)`의 `axis`, `keepdims`처럼 라이브러리가 정의한 keyword argument의 이름은 정해져 있다.

---

### 질문: 왜 확률에 로그가 필요한가?

이번 실습에서는 이후 Cross Entropy를 계산하기 위해 정답 클래스의 log probability가 필요하다.

\[
L = -\log(p_{\text{정답}})
\]

정답 확률이 높을수록 손실은 작아지고, 0에 가까울수록 손실은 커진다.

---

### 질문: 왜 `shifted - np.log(denominator)`인가?

Softmax 확률에 로그를 적용하고 로그의 나눗셈 법칙과 $\log(e^x)=x$를 사용하면 다음과 같이 정리된다.

\[
\log(p_i)
= \log(e^{s_i}) - \log\left(\sum_j e^{s_j}\right)
= s_i - \log(\text{denominator})
\]

따라서 `shifted - np.log(denominator)`는 Cross Entropy 자체가 아니라 Softmax 확률의 log probability를 안정적으로 계산한 값이다.

---

### 이해한 내용: Logit에서 Cross Entropy까지의 흐름

```text
이미 주어진 logits
→ 문의별 최대 logit을 뺌
→ Softmax로 부서별 확률 계산
→ Log probability 계산
→ 이후 정답 클래스와 비교하여 Cross Entropy 계산
```
