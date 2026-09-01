# MLP 모델과 Train·Validation Loop

> 학습일: 2026-08-26

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

8-1강부터 8-5강까지는 앞에서 따로 배운 Model·Loss·Optimizer·DataLoader를 **하나의 실제 학습 흐름으로 연결하는 과정**이었다.

```text
DataLoader의 Batch
→ Model Forward
→ Logits
→ Loss
→ Backward
→ Optimizer Step
→ Epoch 종료 후 Validation
```

`nn.Module`의 `__init__`에서는 사용할 Layer를 준비하고, `forward`에서는 입력이 그 Layer들을 지나는 순서를 정한다. 실제 사용할 때는 `forward(x)`를 직접 호출하기보다 `model(x)`를 호출한다.

28×28 흑백 이미지를 10개 Class로 분류하는 MLP는 다음처럼 만들 수 있다.

```python
from torch import nn


class MLP(nn.Module):
    def __init__(self, hidden_dim=128, num_classes=10):
        super().__init__()

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(28 * 28, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        logits = self.fc2(x)
        return logits
```

```text
(Batch, 1, 28, 28)
→ Flatten
(Batch, 784)
→ Linear·ReLU
(Batch, Hidden Dim)
→ Linear
(Batch, 10) Logits
```

`CrossEntropyLoss`를 사용하는 다중 분류에서는 Model이 Softmax를 직접 적용하지 않은 Raw Logits를 반환한다. Logits Shape는 `(batch_size, num_classes)`, Class Index Label은 `(batch_size,)`이며 Dtype은 `torch.long`이다.

Train과 Validation의 차이는 Parameter를 수정하는지에 있다.

| Train | Validation |
| --- | --- |
| `model.train()` | `model.eval()` |
| `zero_grad → forward → loss → backward → step` | `no_grad → forward → loss·metric 확인` |
| Batch마다 Parameter Update | Parameter Update 없음 |

Model과 `inputs`, `labels`는 같은 Device에 있어야 한다. 한 Epoch 동안 모든 Train Batch를 학습한 뒤 Validation을 실행하고, Train·Validation 결과를 함께 기록하는 흐름으로 연결했다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: MLP가 Flatten한다면 CNN은 Flatten하지 않는가?

MLP의 첫 Layer인 `Linear`는 이미지의 높이·너비 구조를 그대로 받지 않으므로 시작 부분에서 이미지를 하나의 Feature Vector로 펼친다.

CNN의 `Conv2d`는 `(batch, channel, height, width)` 구조를 사용하므로 Convolution을 수행하는 동안에는 펼치지 않는다. 다만 마지막에 Linear 분류기로 연결할 때는 CNN도 Flatten하는 경우가 많다.

```text
MLP: 이미지 → Flatten → Linear → ...
CNN: 이미지 → Conv → ... → Flatten → Linear
```

---

### 질문: 출력 크기가 Class 수와 같다는 것은 무슨 뜻인가?

다중 분류에서는 Sample마다 각 Class에 대한 점수를 하나씩 출력한다.

```text
Class:  고양이  강아지  토끼
Logit:   2.1     0.3   -1.2
```

Class가 3개면 Logit도 Sample마다 3개이고, Class가 10개면 마지막 Linear의 출력 크기도 10이다.

---

### 이해 수정: MLP와 다중 분류의 관계

#### 처음 이해

MLP 자체가 다중 분류 전용 Model이라고 생각했다.

#### 수정된 이해

MLP는 신경망의 **구조**이며 회귀·이진 분류·다중 분류 등 여러 문제에 사용할 수 있다. 이번 MLP가 10개 Class를 구분하는 문제에 쓰이기 때문에 마지막 출력이 10개인 것이다.

---

### 질문: `.to(device)`는 무엇인가?

Tensor나 Model을 실제 계산을 수행할 CPU 또는 GPU로 옮기는 메서드다.

```python
model = model.to(device)
inputs = inputs.to(device)
labels = labels.to(device)
```

Model과 입력이 다른 Device에 있으면 Forward를 계산할 수 없다. Label도 Loss에서 Logits와 함께 계산되므로 같은 Device에 있어야 한다.

---

### 질문: Validation은 Epoch마다 하는가?

일반적으로 한 Epoch의 Train이 끝날 때마다 Validation을 한 번 수행한다.

```text
Epoch 1 → Train → Validation
Epoch 2 → Train → Validation
Epoch 3 → Train → Validation
```

반드시 매 Epoch마다 해야 하는 규칙은 아니지만, 현재 단계에서는 이 흐름으로 이해했다.

---

### 이해한 내용: Validation과 Early Stopping

Early Stopping을 사용하면 코드가 매 Epoch의 Validation 성능을 이전 Best 성능과 비교한다. 정해둔 기간 동안 개선되지 않으면 학습을 자동으로 종료할 수 있다.

학습자가 매 Epoch 결과를 직접 보며 중단할 필요는 없다. 학습이 끝난 뒤 멈춘 Epoch, Best Validation 성능, Train·Validation 변화와 선택된 Best Model을 확인할 수 있다고 이해했다.
