# Shape·Device 오류 디버깅

> 학습일: 2026-08-20

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 오류를 먼저 분류하기

PyTorch 오류가 발생하면 바로 Shape를 바꾸기보다 어떤 종류의 문제인지 먼저 분류한다. 그다음 오류가 난 연산에 함께 참여하는 Tensor의 정보를 확인한다.

```text
shape  → 입력 구조와 연산 조건이 맞는가?
dtype  → 연산이나 Loss가 요구하는 자료형인가?
device → 함께 계산하는 객체가 같은 위치에 있는가?
```

### `nn.Linear`의 입력과 Batch Dimension

`nn.Linear`는 입력 Tensor의 마지막 차원을 Feature 차원으로 사용한다. 따라서 입력의 마지막 차원과 Layer의 `in_features`가 같아야 한다.

```text
입력 Shape = (8, 5)
→ 마지막 차원 5
→ nn.Linear(5, ...)
```

단일 Sample `(5,)`를 Batch 형태로 만들어야 할 때는 크기 1인 Batch Dimension을 앞에 추가한다.

```text
(5,) → unsqueeze(0) → (1, 5)
```

`squeeze()`와 `unsqueeze()`는 모든 Shape Mismatch를 해결하는 함수가 아니다. 크기 1인 차원을 제거하거나 추가하는 것이 실제로 필요한 경우에만 사용한다.

### Device Mismatch 확인

Device 오류에서는 같은 연산에 참여하는 Model, 입력 Tensor, Target 등이 같은 Device에 있는지 비교한다.

`torch.cuda.is_available()`은 CUDA를 사용할 수 있는 환경인지 확인하는 함수다. 실제 Device Mismatch의 직접적인 원인은 CUDA 사용 가능 여부가 아니라 연산에 참여하는 객체들의 Device가 서로 다른 것이다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 디버깅 Checklist에는 무엇을 추가해야 하는가?

이번 문제는 오류 해결 방법을 길게 적는 것이 아니라 Shape·Device 오류가 발생했을 때 먼저 확인할 항목을 정리하는 문제였다.

```python
checklist = [
    "입력과 target의 shape를 확인한다.",
    "입력의 마지막 차원과 Linear의 in_features를 비교한다.",
    "모델과 입력/target이 같은 device에 있는지 확인한다.",
]
```

Broadcasting이나 `squeeze()`·`unsqueeze()`는 정보를 확인한 뒤 필요할 때 선택하는 해결 방법이므로 기본 Checklist에 반드시 넣을 필요는 없다.

---

### 이해 수정: `squeeze()`·`unsqueeze()`와 Shape 오류

#### 처음 이해

Tensor의 차원이 다르면 `squeeze()`나 `unsqueeze()`를 사용해 Shape를 맞출 수 있다고 생각했다.

#### 수정된 이해

단순히 Shape가 다르다는 이유로 사용하는 것은 아니다. `unsqueeze()`는 크기 1인 새 차원이 필요할 때 사용하고, `squeeze()`는 크기가 1인 차원을 제거해야 할 때 사용한다.

이번 실습에서는 단일 Sample `(5,)`에 Batch Dimension이 필요했으므로 다음 수정이 적절했다.

```text
(5,) → unsqueeze(0) → (1, 5)
```

---

### 이해한 내용: Device 오류 확인

Device 오류가 발생하면 다음 정보를 확인한다.

```text
torch.cuda.is_available() → CUDA 사용 가능 환경인지 확인
Model의 device            → Parameter가 위치한 Device 확인
Tensor의 device           → 입력과 Target의 Device 확인
```

환경 확인도 필요하지만, 실제 Mismatch를 찾을 때는 같은 연산에 참여하는 객체들의 Device가 서로 같은지 비교하는 것이 더 직접적이다.

---

### 질문: 결과 `output`의 Device도 따로 맞춰야 하는가?

일반적으로 따로 이동할 필요는 없다.

```python
model = model.to(device)
x = x.to(device)

output = model(x)
```

Model과 입력이 같은 Device에서 연산되면 Output도 해당 Device에서 생성된다. 대신 이후 Loss 계산에 함께 참여하는 Target의 Device가 Output과 같은지는 확인해야 한다.

---

### 이해한 내용: Shape 오류 실습

입력의 마지막 Feature 수가 5이므로 `in_features=5`가 맞다.

```python
x = torch.randn(8, 5)
model = nn.Linear(5, 2)
```

단일 Sample에는 `unsqueeze(0)`으로 Batch Dimension을 추가했다.

```python
single_sample = torch.randn(5)
batch_sample = single_sample.unsqueeze(0)
```

```text
(5,) → (1, 5)
```
