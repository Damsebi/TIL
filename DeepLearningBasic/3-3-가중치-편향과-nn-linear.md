# 가중치·편향과 `nn.Linear`

> 학습일: 2026-08-20

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### `nn.Linear`의 Shape와 Parameter

`nn.Linear(in_features, out_features)`는 입력 Tensor의 마지막 Feature 차원을 `in_features`에서 `out_features`로 바꾸며 Batch Size는 유지한다.

`nn.Linear(5, 3)`을 만들면 PyTorch가 Weight와 Bias를 Layer 내부에 학습 가능한 Parameter로 생성한다.

```text
linear.weight.shape = (3, 5)
linear.bias.shape   = (3,)
```

일반화하면 다음과 같다.

```text
weight.shape = (out_features, in_features)
bias.shape   = (out_features,)
```

출력 Feature마다 Bias가 하나씩 필요하므로 전체 Parameter 수는 다음과 같다.

```text
in_features × out_features + out_features
```

### Linear의 계산과 Parameter 확인

PyTorch의 Weight 저장 방향을 반영해 Linear 계산을 직접 표현하면 다음과 같다.

```python
y_manual = x @ linear.weight.T + linear.bias
```

수학식의 `W`와 `b`는 각각 `linear.weight`와 `linear.bias`로 관리된다.

```text
수학의 W → linear.weight
수학의 b → linear.bias
```

`parameters()`는 Parameter를 순회하는 Iterator를 반환하고, `named_parameters()`는 이름과 Parameter를 함께 제공한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `in_features=5`, `out_features=3`는 지역변수인가?

아니다. 다음 코드의 `in_features`와 `out_features`는 현재 위치에 변수를 선언하는 문법이 아니라 `nn.Linear`에 값을 전달하기 위한 Keyword Argument 이름이다.

```python
linear = nn.Linear(in_features=5, out_features=3)
```

따라서 다음 코드에서는 별도 변수처럼 바로 사용할 수 없다.

```python
manual_param_count = in_features * out_features
```

변수로 직접 선언하거나 생성된 객체의 속성을 사용해야 한다.

```python
linear.in_features
linear.out_features
```

인자 이름을 생략하고 위치에 따라 값을 전달할 수도 있다.

```python
linear = nn.Linear(5, 3)
```

---

### 질문: Bias의 수는 `out_features`만큼인가?

맞다. `nn.Linear(5, 3)`은 출력 Feature 3개를 만들므로 각 출력에 Bias가 하나씩 필요하다.

```text
weight.shape = (3, 5)
bias.shape   = (3,)

weight = 5 × 3 = 15
bias   = 3
전체   = 18
```

---

### 질문: `linear.parameters()`를 마지막에 호출해야 하는가?

`linear.parameters()` 자체는 올바른 코드지만 호출만 하면 Parameter를 순회할 수 있는 Iterator를 얻는다. 실제 내용을 확인하려면 반복문 등으로 Iterator를 순회해야 한다.

```python
for name, param in linear.named_parameters():
    print(name, param.shape, param.numel())
```

이 코드는 Parameter를 새로 만들거나 수정하는 것이 아니라 이미 `linear` 안에 있는 Weight와 Bias의 이름·Shape·원소 수를 확인한다.

```text
parameters()       → parameter
named_parameters() → 이름 + parameter
```

---

### 질문과 이해 수정: 직접 Linear를 계산할 때 `W`와 `b`는 무엇인가?

#### 처음 이해

직접 계산식 `x @ W.T + b`에서 `W`와 `b`를 어떻게 가져와야 하는지 몰라 입력 `x`, Shape 정보, 출력 Feature 수를 사용하려고 했다.

```python
y_manual = x @ x.T + x.shape
y_manual = x @ linear.out_features + linear.out_features
```

#### 수정된 이해

`x`는 입력 데이터이고 `x.shape`는 입력의 크기 정보다. `linear.out_features`도 출력 Feature 수인 정수 `3`일 뿐 실제 Weight나 Bias가 아니다.

`nn.Linear(5, 3)`을 생성하면 PyTorch가 선형 계산에 사용할 `W`와 `b`를 만들고 다음 이름으로 관리한다.

```python
linear.weight
linear.bias
```

출력 3개가 각각 입력 Feature 5개에 대한 Weight를 가지므로 `linear.weight.shape`은 `(3, 5)`가 된다. 직접 계산할 때는 저장 방향에 맞춰 Weight를 전치한다.

```python
y_manual = x @ linear.weight.T + linear.bias
```

---

### 질문: `nn.Linear`를 나중에 만든다면 `W`는 어떻게 되는가?

`W`와 `b`가 `nn.Linear` 때문에 생긴 수학적 개념은 아니다. `nn.Linear`를 사용하지 않으면 직접 만들어 계산할 수 있다.

```python
W = torch.randn(3, 5)
b = torch.randn(3)

y = x @ W.T + b
```

반대로 `nn.Linear(5, 3)`을 만들면 PyTorch가 이 Weight와 Bias를 생성해 `linear.weight`, `linear.bias`라는 학습 가능한 Parameter로 관리한다.

`nn.Linear`는 직접 만들던 `W`와 `b`를 Layer 안에서 생성하고 관리해주는 Module이라고 이해했다.
