# CPU·GPU Device와 `.to(device)`

> 학습일: 2026-08-20

## 1. 오늘 학습 키워드

- CPU·GPU Device
- `torch.cuda.is_available()`
- Tensor와 Model의 `.to(device)`
- Device 일치
- Batch Unpacking과 Device 이동

## 2. 오늘 학습한 내용을 나만의 언어로 정리하기

### Device 선택과 이동

PyTorch의 `device`는 Tensor나 Model이 CPU 메모리와 GPU 메모리 중 어디에 있는지를 나타낸다.

```python
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
```

`torch.cuda.is_available()`로 GPU 사용 가능 여부를 확인해 실행 Device를 선택한다. Tensor는 기본적으로 CPU에 생성되므로 GPU를 사용하려면 직접 이동해야 한다.

```python
x = x.to(device)
```

Tensor의 `.to(device)`는 이동된 Tensor를 반환하므로 결과를 변수에 다시 저장해야 한다.

### 연산에 참여하는 값의 Device 맞추기

Model과 입력 Tensor가 서로 다른 Device에 있으면 연산할 수 없다. 따라서 둘을 같은 Device로 이동한다.

```python
model = model.to(device)
x = x.to(device)
```

학습 Batch에 입력 `x`와 Label `y`가 함께 들어 있다면 Loss 계산까지 같은 Device에서 이루어지도록 두 Tensor를 각각 이동해야 한다.

```text
batch 전달
→ x, y 분리
→ 각각 같은 device로 이동
→ model 연산과 loss 계산
```

## 3. 학습하며 겪었던 문제점과 해결 과정

### 이해한 내용: Model과 Tensor의 Device 맞추기

GPU 사용 가능 여부에 따라 Device를 선택하고 Tensor를 이동하는 코드를 작성했다. Model과 입력 Tensor도 각각 같은 Device로 이동한 뒤 연산해야 한다는 점을 적용했다.

```python
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

model = model.to(device)
x = x.to(device)
```

---

### 이해 수정: Batch 이동 Helper 함수

#### 처음 이해

입력 `x`와 Label `y`를 각각 `.to(device)`로 이동해야 한다는 것은 알고 있었지만, 함수 안에서 아직 정의되지 않은 `x`와 `y`를 바로 사용했다.

```python
def move_batch_to_device(batch, device):
    x, y = x.to(device), y.to(device)
    return x, y
```

#### 수정된 이해

함수에 전달된 값은 `x`와 `y`가 아니라 두 값이 들어 있는 `batch`다. 따라서 먼저 Batch를 Unpacking한 뒤 각각 이동해야 한다.

```python
def move_batch_to_device(batch, device):
    x, y = batch

    x = x.to(device)
    y = y.to(device)

    return x, y
```

처리 흐름을 `batch 전달 → x, y 분리 → 각각 Device 이동 → 반환` 순서로 이해했다.
