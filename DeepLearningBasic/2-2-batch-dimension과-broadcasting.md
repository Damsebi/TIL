# Batch Dimension과 Broadcasting

> 학습일: 2026-08-19

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Batch Dimension과 Shape

Batch Dimension은 여러 Sample을 한 번에 처리하기 위한 차원이다.

```text
표 데이터   = (batch_size, features)
이미지 데이터 = (N, C, H, W)
```

표 데이터에서 `(1, 4)`는 Feature가 4개인 Sample 하나를 Batch 형태로 표현하고, `(2, 4)`는 Feature가 4개인 Sample 두 개를 표현한다.

### `unsqueeze()`와 `squeeze()`

두 연산은 Tensor의 값이 아니라 Shape를 바꾼다.

| 연산 | 역할 |
| --- | --- |
| `unsqueeze(dim)` | 지정한 위치에 크기 1인 차원 추가 |
| `squeeze(dim)` | 지정한 위치의 크기 1인 차원 제거 |

현재 Shape만 보고 습관적으로 사용하지 않고 다음 연산이 어떤 Shape를 요구하는지 먼저 확인해야 한다. 크기가 1이어도 Batch처럼 의미 있는 차원이라면 제거하면 안 된다.

### Bias와 Broadcasting

`y = Wx + b`에서 `b`는 Bias이며 각 출력 Feature에 더하는 보정값이다. 출력 Feature가 4개라면 Bias도 4개가 필요하다.

Broadcasting은 Shape가 달라도 오른쪽 차원부터 비교해 다음 조건 중 하나를 만족하면 자동으로 확장해 연산한다.

```text
두 차원의 크기가 같음
둘 중 하나의 크기가 1
한쪽에 비교할 차원이 없음
```

Broadcasting이 성공했다는 사실만으로 계산이 의도대로 이루어졌다고 볼 수는 없다. 연산 전에 각 차원이 무엇을 의미하는지 확인해야 한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `(4,)`, `(1, 4)`, `(2, 4)`는 각각 무엇을 의미하는가?

`(4,)`는 길이가 4인 1차원 Tensor다. 뒤의 쉼표는 Python에서 원소가 하나인 Tuple을 표현하기 위한 문법이며 새로운 차원이 아니다. `(, 4)`라는 Shape 표기는 없다.

```text
(4,)   → Feature 4개인 1차원 Tensor
(1, 4) → Sample 1개, Feature 4개
(2, 4) → Sample 2개, Feature 4개
```

Batch 형태에서는 Sample 수가 늘어나면 앞쪽 숫자가 증가한다고 이해했다.

---

### 이해 수정: `unsqueeze()`의 위치

#### 처음 이해

`(4,)`에 `unsqueeze(0)`을 적용하면 `(4, 1)`이 되고, `unsqueeze(1)`으로 `(4, 1)`을 만드는 것은 전치와 비슷하다고 생각했다.

#### 수정된 이해

`unsqueeze()`의 인자는 새 차원의 크기가 아니라 새 차원을 넣을 위치다.

```text
(4,) → unsqueeze(0) → (1, 4)
(4,) → unsqueeze(1) → (4, 1)
```

`(4,)`는 행과 열이 구분되지 않는 1차원 Tensor다. `unsqueeze(1)`은 기존 차원의 순서를 바꾸는 전치가 아니라 지정한 위치에 새 차원을 추가하는 연산이다.

위치를 잘못 지정하면 값은 같아도 Tensor의 구조와 의미가 달라져 의도하지 않은 계산이 생길 수 있다.

---

### 이해 수정: `squeeze()`는 계산 전에 항상 사용하는 연산이 아니다

#### 처음 이해

계산하기 편하도록 미리 `squeeze(0)`으로 크기 1인 차원을 제거하는 것이 좋다고 생각했다.

#### 수정된 이해

`squeeze()`는 다음 연산에서 해당 차원이 필요 없을 때만 사용한다. Model이 `(batch_size, features)` 형태를 기대한다면 `(1, 4)`의 앞쪽 `1`은 필요한 Batch Dimension이므로 제거하면 안 된다.

```text
현재 Shape 확인
→ 다음 연산이 요구하는 Shape 확인
→ 필요한 경우에만 squeeze / unsqueeze
```

---

### 질문: Bias는 무엇이고 `WX + b`의 `b`와 같은 것인가?

맞다. `b`는 Bias의 첫 글자에서 가져온 표기이며 계산 결과를 이동시키는 보정값으로 이해했다.

```text
X = 입력
W = Weight
b = Bias

y = Wx + b
```

---

### 질문: Bias의 Feature 수가 부족하면 `0`을 추가해도 되는가?

원래 출력 Feature가 4개이고 네 번째 Bias의 실제 값이 `0`인 것은 정상이다.

```text
[b1, b2, b3, 0]
```

하지만 원래 Bias가 세 개뿐인데 Shape 오류를 없애려고 임의로 `0`을 추가하는 것은 구조상의 문제를 숨길 수 있다.

```text
[b1, b2, b3] → [b1, b2, b3, 0]
```

Padding의 0 채우기는 연산에 포함된 의도적인 규칙이므로 Shape 오류를 숨기기 위한 임의 수정과 구분해야 한다.

---

### 질문: Broadcasting에서는 Feature 수만 맞으면 되는가?

`(batch_size, features) + (features,)` 형태로 Bias를 더할 때는 마지막 Feature 수가 맞아 Broadcasting이 가능하다.

```text
(10, 4) + (4,) → 가능
(10, 4) + (3,) → 불가능
```

하지만 일반적인 Broadcasting은 Feature 수만 보는 것이 아니다. 오른쪽부터 각 차원을 비교해 크기가 같거나, 둘 중 하나가 1이거나, 한쪽 차원이 없으면 연산할 수 있다.

---

### 질문: `pred=(4, 1)`, `target=(4,)`이면 `unsqueeze(1)`을 사용해야 하는가?

두 Tensor를 그대로 계산하면 `target`이 `(1, 4)`처럼 맞춰져 결과 Shape가 `(4, 4)`가 된다.

```text
pred   = (4, 1)
target = (1, 4)
결과   = (4, 4)
```

이 경우 각 Prediction이 모든 Target과 계산되는 의도하지 않은 Broadcasting이 발생한다. Sample별로 하나씩 대응시키려면 Target에 `unsqueeze(1)`을 적용한다.

```python
target = target.unsqueeze(1)
```

```text
pred   = (4, 1)
target = (4, 1)
```

코드가 오류 없이 실행된다는 것과 계산이 의도대로 이루어진다는 것은 다르므로 중요한 연산 전에는 Shape를 확인해야 한다.
