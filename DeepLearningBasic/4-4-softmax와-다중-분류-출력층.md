# Softmax와 다중 분류 출력층

> 학습일: 2026-08-21

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 샘플마다 정답 후보들의 점수를 만든다

다중 분류는 여러 정답 후보 중 하나를 고르는 문제다. `class`는 정답 후보 하나이고, `num_classes`는 후보의 총개수다. 후보가 3개라면 마지막 층을 `nn.Linear(hidden_dim, 3)`으로 만들어 샘플마다 점수 3개를 낸다.

**후보 개수는 입력 데이터에 넣는 값이 아니라 모델의 마지막 출력 개수로 정하는 값**이다.

```text
(8, 4): 샘플 8개, 샘플마다 Feature 4개
→ 모델이 Feature로 각 Class의 점수를 계산
(8, 3): 샘플 8개, 샘플마다 Class 점수 3개
```

Feature를 버리고 Class로 바꾸는 것이 아니라, **Feature를 이용해 각 정답 후보에 점수를 매기는 것**으로 이해했다.

### 학습할 때와 결과를 읽을 때

```text
학습:      Logits → CrossEntropyLoss
확률 확인: Logits → Softmax → Class별 확률
답만 확인: Logits → argmax → 예측 Class 번호
```

앞 강의의 이진 분류에서는 Sigmoid로 확률을 확인했다면, 이번에는 Softmax로 여러 후보의 확률을 구한다. **한 샘플 안에서 Class별 확률의 합이 1**이 된다.

`CrossEntropyLoss`에는 Softmax를 미리 적용하지 않고 Raw Logits를 전달한다. 예측 Class 번호만 필요할 때도 Softmax 없이 Logits에 바로 `argmax`를 적용할 수 있다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: Softmax와 오차를 제곱하는 계산

#### 처음 이해

Softmax를 `(prediction - target)^2`처럼 값을 빼고 제곱하는 계산과 혼동했다.

#### 수정된 이해

음수를 다룬다는 점만 보고 같은 역할이라고 생각하면 안 된다.

- 절대값: 부호를 빼고 크기를 본다. L1 Norm에서 봤던 계산이다.
- 제곱: MSE에서 오차의 부호가 상쇄되지 않게 하고 큰 오차를 더 크게 반영한다.
- Softmax: 각 점수에 지수함수를 적용한 뒤 그 합으로 나눠 Class별 확률을 만든다.

Softmax의 목적은 단순히 음수를 없애는 것이 아니라 **후보들의 점수를 상대적인 확률로 바꾸는 것**이다.

---

### 질문: `dim`은 어떻게 정하는가?

**내가 비교하려는 값들이 어느 축에 있는지** 보고 정한다. `(batch, class)`에서는 한 샘플의 Class 점수끼리 비교해야 하므로 `dim=1`이다.

```text
Shape = (8, 3)
         ↑  ↑
       dim0 dim1
       샘플 Class
```

`dim=-1`은 Class 전용 표기가 아니라 마지막 축을 뜻한다. Class가 마지막 축에 있을 때 사용할 수 있다. 축 번호는 0부터 시작하므로 4차원 Tensor의 축은 `0, 1, 2, 3`이지 `dim=4`가 아니다.

```python
import torch

logits = torch.tensor([[2.0, 1.0, 0.1]])  # Shape: (1, 3)
torch.softmax(logits, dim=0)             # tensor([[1., 1., 1.]])
```

이 2차원 예제에서 `dim=0`은 같은 열의 행들끼리, `dim=1`은 한 행의 열들끼리 계산한다. 행이 하나뿐인데 `dim=0`으로 계산하면 각 열에 값이 하나씩만 있어서 전부 `1`이 된다.

원하는 것은 **샘플끼리 비교하는 것이 아니라 한 샘플의 후보 3개를 비교하는 것**이므로 `torch.softmax(logits, dim=1)`을 사용한다.

---

### 이해한 내용: `argmax`의 번호와 `.item()`, `.tolist()`

`argmax`는 가장 큰 점수 자체가 아니라 **그 점수가 있는 위치의 번호**를 반환한다. `dim`을 생략하면 전체를 펼쳐서 번호 하나만 찾는다.

```python
logits = torch.tensor([
    [0.1, 2.5, 0.3],
    [3.0, 1.0, 0.2]
])

torch.argmax(logits)              # tensor(3): 전체에서 3.0의 위치
pred = torch.argmax(logits, dim=1)
print(pred)                      # tensor([1, 0]): 샘플별 예측 Class
print(pred.tolist())             # [1, 0]
```

`.item()`은 원소 하나짜리 Tensor에서 Python 숫자를 꺼낸다. 위의 `pred`처럼 여러 예측값을 리스트로 꺼낼 때는 `.tolist()`를 쓴다.

`argmax` 결과는 인덱스이므로 `torch.int64`, 즉 `torch.long` Tensor다.

---

### 이해한 내용: Target은 비교할 숫자가 아니라 정답 번호다

Logits가 `[2.0, 1.0, 0.1]`이면 각각 Class `0, 1, 2`의 점수다. 이때 `target=0`은 **점수에서 숫자 0을 빼라는 뜻이 아니라 실제 정답이 Class 0이라는 뜻**이다.

`CrossEntropyLoss`는 모델이 실제 정답 Class에 얼마나 높은 확률을 주었는지 평가한다. 같은 점수라도 정답이 Class 0인지 Class 2인지에 따라 Loss가 달라진다.

MSE처럼 예측값과 정답 숫자의 차이를 계산하는 방식과는 다르다. **Prediction과 Target을 어떤 방식으로 비교하는지는 문제와 Loss에 따라 달라진다.** 이번 Target은 정답의 임베딩 벡터가 아니라 데이터에 붙어 있는 Class Label이다.

이번처럼 정답을 Class 번호로 주는 경우에는 `target.shape == (batch,)`, `dtype == torch.long`을 사용한다. Target이 `long`인 것은 `argmax` 때문이 아니라 **Loss가 정답 Class 인덱스를 받기 때문**이다. 예측 번호와 실제 정답 번호는 역할이 다르다.

---

### 이해한 내용: 샘플별 채점 결과를 Loss 하나로 모은다

```python
from torch import nn

logits = torch.randn(4, 3)
target = torch.tensor([0, 2, 1, 1], dtype=torch.long)

loss = nn.CrossEntropyLoss()(logits, target)
loss_value = loss.item()
```

샘플 4개마다 후보 3개의 점수가 있고, 실제 정답 번호가 각각 `0, 2, 1, 1`이라는 뜻이다.

기본 `CrossEntropyLoss()`는 샘플별 Loss 4개를 구한 뒤 `reduction='mean'`으로 평균내어 **Scalar Loss 하나**를 만든다. `.item()`은 이미 계산된 Loss를 Python 숫자로 꺼낼 뿐, 평균을 계산하는 함수는 아니다.

---

### 이해한 내용: `torch.randn(4, 3)`은 연습용 점수다

위 코드의 `torch.randn(4, 3)`은 학습을 끝낸 모델의 결과가 아니라 **Loss 사용법을 연습하려고 임의로 만든 Logits**다.

실제 모델에서는 `logits = model(x)`로 입력과 현재 Weight·Bias를 이용해 점수를 계산한다. 학습 전에는 초기 Parameter로, 학습 중에는 그때까지 수정된 Parameter로, 학습 후에는 학습된 Parameter로 계산한다. 모델에 Logits 자체를 랜덤하게 넣는다는 뜻은 아니다.

---

### 이해한 내용: 역전파에서 Softmax를 본 이유

숫자 분류처럼 여러 후보 중 하나를 고르는 예제에서 Softmax와 Cross Entropy를 함께 사용했기 때문에 역전파 설명에서도 Softmax를 봤던 것이다. **Softmax가 모든 역전파에 필요한 것은 아니다.**

그때 본 `softmax(logits) - target` 형태는 한 샘플의 일반적인 Cross Entropy를 Logits에 대해 미분한 식이다. 이 식의 Target은 Class 번호 하나가 아니라 **정답 위치만 1인 One-hot 표현**이다. 배치 평균 Loss를 미분하면 배치 크기로 나누는 부분도 반영된다. 코드에서 Loss에 전달하는 정수형 Class 번호와 수식의 Target 표현을 구분해야 한다.
