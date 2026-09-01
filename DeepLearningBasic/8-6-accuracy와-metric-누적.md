# Accuracy와 Metric 누적

> 학습일: 2026-08-26

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

분류 모델은 Loss와 함께 Accuracy를 확인한다. Accuracy는 **전체 Sample 중 예측 Class를 맞힌 Sample의 비율**이다.

다중 분류 Logits의 Shape가 `(batch_size, num_classes)`라면 `dim=0`은 Sample 방향이고 `dim=1`은 Class 방향이다. 따라서 Sample마다 가장 높은 Class 점수를 고르려면 `argmax(dim=1)`을 사용한다.

```text
Logits: (Batch, Classes)
→ argmax(dim=1)
Preds:  (Batch,)
→ Labels와 원소별 비교
Batch에서 맞힌 Sample 수 계산
```

Epoch Metric은 Batch별 비율을 단순 평균하지 않고 **개수와 총합을 먼저 누적한 뒤 마지막에 전체 Sample 수로 나눈다.** 마지막 Batch가 더 작아도 각 Sample이 같은 비중으로 반영되기 때문이다.

```python
total_loss = 0.0
total_correct = 0
total_samples = 0

for inputs, labels in loader:
    logits = model(inputs)
    loss = criterion(logits, labels)

    batch_size = labels.size(0)
    preds = logits.argmax(dim=1)

    total_loss += loss.item() * batch_size
    total_correct += (preds == labels).sum().item()
    total_samples += batch_size

epoch_loss = total_loss / total_samples
epoch_accuracy = total_correct / total_samples
```

Train과 Validation 모두 Metric 누적 방식은 같다. 다만 Train은 `backward()`와 `optimizer.step()`으로 Parameter를 수정하고, Validation은 현재 성능만 확인하므로 두 호출을 사용하지 않는다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `correct_tensor = preds == labels`는 무엇인가?

예측 Class와 정답 Class를 같은 위치끼리 비교해 Boolean Tensor를 만든다.

```python
import torch

preds = torch.tensor([0, 1, 2])
labels = torch.tensor([0, 1, 1])

correct_tensor = preds == labels
# tensor([True, True, False])
```

`correct_tensor.sum()`에서는 `True`가 1, `False`가 0처럼 합산되므로 이 Batch에서 맞힌 Sample 수는 2가 된다. Epoch 누적값에는 `.item()`으로 Python 숫자를 꺼내 더할 수 있다.

---

### 질문: `loss.item() * batch_size`는 왜 계산하는가?

이번 예제의 `CrossEntropyLoss`는 `reduction='mean'`을 사용하므로 `loss.item()`이 현재 Batch의 평균 Loss다.

Batch Size가 4이고 평균 Loss가 `0.5`라면 다음 계산으로 해당 Batch의 Loss 총합을 복원한다.

```text
0.5 × 4 = 2.0
```

각 Batch의 총합을 모두 누적한 뒤 전체 Sample 수로 나누면, 마지막 Batch의 크기가 달라도 Sample 기준 Epoch 평균을 구할 수 있다.

```python
epoch_loss = total_loss / total_samples
```

이 방식은 이번처럼 모든 Sample을 같은 비중으로 포함하고 Loss가 평균으로 반환되는 경우를 기준으로 한다. `reduction='sum'`이나 `'none'`, Class Weight·`ignore_index` 등을 사용한다면 Loss의 집계 기준에 맞게 누적 방식도 다시 확인해야 한다.
