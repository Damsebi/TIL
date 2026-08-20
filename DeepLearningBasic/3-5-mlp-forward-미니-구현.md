# MLP Forward 미니 구현

> 학습일: 2026-08-20

## 핵심 정리

`nn.Module`은 PyTorch가 제공하는 신경망 모델용 Base Class다. `nn.Module` 자체를 수정하는 것이 아니라 이를 상속한 Class에 필요한 Layer와 데이터 흐름을 정의해 나만의 Model을 만든다.

`__init__`에서는 Model이 사용할 Layer를 만들고, `forward`에서는 입력이 그 Layer들을 어떤 순서로 통과할지 정의한다. Layer의 구조는 미리 정하지만 그 안의 Weight와 Bias는 학습하면서 계속 바뀐다.

`nn.Module`을 상속한 Model은 `model.forward(x)`를 직접 호출하기보다 `model(x)`로 호출한다. 그러면 PyTorch의 Module 호출 과정을 거쳐 `forward(x)`가 실행된다.

> 결국 Model을 구현할 때는 `__init__`에서 Layer를 준비하고, `forward`에서는 이미 준비된 Layer에 Tensor를 차례로 통과시킨 뒤 결과를 반환한다.

---

## `nn.Module`의 의미

### `nn.Module`은 PyTorch에서 기본으로 제공할까?

처음에는 `nn.Module`을 가져와 원하는 형태로 튜닝한다고 이해했다. 하지만 이 표현은 `nn.Module` 자체를 직접 수정하는 것처럼 받아들일 수 있었다.

`nn.Module`은 PyTorch가 기본으로 제공하는 신경망 Model용 Base Class다. 직접 수정하는 것이 아니라 상속하여 새로운 Model Class를 정의한다.

```python
import torch.nn as nn


class SimpleMLP(nn.Module):
    ...
```

Unity에서 `MonoBehaviour`를 상속하여 `Player`나 `Enemy` 같은 Class를 만드는 것과 비슷하게 이해했다.

```text
nn.Module
→ 신경망 Model의 공통 기반 기능 제공

SimpleMLP(nn.Module)
→ 필요한 구조와 동작을 추가한 나만의 Model
```

`nn.Module`을 상속하면 다음과 같은 기능을 사용할 수 있다.

- Model 내부에 등록된 Parameter 관리
- `.to(device)`를 통한 Device 이동
- `train()`과 `eval()`을 통한 학습·평가 Mode 전환
- `model(x)` 호출을 통한 `forward(x)` 실행

---

## `nn.Sequential`과 직접 만든 Module

`nn.Sequential`은 Layer를 등록된 순서대로 통과시키는 단순한 구조에 편리하다.

```python
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)
```

직접 `nn.Module`을 상속한 Class를 만들면 `forward`에서 데이터 흐름을 직접 정의할 수 있다.

```python
class SimpleMLP(nn.Module):
    ...
```

```text
nn.Sequential
→ 등록한 Layer를 정해진 순서대로 실행

nn.Module 상속 Class
→ Model 구조와 Forward 흐름을 직접 정의
```

이번 실습처럼 순서가 단순한 MLP는 두 방식으로 모두 만들 수 있다. 직접 Class를 작성하는 방식은 이후 조건문, 여러 입력, Skip Connection처럼 더 복잡한 흐름을 표현할 때 확장하기 좋다.

---

## `__init__`과 `forward`의 역할

`__init__`은 Model에서 사용할 부품인 Layer를 준비하는 곳이다.

```python
def __init__(self):
    super().__init__()

    self.flatten = nn.Flatten()
    self.fc1 = nn.Linear(784, 128)
    self.relu = nn.ReLU()
    self.fc2 = nn.Linear(128, 10)
```

`super().__init__()`은 부모 Class인 `nn.Module`의 초기화 과정을 실행한다. 그다음 Layer를 `self.fc1`과 같은 속성으로 저장하면 Module과 Parameter가 Model 내부에 등록되어 PyTorch가 관리할 수 있다.

`forward`는 준비한 Layer를 어떤 순서로 사용할지 정의하는 곳이다.

```python
def forward(self, x):
    x = self.flatten(x)
    x = self.fc1(x)
    x = self.relu(x)
    x = self.fc2(x)

    return x
```

```text
__init__
→ 사용할 Layer 준비 및 등록

forward
→ 입력이 Layer를 통과하는 순서 정의
```

---

## Layer를 미리 만드는 이유

처음에는 Layer를 `__init__`에서 만드는 것을 Layer를 정적으로 만든다고 이해했다. 하지만 이 표현은 Layer 내부의 값도 고정되어 변하지 않는다는 의미로 오해할 수 있었다.

일반적으로 Model의 Layer 구조는 `__init__`에서 한 번 정의한다.

```text
Model 구조
784 → 128 → 10
→ 미리 정의
```

`forward`가 실행될 때마다 새로운 `nn.Linear`를 만드는 것이 아니라, `__init__`에서 만든 같은 Layer를 반복해서 사용한다.

하지만 Layer 내부의 학습 가능한 값은 고정된 것이 아니다.

```text
Weight와 Bias
→ 학습 과정에서 계속 변화
```

따라서 미리 정하는 것은 주로 Layer의 연결 구조와 입출력 차원이며, 학습을 통해 바꾸는 것은 등록된 Parameter 값이다.

---

## `SimpleMLP` 구현

이번에 구현한 전체 Model은 다음과 같다.

```python
import torch
import torch.nn as nn


class SimpleMLP(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=128, num_classes=10):
        super().__init__()

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        logits = self.fc2(x)

        return logits
```

기본 구조는 다음과 같다.

```text
784 → 128 → 10

784
→ 입력 Feature 수

128
→ hidden_dim, 은닉층 Feature 수

10
→ num_classes, 최종 Class 수
```

첫 번째 Linear는 Feature를 784개에서 128개로 바꾼다.

```python
self.fc1 = nn.Linear(784, 128)
```

ReLU는 이번 강의에서 활성화 함수의 세부 원리보다 `fc1`과 `fc2` 사이에서 값을 변환하되 Shape는 유지한다는 수준으로 이해했다.

```python
self.relu = nn.ReLU()
```

마지막 Linear는 Feature 128개를 Class별 출력값 10개로 바꾼다.

```python
self.fc2 = nn.Linear(128, 10)
```

---

## Tensor Shape 흐름

이미지 8장을 더미 입력으로 만들었다.

```python
images = torch.randn(8, 1, 28, 28)
```

전체 Shape 흐름은 다음과 같다.

```text
(8, 1, 28, 28)
        ↓ Flatten
(8, 784)
        ↓ Linear(784, 128)
(8, 128)
        ↓ ReLU
(8, 128)
        ↓ Linear(128, 10)
(8, 10)
```

Batch Size 8은 유지되고 Feature 차원만 Layer에 따라 바뀐다.

```text
Flatten
→ 1 × 28 × 28 = 784

fc1
→ 784에서 128로 변경

ReLU
→ Shape 유지

fc2
→ 128에서 10으로 변경
```

앞 단계의 마지막 Feature 차원은 다음 Linear의 입력 차원과 일치해야 한다.

```text
이전 단계의 마지막 Feature 차원
= 다음 Linear의 in_features
```

예를 들어 `input_dim=28`로 Model을 만들면 Flatten 결과 784와 첫 번째 Linear의 입력 차원 28이 일치하지 않아 Runtime Error가 발생한다.

---

## Logit의 의미

`logits`는 각 Class에 대한 Model의 최종 출력 점수다.

```text
[-1.2, 0.5, 2.1, -0.3, 0.8, 4.7, 1.0, -2.0, 0.2, 0.4]
```

Class가 10개이면 Sample 하나마다 10개의 Logit이 나온다.

```text
logits.shape = (Batch Size, Class 수)
```

이번 복습에서는 Logit을 확률로 바꾸는 과정은 다루지 않고 Class별 최종 점수라는 의미까지만 이해했다.

---

## `model(images)`와 `forward`

### `forward`를 만들었는데 왜 직접 호출하지 않을까?

`nn.Module`을 상속한 Model은 다음과 같이 호출한다.

```python
logits = model(images)
```

그러면 `nn.Module`의 내부 호출 과정을 거쳐 작성한 `forward(images)`가 실행된다.

```text
model(images)
↓
nn.Module의 호출 처리
↓
forward(images)
↓
logits 반환
```

PyTorch는 이 호출 과정에서 Module Hook 등 `forward` 전후에 필요한 기능을 처리할 수 있다. 따라서 일반적인 사용에서는 `model.forward(images)`를 직접 호출하지 않고 `model(images)`를 사용한다.

---

## 중간 Shape를 출력한 디버깅

Model의 Shape 오류를 찾기 위해 처음에는 각 Layer를 지난 뒤 Shape를 출력할 수 있다.

```python
def forward(self, x):
    print("input  :", x.shape)

    x = self.flatten(x)
    print("flatten:", x.shape)

    x = self.fc1(x)
    print("fc1    :", x.shape)

    x = self.relu(x)
    print("relu   :", x.shape)

    logits = self.fc2(x)
    print("fc2    :", logits.shape)

    return logits
```

예상 출력은 다음과 같다.

```text
input  : torch.Size([8, 1, 28, 28])
flatten: torch.Size([8, 784])
fc1    : torch.Size([8, 128])
relu   : torch.Size([8, 128])
fc2    : torch.Size([8, 10])
```

학습 초기와 디버깅 단계에서는 유용하지만, 확인이 끝난 뒤에도 모든 Forward마다 불필요한 출력이 발생하지 않도록 최종 Model에서는 지나치게 많은 `print`를 제거한다.

---

## `hidden_dim`과 `num_classes`

Model 구조의 숫자를 생성자 인자로 받으면 같은 Class로 여러 크기의 Model을 만들 수 있다.

```python
model = SimpleMLP(
    input_dim=784,
    hidden_dim=64,
    num_classes=5
)
```

이 Model의 구조는 다음과 같다.

```text
784 → 64 → 5
```

`hidden_dim`은 은닉층의 Feature 수이고, `num_classes`는 최종 분류할 Class 수이자 Logit의 마지막 차원이다.

```text
784 → 32  → 5
784 → 64  → 5
784 → 128 → 5
```

Hidden Size가 달라도 `num_classes=5`라면 최종 출력 Shape는 모두 `(Batch Size, 5)`다.

---

## Parameter 수와 출력 Shape 검증

Model에서 학습 대상으로 설정된 Parameter 수는 다음과 같이 계산할 수 있다.

```python
def count_parameters(model):
    return sum(
        p.numel()
        for p in model.parameters()
        if p.requires_grad
    )
```

`model.parameters()`는 Model에 등록된 Parameter를 순회하고, `p.numel()`은 각 Parameter Tensor의 원소 수를 센다. `p.requires_grad` 조건을 사용하면 그중 Gradient 계산이 활성화된 Parameter만 합산한다.

출력 Shape는 `assert`로 검증할 수 있다.

```python
expected_shape = (8, 10)
assert logits.shape == expected_shape
```

조건이 거짓이면 즉시 `AssertionError`가 발생하므로 학습 전에 Model의 출력 규격이 예상과 같은지 확인할 수 있다.

```text
Model 생성
↓
더미 입력 생성
↓
Forward 실행
↓
출력 Shape 검증
↓
문제가 없으면 학습
```

---

## `TinyMLP` 구현에서 겪은 문제

### 첫 번째 시도: `forward`에서 Layer 다시 만들기

처음에는 `forward` 안에서 새로운 Layer를 만들려고 했다.

```python
def forward(self, x):
    self.fc1 = nn.Linear(self.input_dim, self.output_dim)
    self.relu = nn.ReLU()
    self.fc2 = nn.Linear(self.input_dim, self.output_dim)
    return self.fc2(self.fc1(x))
```

이 코드에는 다음 문제가 있었다.

- 실행할 때마다 `forward` 안에서 Layer를 새로 만든다.
- `self.input_dim`과 `self.output_dim`을 속성으로 저장한 적이 없다.
- 만들어 둔 ReLU를 실제 계산 순서에 적용하지 않았다.
- `fc1`의 출력 차원과 `fc2`의 입력 차원이 이어진다는 구조가 반영되지 않았다.

Layer를 Forward마다 다시 만들면 같은 Parameter를 반복해서 학습하는 Model이 되지 않는다. Model이 학습할 Layer는 `__init__`에서 한 번 만들고 등록해야 한다.

### 두 번째 시도: 정의하지 않은 ReLU 호출

두 번째 시도는 다음과 같았다.

```python
def forward(self, x):
    x = self.fc1(x)
    x = self.ReLU()
    x = self.fc2(x)
```

여기에도 세 가지 문제가 있었다.

- `self.ReLU`를 `__init__`에서 정의하지 않았다.
- ReLU에 변환할 입력 `x`를 전달하지 않았다.
- 계산 결과를 돌려주는 `return`이 빠졌다.

### 수정한 `TinyMLP`

최종적으로 Layer 생성과 실행을 분리해 다음과 같이 수정했다.

```python
class TinyMLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)

        return x
```

실행 코드는 다음과 같다.

```python
model = TinyMLP(4, 8, 3)
x = torch.randn(5, 4)

logits = model(x)

print("logits shape:", logits.shape)
```

Shape 흐름은 다음과 같다.

```text
(5, 4)
↓ fc1: 4 → 8
(5, 8)
↓ ReLU
(5, 8)
↓ fc2: 8 → 3
(5, 3)
```

```text
logits shape: torch.Size([5, 3])
```

이번 구현을 통해 다시 확인한 역할은 다음과 같다.

```text
Layer 생성
→ __init__

Layer 실행
→ forward

Forward 마지막
→ 결과 return
```

---

## `output_dim`과 Class 수 확인

다음 연습은 새로운 Model을 구현하는 문제가 아니라 최종 출력 차원과 Class 수가 같은지 확인하는 문제였다.

```python
num_classes = 3

print("num_classes:", num_classes)
print("model output dim:", logits.shape[-1])
```

`TinyMLP(4, 8, 3)`의 마지막 인자 3은 `output_dim`이다. 따라서 출력 `logits`의 Shape는 `(5, 3)`이고 마지막 차원도 3이다.

```text
num_classes
= 마지막 Linear의 out_features
= logits.shape[-1]
```

코드로 관계를 검증할 수도 있다.

```python
assert logits.shape[-1] == num_classes
```

---

## 다시 볼 때 핵심

`nn.Module`은 수정하는 대상이 아니라 상속하여 나만의 Model을 만드는 Base Class다.

`__init__`에서는 Layer를 만들고 Model에 등록하며, `forward`에서는 이미 만든 Layer에 입력을 순서대로 통과시킨다. Forward 안에서 매번 새로운 Linear를 만들지 않는다.

Model의 Layer 구조는 미리 정하지만 Layer 내부의 Weight와 Bias는 학습하면서 바뀐다.

`model(x)`를 호출하면 `nn.Module`의 내부 호출 처리를 거쳐 `forward(x)`가 실행되므로 일반적으로 `model.forward(x)`를 직접 호출하지 않는다.

Batch 차원은 유지되고 Feature 차원은 `Flatten → fc1 → ReLU → fc2`를 지나며 바뀐다. 앞 단계의 마지막 Feature 차원과 다음 Linear의 `in_features`가 일치해야 한다.

분류 Model에서는 `num_classes`, 마지막 Linear의 `out_features`, `logits.shape[-1]`이 서로 같아야 한다.
