# Tensor 생성과 dtype·shape 확인

> 학습일: 2026-08-19

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Tensor의 구조와 주요 속성

Tensor는 딥러닝에서 숫자 데이터를 담는 기본 자료 구조다. Model에 들어가는 데이터는 결국 Tensor 형태로 다뤄진다.

```text
ndim   = Tensor의 차원 수
shape  = 각 차원의 크기
dtype  = 내부 숫자의 자료형
device = Tensor가 저장된 CPU/GPU 위치
```

Shape는 바깥쪽 구조부터 안쪽 순서로 읽는다. 예를 들어 `[32, 5]`는 일반적인 딥러닝 Batch에서 Sample 32개가 있고 각 Sample에 Feature가 5개 있다는 뜻이다.

오류가 발생했을 때는 Model이나 연산이 기대하는 값과 실제 Tensor의 `shape`, `dtype`, `device`가 일치하는지 먼저 확인한다.

### Tensor 생성 방법

`torch.tensor()`는 직접 가지고 있는 값을 Tensor로 만들고, 다른 생성 함수는 인자로 지정한 Shape에 맞춰 값을 채운다.

| 함수 | 의미 |
| --- | --- |
| `torch.tensor(data)` | `data`의 실제 값으로 Tensor 생성 |
| `torch.zeros(5, 3)` | Shape `[5, 3]`을 0으로 채움 |
| `torch.ones(5, 3)` | Shape `[5, 3]`을 1로 채움 |
| `torch.randn(5, 3)` | Shape `[5, 3]`을 Random 실수로 채움 |

Model 입력에는 `float32`가 자주 사용되고 Class Index에는 `long`, 즉 `int64`가 사용될 수 있다. 어떤 Dtype이 필요한지는 단순히 문제 유형만 보는 것이 아니라 사용하는 Loss 함수의 입력 규격을 확인해야 한다.

### 실제 데이터가 Tensor로 들어오는 흐름

실제 대규모 데이터를 하나씩 직접 Tensor로 작성하지는 않는다.

```text
원본 데이터
→ Dataset
→ DataLoader
→ Batch 단위 Tensor
→ Model 입력
```

강의에서 Tensor를 직접 만드는 목적은 모든 데이터를 손으로 입력하기 위해서가 아니라 차원, Shape, Dtype, Device 같은 기본 구조를 이해하기 위해서다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 이진 분류라면 `float32`를 사용하는 것인가?

이진 분류라는 이유만으로 항상 `float32`를 사용하는 것은 아니다.

```text
BCEWithLogitsLoss의 0/1 Target
→ 일반적으로 float32

CrossEntropyLoss의 Class Index Target
→ long(int64)
```

분류 종류만으로 Dtype을 정하기보다 사용하는 Loss 함수가 요구하는 Target Dtype을 확인해야 한다.

---

### 이해 수정: `long`·`int64`·`long long`

#### 처음 이해

`long`은 큰 정수를 표현하는 자료형이고 `long long`도 있었던 것으로 기억했다.

#### 수정된 이해

PyTorch에서 `torch.long`은 `torch.int64`와 같은 64비트 정수형이다. 딥러닝에서는 단순히 큰 숫자를 저장하기 위해서보다 `CrossEntropyLoss`의 Class Index처럼 함수가 `int64`를 요구하기 때문에 자주 사용한다.

`long long`은 C++에서 배웠던 자료형이라는 점도 구분했다.

---

### 질문: Tensor를 왜 직접 만드는가?

현재 강의에서 Tensor를 직접 만드는 것은 실제 데이터를 전부 손으로 입력하기 위해서가 아니다. 직접 만들어보면서 다음 기본 정보를 읽는 연습을 하기 위해서다.

```text
몇 차원인가?
각 차원의 크기는 얼마인가?
내부 숫자의 dtype은 무엇인가?
어느 device에 있는가?
```

---

### 질문: 실제 딥러닝 데이터가 많은데 전부 일일이 Tensor로 만드는가?

그렇지 않다. 실전에서는 대량의 데이터를 Dataset과 DataLoader 등을 통해 가져오고, 여러 Sample을 Batch로 묶은 Tensor 형태로 Model에 전달한다.

```text
shape = [32, 5]
→ Sample 32개
→ Sample마다 Feature 5개
```

---

### 이해 수정: `describe_tensor()`의 동작

#### 처음 이해

`describe_tensor()`를 호출하면 내부에서 반복문을 돌며 Tensor 정보를 자동으로 검사하는 PyTorch 기본 함수라고 생각했다.

#### 수정된 이해

`describe_tensor()`는 강의에서 직접 정의한 사용자 함수이며 PyTorch 기본 함수가 아니다. 함수 내부에 작성된 `shape`, `ndim`, `dtype`, `device` 출력 코드가 위에서 아래로 한 번 실행된다.

여러 Tensor를 반복해서 검사하려면 별도의 반복문이 필요하다. 이 함수를 만드는 목적은 다음 정보를 한 번에 출력해 디버깅을 편하게 하는 것이다.

```text
shape  → 입력 구조가 맞는가?
dtype  → 자료형이 맞는가?
device → CPU/GPU 위치가 맞는가?
```

---

### 이해 수정: `torch.tensor([5, 3])`과 Shape 지정

#### 처음 이해

학생 5명에게 점수 3개가 있는 Tensor를 다음과 같이 만들려고 했다.

```python
x = torch.tensor([5, 3])
```

#### 수정된 이해

`torch.tensor([5, 3])`의 `[5, 3]`은 Shape가 아니라 Tensor에 저장되는 실제 값이다. 따라서 값이 두 개인 1차원 Tensor이고 Shape는 `[2]`다.

학생 5명에게 각각 점수 3개가 있다면 실제 데이터가 5개의 Sample과 3개의 값으로 구성되어야 한다.

```python
x = torch.tensor([
    [80, 90, 85],
    [70, 75, 78],
    [95, 92, 88],
    [60, 65, 70],
    [88, 84, 91]
], dtype=torch.float32)
```

이때 Shape `[5, 3]`은 Sample 5개가 있고 각 Sample에 Feature가 3개 있다는 뜻이다.

다음 두 문법의 차이도 구분했다.

```python
torch.tensor([5, 3])  # 값 5와 3을 저장
torch.randn(5, 3)     # Shape [5, 3]의 Tensor를 생성
```
