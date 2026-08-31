# TensorDataset과 Custom Dataset

> 학습일: 2026-08-25

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

Dataset을 만드는 방법은 데이터가 많고 적은지보다 **샘플을 꺼내는 방식을 직접 정해야 하는지**를 보고 선택한다.

- 데이터가 이미 Tensor로 준비되어 있고 같은 Index끼리 묶기만 하면 되면 `TensorDataset`을 사용한다.
- 파일 읽기, 전처리, Label 생성처럼 Sample을 가져오는 과정을 직접 정해야 하면 Custom Dataset을 만든다.

Custom Dataset은 `Dataset`을 상속하고 세 가지 역할을 구현한다.

```text
__init__
→ 데이터나 파일 경로 등 필요한 정보 준비

__len__
→ 전체 Sample 수 반환

__getitem__(idx)
→ 해당 Index의 Sample 하나 반환
```

`__getitem__()`이 Batch를 만드는 것은 아니다. Dataset이 Sample 하나씩 꺼내는 방법을 제공하면 DataLoader가 여러 Sample을 모아 Batch로 만든다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: TensorDataset과 Custom Dataset의 선택 기준

#### 처음 이해

`TensorDataset`은 빠르고 자원을 적게 사용하며, Custom Dataset은 데이터가 적을 때 사용하는 더 범용적인 방식이라고 생각했다.

#### 수정된 이해

핵심 기준은 속도나 데이터 양이 아니라 **데이터 접근과 전처리를 직접 제어할 필요가 있는가**이다.

`TensorDataset`은 이미 메모리에 Tensor로 준비된 `X`, `y`를 간단히 묶을 때 편하다. Custom Dataset은 이미지·CSV·파일 경로를 가지고 있다가 필요한 Index가 들어왔을 때 읽거나, Sample마다 전처리와 Label 생성을 수행할 수 있다.

따라서 Custom Dataset이 항상 메모리를 더 많이 사용하는 것은 아니다. 큰 데이터의 파일 경로만 저장하고 `__getitem__()`에서 필요한 Sample만 읽도록 만들면 전체 데이터를 한꺼번에 메모리에 올리지 않아도 된다.

---

### 이해한 내용: `__init__`, `__len__`, `__getitem__`

- `__init__`: Dataset 생성 시 필요한 데이터·Label·파일 경로 등을 준비해 저장한다.
- `__len__`: Dataset의 전체 Sample 수를 반환한다.
- `__getitem__(idx)`: 주어진 `idx`에 해당하는 Sample 하나를 반환한다.

`TensorDataset`에도 이런 동작이 필요하지만 PyTorch가 이미 구현해두었기 때문에 직접 작성하지 않는다.

Custom Dataset을 만든 직후에는 DataLoader부터 연결하기 전에 다음을 먼저 확인할 수 있다.

```python
print(len(dataset))

sample_x, sample_y = dataset[0]
print(sample_x.shape, sample_x.dtype)
print(sample_y.shape, sample_y.dtype)
```

---

### 질문: `dtype`은 무엇이 나와야 하는가?

모든 Dataset에 하나의 정답이 있는 것이 아니라 데이터의 역할과 Loss가 요구하는 Dtype에 맞춘다.

| 데이터 역할 | 일반적으로 사용하는 Dtype |
| --- | --- |
| 모델 입력 `x` | `torch.float32` |
| `CrossEntropyLoss`의 Class Index `y` | `torch.long` (`torch.int64`) |
| 회귀 Target `y` | `torch.float32` |
| `BCEWithLogitsLoss`의 Target `y` | `torch.float32` |

이번 분류 예제의 Label은 Class Index이므로 `long`을 사용했다.

---

### 이해한 내용: Dataset 코드와 학습 코드의 역할 분리

Custom Dataset을 사용해도 DataLoader와 학습 코드의 역할은 바뀌지 않는다.

```text
Dataset
→ 데이터 읽기·전처리·Label 준비
→ Sample 하나 반환

DataLoader
→ 여러 Sample을 Batch로 묶음

Model / Loss / Optimizer
→ 예측과 학습 수행
```

데이터 처리 코드를 Dataset에 모아두면 같은 Dataset을 여러 모델에서 다시 사용할 수 있고, 학습 코드와 분리되어 수정할 위치도 명확해진다고 이해했다.

---

### 이해 수정: TensorDataset에서 첫 번째 Sample 꺼내기

#### 처음 이해

다음처럼 `__getitem__()`에 입력과 Label을 뜻하는 두 값을 전달하려고 했다.

```python
dataset.__getitem__(0, 0)
```

#### 수정된 이해

`__getitem__()`은 Sample Index 하나를 받는다. Python에서는 보통 메서드를 직접 호출하지 않고 대괄호로 사용한다.

```python
sample_x, sample_y = dataset[0]
```

`dataset[0]`이 내부적으로 `__getitem__(0)`을 호출하고, `TensorDataset(X, y)`에서는 `(X[0], y[0])`을 반환한다.

---

### 실습: Custom Dataset 기본 구현

```python
from torch.utils.data import Dataset


class TabularDataset(Dataset):
    def __init__(self, x, y):
        self.x = x.float()
        self.y = y.long()

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]
```

이 Dataset에서는 `len(dataset)`이 전체 Sample 수를 반환하고, `dataset[1]`은 `(x[1], y[1])`을 반환한다. `__getitem__()`은 여전히 Batch가 아니라 Sample 하나를 돌려준다.

---

### 질문: `__getitem__()`은 Tuple만 반환해야 하는가?

아니다. 학습 코드에서 다루기 편한 구조라면 Dictionary 형태로도 Sample을 반환할 수 있다.

```python
def __getitem__(self, idx):
    return {
        "id": idx,
        "x": self.x[idx],
        "y": self.y[idx],
    }
```

DataLoader의 기본 묶기 동작은 여러 Dictionary Sample에서 같은 Key의 값들을 모아 Batch로 만든다.

```text
id → 여러 Sample의 ID
x  → 여러 Sample의 Feature
y  → 여러 Sample의 Label
```
