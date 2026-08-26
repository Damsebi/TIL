# 미분·편미분·Gradient와 Gradient Descent

> 학습일: 2026-08-10

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 미분은 변화량이 아니라 변화율

미분은 **현재 위치에서 입력을 조금 움직였을 때 출력이 얼마나 빠르게 변하는지** 나타내는 값으로 이해했다. 그래프에서는 그 점에 그은 접선의 기울기다.

미분값 자체가 출력 변화량은 아니다. 실제 출력 변화량은 다음처럼 근사할 수 있다.

$$
\Delta f \approx f'(x)\Delta x
$$

예를 들어 `f'(2)=4`라면 `x=2` 근처에서 입력이 `0.01` 변할 때 출력은 약 `0.04` 변한다.

한 점의 순간 기울기를 직접 구하기 어려울 때는 아주 가까운 양옆 두 점의 기울기로 근사할 수 있다. 이것이 수치미분이다.

$$
f'(x)\approx\frac{f(x+h)-f(x-h)}{2h}
$$

### 여러 Parameter의 기울기를 모은 Gradient

변수가 여러 개이면 한 변수만 움직이고 나머지는 고정한 채 변화율을 구한다. 이것이 편미분이다.

```text
∂f/∂x → x만 움직였을 때의 변화율
∂f/∂y → y만 움직였을 때의 변화율
```

각 변수의 편미분을 하나로 모은 것이 Gradient다.

$$
\nabla f=\left(\frac{\partial f}{\partial x},\frac{\partial f}{\partial y}\right)
$$

내가 이해한 Gradient는 **여러 Parameter 중 무엇을 어느 방향으로 움직이면 Loss가 가장 빠르게 변하는지 모아둔 정보**다. Gradient는 함수값이 가장 빠르게 증가하는 방향이므로 Loss를 줄일 때는 반대 방향으로 움직인다.

### Gradient Descent와 Learning Rate

Parameter는 다음 방식으로 수정한다.

$$
\theta_{\mathrm{new}}
=\theta_{\mathrm{old}}-\eta\nabla L
$$

```text
Gradient     → 어느 방향으로 얼마나 민감하게 변하는지 알려줌
Learning Rate → 그 방향으로 실제 한 번에 얼마나 움직일지 정함
Optimizer    → 위 정보를 사용해 Weight와 Bias를 실제로 수정함
```

Learning Rate가 너무 작으면 학습이 느릴 수 있고, 너무 크면 최솟값을 지나치거나 학습이 발산할 수 있다.

### Mini-batch 단위의 실제 학습 흐름

전체 데이터를 한 번에 처리하지 않고 작은 묶음인 Mini-batch로 나누어 다음 과정을 반복한다.

```text
Mini-batch
→ 예측
→ Loss 계산
→ Gradient 계산
→ Optimizer가 Parameter 수정
```

- **Batch Size**: Mini-batch 하나에 들어가는 Sample 수
- **Mini-batch**: 한 번에 학습하는 데이터 묶음
- **Epoch**: 전체 학습 데이터를 한 번 모두 사용한 것

데이터가 1,000개이고 `batch_size=100`이면 Mini-batch 10개를 모두 처리했을 때 1 Epoch가 된다. 일반적으로 Mini-batch 하나를 처리할 때마다 Parameter Update가 한 번 일어난다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: 미분값과 변화량

#### 처음 이해

특정 값을 넣어서 나온 기울기 자체가 출력의 변화량이라고 생각했다.

#### 해결 및 이해

미분값은 변화량이 아니라 변화율이다. `f'(2)=4`라면 입력이 변할 때 출력이 약 4배의 비율로 변한다는 뜻이다.

```text
입력 변화량 = 0.01
미분값      = 4

출력 변화량 ≈ 4 × 0.01 = 0.04
```

또한 곡선에서는 함수 전체의 기울기가 아니라 **현재 점에서의 접선 기울기**를 구한다.

---

### 이해 수정: 여러 점에 가까운 직선과 수치미분

#### 처음 이해

수치미분을 여러 데이터 점에 최대한 가까운 직선을 찾는 과정과 연결해서 생각했다.

#### 해결 및 이해

여러 점에 전체적으로 잘 맞는 직선을 찾는 것은 선형회귀·최소제곱법의 개념이다.

수치미분은 전체 데이터에 맞는 선을 찾는 것이 아니라, **특정 한 점의 가까운 양옆 두 점만 사용해 그 지점의 기울기를 근사하는 것**이다.

---

### 질문: 좌표평면에서는 그 양옆의 점도 360도 방향 중 하나 아닌가?

좌표평면에서는 여러 방향으로 움직일 수 있지만, 일변수 함수 `f(x)`는 바꿀 입력이 `x` 하나뿐이다. 따라서 수치미분에서는 x축을 따라 `x-h`, `x+h`만 확인한다.

```text
x-h ← x → x+h
```

`f(x, y)`처럼 입력 변수가 여러 개가 되면 각 변수를 따로 움직이는 편미분과 그 결과를 모은 Gradient가 필요하다.

---

### 이해 수정: Loss와 Gradient, Parameter Update

#### 처음 이해

Loss를 계산하면 Gradient가 바로 나오고, 현재 Parameter에서 Gradient를 그대로 빼면 Loss가 줄어든다고 생각했다.

#### 해결 및 이해

Loss를 계산한 뒤 그 Loss를 각 Parameter에 대해 미분해야 Gradient가 나온다. 그리고 Gradient를 그대로 빼는 것이 아니라 Learning Rate를 곱한 만큼 이동한다.

```text
Loss 계산
→ 각 Parameter에 대한 Gradient 계산
→ Learning Rate를 곱해 이동 크기 결정
→ Optimizer가 Parameter 수정
```

---

### 질문: Mini-batch의 크기는 어떤 조건으로 정하는가?

Batch Size는 정답이 정해진 값이 아니라 사람이 정하는 Hyperparameter다.

- GPU Memory에 들어가는지
- 학습 속도가 적절한지
- Gradient가 지나치게 불안정하지 않은지
- Validation 성능이 어떤지

실제 학습 데이터에서 여러 후보를 시험하고 속도·Memory·Validation 성능을 함께 보며 정한다.
