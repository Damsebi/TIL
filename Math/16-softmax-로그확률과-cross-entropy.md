# Softmax·로그확률·Cross Entropy

> 학습일: 2026-08-07

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Attention Score를 정보 비율로 바꾸는 과정

6장 1강에서 Q와 K를 내적한 값은 **각 V를 얼마나 중요하게 볼지 정하는 점수**라고 이해했다. 이번에는 그 점수를 실제 비율로 바꾸는 과정을 학습했다.

```text
QKᵀ로 관련도 점수 계산
→ Scaling으로 점수가 지나치게 커지는 것 완화
→ Causal Mask로 보면 안 되는 미래 위치 제외
→ Softmax로 각 V를 가져올 비율 생성
→ 비율에 따라 V들을 가중합
```

- **Scaling**: `d_k`가 커져 내적할 항이 많아질 때 점수가 커지는 경향을 줄인다.
- **Causal Mask**: 미래 위치에 `-∞`를 넣어 Softmax 결과가 0이 되게 한다.
- **Softmax**: 남은 점수들을 합이 1인 비율로 바꾼다.
- **Attention Weight**: 각 V의 정보를 몇 퍼센트씩 가져올지 나타낸다.

Scaling은 다음처럼 계산한다.

$$
\frac{QK^\top}{\sqrt{d_k}}
$$

Softmax는 각 점수에 지수함수를 적용하고 그 결과를 전체 합으로 나눈다.

$$
p_i=\frac{e^{z_i}}{\sum_j e^{z_j}}
$$

지수함수는 점수의 순서를 유지하면서 모든 값을 양수로 만들고, 마지막에 전체 합으로 나누기 때문에 결과의 합이 1이 된다.

### Attention Softmax와 Vocabulary Softmax

두 경우 모두 Softmax를 사용하지만 무엇의 비율을 만드는지가 다르다.

```text
Attention Softmax
→ 어떤 Key의 V를 얼마나 가져올지 결정

Vocabulary Softmax
→ 어떤 Token이 다음에 나올 확률이 높은지 결정
```

Attention Softmax의 결과는 V를 섞는 데 사용하고, Vocabulary Softmax의 결과는 다음 토큰 후보들의 확률분포로 사용한다.

### 정답 확률을 Loss로 바꾸는 과정

Vocabulary logits를 확률로 바꾼 뒤 정답 토큰의 확률에 `-log`를 적용하면, 정답 확률이 높을수록 Loss가 작고 낮을수록 Loss가 커진다.

```text
Vocabulary logits
→ Softmax로 확률분포 생성
→ 정답 Token의 확률 확인
→ -log(정답 확률)
→ Loss
```

$$
\mathrm{NLL}=-\log(p_{\mathrm{true}})
$$

Single-label 다중분류에서는 Cross Entropy를 계산하면 결과적으로 정답 Class의 `-log(p_true)`가 남는다. 다만 정답 확률은 모든 Class의 logits를 함께 사용해 만든 Softmax 결과이므로 다른 Class도 계산에 영향을 준다.

PyTorch의 `CrossEntropyLoss`에는 Softmax 결과가 아니라 logits를 그대로 넣는다. 내부에서 Log Softmax와 NLL에 해당하는 계산을 한 번에 처리하기 때문이다.

### Temperature

Temperature는 Softmax 전에 logits를 `T`로 나누어 후보 간 차이를 조절한다.

$$
\mathrm{softmax}\left(\frac{z}{T}\right)
$$

```text
T < 1 → 높은 후보에 더 집중
T > 1 → 후보들의 확률이 더 넓게 퍼짐
```

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 왜 제곱이나 절댓값이 아니라 지수함수를 사용하는가?

제곱이나 절댓값은 음수와 양수의 순서를 망가뜨릴 수 있다.

```text
원래 점수: -2 < 0 < 2

절댓값: 2, 0, 2
제곱:   4, 0, 4
```

반면 지수함수는 `e⁻² < e⁰ < e²`처럼 원래 순서를 유지하면서 모든 값을 양수로 만든다.

---

### 질문: Softmax는 각각의 지수값을 전체 합으로 나누는 것인가?

맞다. 각 점수의 지수값을 구하고, 그 값들을 모두 더한 같은 합으로 각각 나눈다. 그래서 결과 전체를 더하면 1이 된다.

---

### 질문: 지수함수 공식 자체까지 알아야 하는가?

현재는 내부 계산법까지 알 필요는 없다. 다음 성질만 이해하면 된다.

```text
eˣ는 항상 양수
입력이 클수록 결과도 큼
e⁰ = 1
```

실제 계산은 라이브러리가 처리한다.

---

### 질문: 왜 Softmax에서 최댓값을 빼는가?

큰 점수에 지수함수를 바로 적용하면 Overflow가 발생할 수 있기 때문이다.

```text
[1000, 1001, 1002]
→ 최댓값 1002를 뺌
→ [-2, -1, 0]
```

모든 점수에서 같은 값을 빼도 Softmax 결과는 변하지 않으므로 더 안전한 크기로 계산할 수 있다.

---

### 질문: Attention Score는 내적인가?

맞다. Query 하나를 모든 Key와 내적하면 해당 Query가 각 Key를 얼마나 참고할지 나타내는 한 행의 점수들이 만들어진다.

---

### 질문: Causal Mask의 `-∞` 위치가 영상과 달랐던 이유는?

행과 열에 Query와 Key를 어느 방향으로 배치했는지가 달랐기 때문이다.

```text
현재 교안: 행 = Query, 열 = Key
다른 영상: 행 = Key, 열 = Query
```

그래서 `-∞`가 대각선 위나 아래로 다르게 보일 수 있다. 중요한 것은 방향 자체가 아니라 **현재 Query가 미래 Key를 보지 못하게 막는 것**이다.

---

### 이해 수정: Softmax와 Causal Mask의 역할

#### 처음 이해

Softmax의 합을 1로 만드는 것이 미래값을 보지 못하게 하는 과정과 직접 연결된다고 생각했다.

#### 해결 및 이해

두 연산의 역할은 다르다.

```text
Causal Mask → 미래 위치를 선택지에서 제외
Softmax     → 남은 점수를 합이 1인 비율로 변환
```

---

### 질문: Attention Weight란 무엇인가?

Softmax를 통과한 Attention Score이며, 각 V를 몇 퍼센트씩 가져올지 나타내는 비율이다.

```text
Attention Weight = [0.665, 0.245, 0.090]

→ 0.665V₁ + 0.245V₂ + 0.090V₃
```

이 가중합이 문맥을 반영한 Attention Output이 된다.

---

### 질문: Attention Softmax와 Vocabulary Softmax의 차이는?

연산은 같지만 대상과 목적이 다르다.

```text
Attention Softmax  → 어떤 V를 얼마나 참고할지 결정
Vocabulary Softmax → 다음 Token들의 확률분포 생성
```

---

### 질문: 지수함수 대신 로그함수를 쓰는 이유는 무엇인가?

로그는 지수함수 대신 사용하는 것이 아니다. Softmax에서는 지수함수로 확률을 만들고, 그다음 정답 확률을 Loss로 표현할 때 로그를 사용한다.

#### 처음 이해

로그가 지수함수의 반대 역할을 하며 음수는 더 작게, 양수는 더 크게 만들기 위해 사용한다고 생각했다.

#### 해결 및 이해

로그는 확률의 곱셈을 덧셈으로 바꿔 계산하기 쉽게 하고, 정답 확률이 낮을수록 큰 Loss를 만들기 좋은 성질 때문에 사용한다.

---

### 질문: NLL은 무엇인가?

정답 Token의 확률 `p_true`에 `-log`를 적용한 값이다.

```text
정답 확률이 높음 → NLL이 작음
정답 확률이 낮음 → NLL이 큼
```

---

### 질문: Cross Entropy는 무조건 One-hot인가?

아니다. Cross Entropy의 기본 형태는 다음과 같다.

$$
-\sum_i y_i\log p_i
$$

Single-label 다중분류에서는 정답이 하나이므로 One-hot으로 생각하면 정답 Class의 `-log(p_true)`만 남는다. 하지만 Soft Target도 사용할 수 있으므로 Cross Entropy 자체가 One-hot 전용인 것은 아니다.

PyTorch에서는 일반적으로 One-hot을 직접 만들지 않고 정답 Class Index를 전달한다.

---

### 질문: 다중분류에서 정답 하나만 고르는 것과 Cross Entropy가 연관되는가?

연관된다. Single-label 다중분류에서는 여러 Class 중 정답 하나의 확률을 높이도록 학습한다. 다만 그 확률은 모든 Class의 logits를 사용해 계산하므로 나머지 Class가 무시되는 것은 아니다.

---

### 질문: 왜 `CrossEntropyLoss`에는 Softmax 결과가 아니라 logits를 넣는가?

`CrossEntropyLoss`가 내부에서 Log Softmax와 NLL 계산을 수치적으로 안정되게 처리하기 때문이다.

```python
loss = F.cross_entropy(logits, labels)
```

확률을 직접 확인할 때만 별도로 Softmax를 적용한다.

---

### 질문: Temperature는 어떻게 작동하는가?

Softmax 전에 logits를 `T`로 나누어 차이를 조절한다.

```text
T < 1
→ logits 차이가 커짐
→ 높은 후보에 확률이 집중됨

T > 1
→ logits 차이가 줄어듦
→ 확률분포가 더 퍼짐
```

---

### 이해 수정: Scaling의 이유

#### 처음 이해

Q와 K의 단위가 달라 점수가 너무 커지거나 작아지는 것을 막기 위해 Scaling한다고 생각했다.

#### 해결 및 이해

`d_k`가 커지면 내적할 항이 많아져 Attention Score가 커지는 경향이 있다. 이를 완화하기 위해 `√d_k`로 나눈다.

---

### 이해 수정: V의 역할

#### 처음 이해

V도 Q와 K처럼 비슷한 값을 찾기 위한 표현이라고 생각했다.

#### 해결 및 이해

비슷한 정도를 판단하는 것은 Q/K의 역할이다. V는 Attention Weight가 정해진 뒤 실제로 가져와 섞을 정보다.
