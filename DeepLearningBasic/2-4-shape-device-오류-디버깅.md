# Shape·Device 오류 디버깅

> 학습일: 2026-08-20

## 핵심 정리

PyTorch에서 오류가 발생하면 긴 Traceback을 처음부터 모두 해석하려 하기보다 먼저 Shape, dtype, Device 중 어떤 종류의 문제인지 분류한다.

Shape 오류에서는 실제 Tensor의 Shape와 모델이 기대하는 Shape를 비교한다. `nn.Linear`라면 입력 Tensor의 마지막 차원과 `in_features`가 같은지 확인한다.

Device 오류에서는 CUDA를 사용할 수 있는지보다 같은 연산에 참여하는 모델, 입력, Target이 실제로 같은 Device에 있는지를 확인하는 것이 중요하다.

> 결국 오류를 바로 고치려 하기보다 “어떤 정보를 확인해야 하는가?”부터 체크하고, 실제 값과 모델이 기대하는 값을 비교한 뒤 필요한 수정만 해야 한다.

---

## 오류별 디버깅 체크리스트

PyTorch 오류는 먼저 다음 세 종류를 확인한다.

```text
Shape
→ Tensor 모양 문제

dtype
→ 데이터 자료형 문제

Device
→ CPU와 GPU 위치 문제
```

오류 종류에 따라 실제 정보와 기대 정보를 비교한다.

```text
Shape 오류
→ 실제 Tensor Shape
→ 모델과 연산이 기대하는 Shape

dtype 오류
→ 실제 Tensor dtype
→ 모델이나 Loss가 요구하는 dtype

Device 오류
→ 모델 파라미터 Device
→ 입력 Tensor Device
→ Target Tensor Device
```

Tensor를 디버깅할 때 자주 확인하는 값은 다음과 같다.

```python
print(x.shape)
print(x.dtype)
print(x.device)
```

수정 도구부터 고르지 않고 다음 순서로 확인한다.

```text
오류 종류 분류
→ 오류가 난 연산에 참여하는 대상 확인
→ 실제 정보와 기대 정보 비교
→ 원인에 맞는 부분만 수정
→ 다시 실행해 검증
```

---

## `nn.Linear`의 입력 Feature 차원

다음 입력과 모델을 확인했다.

```python
x = torch.randn(8, 5)
model = nn.Linear(5, 2)

print("x shape:", x.shape)
print("model expects in_features:", model.in_features)
```

`nn.Linear`에서는 입력 Tensor의 마지막 차원과 `in_features`가 같아야 한다.

```text
x.shape = (8, 5)

8 = Batch Size
5 = Feature 수
```

따라서 `nn.Linear(5, 2)`는 이 입력의 Feature 5개를 받아 출력 2개를 만드는 올바른 구조다.

핵심 비교는 다음과 같다.

```python
x.shape[-1] == model.in_features
```

---

## Shape 오류 실습: 단일 Sample과 Batch 차원

Feature가 5개인 단일 Sample을 다음처럼 만들었다.

```python
single_sample = torch.randn(5)
batch_sample = single_sample.unsqueeze(0)

print("single shape:", single_sample.shape)
print("batch shape:", batch_sample.shape)
```

Shape는 다음처럼 바뀐다.

```text
(5,)
→ unsqueeze(0)
→ (1, 5)
```

`(5,)`는 Feature 5개를 가진 단일 Sample이고, `(1, 5)`는 Sample 1개와 Feature 5개를 가진 Batch 형태다.

처음에는 두 Tensor의 Shape가 다르면 `squeeze`나 `unsqueeze`로 Shape를 맞출 수 있다고 생각했다.

하지만 두 연산은 모든 Shape Mismatch를 해결하는 도구가 아니다. 이번에는 모델에 넣을 Batch 차원이 실제로 하나 필요했기 때문에 `unsqueeze(0)`이 올바른 수정이었다.

Shape가 다르다는 이유만으로 차원을 추가하거나 제거하지 않고 모델과 연산이 어떤 Shape를 요구하는지 먼저 확인한다.

---

## Broadcasting은 항상 확인해야 할까?

처음에는 Shape 오류를 만나면 다음 항목을 모두 확인해야 한다고 생각했다.

- 각 Tensor의 Shape
- Feature 수
- `squeeze`와 `unsqueeze` 사용 가능 여부
- Broadcasting 조건
- Broadcasting 결과 Shape

이 항목들은 잘못된 내용은 아니다.

하지만 이번 Shape·Device 디버깅 체크리스트 과제에서는 Broadcasting까지 넣을 필요는 없었다.

먼저 확인할 핵심은 다음 세 가지다.

```text
1. 실제 Tensor Shape 확인
2. 모델이 기대하는 Shape와 비교
3. 모델과 Tensor의 Device 확인
```

Broadcasting은 오류가 난 연산에서 실제로 서로 다른 Shape의 Tensor를 함께 계산하는 경우 추가로 확인한다.

---

## 디버깅 체크리스트 작성

### `checklist = []`에는 무엇을 넣어야 할까?

처음에는 단순 문자열을 적는 과제인지 실제 해결 방법까지 자세히 적어야 하는지 헷갈렸다.

이 문제는 Shape나 Device 오류가 발생했을 때 무엇을 확인할 것인지 문자열로 세 가지 정도 정리하는 문제였다.

```python
checklist = [
    "입력과 target의 shape를 확인한다.",
    "입력의 마지막 차원과 모델의 in_features를 비교한다.",
    "모델과 입력/target Tensor의 device를 확인한다."
]

for i, item in enumerate(checklist, 1):
    print(i, item)
```

여기서는 `squeeze`, `unsqueeze`, Broadcasting 같은 해결 방법을 바로 나열하기보다 무엇을 검사할 것인지부터 적는 것이 핵심이다.

---

## Device Mismatch에서 확인할 것

### `torch.cuda.is_available()`이 핵심 검사일까?

Device 오류를 생각하면서 처음에는 다음 항목을 떠올렸다.

- `torch.cuda.is_available()` 확인
- 모델 Device 확인
- Tensor Device 확인

하지만 `torch.cuda.is_available()`은 현재 환경에서 CUDA를 사용할 수 있는지 확인하는 함수다. 이미 발생한 Device Mismatch에서 어떤 객체들의 위치가 다른지 직접 찾아주는 검사는 아니다.

Device Mismatch에서는 같은 연산에 참여하는 모델과 Tensor가 같은 Device에 있는지를 확인해야 한다.

```text
model  → cuda
x      → cuda
target → cuda
```

입력과 모델 파라미터의 Device는 다음처럼 확인할 수 있다.

```python
print(x.device)
print(next(model.parameters()).device)
```

`CrossEntropyLoss`처럼 Output과 Target을 함께 사용하는 연산에서는 Target의 Device도 중요하다.

```python
print(output.device)
print(target.device)
```

---

## 다시 볼 때 핵심

PyTorch 오류가 발생하면 Shape, dtype, Device부터 확인한다.

`nn.Linear`에서는 입력 Tensor의 마지막 차원과 `in_features`가 같아야 한다.

`(5,)`인 단일 Sample에 Batch 차원이 필요하다면 `unsqueeze(0)`으로 `(1, 5)`를 만든다.

`squeeze`와 `unsqueeze`는 모든 Shape Mismatch의 해결책이 아니다. 모델이 요구하는 Shape를 먼저 확인한다.

`torch.cuda.is_available()`은 CUDA 사용 가능 여부를 확인한다. Device Mismatch의 원인은 같은 연산에 참여하는 모델과 Tensor의 실제 Device를 비교해 찾는다.

해결 방법을 바로 적용하기보다 무엇이 다른지 검사하고 원인에 맞는 수정만 한다.
