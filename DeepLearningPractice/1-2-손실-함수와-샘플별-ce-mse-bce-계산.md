# 손실 함수와 샘플별 CE·MSE·BCE 계산

> 학습일: 2026-09-10

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 손실 함수는 계산 규칙이고 Loss는 계산 결과다

손실 함수(loss function)는 모델의 예측값과 정답을 비교해 오차를 계산하는 **규칙**이다. `loss`는 그 규칙을 실제 데이터에 적용해서 얻은 **결과값**이다.

```text
prediction
→ target과 비교
→ loss function 적용
→ loss 계산
→ gradient 계산
→ optimizer가 parameter 수정
```

어떤 출력을 예측하는지에 따라 사용하는 손실 함수가 달라진다.

```text
담당 부서처럼 여러 클래스 중 하나를 분류
→ Cross Entropy

연속적인 품질 점수를 예측
→ Mean Squared Error

민감정보 여부처럼 0 또는 1을 판정
→ Binary Cross Entropy
```

### MSE는 예측값과 정답의 차이를 제곱한다

MSE는 회귀 문제에서 예측값과 정답의 차이를 제곱해 오차를 계산한다.

\[
\ell_i = (\hat{y}_i-y_i)^2
\]

여러 오차의 평균을 구하면 Mean Squared Error가 된다.

\[
\operatorname{MSE}
= \frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i-y_i)^2
\]

`np.mean()`은 배열의 값을 모두 더한 뒤 원소 개수로 나누는 연산이므로 다음 두 흐름은 같다.

```python
np.mean((y_pred - y_true) ** 2)
```

```python
np.sum((y_pred - y_true) ** 2) / y_true.size
```

다만 TODO 2에서는 batch 평균이 아니라 **문의별 loss**를 다음 단계로 전달해야 하므로 아직 `np.mean()`을 적용하지 않는다.

```python
mse_losses = (quality_pred - quality_gold) ** 2
```

### BCE는 정답이 0인지 1인지에 따라 확률을 평가한다

BCE는 이진 분류에서 정답이 1이면 예측 확률 $p$가 높은지를, 정답이 0이면 $1-p$가 높은지를 평가한다.

\[
\ell_i
= -\left[y_i\log(p_i)+(1-y_i)\log(1-p_i)\right]
\]

정답이 1이면 $-\log(p)$만 남고, 정답이 0이면 $-\log(1-p)$만 남는다.

정확한 0이나 1이 들어오면 $\log(0)$을 계산할 수 있으므로 확률을 작은 범위 안쪽으로 제한한다.

```python
eps = float(1e-12)
safe_probs = np.clip(flag_prob, eps, 1.0 - eps)

bce_losses = -(
    flag_gold * np.log(safe_probs)
    + (1.0 - flag_gold) * np.log(1.0 - safe_probs)
)
```

$\log(0)$은 정의되지 않아 음의 무한대로 발산하지만, 0에 매우 가까운 양수의 로그는 크기가 큰 음수이더라도 유한하다. Clipping은 이 차이를 이용해 무한대가 생기는 것을 막는 수치 안정화 방법이다.

### Cross Entropy는 정답 클래스의 확률을 평가한다

다중 분류의 Cross Entropy는 다음과 같다.

\[
\ell_i = -\sum_{c=1}^{C} y_{i,c}\log(p_{i,c})
\]

One-hot target에서는 정답 클래스 위치만 1이고 나머지는 0이므로 정답 클래스의 항만 남는다.

\[
\ell_i = -\log(p_{i,\text{정답}})
\]

예측 확률과 one-hot target이 다음과 같다면 정답 클래스의 확률 `0.7`만 loss 계산에 사용된다.

```text
prediction = [0.1, 0.7, 0.2]
target     = [0,   1,   0]

CE = -(0 × log(0.1) + 1 × log(0.7) + 0 × log(0.2))
   = -log(0.7)
```

PyTorch의 일반적인 `CrossEntropyLoss`에는 one-hot vector보다 정답 클래스 번호를 전달한다.

```text
prediction logits: [B, C]
target class index: [B]
```

`target[b]`가 batch의 $b$번째 샘플에서 선택할 정답 클래스 위치를 지정한다. `[B, C]`와 `[B]`를 직접 빼거나 곱하는 것이 아니다. PyTorch의 `CrossEntropyLoss`는 logits를 입력받아 내부적으로 log probability와 정답 클래스 loss를 계산한다.

### Reduction은 여러 Loss를 하나로 축약하는 방법이다

PyTorch의 `MSELoss`, `BCELoss`, `CrossEntropyLoss`는 기본적으로 `reduction="mean"`을 사용한다.

```text
none
→ 개별 loss 유지

sum
→ 개별 loss를 모두 더함

mean
→ 개별 loss의 평균
```

이번 실습처럼 샘플마다 출력이 하나인 경우의 Shape는 다음과 같다.

| 손실 함수 | Prediction | Target | `reduction="none"` | 기본 `mean` |
| --- | --- | --- | --- | --- |
| MSE | `[B]` | `[B]` | `[B]` | `[]` |
| BCE | `[B]` | `[B]` | `[B]` | `[]` |
| Cross Entropy | `[B, C]` | `[B]` | `[B]` | `[]` |

`[]`는 원소가 하나인 scalar loss를 뜻한다. MSE와 BCE에서 샘플마다 여러 출력값이 있다면 `reduction="none"`의 결과는 입력과 같은 Shape를 유지하며, 기본 `mean`은 그 원소들을 모두 평균낸다.

### TODO 2에서는 문의별 Loss를 그대로 유지한다

TODO 1의 `distribution()`은 logits로부터 확률과 `log_probs`를 만드는 역할까지만 담당한다. Cross Entropy는 TODO 2의 `sample_losses()`가 이미 전달받은 `log_probs`에서 정답 클래스 값을 선택해 계산한다.

```text
LOGITS
→ distribution()
→ log_probs
→ sample_losses()
→ 문의별 CE 계산
```

세 종류의 문의별 loss는 다음과 같이 계산할 수 있다.

```python
import numpy as np


def sample_losses(
    log_probs,
    targets,
    quality_pred,
    quality_gold,
    flag_prob,
    flag_gold,
):
    sample_indices = np.arange(log_probs.shape[0])
    correct_log_probs = log_probs[sample_indices, targets]
    ce_losses = -correct_log_probs

    mse_losses = (quality_pred - quality_gold) ** 2

    eps = float(1e-12)
    safe_probs = np.clip(flag_prob, eps, 1.0 - eps)
    bce_losses = -(
        flag_gold * np.log(safe_probs)
        + (1.0 - flag_gold) * np.log(1.0 - safe_probs)
    )

    return ce_losses, mse_losses, bce_losses
```

TODO 2의 목적은 문의별 손실을 유지하는 것이므로 세 결과는 모두 `[B]`이며 여기서는 평균을 내지 않는다. 이후 단계에서 필요한 방식으로 reduction한다.

### 평균 CE Loss만으로 개별 확률을 알 수는 없다

개별 샘플의 CE loss가 약 `0.357`이라면 다음 관계로부터 정답 클래스 확률이 약 `0.7`임을 알 수 있다.

\[
-\log(0.7) \approx 0.357
\]

하지만 실제 학습 화면에 표시되는 loss는 보통 batch의 개별 loss를 평균낸 scalar다. 평균값이 `0.357`이라는 사실만으로 특정 샘플 하나의 예측 확률이 `0.7`이었다고 판단할 수는 없다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| 최종 CE loss가 `0.357`이면 모델이 약 `70%`로 예측했다고 이해했다. | 개별 샘플의 CE loss라면 가능하지만, batch 평균 loss만으로 특정 샘플의 예측 확률을 알 수는 없다. |
| `distribution()`에서 Cross Entropy까지 계산됐다고 이해했다. | `distribution()`은 확률과 `log_probs`까지만 만들고, `sample_losses()`가 정답 클래스의 `log_probs`를 선택해 CE를 계산한다. |
| MSE를 처음부터 `np.mean()`으로 계산했다. | TODO 2에서는 문의별 손실이 필요하므로 차이의 제곱까지만 계산하고 평균은 이후 단계에서 낸다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: MSE 코드에서 `mean()`만 쓰는데 오차들을 모두 더하는 과정은 어디에 있는가?

`np.mean()` 자체가 모든 원소를 더한 뒤 원소 개수로 나누는 연산이다.

```text
np.mean(squared_errors)
→ np.sum(squared_errors) / 원소 개수
```

---

### 질문: BCE에서 로그를 계산하기 전에 Clipping을 하는 이유는 무엇인가?

BCE에는 `log(p)`와 `log(1-p)`가 들어간다. `p=0`이나 `p=1`이면 둘 중 하나가 `log(0)`이 될 수 있으므로, 확률을 `eps`와 `1-eps` 사이로 제한해 무한대가 발생하는 것을 막는다.

---

### 이해한 내용: 0과 0에 가까운 값의 차이

`log(0)`은 정의되지 않아 무한대로 발산하지만, 0에 아주 가까운 양수의 로그는 매우 큰 음수일 뿐 유한한 값이다. 따라서 BCE에서는 정확한 0과 1을 피하도록 clipping한다고 이해했다.

---

### 질문: BCE와 Cross Entropy의 식이 다른 이유는 무엇인가?

BCE는 정답이 0 또는 1인 이진 분류이므로 정답이 1일 때의 확률 $p$와 정답이 0일 때의 확률 $1-p$를 한 식에 함께 표현한다.

\[
-\left[y\log(p)+(1-y)\log(1-p)\right]
\]

다중 분류의 Cross Entropy는 여러 클래스 중 정답 클래스에 부여한 확률을 사용한다. One-hot target에서 정답 위치만 1이므로 결국 정답 클래스의 $-\log(p)$만 남는다.

---

### 질문: 손실 함수의 Shape는 어떻게 되는가?

`reduction="none"`이면 개별 loss의 Shape를 유지하고, 기본 `reduction="mean"`이면 전체를 평균내므로 최종 loss는 scalar `[]`가 된다.

이번 실습에서는 MSE와 BCE의 입력이 `[B]`이므로 개별 loss도 `[B]`다. Cross Entropy는 logits `[B, C]`와 정답 클래스 번호 `[B]`를 받아 샘플별 loss `[B]`를 만든다.

---

### 질문: `reduction`은 무엇인가?

여러 loss를 어떤 방식으로 축약할지 정하는 옵션이다. `none`은 개별 값을 유지하고, `sum`은 모두 더하며, `mean`은 평균을 낸다. 현재 배운 세 PyTorch 손실 함수의 기본값은 `mean`이다.

---

### 질문: Cross Entropy에서 Prediction은 `[B, C]`인데 Target은 `[B]`여도 어떻게 계산되는가?

`prediction[b]`에는 $b$번째 샘플의 클래스별 점수 $C$개가 들어 있고, `target[b]`에는 그 샘플의 정답 클래스 번호 하나가 들어 있다.

```text
prediction [B, C]
→ target [B]로 각 샘플의 정답 클래스 위치 선택
→ 샘플별 loss [B]
→ mean
→ scalar loss []
```

두 Tensor를 직접 빼거나 곱하지 않고 target을 index처럼 사용해 각 샘플의 정답 클래스 loss를 계산한다.

---

### 질문: One-hot에서는 Cross Entropy Loss를 어떻게 구하는가?

One-hot target의 1이 있는 위치가 정답 클래스다. 정답 위치를 제외한 항은 모두 0이 되므로 정답 클래스의 예측 확률에 대한 $-\log(p)$만 남는다.

PyTorch의 일반적인 `CrossEntropyLoss`에서는 one-hot을 직접 만들기보다 정답 클래스 번호를 `[B]`로 전달한다.

---

### 질문: `sample_losses()`에서 `distribution()`을 다시 호출해야 하는가?

아니다. 먼저 `distribution(LOGITS)`으로 만든 `log_probs`를 `sample_losses()`의 인자로 전달하므로 TODO 2에서는 이미 받은 값을 사용해 CE를 계산한다.

```text
LOGITS
→ distribution()
→ log_probs
→ sample_losses()
```

---

### 이해한 내용: TODO 2의 샘플별 Loss 계산

```text
log_probs와 정답 클래스 번호
→ 정답 위치의 log probability 선택
→ 부호를 바꿔 문의별 CE 계산

품질 예측값과 정답
→ 차이의 제곱
→ 문의별 MSE 계산

민감정보 확률과 0/1 정답
→ 확률 clipping
→ 문의별 BCE 계산

TODO 2
→ 세 loss 모두 평균내지 않고 [B]로 유지
```
