# `zero_grad`, `backward`, `step` 순서

> 학습일: 2026-08-25

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

한 번의 학습 순서는 **이전 Gradient를 비우고 → 예측과 Loss를 만들고 → 새 Gradient를 구하고 → Parameter를 고치는 흐름**이다.

```text
zero_grad → forward → loss → backward → step
```

각 단계가 건드리는 대상은 서로 다르다. `zero_grad()`는 이전 `.grad`를 비우고, `backward()`는 이번 Loss에서 계산한 Gradient를 `.grad`에 저장한다. 여기까지는 Weight와 Bias가 그대로이며, `step()`을 호출해야 Parameter가 실제로 바뀐다.

```python
for x, y in train_loader:
    optimizer.zero_grad()

    prediction = model(x)
    loss = criterion(prediction, y)

    loss.backward()
    optimizer.step()
```

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `backward()`가 Gradient를 계산하는가?

맞다. `loss.backward()`는 Loss에서 출발해 계산 그래프를 거꾸로 따라가며 각 Parameter에 대한 Gradient를 계산하고 `.grad`에 저장한다.

```text
backward()
→ Gradient 계산
→ parameter.grad에 저장
```

이 단계에서는 Parameter 값이 바뀌지 않는다. 실제 수정은 그다음 `optimizer.step()`이 담당한다.

---

### 질문: `zero_grad()`는 Gradient 계산 전에만 실행하면 되는가?

핵심은 **새로운 `backward()` 전에 이전 Gradient가 제거되어 있어야 한다는 것**이다. PyTorch는 새 Gradient로 `.grad`를 덮어쓰지 않고 기존 값에 누적하기 때문이다.

Forward와 Loss 계산은 기존 `.grad`를 사용하지 않으므로 `zero_grad()`가 반드시 Forward보다 먼저여야 하는 것은 아니다. 그래도 어느 학습 단계의 Gradient인지 헷갈리지 않게 보통 Training Step의 시작 부분에 둔다.

```text
이전 .grad
→ zero_grad()
→ forward와 loss
→ backward()
→ 이번 Step의 .grad
```

---

### 이해 수정: SGD와 `optimizer.step()`의 관계

#### 처음 이해

`backward()`가 Gradient를 계산하면 SGD가 변경량을 따로 결정하고, 마지막으로 `step()`이 그 결과를 단순히 실행한다고 이해했다.

#### 수정된 이해

SGD는 Parameter를 업데이트하는 **방식**이고, `optimizer.step()`은 현재 `.grad`에 그 방식을 적용해 **계산과 실제 업데이트를 수행하는 호출**이다.

```text
SGD Optimizer 생성
→ 업데이트 규칙과 학습 대상 Parameter 설정

backward()
→ Gradient 계산

optimizer.step()
→ SGD 규칙으로 Parameter 업데이트
```

즉 SGD와 `step()` 사이에 별도의 자동 계산 단계가 하나 더 있는 것은 아니다.

---

### 질문: 모델을 만들면 학습 전에도 Weight가 존재하는가?

그렇다. 모델을 생성하는 순간 Weight와 Bias가 초기화 규칙에 따라 만들어진다.

```python
model = nn.Linear(2, 1)
```

따라서 학습은 Weight를 처음 만드는 과정이 아니라, **이미 만들어진 초기값을 데이터에 맞게 계속 수정하는 과정**이다.

---

### 질문: `weight_before`는 언제 저장해도 같은가?

모델을 만든 뒤 아직 `optimizer.step()`을 호출하지 않았다면 다음 시점의 Weight 값은 같다.

```text
모델 생성 직후
= Forward 후
= Loss 계산 후
= Backward 후
```

Forward와 Loss 계산은 예측과 Loss를 만들고, Backward는 `.grad`를 만든다. 이 과정에서는 Weight 자체가 바뀌지 않으며, `optimizer.step()`을 호출하는 순간 Weight가 실제로 변경된다.

업데이트 전 값을 독립적으로 보관하려면 다음처럼 복사할 수 있다.

```python
weight_before = model.weight.detach().clone()
```

---

### 질문: `loss.item()`으로 꺼낸 값을 다시 Tensor로 만들면 계산 그래프가 복구되는가?

아니다. `.item()`이 반환한 Python 숫자에는 원래 Loss까지 이어진 계산 경로가 없다. 그 숫자를 다시 Tensor로 감싸도 **값이 같은 새 Tensor가 생길 뿐, 모델 Parameter와의 연결은 돌아오지 않는다.**

```text
Parameter → Prediction → Loss Tensor
                            ↓ .item()
                       Python 숫자
                            ↓ torch.tensor(...)
                       새로운 독립 Tensor
```

따라서 원래 `loss` Tensor로 학습하고, `.item()`으로 꺼낸 숫자는 출력이나 기록에만 사용한다.

```python
loss_value = loss.item()  # 출력·기록용
loss.backward()          # 학습용
```

`.item()`을 호출해도 원래 `loss` Tensor의 계산 그래프가 사라지는 것은 아니다. 연결이 없는 것은 `.item()`이 반환한 Python 숫자다.
