# 입출력 차원 계산과 Flatten

> 학습일: 2026-08-20

## 1. 오늘 학습 키워드

- MLP 입력 Shape
- 이미지 Tensor와 Flatten
- Batch Dimension 유지
- `torch.flatten(x, start_dim=1)`
- `nn.Linear`의 `in_features`

## 2. 오늘 학습한 내용을 나만의 언어로 정리하기

### 이미지 Tensor를 MLP 입력으로 바꾸기

MLP의 `nn.Linear`에 넣는 입력은 기본적으로 `(batch_size, features)` 형태로 생각한다. 이미지 Tensor는 `(batch_size, channels, height, width)` 형태이므로 한 Sample의 `channels × height × width`를 하나의 Feature 차원으로 펼쳐야 한다.

```text
(batch_size, channels, height, width)
→ flatten
→ (batch_size, channels × height × width)
```

`torch.flatten(x, start_dim=1)`은 0번 차원인 Batch Dimension을 유지하고 1번 차원부터 마지막 차원까지 펼친다.

```python
flat = torch.flatten(images, start_dim=1)
```

### `in_features` 계산

이미지의 첫 Linear가 받는 `in_features`는 Batch Size가 아니라 Sample 하나의 전체 Feature 수다.

```text
in_features = channels × height × width
```

`nn.Linear`에 입력할 때는 Flatten 결과의 마지막 차원과 `in_features`가 일치해야 한다.

## 3. 학습하며 겪었던 문제점과 해결 과정

### 질문: 이미지 Flatten과 `in_features` 실습 풀이가 맞는가?

이미지 Shape가 `(8, 1, 28, 28)`일 때 다음 풀이는 맞았다.

```python
flat = torch.flatten(images, start_dim=1)
```

```text
(8, 1, 28, 28)
→ (8, 784)

8          = 유지된 Batch Size
1 × 28 × 28 = Sample 하나의 Feature 수 784
```

첫 Linear의 입력 차원을 다음처럼 계산한 것도 맞았다.

```python
in_features = 1 * 28 * 28
model = nn.Linear(in_features, 4)
```

`in_features`는 `784`이며 Flatten된 입력의 마지막 차원과 일치한다.

---

### 이해한 내용: `reshape`·`view` 실습에서 `flatten`을 사용한 부분

다음 코드로 `(2, 3, 4)`를 `(2, 12)`로 만드는 원리 자체는 맞게 이해했다.

```python
small = torch.randn(2, 3, 4)
small_flat = torch.flatten(small, start_dim=1)
```

다만 해당 문제의 목적은 `reshape` 또는 `view`를 연습하는 것이었다. 아직 두 방법을 복습하지 않아 알고 있는 `flatten`으로 해결했으므로 `reshape`와 `view`의 사용법 및 차이는 이번 문서에서 확정적으로 다루지 않는다.
