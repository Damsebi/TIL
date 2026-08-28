# `loss.backward()`와 `.grad` 확인

> 학습일: 2026-08-25

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

Loss를 숫자 하나로 정리했다고 Gradient도 모델 전체에 하나만 나오는 것은 아니다. **고쳐야 할 Weight·Bias의 각 값에 대응하는 Gradient가 필요하다.**

이번에는 Loss 객체에 예측값과 정답을 넣어 Loss를 계산한 뒤, `backward()` 후 각 Parameter에 `.grad`가 생겼는지와 Shape가 맞는지를 확인했다. `.grad`가 `None`이면 곧바로 Shape를 읽지 말고 계산 경로부터 확인한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: Weight·Bias와 Gradient의 개수

#### 처음 이해

Weight가 입력 Feature마다 하나씩 있는지, Bias도 Feature마다 있는지 헷갈렸다.

#### 수정된 이해

`nn.Linear(in, out)`에서는 **입력 Feature와 출력 뉴런의 연결마다 Weight 하나**, **출력 뉴런마다 Bias 하나**가 있다. 따라서 Weight는 `in × out`개, Bias는 `out`개다.

`nn.Linear(3, 4)`를 예로 들면 다음과 같다.

| Parameter | 값의 개수 | Parameter Shape | 계산된 Gradient Shape |
| --- | --- | --- | --- |
| `weight` | `3 × 4 = 12` | `(4, 3)` | `(4, 3)` |
| `bias` | `4` | `(4,)` | `(4,)` |

둘 다 Parameter라고 부르지만 하나의 Tensor로 합쳐 저장하는 것은 아니다. **Weight와 Bias는 각각 자기 Shape가 있고, Gradient도 해당 값마다 하나씩 대응한다.**

---

### 이해한 내용: 층을 지나며 바뀌는 Feature 수

`Linear(1, 3) → Linear(3, 4) → Linear(4, 5)`라면 앞 층의 출력 수가 다음 층의 입력 수와 맞아야 한다.

```text
(batch, 1) → (batch, 3) → (batch, 4) → (batch, 5)
```

Batch는 유지되고 Feature 수만 바뀐다. Feature가 저절로 늘어나는 것이 아니라 **각 층의 `out_features`를 그렇게 정했기 때문**이다.

---

### 질문: MSE가 아닌 다른 손실 함수도 무조건 평균을 내는가?

아니다. 평균은 많이 쓰는 방식이지 필수 규칙은 아니다.

- `mean`: 개별 Loss의 평균을 낸다.
- `sum`: 개별 Loss를 더한다.
- `none`: 개별 Loss를 그대로 남긴다.

처음에는 “어떤 값을 줄여야 할지 알기 위해 평균을 낸다”는 식으로 연결했다. 다시 정리하면 **평균은 여러 Loss를 하나의 학습 목표로 모으는 역할**이고, 수정에 사용할 Gradient는 그 Loss를 미분해서 구한다.

`none`으로 여러 원소가 남았다면 이번처럼 인자 없이 `loss.backward()`를 호출하기 전에 `mean()`이나 `sum()` 등으로 하나의 Loss로 모아야 한다.

---

### 이해한 내용: 학습용 `loss`와 기록용 `loss.item()`

이번 학습의 `loss`는 모델 Parameter와 계산 그래프로 연결된 Tensor다. 반면 `.item()`으로 꺼낸 값은 Python 숫자라 그 값에 `backward()`를 할 수 없다.

```python
loss_value = loss.item()  # 출력·기록용 숫자
loss.backward()          # 원래 Loss Tensor에서 미분
```

`.item()`을 호출했다고 원래 `loss`의 그래프가 사라지는 것은 아니다. **미분은 원래 Tensor로 하고, 꺼낸 숫자는 성적을 출력하거나 기록할 때 쓴다.**

---

### 이해한 내용: `.grad is None`

`backward()`를 실행했다고 모든 Parameter에 Gradient가 생기는 것은 아니다. **해당 Parameter가 이번 Loss를 만드는 경로에 참여했는지**를 확인해야 한다.

새 모델이거나 이전 `.grad`를 `None`으로 비운 상태에서, 어떤 Parameter가 Loss 경로에 참여하지 않았다면 Backward 후에도 `.grad`가 `None`일 수 있다. 이전 Gradient가 남아 있다면 이번 계산 결과와 혼동할 수 있으므로 초기화 상태도 함께 본다.

`None`은 Gradient Tensor가 없다는 뜻이다. 계산 결과가 숫자 `0`인 Gradient와는 구분한다.

---

### 이해한 내용: Loss 객체를 만든 뒤 입력값을 넣는다

`loss = nn.MSELoss()`라고 쓰면 채점 결과를 얻은 것이 아니라 **MSE를 계산할 객체만 만든 것**이다.

```python
from torch import nn

loss_mse = nn.MSELoss()
loss = loss_mse(pred, y)
loss.backward()
```

`loss_mse`는 손실 함수 객체이고, `loss`는 예측값과 정답을 넣어 실제로 계산한 결과다.

`nn.CrossEntropyLoss`도 클래스이므로 `nn.CrossEntropyLoss(logits, y)`처럼 계산 데이터를 생성자에 넣지 않는다. 먼저 객체를 만든 뒤 그 객체에 `logits`, `y`를 전달한다.

함수형 API는 바로 값을 넣어 호출할 수 있다. Cross Entropy 객체를 만들고 호출하는 대신 다음처럼 쓰는 차이를 확인했다.

```python
import torch.nn.functional as F

loss = F.cross_entropy(logits, y)
```

---

### 실습: CrossEntropyLoss 계산 후 Layer별 `.grad` 확인

```python
import torch
from torch import nn

model = nn.Sequential(
    nn.Linear(4, 5),
    nn.ReLU(),
    nn.Linear(5, 3)
)

x = torch.randn(6, 4)
y = torch.tensor([0, 1, 2, 1, 0, 2], dtype=torch.long)

logits = model(x)
loss_cross = nn.CrossEntropyLoss()
loss = loss_cross(logits, y)
loss.backward()
```

입력은 샘플 6개에 Feature 4개인 `(6, 4)`이고, 모델은 샘플마다 후보 3개의 점수를 내므로 Logits는 `(6, 3)`이다. 정답은 샘플마다 클래스 번호 하나이므로 `y`의 Shape는 `(6,)`다.

Backward 후 확인할 Gradient Shape는 다음과 같다.

| Layer | `weight.grad` | `bias.grad` |
| --- | --- | --- |
| `model[0]`: `Linear(4, 5)` | `(5, 4)` | `(5,)` |
| `model[2]`: `Linear(5, 3)` | `(3, 5)` | `(3,)` |

**최종 Logits의 Shape를 모든 Gradient에 대입하는 것이 아니라, 각 층의 Parameter Shape와 그 `.grad`를 하나씩 대응해서 확인한다.**
