# Autograd 디버깅과 안전한 평가 코드

> 학습일: 2026-08-25

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

평가할 때는 두 개의 스위치를 따로 생각해야 한다. **`model.eval()`은 Layer의 동작 방식을 평가용으로 바꾸고, `torch.no_grad()`는 Autograd가 계산 과정을 기록하지 않게 한다.** 역할이 다르기 때문에 보통 둘을 함께 쓴다.

```python
model.eval()

with torch.no_grad():
    prediction = model(X)
    loss = criterion(prediction, y)
```

`train()`과 `eval()`은 모드만 바꾸며 Forward를 실행하지 않는다. 실제 예측은 `model(X)`가 수행한다. 설정한 모드는 다른 모드로 다시 바꿀 때까지 유지되므로 평가가 끝난 뒤 학습을 계속한다면 `model.train()`을 다시 호출해야 한다.

Autograd를 디버깅할 때는 먼저 Tensor가 Gradient 추적 대상인지, Leaf인지, Loss까지 연결되어 있는지를 본다. 기본적으로 Leaf Tensor의 `.grad`만 남지만, 추적 중인 Non-leaf Tensor의 중간 Gradient가 필요하면 `retain_grad()`로 따로 보관하도록 설정할 수 있다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: `model.eval()`과 Gradient 추적

#### 처음 이해

평가에서 `model.eval()`을 호출하면 Gradient 추적도 함께 꺼진다고 생각했다.

#### 수정된 이해

`model.eval()`은 Dropout이나 BatchNorm처럼 학습·평가 모드에서 동작이 달라지는 Layer를 평가 방식으로 바꾼다. Autograd 추적 여부는 바꾸지 않는다.

```text
model.eval()
→ Layer의 평가 동작 설정

torch.no_grad()
→ 해당 블록의 Autograd 추적 중단
```

`no_grad()` 없이도 Forward는 실행되지만, 필요 없는 계산 그래프가 만들어져 메모리와 계산 자원을 더 사용한다. 반대로 `eval()`을 빼면 Dropout·BatchNorm 등의 동작 때문에 평가 결과가 의도와 달라질 수 있다.

---

### 질문: `model.train()`과 `model(X)`은 무엇이 다른가?

`model.train()`은 모델을 학습 모드로 설정할 뿐, 데이터로 예측을 만들지는 않는다.

```python
model.train()          # 학습 모드 설정
prediction = model(X)  # 현재 모드로 Forward 실행
```

`train()`이나 `eval()`로 동작 방식을 정하고, `model(X)`를 호출해야 실제 Forward가 실행된다고 이해했다.

---

### 질문: Python의 `with`는 무엇인가?

`with`는 들여쓰기된 블록 안에서만 특정 상태를 적용하고, 블록이 끝나면 자동으로 정리하는 문법이다.

```python
with torch.no_grad():
    prediction = model(X)
```

여기서는 블록 안의 연산만 Gradient 추적 없이 실행한다. 블록을 벗어나면 `no_grad()`를 쓰기 전의 추적 상태로 돌아간다.

다만 `with`가 되돌리는 것은 Gradient 추적 상태다. 별도로 호출한 `model.eval()`의 평가 모드까지 자동으로 `train` 모드로 바꾸지는 않는다.

---

### 질문: `detach()`와 `no_grad()`는 어떻게 다른가?

이전에 배운 내용을 평가 코드와 연결해 다음처럼 구분했다.

```text
detach()
→ 특정 Tensor에서 이전 계산으로 이어지는 Gradient 연결을 끊음

no_grad()
→ 블록 안에서 실행하는 연산을 처음부터 기록하지 않음
```

평가 구간 전체에는 `no_grad()`가 맞고, 특정 Tensor의 값은 사용하되 그 Tensor 이전으로 Gradient를 보내지 않을 때는 `detach()`를 사용한다.

---

### 질문: Loss를 직접 정의해도 되는가?

가능하다. Autograd 예제에 `MSELoss`나 `CrossEntropyLoss`가 없었던 것은 회귀 문제라서가 아니라, 미분 과정을 간단히 보기 위해 Loss를 직접 만들었기 때문이다.

```python
import torch

x = torch.tensor(2.0, requires_grad=True)
y = x * 3
loss = y ** 2

loss.backward()
```

이 예제의 `loss`는 미분 가능한 연산으로 만들어진 Scalar Tensor이므로 Backward의 출발점으로 사용할 수 있다.

---

### 질문: 평가에서 Loss와 Accuracy를 왜 반환하는가?

평가 함수 안에서 계산한 결과를 밖에서 출력하거나 Epoch별로 기록하고, 모델을 비교하기 위해서다.

분류에서는 Loss와 Accuracy를 함께 보면 **얼마나 틀렸는지**와 **몇 개를 맞혔는지**를 서로 다른 관점에서 확인할 수 있다. 회귀에는 일반적인 분류 Accuracy 대신 MSE·RMSE·MAE 같은 회귀 지표를 사용한다.

---

### 이해한 내용: 일반 Tensor와 Parameter의 `requires_grad`

일반 Tensor를 직접 만들면 `requires_grad`의 기본값은 `False`다.

```python
x = torch.tensor(2.0)
tracked_x = torch.tensor(2.0, requires_grad=True)
```

반면 `nn.Linear`의 Weight와 Bias처럼 학습할 Parameter는 보통 `requires_grad=True`로 만들어진다. 학습에서 제외하도록 Freeze한 Parameter는 예외다.

---

### 질문: Non-leaf Tensor의 Gradient도 확인할 수 있는가?

Backward 과정에서는 중간 Tensor의 Gradient도 계산에 사용하지만, 기본적으로 Non-leaf Tensor의 `.grad`에는 그 값을 따로 남기지 않는다.

Autograd가 추적 중인 중간 Tensor의 Gradient를 디버깅 목적으로 보관하려면 Backward 전에 `retain_grad()`를 호출한다.

```python
x = torch.tensor(2.0, requires_grad=True)
y = x * 3
loss = y ** 2

y.retain_grad()
loss.backward()

print(x.grad)  # Leaf Tensor의 Gradient
print(y.grad)  # retain_grad()로 보관한 중간 Gradient
```

즉 `retain_grad()`는 중간 계산을 새로 만드는 기능이 아니라, **원래 Backward에서 계산하는 Non-leaf Tensor의 Gradient도 `.grad`에 남겨 달라고 요청하는 기능**이다.
