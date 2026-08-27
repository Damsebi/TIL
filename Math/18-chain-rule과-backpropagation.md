# Chain Rule과 Backpropagation

> 학습일: 2026-08-10

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 역전파는 수정이 아니라 수정에 필요한 정보 계산

7장 1강에서 Gradient를 이용해 Parameter를 움직인다고 배웠다. 이번에는 **그 Gradient를 여러 연산 사이에서 어떻게 구하는지** 연결해서 이해했다.

- **Forward**: 현재 Weight와 Bias로 예측값과 Loss를 계산한다.
- **Backward**: 최종 Loss부터 거슬러 올라가며 각 Weight와 Bias가 Loss에 얼마나 영향을 주는지 계산한다.
- **Optimizer**: 계산된 Gradient와 Learning Rate를 이용해 실제 Weight와 Bias를 수정한다.

Backpropagation이 새로운 종류의 미분인 것은 아니다. 각 연산의 변화율을 이어주는 Chain Rule을 뒤에서부터 반복 적용하는 방법이다.

### 내가 이해한 전체 학습 흐름

```text
Mini-batch로 예측
→ 예측값과 정답의 오차
→ 데이터별 Loss
→ 평균 Loss
→ Backpropagation으로 Gradient 계산
→ Optimizer가 Parameter 수정
```

이 과정에서 데이터마다 따로 모델을 고치는 것이 아니다. 여러 데이터가 **같은 Weight와 Bias를 공유**하고, 그 데이터들의 Loss를 함께 줄이려는 방향으로 학습한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 역전파로 Gradient를 계산하는가?

#### 처음 이해

Backpropagation이 Cost를 가장 빠르게 줄이도록 Weight와 Bias를 직접 올리거나 내리는 과정이라고 생각했다.

#### 수정된 이해

역전파가 하는 일은 Gradient 계산까지다. 실제 Parameter 수정은 Optimizer가 담당한다.

```python
loss.backward()      # gradient 계산
optimizer.step()     # parameter 수정
```

---

### 질문: Chain Rule은 역전파에서 어떤 역할을 하는가?

각 연산을 미분한 값은 그 연산의 변화율이고, Chain Rule은 **여러 단계의 변화율을 이어주는 역할**이다.

`w → z → a → L`처럼 연결되어 있다면 다음처럼 계산한다.

$$
\frac{\partial L}{\partial w}
=\frac{\partial L}{\partial a}
\frac{\partial a}{\partial z}
\frac{\partial z}{\partial w}
$$

중간 연산들의 미분을 연결하면, 처음의 `w`가 최종 Loss에 얼마나 영향을 주는지 구할 수 있다.

---

### 질문: Backpropagation은 `dz/dw`부터 계산하는가?

손으로 각 미분값을 따로 구할 때는 어느 것부터 계산해도 된다. 하지만 Backpropagation은 **최종 Loss에서 시작해 앞쪽 연산으로 거슬러 올라간다.**

```text
Forward  : w → z → a → L
Backward : L → a → z → w
```

---

### 질문: 역전파가 왜 필요한가?

작은 식이라면 중간 변수를 모두 대입한 뒤 한 번에 미분할 수도 있다. 하지만 신경망은 연산과 Parameter가 많다.

그래서 Forward에서 구한 중간값을 저장해 두고, Backward에서 그 값을 사용해 한 단계씩 미분을 이어간다. **큰 식의 Gradient를 효율적으로 계산하려는 방법**으로 이해했다.

---

### 질문: 왜 `a^(L) - y`를 제곱하는가?

#### 처음 이해

제곱하기 전의 차이와 제곱한 값을 모두 Loss처럼 생각했다.

#### 수정된 이해

`a^(L)`은 마지막 층의 예측값이고 `y`는 정답이다. 여기서 위첨자 `L`은 마지막 층을 가리키는 표기다. 예측값이 하나인 MSE 예제에서는 다음처럼 구분한다.

```text
예측값 - 정답값          → 오차(Error)
(예측값 - 정답값)의 제곱 → 데이터 하나의 Loss
```

제곱하면 양수·음수 오차가 서로 상쇄되지 않는다. 큰 오차에 상대적으로 더 큰 영향을 주는 효과도 있다.

---

### 질문: 여러 데이터의 Loss를 왜 더해서 평균내는가?

여러 데이터의 성적을 **하나의 학습 목표로 모으기 위해서**다. 이번에는 데이터별 Loss를 평균내 그 값을 줄이는 방향으로 학습한다.

$$
J=\frac{1}{N}\sum_{i=1}^{N}L_i
$$

여기서 `N`은 평균에 포함된 데이터 수다. Mini-batch 학습에서는 그 묶음의 평균 Loss를 사용한다.

---

### 질문: 왜 한 데이터의 여러 가중치를 평균내지 않고, 한 가중치에 대한 여러 데이터의 Gradient를 평균내는가?

#### 처음 이해

각 데이터가 자기 Weight를 따로 가지고 있다고 생각해서, 한 데이터 안의 여러 Weight에 대한 값을 평균내는 것으로 이해했다.

#### 수정된 이해

데이터마다 Weight가 있는 것이 아니라 **모델의 같은 Weight를 여러 데이터가 함께 사용한다.**

평균 Loss `J`를 하나의 Weight `w`에 대해 미분하면, 각 데이터가 그 `w`에 대해 만든 Gradient가 평균된다.

$$
\frac{\partial J}{\partial w}
=\frac{1}{N}\sum_{i=1}^{N}\frac{\partial L_i}{\partial w}
$$

반면 `w₁`, `w₂`는 서로 다른 수정 대상이다. 두 Gradient를 서로 평균내 하나로 만드는 것이 아니라, 각 Weight에 맞는 Gradient를 따로 계산한다.

---

### 질문: 역전파를 사용하려면 충분한 데이터셋이 필요한가?

역전파 자체는 데이터 하나로도 가능하다. 충분한 데이터가 필요한 것은 역전파를 실행하기 위해서가 아니라, 모델이 일부 데이터만 외우지 않고 새로운 데이터에도 잘 작동하게 학습하기 위해서다.

Mini-batch도 역전파의 필수 조건이 아니라 많은 데이터를 나눠 처리하는 방식이다.

---

### 질문: Backpropagation은 Sigmoid나 MLP에서만 사용하는가?

아니다. Sigmoid는 활성화 함수이고 MLP는 신경망 구조다. 역전파는 CNN, RNN, Transformer 등에서도 사용한다.

핵심은 특정 구조인지가 아니라 **Loss까지 이어진 연산들의 미분을 연결해 구할 수 있는지**다.
