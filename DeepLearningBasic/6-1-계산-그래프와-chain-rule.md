# 계산 그래프와 Chain Rule

> 학습일: 2026-08-25

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

이번에는 **계산한 경로를 기록하는 것과 실제 Gradient를 구하는 것**을 구분했다. Forward에서 예측과 Loss를 계산하며 추적한 연산 관계가 계산 그래프이고, Autograd는 Backward에서 그 연결을 거꾸로 따라 Chain Rule을 적용한다.

| 구분 | 내가 이해한 역할 |
| --- | --- |
| `requires_grad=True` | 나중에 미분할 수 있도록 연산 추적을 허용하는 설정 |
| `grad_fn` | 이 결과를 만든 연산과 역전파에 필요한 연결·규칙 |
| `parameter.grad` | `backward()`로 계산한 Gradient가 누적되어 저장되는 곳 |

**Forward에서 준비한 정보가 있다고 Gradient까지 이미 계산된 것은 아니다.** `backward()`가 Gradient를 계산하고, `optimizer.step()`이 이를 이용해 Parameter를 바꾼다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `requires_grad=True`는 무엇인가?

#### 처음 이해

이미 계산된 Gradient를 저장하고 추적하는 설정으로 생각했다.

#### 수정된 이해

**나중에 Gradient를 계산할 수 있도록 연산 추적을 허용하는 설정**이다. 이 설정을 켰다는 이유만으로 Gradient가 바로 생기는 것은 아니다.

일반적인 학습에서는 연산을 추적한 뒤 `backward()`에서 미분하고, 모델 Parameter처럼 추적 대상인 Leaf Tensor의 `.grad`에 결과를 저장한다. 중간 연산 결과는 `requires_grad=True`여도 기본적으로 `.grad`를 따로 저장하지 않는다.

검증할 때는 Parameter의 `requires_grad`를 매번 `False`로 바꾸기보다 보통 `torch.no_grad()` 안에서 계산해 Gradient 추적을 끈다.

---

### 질문: `grad_fn`은 Backward 전에 왜 존재하는가?

`grad_fn`은 **이미 구한 Gradient가 아니라, 나중에 어떻게 역전파할지에 관한 정보**다. Forward 중 어떤 연산으로 Tensor가 만들어졌는지를 따라 연결된다.

직접 만든 Leaf Tensor에는 `grad_fn`이 없다. Gradient 추적이 켜져 있고 `requires_grad=True`인 Tensor가 참여한 미분 가능한 연산의 결과에는 `grad_fn`이 생긴다.

따라서 `grad_fn`이 먼저 보이는 것은 Gradient를 미리 계산했다는 뜻이 아니라 **Backward에 필요한 연결을 준비했다는 뜻**이다.

---

### 이해 수정: `backward()`가 Gradient를 계산하는 시점

#### 처음 이해

`backward()`가 이미 구해진 Gradient를 이용해 Loss를 줄이는 방향을 계산한다고 생각했다.

#### 수정된 이해

`loss.backward()`를 실행하면 **Autograd가 계산 그래프를 거꾸로 따라가며 Chain Rule로 이번 Gradient를 계산**한다. 이전에 저장된 Gradient를 읽어 Parameter를 수정하는 단계가 아니다.

계산 결과는 각 Parameter의 `.grad`에 누적된다. 이 값을 실제 수정에 사용하는 것은 `optimizer.step()`이다.

---

### 실습: Chain Rule의 각 항을 직접 계산하기

이 문제는 `backward()`에 맡기는 것이 아니라 **중간 미분값을 직접 구해 곱하는 것**이 목적이었다.

```python
import torch

x = torch.tensor(4.0)

a = 2 * x + 3      # 11
y = a ** 2

dy_da = 2 * a      # 22
da_dx = 2
dy_dx = dy_da * da_dx  # 44
```

`x → a → y`로 이어져 있으므로 `dy/dx = dy/da × da/dx = 22 × 2 = 44`가 된다.

위 코드는 직접 계산용이라 `x`의 Gradient 추적을 켜지 않았다. Autograd로 구하려면 `x`를 `requires_grad=True`로 만들고 Forward를 다시 계산해야 한다.

그 경우에도 `dy_da = y.backward()`처럼 미분값을 반환받는 것은 아니다. `backward()`의 반환값은 `None`이며, 이 예제에서 한 번 실행하면 Chain Rule이 내부적으로 적용되어 최종 `dy/dx`가 `x.grad`에 저장된다.

---

### 질문: `zero_grad()`는 Forward 전에 실행해도 되는가?

가능하다. 일반적인 학습에서는 다음처럼 Forward 전에 두기도 한다.

```python
optimizer.zero_grad()

pred = model(x)
loss = criterion(pred, y)

loss.backward()
optimizer.step()
```

`zero_grad()`가 지우는 것은 **계산 그래프나 `grad_fn`이 아니라 Optimizer가 관리하는 Parameter의 이전 `.grad`**다.

따라서 의도적으로 Gradient를 누적하는 경우가 아니라면, 새로운 `backward()` 전에 이전 Gradient를 비우는 것이 중요하다. Forward보다 먼저 실행해도 이번 계산 그래프를 만드는 데 문제가 없다.

---

### 질문: `grad_fn`은 직접 확인하지 않아도 필요한가?

`print(tensor.grad_fn)`은 사람이 내부 정보를 확인하는 코드일 뿐이다. 출력해야 추적이 시작되는 것은 아니다.

추적 조건을 만족하는 연산에서는 PyTorch가 필요한 계산 그래프와 `grad_fn`을 자동으로 구성한다. **내가 출력해서 보지 않아도 Backward는 그 연결 정보를 사용한다.**
