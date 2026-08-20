# Tensor 생성과 dtype·shape 확인

> 학습일: 2026-08-19

## 핵심 정리

PyTorch에서 Tensor는 딥러닝 모델이 계산할 숫자 데이터를 담는 다차원 자료형이다. 이미지나 텍스트처럼 원래 숫자로 보이지 않는 데이터도 모델에 들어가기 전에는 숫자로 표현된다.

Tensor를 볼 때는 값만 확인하기보다 `shape`, `ndim`, `dtype`, `device`를 먼저 확인하는 습관이 중요하다. 이 정보가 모델이 기대하는 입력과 맞지 않으면 학습 코드에서 오류가 발생할 수 있다.

`torch.tensor([5, 3])`은 Shape를 `[5, 3]`으로 지정한 것이 아니라 값 5와 3을 담은 1차원 Tensor를 만든 것이다. 반면 `torch.randn(5, 3)`에서는 인자 `5, 3`이 Shape를 뜻한다.

> 결국 Tensor를 직접 만드는 문법을 외우는 것보다 “몇 차원인가, 각 차원의 크기는 얼마인가, 어떤 자료형이며 어디에 저장되어 있는가?”를 읽을 수 있는 것이 더 중요하다고 이해했다.

---

## Tensor의 기본 개념

딥러닝 모델은 숫자를 입력받아 계산한 뒤 숫자를 출력한다.

PyTorch에서 이런 숫자 데이터를 담는 기본 자료구조가 Tensor다.

```text
이미지
텍스트
정답 Label
기타 데이터
→ 숫자로 표현
→ Tensor에 담음
→ 모델에 입력
```

현재는 Tensor를 다음처럼 이해한다.

> Tensor는 딥러닝 모델이 사용하는 숫자 상자다.

---

## Tensor의 차원

Tensor의 차원은 숫자가 몇 겹의 구조로 들어 있는지를 나타낸다.

```text
7
→ 0차원 Scalar

[1, 2, 3]
→ 1차원 Vector

[
    [1, 2, 3],
    [4, 5, 6]
]
→ 2차원 Matrix

[
    [
        [1, 2, 3],
        [4, 5, 6]
    ],
    [
        [7, 8, 9],
        [10, 11, 12]
    ]
]
→ 3차원 Tensor
```

`ndim`은 Tensor가 몇 차원인지 나타내고, `shape`는 각 차원에 데이터가 몇 개씩 있는지 나타낸다.

```text
shape = [2, 3]
ndim  = 2
```

이 Tensor는 바깥 묶음이 2개이고 각 묶음에 값이 3개 있는 2차원 구조다.

---

## Shape 읽는 방법

Shape는 가장 바깥쪽 구조부터 안쪽으로 읽는다.

```text
[10, 4]
```

딥러닝의 표 데이터라고 가정하면 Sample 10개가 있고 각 Sample에 Feature가 4개 있다는 뜻으로 읽을 수 있다.

이미지 데이터가 다음 Shape를 가진다고 하자.

```text
[32, 3, 224, 224]

32  → 이미지 32장
3   → 채널 3개
224 → 높이
224 → 너비
```

처음부터 행렬 수식처럼 생각하기보다 다음 질문을 반복하면 읽기 쉽다.

```text
가장 바깥에 몇 개가 있는가?
그 안에는 몇 개가 있는가?
그보다 안에는 몇 개가 있는가?
```

---

## Tensor의 기본 속성

Tensor는 값 외에도 자신의 구조와 저장 상태에 관한 정보를 가진다.

```text
shape
→ Tensor가 어떤 모양인지

ndim
→ 몇 차원인지

dtype
→ 내부 숫자의 자료형

device
→ CPU와 GPU 중 어디에 있는지
```

다음 정보를 가진 Tensor가 있다고 하자.

```text
shape  = [3, 4]
ndim   = 2
dtype  = float32
device = cpu
```

CPU에 저장된 `float32` 자료형의 `3 × 4` 크기 2차원 Tensor라고 읽을 수 있다.

---

## dtype

### 이진 분류라면 항상 `float32`를 사용할까?

처음에는 이진 분류의 정답 Tensor에는 무조건 `float32`를 사용한다고 이해했다.

하지만 분류 종류만 보고 자료형을 정하는 것은 아니다. 어떤 Loss가 Target에 어떤 자료형을 요구하는지를 함께 확인해야 한다.

대표적으로 현재 확인한 조합은 다음과 같다.

```text
BCEWithLogitsLoss
+ 0/1 Target
→ 보통 float32

CrossEntropyLoss
+ Class Index Target
→ long(int64)
```

> 이진 분류이기 때문에 무조건 `float32`인 것이 아니라 `BCEWithLogitsLoss`가 실수형 Target을 사용하기 때문에 `float32`를 사용하는 경우가 많다고 이해했다.

---

## `long`, `int64`, C++의 `long long`

### `long`은 큰 정수를 저장하는 자료형 아닌가?

기존에 배운 `long`은 큰 정수를 저장하는 자료형이라는 기억이 있어 PyTorch의 `torch.long`도 단순히 큰 숫자를 위한 것인지 궁금했다.

PyTorch에서는 다음 두 자료형이 같다.

```python
torch.long
torch.int64
```

즉 `torch.long`은 64비트 정수형이다.

딥러닝 코드에서는 큰 숫자를 저장하기 위해서라기보다 다음과 같은 Class Index를 Loss가 `int64`로 요구하기 때문에 자주 사용한다.

```text
0 = 고양이
1 = 강아지
2 = 새
```

### `long long`도 있지 않았나?

`long long`은 C/C++에서 봤던 자료형이고, C#의 `long`은 64비트 정수형이다. PyTorch의 `torch.long`도 `torch.int64`와 같은 64비트 정수형이다.

언어마다 비슷한 이름이 서로 다른 방식으로 사용될 수 있으므로 PyTorch 코드에서는 `torch.long = torch.int64`라는 관계를 기준으로 이해한다.

---

## Tensor 생성 방법

### 가지고 있는 값으로 생성하기

`torch.tensor()`는 직접 가지고 있는 값을 Tensor로 만든다.

```python
x = torch.tensor([
    [1, 2, 3],
    [4, 5, 6]
])
```

### 특정 값이나 랜덤값으로 생성하기

```python
zeros = torch.zeros(4, 5)
ones = torch.ones(4, 5)
random_values = torch.randn(4, 5)
```

```text
torch.zeros()
→ 모든 값이 0인 Tensor

torch.ones()
→ 모든 값이 1인 Tensor

torch.randn()
→ 랜덤한 실수 값이 들어 있는 Tensor
```

위 세 Tensor의 Shape는 모두 `[4, 5]`다.

딥러닝의 표 데이터라고 가정하면 Sample 4개가 있고 각 Sample에 Feature가 5개 있다고 해석할 수 있다.

---

## 왜 Tensor를 직접 만들까?

### 실전에서도 모든 데이터를 직접 작성할까?

Tensor를 직접 만드는 문법 자체가 최종 목적은 아니다.

현재 강의에서 작은 Tensor를 직접 만들어보는 이유는 다음 정보를 익히기 위해서다.

- Tensor의 구조
- Shape
- 차원
- dtype
- device

실전에서는 실제 데이터를 모델이 계산할 수 있는 Tensor 형태로 변환해서 사용한다.

---

## 대량 데이터도 하나씩 Tensor로 만들까?

처음에는 많은 데이터를 모두 `torch.tensor()` 코드로 하나씩 작성해야 하는 것처럼 느껴졌다.

실전에서는 데이터를 손으로 하나씩 Tensor로 만들지 않는다. 현재 이해한 대략적인 흐름은 다음과 같다.

```text
CSV / 이미지 / 파일 등의 데이터
→ Dataset
→ DataLoader
→ Batch 단위로 로드
→ Tensor
→ 모델
```

데이터가 100,000개여도 한 번에 모두 모델에 넣지 않고 다음처럼 Batch 단위로 가져올 수 있다.

```text
전체 데이터 100,000개

32개
32개
32개
...
```

따라서 Tensor 생성 방법을 배우는 목적은 나중에 Dataset과 DataLoader가 전달한 Tensor를 보고 이해하기 위해서다.

```python
for X, y in dataloader:
    print(X.shape)
```

결과가 `[32, 5]`라면 Sample 32개와 Sample마다 5개의 Feature가 있다고 읽을 수 있다.

---

## `describe_tensor()` 디버깅 함수

### PyTorch가 제공하는 자동 검사 함수일까?

처음에는 `describe_tensor()`를 호출하면 PyTorch가 내부에서 반복문을 돌며 여러 Tensor를 자동으로 검사한다고 생각했다.

하지만 `describe_tensor()`는 PyTorch가 제공하는 함수가 아니라 강의에서 직접 만든 사용자 정의 함수다.

```python
def describe_tensor(name, tensor):
    print(name)
    print(tensor.shape)
    print(tensor.ndim)
    print(tensor.dtype)
    print(tensor.device)
```

함수를 한 번 호출하면 내부 코드가 위에서 아래로 한 번 실행될 뿐 자동으로 반복되지는 않는다.

여러 Tensor를 검사하려면 별도의 반복문이 필요하다.

```python
for name, tensor in tensors:
    describe_tensor(name, tensor)
```

이 함수의 목적은 자주 사용하는 Tensor 정보 출력 코드를 하나로 묶어 디버깅을 편하게 만드는 것이다.

---

## 연습문제: 학생 5명과 점수 3개

### `torch.tensor([5, 3])`은 `[5, 3]` Shape일까?

학생 5명의 점수 3개를 담으려고 다음 코드를 작성했다.

```python
x = torch.tensor([5, 3])

print(x.shape)
print(x.ndim)
print(x.dtype)
print(x.device)
```

처음에는 `[5, 3]`이 학생 수와 점수 개수를 지정한다고 생각했다.

하지만 `torch.tensor([5, 3])`의 `[5, 3]`은 Shape가 아니라 실제로 저장할 값 5와 3이다.

```text
값    = [5, 3]
shape = [2]
ndim  = 1
```

반면 다음 함수들의 인자 `5, 3`은 Shape를 지정한다.

```python
torch.zeros(5, 3)
torch.ones(5, 3)
torch.randn(5, 3)
```

학생 5명과 학생마다 점수 3개를 직접 입력한다면 데이터가 5줄이고 각 줄에 값이 3개 있어야 한다.

```python
x = torch.tensor([
    [80, 90, 85],
    [70, 75, 78],
    [95, 92, 88],
    [60, 65, 70],
    [88, 84, 91]
], dtype=torch.float32)

print(x.shape)
print(x.ndim)
print(x.dtype)
print(x.device)
```

예상되는 정보는 다음과 같다.

```text
shape  = [5, 3]
ndim   = 2
dtype  = float32
device = cpu
```

Shape `[5, 3]`은 Sample인 학생이 5명이고 각 Sample에 점수 Feature가 3개 있다는 뜻이다.

---

## 다시 볼 때 핵심

Tensor는 숫자 데이터를 담는 다차원 자료형이다.

`ndim`은 차원의 개수이고 `shape`는 각 차원의 크기다. Shape는 가장 바깥쪽 구조부터 안쪽으로 읽는다.

`dtype`은 내부 숫자의 자료형이고 `device`는 Tensor가 CPU와 GPU 중 어디에 있는지를 나타낸다.

Target의 dtype은 단순히 분류 종류만 보고 정하는 것이 아니라 사용하는 Loss가 요구하는 형태를 확인해야 한다.

`torch.tensor([5, 3])`은 값 5와 3을 담지만 `torch.randn(5, 3)`은 `[5, 3]` Shape의 Tensor를 만든다.

Tensor 오류가 발생하면 값만 보지 말고 `shape`, `dtype`, `device`부터 확인한다.
