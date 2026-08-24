# MLP의 입력층·은닉층·출력층

> 학습일: 2026-08-20

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### MLP의 구조와 Shape 흐름

MLP는 입력을 하나 이상의 Hidden Layer에 통과시켜 새로운 표현으로 바꾼 뒤 Output Layer에서 최종 결과를 만든다.

```text
입력
→ hidden layer
→ output layer
```

각 Layer를 통과할 때 일반적으로 Batch Size는 유지되고 Feature 차원이 바뀐다.

```text
(4, 6)
→ Linear(6, 3)
→ (4, 3)
→ Linear(3, 2)
→ (4, 2)
```

`nn.Linear(in_features, out_features)`는 입력의 마지막 Feature 수를 `in_features`에서 `out_features`로 변환한다. Layer 객체만 변수에 대입하는 것으로 계산되지는 않으며 `layer(x)`처럼 입력을 전달해야 한다.

### Hidden Size와 Layer 개수

Hidden Size는 Hidden Layer의 개수가 아니라 해당 Layer가 출력하는 Feature 수, 즉 뉴런 수를 뜻한다.

```text
depth = Layer를 얼마나 깊게 쌓았는가
width = 한 Hidden Layer의 크기가 얼마인가
```

ReLU는 Hidden 표현에 비선형성을 적용하지만 그 자체를 Hidden Linear Layer로 세지는 않는다. 각 Hidden Linear 뒤에 ReLU가 하나씩 있다면 두 개수가 우연히 같아 보일 수 있다.

### Linear의 Parameter 수

Linear Layer의 Parameter는 Weight와 Bias로 구성된다.

```text
parameter 수
= 입력 수 × 출력 수
+ 출력 수만큼의 bias
```

ReLU에는 학습되는 Weight와 Bias가 없으므로 학습 가능한 Parameter 수는 0개다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `hidden = layer1`, `logits = layer2`처럼 쓰는 것인가?

아니다. `layer1`과 `layer2`는 Linear Layer 객체이므로 실제 Tensor 결과를 얻으려면 이전 단계의 데이터를 전달해 호출해야 한다.

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

`nn.Sequential`로 여러 Layer를 묶었다면 `model(x)`를 호출할 때 입력이 등록된 Layer를 순서대로 통과한다.

---

### 질문: `hidden_dim=4`는 Linear의 숫자를 4로 바꾸는 것인가, Layer를 4개 만드는 것인가?

`hidden_dim=4`는 Hidden Layer를 4개 만든다는 뜻이 아니라 Hidden Layer가 출력하는 Feature 수를 4로 정한다는 뜻이다.

```python
nn.Linear(6, 4)
nn.Linear(4, 2)
```

앞 Layer가 Hidden Feature 4개를 만들면 다음 Layer도 그 4개를 입력으로 받아야 한다.

---

### 질문: Hidden Layer 개수는 ReLU 개수로 세는가?

아니다. ReLU 자체가 Hidden Layer인 것은 아니다.

```python
nn.Linear(6, 4)
nn.ReLU()
nn.Linear(4, 4)
nn.ReLU()
nn.Linear(4, 2)
```

이 구조에서는 처음 두 Linear가 Hidden 표현을 만들기 때문에 Hidden Layer가 2개다. 각 Hidden Linear 뒤에 ReLU가 하나씩 있어 개수가 같아 보일 뿐이다.

---

### 이해한 내용: Parameter 수 계산

Linear Layer의 Parameter 수는 `입력 수 × 출력 수 + 출력 수`로 계산한다.

```text
Linear(6, 4)
= 6 × 4 + 4
= 28

Linear(4, 2)
= 4 × 2 + 2
= 10

전체 = 38
```

Hidden Layer가 두 개인 Model에서는 `Linear(4, 4)`가 추가된다.

```text
Linear(4, 4)
= 4 × 4 + 4
= 20

전체 = 38 + 20 = 58
```
