# Sequence Data와 RNN Hidden State

> 학습일: 2026-08-31

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### RNN은 이전 정보를 상태로 넘기면서 순서대로 읽는다

Sequence Data는 앞뒤 순서가 의미에 영향을 주는 데이터다. RNN은 현재 입력만 따로 보는 것이 아니라, 이전 시점까지의 정보를 요약한 Hidden State를 함께 사용한다.

```text
현재 입력 x_t
+ 이전 Hidden State h_(t-1)
→ 새로운 Hidden State h_t
```

Hidden State는 이전 토큰 자체를 다시 가져오는 값이 아니라, **지금까지 읽은 정보가 반영된 중간 상태**다.

```text
"나는" 처리
→ h₁

"책을" + h₁
→ h₂
```

Hidden State는 정보를 담는 표현일 뿐, 그 자체가 항상 다음 토큰을 예측하는 것은 아니다. 문장 분류, 토큰별 예측, 다음 토큰 예측처럼 어떤 결과를 만들지는 학습 목표와 출력층이 결정한다.

### RNN의 B, L, D와 출력 Shape

`batch_first=True`를 사용하는 현재 기준에서 RNN 입력은 `(B, L, D)`로 표현한다.

```text
B = Batch Size
    한 번에 처리하는 sequence 수

L = Sequence Length
    순서대로 처리할 time step 수
    NLP에서는 보통 토큰 수

D = Input Size
    토큰 하나를 나타내는 입력 벡터의 크기
```

RNN을 통과하면 입력 벡터 크기 `D`가 Hidden State 크기 `H`로 바뀐다.

```text
입력    (B, L, D)
  ↓ RNN
output  (B, L, H)
h_n     (1, B, H)
```

`h_n`의 첫 번째 차원이 `1`인 것은 **1-layer, 단방향 RNN**을 기준으로 했기 때문이다. 하나의 RNN 안에서 `hidden_size=H`를 정하면 `h₁`, `h₂`, `h₃`의 크기는 모두 H로 유지되며 time step이 진행된다고 계속 커지지 않는다.

### `output`과 `h_n`의 역할

`output`은 모든 time step에서 만들어진 Hidden State를 가지고 있고, `h_n`은 마지막 Hidden State를 가진다.

```text
Sequence 전체에서 결과 하나 필요
→ 마지막 Hidden State 활용 가능

각 Token / Time Step마다 결과 필요
→ output 전체 활용
```

무엇을 선택할지는 이진·다중분류처럼 class 수로 정하지 않는다. **Sequence 전체에 답 하나가 필요한지, 각 시점마다 답이 필요한지**가 기준이다.

Padding이 없다면 1-layer, 단방향 기본 구조에서 `output[:, -1, :]`과 `h_n[0]`은 마지막 시점의 같은 Hidden State를 가리킨다. Padding이 있다면 `-1` 위치가 PAD일 수 있으므로 각 문장의 실제 길이를 이용해 마지막 유효 토큰의 위치를 찾아야 한다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| `h_n`의 Shape는 `(1, B, D)`다. | RNN을 통과한 마지막 차원은 `hidden_size`이므로 `(1, B, H)`다. |
| Hidden State는 항상 다음 토큰을 예측한다. | Hidden State는 이전 정보를 담은 표현이며, 예측 대상은 학습 목표가 결정한다. |
| RNN Forward는 전체 학습 과정이다. | Forward는 입력으로 출력을 계산하는 순전파이며, 전체 학습에는 loss·backward·parameter update도 필요하다. |
| `output[:, -1, :]`에서 `:` 때문에 L축이 사라진다. | `-1`로 L축의 index 하나를 선택했기 때문에 해당 축이 사라진다. |
| PAD 위치에는 Hidden State가 없다. | PAD가 입력되면 그 위치에서도 Hidden State가 계산될 수 있다. |
| `length - 1`의 `-1`은 Padding 때문에 필요하다. | Python index가 0부터 시작하므로 마지막 유효 index가 `length - 1`이다. |
| 이진분류는 `h_n`, 다중분류는 `output`을 사용한다. | class 수가 아니라 Sequence 전체와 각 time step 중 어디에 출력이 필요한지를 기준으로 선택한다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Hidden State는 이전 토큰 자체를 사용하는가?

이전 토큰을 그대로 다시 사용하는 것이 아니다. 이전 토큰까지 순서대로 처리하면서 만들어진 Hidden State를 현재 입력과 함께 사용한다.

```text
이전 토큰까지 요약된 h_(t-1)
+ 현재 입력 x_t
→ 현재 상태 h_t
```

---

### 질문: RNN을 통과할 때 D가 계속 증가하는가?

아니다. `input_size=64`, `hidden_size=128`로 정했다면 입력 벡터는 처음 RNN에 들어갈 때 64차원이고, 각 시점의 Hidden State는 모두 128차원이다.

```text
h₁ = 128
h₂ = 128
h₃ = 128
```

Time step이 늘어나는 것과 Hidden State의 차원이 커지는 것은 다른 개념이다.

---

### 질문: RNN은 다중 Layer를 사용하지 않는가?

RNN도 여러 layer를 쌓을 수 있다. 다만 이번 강의에서는 Shape 흐름을 먼저 이해하기 위해 1-layer, 단방향 RNN을 기준으로 학습했다.

---

### 질문: Sequence Length는 글자 수인가?

Sequence Length는 문자열의 글자 수가 아니라 **RNN이 순서대로 처리할 time step의 개수**다.

NLP에서 토큰 하나를 한 time step으로 사용한다면 토큰 수가 Sequence Length가 된다. 토큰화 방식에 따라 한 문장이 나뉘는 단위가 달라질 수 있으므로 단순한 글자 수와는 다르다.

---

### 질문: B, L, D는 누가 정하는가?

```text
B
→ DataLoader의 batch size 설정에 영향받음

L
→ 실제 sequence 길이와 padding·truncation·max length에 영향받음

D
→ embedding dimension 또는 RNN의 input_size로 설계
```

각 값이 모두 데이터에서 자동으로 정해지거나 모두 사람이 임의로 정하는 것이 아니라, 데이터와 전처리·모델 설정이 함께 결정한다.

---

### 질문: `output[:, -1, :]`은 무엇을 선택하는가?

`output`의 Shape가 `(B, L, H)`일 때 다음과 같이 읽는다.

```python
output[:, -1, :]
```

```text
첫 번째 :
→ 모든 batch 선택

-1
→ Sequence 축의 마지막 index 하나 선택

마지막 :
→ Hidden 축의 모든 값 선택
```

L축에서 index 하나만 선택했으므로 결과 Shape는 `(B, H)`가 된다.

---

### 질문: `output[:, -1, :]`과 `h_n`은 같은가?

Padding이 없고 1-layer, 단방향인 기본 구조에서는 `output[:, -1, :]`과 `h_n[0]`이 마지막 시점의 Hidden State를 가리킨다.

하지만 Padding이 있으면 마지막 배열 위치가 실제 문장의 끝이 아닐 수 있다.

```text
[나는, 책을, 읽었다, PAD, PAD]
```

이 문장의 실제 길이가 3이면 마지막 유효 index는 `3 - 1 = 2`다. PAD도 RNN에 입력되면 Hidden State가 계산될 수 있으므로 실제 length를 기준으로 필요한 위치를 찾아야 한다.

---

### 질문: `output`과 `h_n`은 무엇을 기준으로 선택하는가?

이진분류인지 다중분류인지가 아니라 출력이 필요한 단위를 본다.

문장 하나를 여러 주제 중 하나로 분류하는 문제는 다중분류이지만 문장당 결과 하나만 필요하므로 마지막 Hidden State를 사용할 수 있다. 반대로 각 토큰마다 결과를 예측해야 한다면 `output`의 모든 시점 정보가 필요하다.

---

### 질문: RNN의 Label은 어떻게 만드는가?

RNN이 label 형태를 정하는 것이 아니라 학습 목표에 따라 입력과 정답을 구성한다.

문장 전체 분류라면 문장마다 별도의 label을 사용할 수 있다.

```text
"이 영화는 재미있다"
→ 긍정
```

다음 토큰 예측에서는 원본 sequence를 한 칸씩 밀어 입력과 정답으로 만들 수 있다.

```text
원본
[나는, 책을, 읽었다]

입력 X
[나는, 책을]

정답 Y
[책을, 읽었다]
```

따라서 같은 RNN을 사용해도 학습 목표에 따라 필요한 출력과 label 구성이 달라진다.
