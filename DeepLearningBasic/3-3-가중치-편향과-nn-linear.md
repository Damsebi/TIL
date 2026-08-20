# 가중치·편향과 `nn.Linear`

> 학습일: 2026-08-20

## 핵심 정리

`nn.Linear(in_features, out_features)`는 입력 Tensor의 마지막 Feature 차원을 `in_features`에서 `out_features`로 바꾸는 Layer다. Batch Size는 유지된다.

`in_features`와 `out_features`는 생성자에 값을 전달하는 Keyword Argument 이름이지 현재 코드에 새 변수를 선언하는 문법이 아니다.

`nn.Linear`를 만들면 실제 학습 Parameter인 `weight`와 `bias`가 객체 내부에 생성된다. PyTorch는 Weight를 `(out_features, in_features)` Shape로 저장하므로 직접 계산할 때는 `x @ linear.weight.T + linear.bias`를 사용한다.

> 결국 설정값인 `in_features`·`out_features`와 실제 학습값인 `weight`·`bias`를 구분해야 Linear의 Shape와 계산을 올바르게 이해할 수 있다.

---

## `nn.Linear(in_features, out_features)`의 의미

앞 강의에서 `nn.Linear(5, 3)`이 입력 Feature 5개를 출력 Feature 3개로 바꾸고 Batch Size는 유지한다는 점을 확인했다. 이번 강의에서는 이 Shape 변환을 반복하기보다 Linear 객체 내부의 Weight와 Bias가 어떻게 만들어지고 계산에 사용되는지에 집중했다.

```text
(2, 5) → Linear(5, 3) → (2, 3)
```

---

## `in_features`와 `out_features`는 변수일까?

다음 코드에서 `in_features`와 `out_features`가 현재 코드의 지역변수로 선언되는지 궁금했다.

```python
linear = nn.Linear(
    in_features=5,
    out_features=3
)
```

처음에는 다음처럼 바로 사용할 수 있다고 생각했다.

```python
manual_param_count = (
    in_features * out_features
    + in_features
)
```

하지만 `nn.Linear(in_features=5, out_features=3)`의 `in_features`와 `out_features`는 현재 Scope에 변수를 선언하는 문법이 아니다.

`nn.Linear` 생성자에 값을 전달하기 위한 Keyword Argument 이름이다.

따로 변수로 사용하려면 직접 선언해야 한다.

```python
in_features = 5
out_features = 3

linear = nn.Linear(
    in_features,
    out_features
)
```

이름 없이 위치에 따라 바로 전달할 수도 있다.

```python
linear = nn.Linear(5, 3)
```

두 생성 방식은 같은 의미다.

이미 생성한 객체에서는 설정값을 다음처럼 확인할 수 있다.

```python
print(linear.in_features)
print(linear.out_features)
```

---

## Weight와 Bias의 Shape

`nn.Linear(5, 3)`을 만들면 Weight와 Bias의 Shape는 다음과 같다.

```text
weight.shape = (3, 5)
bias.shape   = (3,)
```

일반화하면 다음과 같다.

```text
weight.shape
= (out_features, in_features)

bias.shape
= (out_features,)
```

Weight Shape가 `(in_features, out_features)`가 아니라 `(out_features, in_features)` 순서라는 점에 주의한다.

---

## Bias 개수

### Bias는 `out_features`만큼 있을까?

맞다.

`nn.Linear(5, 3)`은 출력 Feature를 3개 만들므로 Bias도 3개다.

```text
출력 Feature 1
→ Bias 1개

출력 Feature 2
→ Bias 1개

출력 Feature 3
→ Bias 1개
```

따라서 다음 관계가 성립한다.

```text
Bias 개수
= out_features
```

---

## Linear의 Parameter 수

처음에는 다음 식으로 Parameter 수를 계산하려고 했다.

```python
manual_param_count = (
    in_features * out_features
    + in_features
)
```

마지막에 `in_features`를 더한 것이 문제였다. Bias 개수는 입력 Feature 수가 아니라 출력 Feature 수다.

```text
Weight 개수
= in_features × out_features

Bias 개수
= out_features
```

전체 Parameter 수는 다음과 같다.

```text
in_features × out_features + out_features
```

`nn.Linear(5, 3)`의 경우 다음과 같다.

```text
Weight = 5 × 3 = 15개
Bias   = 3개

전체 = 18개
```

객체의 설정값을 사용해 코드로 계산하면 다음과 같다.

```python
manual_param_count = (
    linear.in_features
    * linear.out_features
    + linear.out_features
)
```

---

## `parameters()`와 `named_parameters()`

### `linear.parameters()`를 마지막에 호출해야 확인이 끝날까?

다음 코드를 실행한 뒤 마지막에 `linear.parameters()`를 추가로 호출해야 Parameter 확인이 완료되는지 궁금했다.

```python
for name, param in linear.named_parameters():
    print(name, param.shape, param.numel())

linear.parameters()
```

처음에는 `linear.parameters()`를 호출해야 Parameter가 실제로 준비되거나 확인이 끝나는 것으로 생각했다.

하지만 `linear.parameters()`는 Parameter를 순회할 수 있는 Iterator를 반환한다. 호출만 해서는 각 Parameter의 내용을 출력하거나 변경하지 않는다.

내용을 확인하려면 직접 순회해야 한다.

```python
for param in linear.parameters():
    print(param.shape, param.numel())
```

`named_parameters()`는 Parameter와 함께 이름도 제공한다.

```python
for name, param in linear.named_parameters():
    print(name, param.shape, param.numel())
```

```text
parameters()
→ Parameter

named_parameters()
→ 이름 + Parameter
```

이 예제의 목적은 Parameter를 새로 만드는 것이 아니라 `linear` 내부에 이미 생성된 Weight와 Bias의 이름, Shape, 원소 수를 확인하는 것이다.

```text
weight
→ Shape (3, 5)
→ 15개

bias
→ Shape (3,)
→ 3개
```

---

## `nn.Linear`의 실제 계산

### 수학식의 `W`와 `b`는 코드에서 무엇일까?

다음 Forward 계산을 직접 표현하면서 Weight와 Bias를 어떻게 가져와야 하는지 헷갈렸다.

```python
x = torch.randn(2, 5)
y_layer = linear(x)
```

처음에는 다음처럼 입력 `x`를 Weight처럼 사용하려고 했다.

```python
y_manual = x @ x.T + x.shape
```

이후에는 설정값인 `out_features`를 실제 Weight와 Bias처럼 사용하려고 했다.

```python
y_manual = (
    x @ linear.out_features
    + linear.out_features
)
```

하지만 다음 값들은 서로 역할이 다르다.

```text
x
→ 입력 데이터

x.shape
→ 입력 Tensor의 크기 정보

linear.out_features
→ 출력 Feature 수를 나타내는 정수

linear.weight
→ 실제 학습되는 Weight

linear.bias
→ 실제 학습되는 Bias
```

수학에서 사용하는 `W`와 `b`는 `nn.Linear` 객체 안에서 다음 이름으로 저장된다.

```python
W = linear.weight
b = linear.bias
```

PyTorch의 Linear Forward를 직접 표현하면 다음과 같다.

```python
y_manual = (
    x @ linear.weight.T
    + linear.bias
)
```

$$
\mathbf{y}
=
\mathbf{x}\mathbf{W}^{T}+\mathbf{b}
$$

---

수학식의 `W`와 `b`는 별도의 추상적인 값이 아니라 PyTorch가 Linear 객체에 등록한 `linear.weight`와 `linear.bias`다. 위에서 확인한 Shape 때문에 직접 행렬곱할 때는 `linear.weight.T`를 사용한다.

---

## `nn.Linear`를 만들기 전의 `W`와 `b`

### `nn.Linear`가 없다면 Weight도 없을까?

`W`라는 개념 자체가 `nn.Linear` 때문에 존재하는 것은 아니다.

선형 계산은 Weight와 Bias를 직접 만들어서 수행할 수도 있다.

```python
x = torch.randn(2, 5)

W = torch.randn(3, 5)
b = torch.randn(3)

y = x @ W.T + b
```

이 경우에는 `W`와 `b`를 직접 만들고 관리한다.

반면 `nn.Linear`를 사용하면 PyTorch가 Weight와 Bias를 만들어 객체 내부에서 관리한다.

```python
linear = nn.Linear(5, 3)
y = linear(x)
```

두 방식을 비교하면 다음과 같다.

```text
직접 구현

x, W, b
→ x @ W.T + b
```

```text
nn.Linear 사용

nn.Linear(5, 3)
→ 내부에 Weight와 Bias 생성
→ linear(x)
→ x @ linear.weight.T + linear.bias
```

`nn.Linear`는 선형 계산에 필요한 Weight와 Bias를 생성하고 학습 가능한 Parameter로 관리해주는 PyTorch Module이라고 이해했다.

---

## 다시 볼 때 핵심

`nn.Linear(5, 3)`은 입력 Feature 5개를 출력 Feature 3개로 바꾸며 Batch Size는 유지한다.

Keyword Argument인 `in_features=5`와 `out_features=3`은 현재 Scope에 변수를 선언하지 않는다.

Weight Shape는 `(out_features, in_features)`이고 Bias Shape는 `(out_features,)`다.

Bias 개수는 출력 Feature 수와 같으므로 Linear의 전체 Parameter 수는 `in_features × out_features + out_features`다.

`parameters()`는 Parameter Iterator를 반환하고 `named_parameters()`는 이름과 Parameter를 함께 제공한다.

`linear.out_features`는 설정값인 정수이고, 실제 Weight와 Bias는 `linear.weight`와 `linear.bias`에 저장된다.

직접 Forward를 계산하면 `x @ linear.weight.T + linear.bias`가 된다.
