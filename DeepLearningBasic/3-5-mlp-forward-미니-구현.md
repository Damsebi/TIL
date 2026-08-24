# MLP Forward 미니 구현

> 학습일: 2026-08-20

## 1. 오늘 학습 키워드

- `nn.Module` 상속
- `__init__`과 `forward`
- Layer 구조와 학습 Parameter
- MLP의 Shape 흐름
- `input_dim`·`hidden_dim`·`output_dim`

## 2. 오늘 학습한 내용을 나만의 언어로 정리하기

### `nn.Module`로 Model 정의하기

`nn.Module`은 PyTorch가 제공하는 Model용 Base Class다. 이를 상속한 새로운 Class에 필요한 Layer와 데이터 흐름을 정의해 원하는 Model을 만든다.

```text
__init__
→ Linear, ReLU 등 사용할 layer 준비

forward
→ 입력 Tensor가 layer를 통과하는 순서 정의
```

Layer의 종류와 입출력 구조는 `__init__`에서 미리 정하지만, Linear 내부의 Weight와 Bias는 학습하면서 변경된다. `forward`에서는 매번 새 Layer를 만들지 않고 `__init__`에서 준비한 Layer를 재사용한다.

### MLP의 Shape 흐름과 차원 검증

MLP에서는 Batch Dimension을 유지하면서 Feature 차원이 Layer 구조에 맞게 바뀐다.

```text
(8, 1, 28, 28)
→ Flatten
(8, 784)
→ Linear(784, 128)
(8, 128)
→ ReLU
(8, 128)
→ Linear(128, 10)
(8, 10)
```

```text
input_dim   = 첫 Linear가 받는 Feature 수
hidden_dim  = 중간 Feature 수
output_dim  = 최종 출력 Feature 수
num_classes = 분류할 Class 수
```

분류 Model에서는 최종 Logits의 마지막 차원이 Class 수와 같아야 한다. Model을 만든 뒤 더미 입력으로 Forward를 실행하고 중간 Shape와 최종 Shape를 확인하면 Linear의 입력 차원 불일치 같은 오류를 미리 찾을 수 있다.

## 3. 학습하며 겪었던 문제점과 해결 과정

### 질문과 이해 수정: `nn.Module`은 기본으로 제공되는가?

#### 처음 이해

PyTorch가 제공하는 기본 `nn.Module` 자체를 튜닝해 원하는 Model로 만드는 것으로 이해했다.

#### 수정된 이해

`nn.Module`은 PyTorch가 기본으로 제공하는 Class지만 직접 수정하는 대상은 아니다. 이를 상속한 새로운 Model Class를 만들고 그 안에 원하는 Layer와 Forward 흐름을 정의한다.

```python
class SimpleMLP(nn.Module):
    ...
```

Unity에서 `MonoBehaviour`를 상속해 새로운 Component를 만드는 것과 비슷하게 이해했다.

---

### 이해 수정: Layer를 정적으로 만든다는 의미

#### 처음 이해

Layer를 `__init__`에서 정적으로 만들어둔다고 이해했다.

#### 수정된 이해

Layer의 구조와 종류를 `__init__`에서 미리 정의한다는 의미에서는 맞다. 하지만 Linear 내부의 Weight와 Bias는 고정되지 않고 학습하면서 계속 변경된다.

`__init__`에서는 Model이 사용할 Layer를 준비하고, `forward`에서는 이미 만든 Layer를 어떤 순서로 사용할지 작성한다.

```python
def forward(self, x):
    x = self.fc1(x)
    x = self.relu(x)
    x = self.fc2(x)
    return x
```

Forward 안에서 새로운 Linear를 만들지 않고 `self.fc1`, `self.fc2`처럼 미리 등록한 Layer를 사용한다.

---

### 이해한 내용: Tensor Shape와 `input_dim`

28×28 흑백 이미지 8장을 입력하면 Batch Size `8`은 유지되고 Feature 차원만 바뀐다. ReLU는 값을 바꾸지만 Shape는 바꾸지 않는다.

```text
(8, 1, 28, 28)
→ (8, 784)
→ (8, 128)
→ (8, 128)
→ (8, 10)
```

Flatten 이후 Feature 수와 첫 Linear가 기대하는 `input_dim`은 같아야 한다.

```text
1 × 28 × 28 = 784
```

```python
nn.Linear(784, hidden_dim)
```

`input_dim=28`로 지정하면 실제 입력의 마지막 차원 `784`와 Layer가 기대하는 크기가 달라 오류가 발생한다.

---

### 이해 수정: `TinyMLP` 구현

#### 처음 시도

`forward()` 안에서 `nn.Linear`와 ReLU를 새로 만들려고 했다.

#### 수정된 이해

Layer는 `__init__`에서 미리 준비하고 `forward`에서는 `fc1 → ReLU → fc2 → return` 순서로 실행해야 한다.

```python
class TinyMLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
```

입력이 `(5, 4)`이고 Model이 `TinyMLP(4, 8, 3)`이면 Shape는 다음과 같이 흐른다.

```text
(5, 4)
→ (5, 8)
→ (5, 8)
→ (5, 3)
```

---

### 질문: `output_dim`을 Class 수와 맞추는 문제는 별도 구현이 필요한가?

새로운 Model을 구현하는 문제라기보다 이미 계산된 Logits의 마지막 차원과 Class 수가 같은지 확인하는 문제다.

```python
num_classes = 3

print(num_classes)
print(logits.shape[-1])
```

`TinyMLP(4, 8, 3)`의 마지막 인자 `3`이 `output_dim`이고 최종 Logits의 Shape가 `(5, 3)`이므로 다음 관계가 성립한다.

```text
num_classes
= output_dim
= logits.shape[-1]
```
