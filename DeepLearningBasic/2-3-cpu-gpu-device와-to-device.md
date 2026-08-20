# CPU·GPU Device와 `.to(device)`

> 학습일: 2026-08-20

## 핵심 정리

`device`는 Tensor나 모델이 CPU 메모리와 GPU 메모리 중 어디에 있는지를 나타낸다. Colab에서 GPU 런타임을 켰다고 해서 Tensor와 모델이 자동으로 GPU로 이동하지는 않는다.

먼저 GPU 사용 가능 여부에 따라 사용할 Device를 정하고, 모델과 입력·정답 Tensor를 모두 같은 Device로 이동해야 한다.

Tensor의 `.to(device)`는 이동된 Tensor를 반환하므로 결과를 변수에 다시 저장해야 한다. Batch Helper 함수에서는 전달받은 `batch`를 먼저 `x`와 `y`로 분리한 뒤 각각 이동한다.

> 결국 “GPU를 켰는가?”보다 “실제로 연산에 참여하는 모델과 모든 Tensor가 같은 Device에 있는가?”를 확인하는 것이 중요하다고 이해했다.

---

## Device의 기본 개념

`device`는 Tensor나 모델이 현재 어느 장치의 메모리에 있는지를 나타낸다.

```text
cpu
→ CPU 메모리에 있음

cuda 또는 cuda:0
→ NVIDIA GPU 메모리에 있음
```

PyTorch Tensor는 기본적으로 CPU에 생성된다.

```python
x = torch.randn(2, 3)
print(x.device)
```

Colab에서 GPU 런타임을 켰더라도 Tensor가 자동으로 GPU로 옮겨지는 것은 아니다. 위 코드는 기본적으로 `cpu`를 출력할 수 있다.

---

## GPU 사용 가능 여부와 Device 선택

GPU를 사용할 수 있는지는 다음 코드로 확인한다.

```python
torch.cuda.is_available()
```

실전에서는 GPU를 사용할 수 있으면 CUDA를, 그렇지 않으면 CPU를 사용하도록 Device를 정할 수 있다.

```python
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
```

전체 흐름은 다음과 같다.

```text
GPU 사용 가능 여부 확인
→ 사용할 Device 결정
→ Tensor와 모델을 같은 Device로 이동
→ 연산
```

---

## Tensor를 다른 Device로 이동하기

Tensor는 `.to(device)`를 이용해 이동한다.

```python
x_device = x.to(device)
```

기존 변수 이름을 계속 사용하려면 다음처럼 다시 저장할 수 있다.

```python
x = x.to(device)
```

Tensor의 `.to(device)`는 이동된 Tensor를 반환한다. 따라서 다음처럼 반환값을 사용하지 않으면 이후 코드의 `x`가 이동된 Tensor를 가리키지 않는다.

```text
x.to(device)
→ 반환값을 저장하지 않음

x = x.to(device)
→ 이동된 Tensor를 x에 다시 저장
```

---

## 모델과 입력 Tensor의 Device 맞추기

모델과 입력 Tensor는 같은 Device에 있어야 한다.

```python
model = nn.Linear(4, 2)
x = torch.randn(5, 4)

model = model.to(device)
x = x.to(device)

out = model(x)
```

모델이 GPU에 있고 입력 Tensor가 CPU에 있는 것처럼 서로 다른 Device에 있으면 Device Mismatch 오류가 발생할 수 있다.

이 코드를 실행하기 전에는 `device`가 먼저 정의되어 있어야 한다.

```python
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
```

### 모델 Output도 직접 이동해야 할까?

처음에는 모델의 결과인 Output까지 직접 `.to(device)`로 옮겨야 하는지 궁금했다.

보통 Output은 따로 이동할 필요가 없다.

```python
model = model.to(device)
x = x.to(device)

output = model(x)
```

모델과 입력이 같은 Device에서 연산되면 Output도 그 Device에서 생성된다.

따라서 다음처럼 Output을 다시 옮기는 것이 핵심은 아니다.

```python
output = output.to(device)
```

대신 Loss 계산처럼 Output과 함께 연산하는 Target이 같은 Device에 있는지를 확인해야 한다.

```text
output.device = cuda
target.device = cpu
→ Loss 계산에서 Device Mismatch가 발생할 수 있음
```

---

## 필수 문제 1: Device 확인과 Tensor 이동

다음처럼 Device를 선택하고 Tensor를 이동했다.

```python
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
print("선택된 device:", device)

x = torch.randn(3, 4)
x_device = x.to(device)

print("x_device.device:", x_device.device)
```

이 코드는 올바르게 작성했다.

핵심은 `x.to(device)`의 반환값을 `x_device`에 저장해 선택된 Device에 있는 새로운 Tensor를 받는 것이다.

---

## 필수 문제 2: 모델과 입력을 같은 Device로 이동

다음 코드에서는 모델과 입력 Tensor를 모두 같은 Device로 이동한 뒤 연산했다.

```python
model = nn.Linear(4, 2)
x = torch.randn(5, 4)

model = model.to(device)
x = x.to(device)

out = model(x)
print("out shape:", out.shape)
```

이 코드도 올바르게 작성했다.

```text
모델을 Device로 이동
→ 입력 Tensor를 같은 Device로 이동
→ 모델 연산
```

---

## Batch 이동 Helper 함수

### `x`와 `y`를 바로 이동하면 될까?

입력과 Label을 한 번에 옮기는 Helper 함수를 처음에는 다음처럼 작성했다.

```python
def move_batch_to_device(batch, device):
    x, y = x.to(device), y.to(device)
    return x, y
```

`x`와 `y`를 각각 `.to(device)`로 이동해야 한다는 방식 자체는 알고 있었다.

하지만 함수 내부에서 `x`와 `y`가 아직 정의되지 않았는데 바로 사용했다. 함수가 전달받은 값은 `x`와 `y`가 아니라 `batch`다.

예제 Batch는 입력 Tensor와 Label Tensor를 묶은 Tuple이다.

```python
batch = (
    torch.randn(2, 4),
    torch.tensor([0, 1])
)
```

따라서 먼저 `batch`를 `x`와 `y`로 분리해야 한다.

```text
Batch 전달받기
→ Batch를 x와 y로 분리
→ x와 y를 각각 Device로 이동
→ 이동된 x와 y 반환
```

수정한 코드는 다음과 같다.

```python
def move_batch_to_device(batch, device):
    x, y = batch

    x = x.to(device)
    y = y.to(device)

    return x, y


batch = (
    torch.randn(2, 4),
    torch.tensor([0, 1])
)

x_moved, y_moved = move_batch_to_device(batch, device)

print(x_moved.device, y_moved.device)
```

이 코드는 올바르게 작성했다.

핵심은 함수로 받은 `batch`를 먼저 Unpacking하는 것이다.

```python
x, y = batch
```

그다음 각 Tensor를 같은 Device로 이동한다.

```python
x = x.to(device)
y = y.to(device)
```

---

## 다시 볼 때 핵심

GPU 런타임을 켜는 것과 Tensor가 실제로 GPU에 있는 것은 서로 다른 문제다.

`torch.cuda.is_available()`로 GPU 사용 가능 여부를 확인하고 사용할 `device`를 정한다.

모델, 입력 Tensor, Label Tensor처럼 같은 연산에 참여하는 대상은 같은 Device에 있어야 한다.

Tensor의 `.to(device)`는 이동된 Tensor를 반환하므로 반환값을 변수에 저장한다.

모델과 입력이 같은 Device에서 연산되면 Output도 같은 Device에서 생성된다. Loss 계산에 참여하는 Target의 Device를 추가로 확인한다.

Batch Helper 함수에서는 전달받은 `batch`를 먼저 `x, y = batch`로 분리한 뒤 두 Tensor를 각각 이동한다.
