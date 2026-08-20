# MLP의 입력층·은닉층·출력층

> 학습일: 2026-08-20

## 핵심 정리

MLP는 입력을 바로 최종 출력으로 보내지 않고 하나 이상의 Hidden Layer를 거치며 Feature 표현을 바꾼다. Linear Layer를 통과할 때 일반적으로 Batch Size는 유지되고 Feature 수가 바뀐다.

`layer1`은 계산 결과가 아니라 Layer 객체다. 실제 Tensor 결과를 얻으려면 `layer1(x)`처럼 이전 데이터를 인자로 넣어 호출해야 한다.

Hidden Size는 Hidden Layer의 개수가 아니라 해당 Layer가 출력하는 Feature 수다. Hidden Size를 바꾸면 다음 Linear Layer가 받는 입력 Feature 수도 함께 맞춰야 한다.

> 결국 MLP 코드를 읽을 때는 Layer 개수만 세지 말고, 각 Linear의 입력·출력 Feature가 어떻게 이어지는지와 Layer마다 Weight·Bias가 몇 개 생기는지를 함께 확인해야 한다.

---

## MLP의 기본 구조

MLP는 입력을 Hidden Layer에서 새로운 Feature 표현으로 바꾼 뒤 Output Layer에서 최종 예측 Score를 만든다.

```text
입력
→ Hidden Layer
→ Output Layer
→ 예측
```

각 부분은 다음 역할을 한다.

```text
입력
→ 원본 데이터를 받음

Hidden Layer
→ 입력 Feature를 새로운 Feature 표현으로 변환

Output Layer
→ 최종 예측 Score인 Logit 생성
```

MLP를 통과할 때 Batch Size는 유지되고 Feature 차원이 바뀔 수 있다.

```text
입력          = (4, 3)
Hidden 출력   = (4, 5)
최종 출력     = (4, 2)

4 = Batch Size
3 = 입력 Feature 수
5 = Hidden Size
2 = 출력 Class 수
```

```text
(Batch, Feature)

Linear Layer
→ Batch Size 유지
→ Feature 수 변경
```

---

## Linear Layer에 데이터를 통과시키는 방법

### Layer 객체를 변수에 대입하면 계산 결과가 될까?

처음에는 다음처럼 `layer1`과 `layer2` 자체를 변수에 넣으려고 했다.

```python
hidden = layer1
logits = layer2
```

하지만 `layer1`은 Tensor 계산 결과가 아니라 `nn.Linear` Layer 객체다.

실제 결과를 얻으려면 이전 Tensor를 괄호 안에 넣어 Layer를 호출해야 한다.

```python
hidden = layer1(x)
logits = layer2(hidden)
```

```text
x
→ layer1(x)
→ hidden
→ layer2(hidden)
→ logits
```

기억할 형태는 다음과 같다.

```text
layer(이전 데이터)
```

`nn.Sequential`을 사용하면 여러 Layer가 하나의 Model로 묶이므로 한 번에 호출할 수 있다.

```python
logits = model(x)
```

개념적으로는 내부에서 다음 계산이 차례대로 이어진다.

```text
x
→ 첫 번째 Linear
→ Activation
→ 다음 Linear
→ logits
```

---

## Hidden Size의 의미

### `hidden_dim=4`는 Hidden Layer를 4개 만들라는 뜻일까?

처음에는 다음 두 가지 중 무엇을 바꿔야 하는지 헷갈렸다.

```text
Linear 안의 출력 숫자를 4로 변경
또는
Hidden Layer 자체를 4개 생성
```

Hidden Size와 Hidden Layer 개수를 혼동한 것이다.

`hidden_dim=4`는 Hidden Layer가 출력하는 Feature 수가 4개라는 뜻이다.

기존 모델의 Hidden Size가 3이라고 하자.

```python
model = nn.Sequential(
    nn.Linear(6, 3),
    nn.ReLU(),
    nn.Linear(3, 2)
)
```

Hidden Size를 4로 바꾸면 다음과 같다.

```python
model = nn.Sequential(
    nn.Linear(6, 4),
    nn.ReLU(),
    nn.Linear(4, 2)
)
```

첫 번째 Linear가 Feature를 `6 → 4`로 바꿨으므로 다음 Linear도 Feature 4개를 입력으로 받아야 한다.

```text
입력 Feature 6
→ Hidden Feature 4
→ 출력 Feature 2

Linear(6, 4)
Linear(4, 2)
```

```text
Hidden Size
≠ Hidden Layer 개수

Hidden Size
= Hidden Layer의 Feature 수
```

---

## Hidden Layer 개수와 ReLU

### ReLU 개수로 Hidden Layer 개수를 셀 수 있을까?

다음 두 모델을 비교했다.

```python
model_a = nn.Sequential(
    nn.Linear(6, 4),
    nn.ReLU(),
    nn.Linear(4, 2)
)

model_b = nn.Sequential(
    nn.Linear(6, 4),
    nn.ReLU(),
    nn.Linear(4, 4),
    nn.ReLU(),
    nn.Linear(4, 2)
)
```

처음에는 ReLU 개수로 Hidden Layer 개수를 알 수 있는지 생각했다.

하지만 ReLU 자체가 Hidden Layer인 것은 아니다. 이 예제에서는 각 Hidden Linear 뒤에 ReLU가 하나씩 붙어 있어 개수가 우연히 같아 보인다.

`model_a`의 구조는 다음과 같다.

```text
Linear(6, 4)
→ Hidden Layer 1

ReLU

Linear(4, 2)
→ Output Layer
```

따라서 Hidden Layer는 1개다.

`model_b`의 구조는 다음과 같다.

```text
Linear(6, 4)
→ Hidden Layer 1

ReLU

Linear(4, 4)
→ Hidden Layer 2

ReLU

Linear(4, 2)
→ Output Layer
```

따라서 Hidden Layer는 2개다.

> ReLU 개수로 Hidden Layer를 세는 것이 아니라 Output Layer를 제외한 Hidden Linear 구조를 확인한다.

---

## Linear의 Parameter 수 계산

Linear Layer 하나의 Parameter 수는 Weight 수와 Bias 수를 더해 계산한다.

```text
Linear(입력 Feature 수, 출력 Feature 수)

Weight 수
= 입력 Feature 수 × 출력 Feature 수

Bias 수
= 출력 Feature 수
```

따라서 공식은 다음처럼 기억할 수 있다.

```text
Linear Parameter 수
= 입력 수 × 출력 수 + 출력 수
```

### `Linear(6, 4)`

```text
Weight = 6 × 4 = 24개
Bias   = 4개

전체 = 28개
```

### `model_a`

```python
model_a = nn.Sequential(
    nn.Linear(6, 4),
    nn.ReLU(),
    nn.Linear(4, 2)
)
```

각 Linear의 Parameter 수는 다음과 같다.

```text
Linear(6, 4)
= 6 × 4 + 4
= 28

Linear(4, 2)
= 4 × 2 + 2
= 10

model_a 전체
= 28 + 10
= 38
```

ReLU에는 학습할 Weight나 Bias가 없으므로 학습 가능한 Parameter는 0개다.

### `model_b`

`model_b`에는 가운데 `Linear(4, 4)`가 하나 더 있다.

```text
Linear(4, 4)
= 4 × 4 + 4
= 20

model_b 전체
= model_a 38 + 20
= 58
```

Linear Layer가 추가되면 그 Layer의 Weight와 Bias만큼 전체 Parameter 수도 증가한다.

---

## 다시 볼 때 핵심

MLP는 입력 Feature를 Hidden Layer에서 새로운 표현으로 바꾸고 Output Layer에서 최종 Logit을 만든다.

Layer 객체만 변수에 넣으면 계산되지 않는다. `layer(x)`처럼 이전 Tensor를 넣어 호출해야 한다.

Hidden Size는 Hidden Layer의 개수가 아니라 Hidden Layer가 출력하는 Feature 수다.

첫 번째 Linear의 출력 Feature 수와 다음 Linear의 입력 Feature 수가 이어져야 한다.

ReLU 자체를 Hidden Layer로 세지 않는다. 이 예제에서는 각 Hidden Linear 뒤에 ReLU가 하나씩 있어 개수가 같아 보일 뿐이다.

Linear의 Parameter 수는 `입력 수 × 출력 수 + 출력 수`이며, ReLU에는 학습 가능한 Parameter가 없다.
