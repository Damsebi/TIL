# SGD, Adam과 Learning Rate

> 학습일: 2026-08-24

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Optimizer에게 고칠 대상을 연결한다

Loss는 채점, `backward()`는 Gradient 계산, Optimizer는 실제 Parameter 수정으로 나눠서 본다. `model.parameters()`는 모델의 Weight·Bias 같은 Parameter들을 넘겨 **“이 값들을 수정해라”** 하고 대상을 연결하는 역할이다.

```python
from torch import optim

optimizer = optim.SGD(model.parameters(), lr=0.01)

optimizer.zero_grad()                 # 이전 Gradient 초기화
prediction = model(x)
loss = loss_fn(prediction, target)
loss.backward()                      # 현재 Gradient 계산
optimizer.step()                     # Parameter 수정
```

Gradient는 기본적으로 누적된다. 여러 배치의 Gradient를 일부러 모으려는 경우가 아니라면 새로운 계산 전에 `zero_grad()`로 비운다.

### Learning Rate는 실제 이동량을 정하는 배율이다

Momentum·Weight Decay가 없는 기본 SGD는 `새 Parameter = 현재 Parameter - lr × Gradient`로 수정한다. **Gradient가 알려주는 변화율에 Learning Rate를 곱해 얼마나 움직일지 정하는 것**이다.

Learning Rate가 너무 작으면 학습이 느려지고, 너무 크면 최소점을 지나치는 Overshoot가 생길 수 있다. 이를 반복하면 Loss가 진동하거나 계속 커지며 발산할 수 있으므로, 한 번 수정했다고 Loss가 반드시 줄어드는 것은 아니다.

Optimizer나 Learning Rate를 비교할 때는 모델 구조·데이터·초기 Parameter를 같게 둔다. 시작 조건까지 다르면 어떤 설정 때문에 결과가 달라졌는지 구분하기 어렵다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: Gradient와 Feature의 중요도

#### 처음 이해

Gradient의 방향이 어떤 Feature를 더 중요하게 볼지, 덜 중요하게 볼지를 직접 정한다고 생각했다.

#### 수정된 이해

Gradient는 Feature의 중요도를 직접 매기는 점수가 아니다. **현재 지점에서 Parameter를 어떻게 바꾸면 Loss가 가장 빠르게 증가하는지와 그 변화율**을 나타낸다. 기본 SGD는 그 반대 방향으로 수정한다.

Weight가 바뀌면 입력이 예측에 미치는 영향도 달라질 수 있지만, 이것은 수정의 결과다. 선형 모델에서도 입력의 부호 등에 따라 효과가 달라지므로 **Weight가 증가했다고 출력도 항상 증가하는 것은 아니다.**

---

### 이해 수정: 오차의 부호와 Gradient의 방향

#### 처음 이해

MSE가 제곱으로 부호를 없앤다고 해서 Loss 자체에도 양수·음수 방향이 있다고 생각했다. Gradient도 “오차를 제곱한 값이 가장 빠르게 증가하는 방향”으로만 이해했다.

#### 수정된 이해

MSE에서 없어지는 것은 `prediction - target`이라는 **오차의 부호**다. 오차가 `+2`든 `-2`든 제곱하면 `4`이므로 MSE Loss는 0 이상이다.

반면 Gradient는 **Parameter를 바꿀 때 Loss가 어떻게 변하는지**에 관한 방향이다. 오차의 부호와 Parameter 공간에서의 변화 방향은 같은 말이 아니다.

또한 Gradient를 구하는 대상이 항상 제곱 오차인 것도 아니다. MSE를 쓰면 MSE를, BCE를 쓰면 BCE를, Cross Entropy를 쓰면 그 Loss를 Parameter에 대해 미분한다.

---

### 질문: SGD에 Momentum을 추가한 것이 Adam인가?

같은 것이 아니다. Gradient를 수정에 사용하는 방식이 다르다.

- 기본 SGD: 현재 Gradient를 직접 사용한다.
- SGD + Momentum: 이전 Gradient의 흐름을 누적해 이동에 관성을 준다.
- Adam: 과거 Gradient와 Gradient 제곱의 통계를 함께 추적해 Parameter별 수정량을 조절한다.

Momentum·Adam은 과거 정보도 사용하므로 **항상 현재 Gradient의 반대 방향 그대로 움직이는 것은 아니다.**

#### Momentum에서 헷갈린 부분

처음에는 이전 Update가 음수면 다음 양수 Update를 작게 만드는 부호 보정으로 생각했다. 방향이 반대이면 누적된 흐름과 상쇄될 수는 있지만, 핵심은 **최근까지 움직여 온 방향을 기억하는 것**이다.

#### Adam에서 헷갈린 부분

처음에는 Parameter마다 별도의 Optimizer를 붙이는 것으로 생각했다. SGD도 각 Parameter의 Gradient를 사용한다. Adam의 차이는 **Parameter별로 과거 Gradient의 방향·크기 정보를 따로 쌓아 수정량에 반영하는 것**이다.

Adam은 1차·2차 Moment 상태를 추가로 저장하므로 기본 SGD보다 메모리를 더 쓴다. 계산도 더 복잡하지만 Forward·Backward가 차지하는 비중도 있으므로, Adam을 쓴다고 학습 전체가 반드시 크게 느려지는 것은 아니다.

---

### 질문: AdamW는 Weight를 한 번 더 수정하는가? 작은 Weight는 그대로 두는가?

#### 처음 이해

Adam의 수정에 Weight Decay가 추가되니 Weight를 두 번 줄이는 것처럼 생각했다. 작은 Weight는 건드리지 않는 것인지도 궁금했다.

#### 수정된 이해

두 역할을 나눠서 본다.

- Adam의 학습 Update: Gradient 정보를 이용한 수정이며, Weight를 늘릴 수도 줄일 수도 있다.
- Weight Decay: Adam의 Gradient 기반 수정과 분리해서, 적용 대상 Weight를 0 쪽으로 조금 당기는 규제다.

따라서 **“두 번 감소”가 아니라 “학습을 위한 수정 + 0 쪽으로 당기는 효과”**다. 둘을 합친 최종 Weight가 반드시 작아지는 것은 아니다.

작은 Weight를 아예 제외하는 것도 아니다. Decay에 의한 변화량은 Weight 크기에 비례하므로, 작은 Weight는 절대적인 변화량도 작다.

---

### 이해한 내용: 다음 토큰 예측의 Cross Entropy

LLM의 다음 토큰 예측에서는 **정답 토큰에 얼마나 높은 확률을 주었는지**로 채점한다. 한 위치의 기본 Cross Entropy는 다음처럼 읽는다.

$$
L = -\log(p_{\mathrm{target}})
$$

`p_target`은 정답 토큰에 준 확률이다. 정답 확률이 `0.9`이면 Loss가 작고, `0.1`, `0.01`로 내려갈수록 Loss가 커진다.

학습 대상인 여러 토큰 위치에서 다음 정답 토큰의 Loss를 각각 계산하고, 이를 모아 학습 Loss로 사용한다.
