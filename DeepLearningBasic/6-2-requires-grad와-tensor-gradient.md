# `requires_grad`와 Tensor Gradient

> 학습일: 2026-08-25

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

이번에는 **값을 계산에 쓰는 것과 그 값이 만들어진 경로까지 미분하는 것은 별개**라고 이해했다. Gradient가 필요하지 않을 때도 어디까지 제외할지에 따라 사용하는 방법이 다르다.

| 방법 | 제외하는 대상 |
| --- | --- |
| `torch.no_grad()` | 해당 코드 구간에서 실행하는 연산의 Gradient 추적 |
| `detach()` | 반환된 Tensor에서 이전 계산으로 이어지는 Gradient 연결 |
| Parameter의 `requires_grad=False` | 해당 Parameter에 대한 Gradient 계산 |

학습할 때는 추적 대상 연산들이 계산 그래프로 연결된다. `backward()`가 이를 따라 Gradient를 계산하고, 기본적으로 학습 대상 Leaf Tensor의 `.grad`에 저장한다. 실제 Parameter 수정은 여전히 `optimizer.step()`의 역할이다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 계산 그래프는 사람이 보는 그림인가? PyTorch도 그래프 형태로 기억하는가?

그림으로 그릴 수는 있지만, 그림 파일을 저장한다는 뜻은 아니다. PyTorch가 **어떤 Tensor가 어떤 연산을 거쳐 다음 값을 만들었는지 연결 관계를 실제 구조로 기록**한다.

```text
w ──┐
    × → y → 제곱 → loss
x ──┘
```

Gradient 추적이 켜진 연산에서는 이 연결을 거꾸로 따라갈 수 있어서 `loss.backward()`가 미분을 계산한다. `grad_fn`은 Tensor를 만든 연산과 역전파 연결을 확인하는 방법이다.

---

### 이해한 내용: Leaf·Non-leaf와 `.is_leaf`

이번처럼 Gradient를 추적하는 Tensor에서는 **직접 만든 시작 Tensor인지, 추적된 연산의 결과인지**로 구분했다.

```python
import torch

w = torch.tensor(3.0, requires_grad=True)
y = w * 2

print(w.is_leaf)  # True
print(y.is_leaf)  # False
```

`w`는 Leaf이고 `y`는 Non-leaf다. `.is_leaf`는 이 구분을 `True / False`로 알려주는 속성이다. 그래프 그림의 위쪽·아래쪽 위치를 기준으로 판단하는 것은 아니다.

다만 **연산 결과면 무조건 Non-leaf인 것은 아니다.** PyTorch는 `requires_grad=False`인 Tensor도 Leaf로 취급하므로, 추적 여부까지 함께 봐야 한다. [PyTorch의 Leaf 판정 기준](https://docs.pytorch.org/docs/2.13/generated/torch.Tensor.is_leaf.html)

---

### 질문: Non-leaf Tensor가 없어도 `.grad`가 생기는가?

Tensor를 만들기만 했다면 아직 Gradient를 계산하지 않았으므로 `.grad`는 `None`이다. 하지만 Scalar인 `w` 자체를 미분할 수도 있다.

```python
w = torch.tensor(3.0, requires_grad=True)
print(w.grad)  # None

w.backward()
print(w.grad)  # tensor(1.)
```

여기서는 `dw/dw = 1`이므로 Gradient가 `1`이다. **Non-leaf가 반드시 있어야 하는 것이 아니라, 추적 대상 Tensor에 대해 실제 미분을 실행했는지가 중요**하다.

---

### 질문: `.grad`는 어디에 저장되는가?

Backward는 중간 Tensor도 거쳐 계산하지만, 기본적으로는 **`requires_grad=True`인 Leaf Tensor의 `.grad`에 결과를 보관**한다. 모델의 Weight·Bias가 보통 이 대상이다.

Non-leaf도 미분 계산에는 사용된다. 다만 기본 설정에서 그 Tensor의 `.grad`까지 따로 저장하지 않을 뿐이다. **중간 Gradient가 계산에 쓰이는 것과 그 값을 `.grad`로 남겨 두는 것은 다르다.**

---

### 이해 수정: `backward()`가 하는 일

처음에는 이미 있는 Gradient를 이용해 Weight를 얼마나 바꿀지 계산하는 것으로 생각했다.

수정된 이해는 **`backward()`가 Loss를 각 Parameter에 대해 미분해 Gradient를 구하고 `.grad`에 누적한다**는 것이다. 그 Gradient를 실제 Update로 사용하는 것은 Optimizer이므로, 미분과 Parameter 변경을 나눠서 본다.

---

### 질문: `torch.no_grad()`는 언제 사용하는가?

Validation·Inference처럼 Gradient가 필요 없는 구간에서 쓴다. 이 구간에서는 예측값은 계산하되 역전파를 위한 연산 추적은 하지 않는다.

```python
model.eval()
with torch.no_grad():
    pred = model(x)
```

`eval`은 Evaluation, 즉 평가를 뜻한다. 두 기능은 자주 같이 쓰지만 같은 역할은 아니다.

- `model.eval()`: 모델을 평가 모드로 바꾼다.
- `torch.no_grad()`: 해당 구간의 Gradient 추적을 끈다.

따라서 **`eval()`을 호출했다고 Gradient 추적까지 자동으로 꺼지는 것은 아니다.**

---

### 질문: 값을 사용하면서 Gradient 전달은 왜 막아야 하는가?

처음에는 값을 계산에 쓸 거라면 왜 그 이전 경로로 Gradient가 전달되는 것은 막아야 하는지 이해되지 않았다.

GAN에서 **Discriminator D만 학습시키는 단계**로 연결해 이해했다. G가 만든 이미지는 D의 입력으로 필요하지만, 이번 D의 Loss를 G까지 역전파할 필요는 없다.

```python
fake_image = G(z).detach()
pred = D(fake_image)
```

이미지 값은 D로 전달되지만, 이 경로에서 G로 돌아가는 Gradient 연결은 끊어진다. D 자신의 Parameter에 대한 Gradient는 계산할 수 있다.

즉 `no_grad()`는 **코드 구간의 추적을 끄는 것**, `detach()`는 **특정 Tensor에서 이전 경로로 돌아가는 연결을 끊는 것**이다. `detach()`가 G 자체를 영구적으로 Freeze하는 것은 아니다.

앞서 배운 `weight_before = model.weight.detach().clone()`도 다시 확인했다. `detach()`로 그래프와 분리하고 `clone()`으로 별도 메모리에 복사하면, 원본 Weight가 바뀌어도 업데이트 전 값을 비교용으로 보관할 수 있다.

---

### 실습: 첫 번째 Linear Layer를 Freeze하기

```python
from torch import nn

model = nn.Sequential(
    nn.Linear(3, 4),
    nn.ReLU(),
    nn.Linear(4, 1)
)

for p in model[0].parameters():
    p.requires_grad = False
```

첫 번째 Linear는 `model[0]`이다. Parameter 한 개만 고르는 것이 아니라 **이 레이어의 Weight와 Bias 모두를 학습 대상에서 제외**한다.

이번처럼 학습 전에 설정하면 첫 번째 Linear의 Parameter에는 새 Gradient가 쌓이지 않고, 일반적인 Optimizer Update에서도 그 값이 유지된다. 레이어 계산 자체를 없애거나 `detach()`처럼 중간 경로를 끊는 것과는 다르다.

학습 도중 Freeze하는 경우에는 이전 `.grad`도 `None`으로 비워야 한다. 추적을 끄는 설정이 기존 Gradient까지 지우지는 않으며, Optimizer는 Gradient가 `None`인 Parameter의 Update를 건너뛴다. [PyTorch의 Gradient 초기화 동작](https://docs.pytorch.org/docs/2.13/generated/torch.optim.Optimizer.zero_grad.html)
