# 입출력 차원 계산과 Flatten

> 학습일: 2026-08-20

## 핵심 정리

이미지 Tensor를 MLP에 입력하려면 Sample 하나의 `channels × height × width`를 하나의 긴 Feature 차원으로 펼쳐야 한다. 이 과정을 Flatten이라고 한다.

이때 Batch 차원은 유지해야 하므로 `torch.flatten(images, start_dim=1)`을 사용한다. 첫 번째 Linear의 `in_features`에는 Batch Size가 아니라 Flatten한 Sample 하나의 Feature 수를 지정한다.

`nn.Linear`는 입력 Tensor의 마지막 차원을 Feature 차원으로 사용한다. 따라서 Linear에 넣기 직전에는 `입력.shape[-1]`과 `in_features`가 일치하는지 확인해야 한다.

> 결국 이미지 입력의 전체 Shape를 외우는 것보다 Batch 차원과 Sample 하나의 Feature 차원을 구분하고, Linear 직전의 마지막 차원을 확인하는 것이 중요하다.

---

## MLP에 이미지 Tensor를 입력하는 방법

MLP의 Linear Layer에는 일반적으로 다음과 같이 Sample별 Feature가 한 차원에 모인 입력을 사용한다.

```text
(Batch Size, Features)
```

반면 이미지 Tensor는 보통 다음 Shape를 가진다.

```text
(Batch Size, Channels, Height, Width)
```

예를 들어 흑백 이미지 16장의 Shape가 `(16, 1, 28, 28)`이라면 각 Sample의 정보가 Channel, Height, Width 세 차원에 나뉘어 있다.

```text
(16, 1, 28, 28)
→ Flatten
(16, 784)
```

Sample 하나의 Feature 수는 다음과 같다.

```text
1 × 28 × 28 = 784
```

따라서 첫 번째 Linear의 입력 차원도 784로 맞춘다.

```python
nn.Linear(784, hidden_dim)
```

여기서 `16`은 한 번에 처리하는 Sample 수인 Batch Size이므로 `in_features` 계산에 포함하지 않는다.

```text
in_features
= Sample 하나의 Feature 개수

Batch Size
≠ in_features의 일부
```

---

## Batch 차원을 유지한 Flatten

이미지를 펼칠 때는 여러 Sample이 하나로 섞이지 않도록 Batch 차원을 유지해야 한다.

```python
images = torch.randn(8, 1, 28, 28)

flat = torch.flatten(images, start_dim=1)
```

`start_dim=1`은 0번 차원부터 펼친다는 뜻이 아니라 1번 차원부터 마지막 차원까지 합친다는 뜻이다.

```text
0번 차원
→ Batch 차원이므로 유지

1번 차원부터 마지막 차원
→ 하나의 Feature 차원으로 펼침
```

결과 Shape는 다음과 같다.

```text
images.shape = (8, 1, 28, 28)
flat.shape   = (8, 784)
```

만약 0번 차원부터 모두 펼치면 Batch 구분까지 사라져 전체가 하나의 1차원 Tensor가 된다. MLP 입력을 만들 때는 보통 원하는 형태가 아니다.

---

## `nn.Linear`의 `in_features`와 입력 Shape

### 왜 이미지 입력에 Flatten이 필요할까?

처음에는 이미지를 `nn.Linear(784, 10)`에 넣을 때 왜 Flatten해야 하는지 확인했다.

`nn.Linear`는 정확히 2차원 Tensor만 받는 Layer라기보다 입력 Tensor의 **마지막 차원**을 Feature 차원으로 보고 계산하는 Layer다. 따라서 입력의 마지막 차원이 자신의 `in_features`와 같아야 한다.

Flatten 전 이미지 Shape는 다음과 같다.

```text
images.shape = (16, 1, 28, 28)

입력의 마지막 차원 = 28
Linear의 in_features = 784
```

마지막 차원 28과 `in_features` 784가 일치하지 않으므로 `nn.Linear(784, 10)`에 바로 넣을 수 없다.

```text
(16, 1, 28, 28)
→ Flatten
(16, 784)
```

Flatten 후에는 마지막 차원이 784가 되므로 Linear의 입력 조건과 일치한다.

```python
linear = nn.Linear(784, 10)
output = linear(flat)
```

Shape의 흐름은 다음과 같다.

```text
(16, 1, 28, 28)
→ Flatten
(16, 784)
→ Linear(784, 10)
(16, 10)
```

실전에서는 Linear에 데이터를 넣기 전에 다음 조건을 확인한다.

```text
입력.shape[-1] == linear.in_features
```

---

## 이미지 Tensor Flatten 실습

다음 코드로 이미지 8장의 Batch 차원을 유지하면서 나머지 차원을 펼쳤다.

```python
images = torch.randn(8, 1, 28, 28)

flat = torch.flatten(images, start_dim=1)

print("images shape:", images.shape)
print("flat shape:", flat.shape)
```

예상 결과는 다음과 같다.

```text
images shape: torch.Size([8, 1, 28, 28])
flat shape: torch.Size([8, 784])
```

Batch Size 8은 유지되고 나머지 `1 × 28 × 28`이 Feature 784개로 합쳐진다.

---

## MLP 입력 차원 맞추기 실습

첫 번째 Linear의 `in_features`를 Sample 하나의 Feature 수로 계산했다.

```python
in_features = 1 * 28 * 28

model = nn.Linear(in_features, 4)

print("model.in_features:", model.in_features)
```

```text
in_features = 784
```

Flatten한 입력의 마지막 차원과 Linear의 `in_features`가 모두 784이므로 서로 연결할 수 있다.

```text
flat.shape           = (8, 784)
model.in_features    = 784
model(flat).shape    = (8, 4)
```

---

## `reshape`와 `view` 문제에서 겪은 혼동

다음 Tensor를 `(2, 12)` Shape로 만드는 문제를 풀었다.

```python
small = torch.randn(2, 3, 4)
```

작성한 코드는 다음과 같다.

```python
small_flat = torch.flatten(small, start_dim=1)
```

결과 Shape는 정확히 `(2, 12)`이므로 Batch 차원을 유지하며 나머지 차원을 펼친다는 개념에는 맞는 풀이였다.

```text
(2, 3, 4)
→ Flatten
(2, 12)
```

다만 문제 제목은 `reshape/view 사용 시 batch 차원을 유지하기`였으므로 문제의 의도는 `reshape` 또는 `view`를 직접 사용해보는 것이었다.

현재는 `reshape`와 `view`를 아직 복습하지 않았기 때문에 이미 학습한 `flatten`으로 문제를 해결했다. 따라서 이번 학습에서는 세 함수의 차이를 추측해서 확정하지 않고 다음 내용만 이해한 상태로 남겨둔다.

```text
torch.flatten(small, start_dim=1)
→ 0번 Batch 차원 유지
→ 나머지 차원을 하나로 합침
→ (2, 12)
```

아직 복습이 필요한 내용은 다음과 같다.

- `reshape` 사용법
- `view` 사용법
- `flatten`, `reshape`, `view`의 차이

---

## 다시 볼 때 핵심

이미지 Tensor는 보통 `(Batch Size, Channels, Height, Width)` Shape를 가지며, MLP에 넣을 때는 Sample 하나의 `Channels × Height × Width`를 하나의 Feature 차원으로 펼친다.

`torch.flatten(images, start_dim=1)`은 0번 Batch 차원을 유지하고 1번 차원부터 마지막 차원까지 펼친다.

첫 번째 Linear의 `in_features`에는 Batch Size가 아니라 Sample 하나의 Feature 수를 지정한다.

`nn.Linear`는 입력의 마지막 차원을 Feature 차원으로 사용하므로 `입력.shape[-1] == linear.in_features`인지 확인한다.

`flatten`으로 `(2, 3, 4)`를 `(2, 12)`로 만드는 원리는 이해했지만, `reshape`와 `view`의 사용법 및 세 함수의 차이는 아직 복습 전이므로 이번 문서에서 확정적으로 다루지 않는다.
