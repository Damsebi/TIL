# Dataset과 DataLoader 역할

> 학습일: 2026-08-31

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

Dataset과 DataLoader를 **샘플을 꺼내는 규칙**과 **그 샘플을 Batch로 배달하는 역할**로 나눠서 이해했다.

Dataset은 전체 샘플 수와 Index별 Sample·Label을 알려준다. Dataset 전체가 DataLoader로 한꺼번에 옮겨지는 것은 아니다. DataLoader가 현재 필요한 샘플들을 가져와 `batch_size`만큼 묶고, `shuffle=True`이면 **Sample과 Label의 짝은 유지한 채 샘플 순서만 섞는다.**

학습 Loop에서는 Batch마다 `Forward → Loss → Backward → Step`을 실행한다. 모든 Batch를 한 바퀴 처리한 범위가 1 Epoch다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Dataset의 데이터는 DataLoader로 어떻게 넘어가는가?

Dataset의 데이터를 전부 한 번에 넘기는 것이 아니다. DataLoader가 현재 필요한 Index들을 정하고, Dataset에서 `dataset[idx]` 결과를 가져와 하나의 Batch로 묶는다.

예를 들어 `batch_size=5`이면 Sample 다섯 개를 요청해 `batch_x`, `batch_y`로 만든다. `shuffle=True`일 때 달라지는 것은 요청할 Index의 순서이며, `X[idx]`와 `y[idx]`의 대응 관계는 그대로 유지된다.

---

### 질문: `[0, 1] * 10`인데 왜 Shape가 `(20,)`인가?

Python List에서 `* 10`은 숫자 하나를 열 번 만드는 것이 아니라 List 전체를 열 번 반복한다.

```python
labels = [0, 1] * 10
len(labels)  # 2 × 10 = 20
```

원소가 20개인 1차원 Tensor로 만들면 Shape는 `(20,)`이 된다.

---

### 질문: 특정 Index와 `next(iter(loader))`는 어떻게 다른가?

특정 **Sample 하나**가 필요할 때는 Dataset에 직접 Index를 사용한다.

```python
sample_x, sample_y = dataset[3]
```

DataLoader는 Batch를 차례로 공급하는 반복 가능한 객체다. `iter(loader)`로 반복자를 만들고 `next()`를 호출하면 그 반복자의 다음 Batch를 가져온다.

```python
loader_iterator = iter(loader)

first_batch = next(loader_iterator)
second_batch = next(loader_iterator)
```

따라서 `next(iter(loader))`는 특별한 Batch를 고르는 코드가 아니다. **현재 반복의 첫 Batch 하나만 꺼내 Shape와 Dtype을 빠르게 검사할 때** 사용한다. `shuffle=True`라면 이 첫 Batch의 Sample 구성은 달라질 수 있다.

---

### 이해 수정: Batch와 Epoch

#### 처음 이해

Forward부터 Parameter Update까지의 학습이 Epoch마다 한 번 실행된다고 생각했다.

#### 수정된 이해

학습과 `optimizer.step()`은 Batch마다 실행된다. Epoch는 전체 데이터의 모든 Batch를 한 번 처리한 범위다.

샘플 20개를 `batch_size=5`로 처리하면 다음처럼 이해할 수 있다.

```text
1 Epoch
├─ Batch 1 → Forward → Loss → Backward → Step
├─ Batch 2 → Forward → Loss → Backward → Step
├─ Batch 3 → Forward → Loss → Backward → Step
└─ Batch 4 → Forward → Loss → Backward → Step
```

따라서 이 경우 1 Epoch 동안 Parameter Update가 네 번 일어난다.

---

### 이해 수정: `TensorDataset`의 역할

#### 처음 이해

일반 데이터를 Tensor로 변환해주는 기능이라고 생각했다.

#### 수정된 이해

`TensorDataset`은 **이미 만들어진 Tensor들을 첫 번째 차원의 같은 Index끼리 묶어 Dataset으로 만드는 기능**이다.

```python
dataset = TensorDataset(X, y)

sample_x, sample_y = dataset[0]
# sample_x는 X[0], sample_y는 y[0]
```

따라서 함께 묶는 `X`와 `y`의 첫 번째 차원, 즉 Sample 수가 같아야 한다. Tensor로 바꾸는 과정은 `TensorDataset`을 만들기 전에 끝나 있어야 한다.

---

### 실습에서 확인한 Batch Shape와 Dtype

```python
x = torch.arange(20, dtype=torch.float32).view(10, 2)
y = torch.tensor([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

dataset = TensorDataset(x, y)
loader = DataLoader(dataset, batch_size=5, shuffle=True)
```

Sample은 10개이고 Sample 하나의 Feature는 2개이므로 Batch Shape는 다음과 같다.

```text
batch_x.shape = (5, 2)
batch_y.shape = (5,)
```

처음에는 `x.type`을 확인했지만, Tensor에 실제로 저장된 숫자의 자료형은 `.dtype`으로 확인한다.

```python
print(x.dtype)
print(y.dtype)
```

전체 Label 평균은 Batch Tensor 자체를 계속 더하는 대신, 각 Batch의 합과 원소 수를 누적해 구했다.

```python
total_sum = 0
total_count = 0

for _, batch_y in loader:
    total_sum += batch_y.sum().item()
    total_count += batch_y.numel()

mean_label = total_sum / total_count
```

---

### 질문: 모든 Label은 `torch.long`이어야 하는가?

아니다. 필요한 Dtype은 데이터의 역할과 사용하는 Loss가 무엇을 요구하는지에 따라 다르다.

`CrossEntropyLoss`에서 정답을 Class Index로 전달할 때는 각 숫자가 계산용 연속값이 아니라 클래스 번호이므로 보통 `torch.long`을 사용한다.

```python
y = torch.tensor([0, 1, 2], dtype=torch.long)
```

즉 **Label이라는 이유로 무조건 `long`을 쓰는 것이 아니라, Class Index를 요구하는 Loss에 맞추는 것**이라고 이해했다.
