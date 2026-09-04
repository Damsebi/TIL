# Dropout과 BatchNorm 적용

> 학습일: 2026-08-28

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

Dropout은 **이번 Forward에서 일부 Activation을 무작위로 0으로 만들어**, 특정 뉴런이나 특징 조합에 지나치게 의존하는 것을 줄이는 방법이다. Weight를 지우는 것이 아니며 Tensor의 Shape도 그대로 유지된다.

`p`는 각 Activation을 0으로 만들 확률이다. 너무 크게 설정하면 전달되는 정보가 지나치게 줄어 학습이 어려워질 수 있다. PyTorch에서는 학습 시 남은 값도 `1 / (1 - p)`배로 보정한다 (`p < 1`). 따라서 단순히 일부 값을 0으로 만드는 것만 수행하는 것은 아니다. ([PyTorch Dropout](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Dropout.html))

BatchNorm은 **같은 Hidden Feature를 여러 Sample에서 모아 평균·분산을 구하고 정규화**해 학습을 안정적으로 만드는 데 사용한다. 정규화 뒤에는 Feature별로 학습 가능한 `γ(scale)`와 `β(shift)`를 적용해 크기와 위치를 다시 조정한다.

이번 MLP에서 각 Layer를 넣는 위치는 다음처럼 이해했다.

```text
Dropout 적용
Linear → ReLU → Dropout → 다음 Linear

BatchNorm 적용
Linear → BatchNorm → ReLU
```

학습과 평가에서의 동작도 다르다. BatchNorm은 기본 설정인 `track_running_stats=True`를 기준으로 한다.

| Layer | `model.train()` | `model.eval()` |
| --- | --- | --- |
| Dropout | 무작위로 일부 Activation을 0으로 만들고 남은 값 보정 | 입력을 그대로 통과시킴 |
| BatchNorm | 현재 Batch의 평균·분산 사용, `running_mean`·`running_var` 갱신 | 저장된 Running Statistics 사용, 갱신하지 않음 |

MLP의 `(batch, features)` 출력에는 `BatchNorm1d(feature 수)`, CNN의 Conv 출력에는 `BatchNorm2d(channel 수)`를 연결한다는 정도까지 확인했다. CNN의 세부 동작은 이번 복습에서 확장하지 않는다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Activation(활성화값)이 무엇인가?

이번 예제에서는 Linear가 계산한 값을 ReLU에 통과시킨 뒤 다음 층으로 보내는 출력값을 말한다.

```text
Linear → ReLU → Activation → 다음 Layer
```

Dropout은 이렇게 만들어진 Hidden Activation 중 일부를 0으로 만든다고 이해했다.

---

### 질문: Dropout을 적용해도 가중치는 다음에 다시 사용할 수 있는가?

가중치는 삭제되지 않는다. 어떤 Activation이 0이 된 Forward에서는 그 값이 다음 층에 기여하지 않을 뿐이다.

다음 Forward에서는 다시 무작위로 선택하므로, 해당 Activation이 차단되지 않으면 다시 다음 층에 전달된다.

---

### 질문: Activation을 없애는 것이라면 왜 Linear 전에 넣지 않는가?

`Linear → ReLU → Dropout → 다음 Linear`에서 Dropout은 이미 **다음 Linear 바로 앞**에 있다. 먼저 만든 Hidden Activation 일부를 차단한 뒤 다음 층에 보내는 구조다.

첫 번째 Linear 앞에도 넣을 수 있지만, 그때는 Hidden Activation이 아니라 원래 입력 Feature 일부를 차단한다는 차이가 있다.

---

### 질문: BatchNorm의 `Norm`은 노름인가, 정규화인가?

여기서는 **Normalization(정규화)**을 뜻한다. 벡터의 크기를 나타내는 Norm과는 다른 개념이다.

---

### 질문: Sample 10개, Feature 3개라면 평균과 분산은 어떻게 계산하는가?

Shape가 `(10, 3)`이면 값 30개를 전부 합쳐 평균 하나를 구하지 않는다.

```text
Feature 1의 Sample 10개 → 평균·분산
Feature 2의 Sample 10개 → 평균·분산
Feature 3의 Sample 10개 → 평균·분산
```

즉 Feature별로 Batch 방향의 통계를 구하므로 평균과 분산도 각각 3개씩 필요하다.

---

### 질문: 특정 Sample에 Feature 값이 없을 수도 있지 않은가?

실제 데이터에는 결측값이 있을 수 있다. 하지만 모델에 넣을 Tensor의 Feature 구조는 일정해야 하며, BatchNorm이 결측값을 자동으로 처리해주는 것은 아니므로 사전에 처리해야 한다.

결측값을 채운 뒤 결측 여부를 별도의 Mask Feature로 추가하는 방법도 확인했다.

```text
원본:      [180, 결측, 30]
값 채우기: [180, 65, 30]
Mask:      [0, 1, 0]
최종 입력: [180, 65, 30, 0, 1, 0]
```

여기서 `65`는 값을 채우는 예시일 뿐, 모든 결측값을 이 값으로 처리한다는 뜻은 아니다.

---

### 질문: 예전에는 Batch마다 Feature 값을 합했던 것 같은데?

그 기억은 BatchNorm이 아니라 **Linear가 각 Sample 내부의 Feature를 가중합하는 계산**과 연결된다.

```text
Linear
→ 각 Sample 안의 Feature를 조합
→ 새로운 Hidden Feature 생성

BatchNorm
→ 같은 Hidden Feature를 여러 Sample에서 모음
→ Feature별 평균·분산 계산
```

같은 Tensor를 보더라도 Linear는 Sample 내부의 Feature 조합을, BatchNorm은 같은 Feature의 Sample 간 통계를 다룬다고 구분했다.

---

### 질문: Hidden Feature가 많아지면 어떻게 되는가?

BatchNorm도 늘어난 Feature 각각의 통계와 `γ`, `β`를 관리한다.

```python
nn.Linear(3, 1000)
nn.BatchNorm1d(1000)
```

이 경우 Linear가 만든 Hidden Feature가 1,000개이므로 BatchNorm도 1,000개를 각각 관리한다.

---

### 질문: Hidden Feature 개수는 누가 정하며 기준은 무엇인가?

`hidden_dim`은 모델 설계자가 정하는 Hyperparameter다.

너무 작으면 표현력이 부족해 과소적합이 생길 수 있고, 너무 크면 Parameter·계산량이 늘어나고 과적합 가능성도 커질 수 있다. 고정된 정답이 아니라 Train·Validation 결과를 비교하며 조정한다.

---

### 질문: `nn.BatchNorm1d(hidden_dim)`에 왜 `hidden_dim`을 넣는가?

BatchNorm이 **관리해야 하는 Feature 수**를 알려주기 위해서다.

```python
nn.Linear(20, 128)
nn.BatchNorm1d(128)
```

Linear 출력이 `(batch, 128)`이므로 BatchNorm에는 128을 넣는다. Batch Size가 아니라 Hidden Feature 개수에 맞춘다는 점을 이해했다.

---

### 이해 수정: BatchNorm 결과의 범위

처음에는 BatchNorm을 적용하면 값이 `0~1` 사이로 정규화된다고 생각했다.

BatchNorm은 범위를 `0~1`로 제한하지 않는다. 학습 시 Feature별 평균·분산을 기준으로 표준화하므로 음수나 1보다 큰 값도 나올 수 있다.

평균 약 0·분산 약 1이라는 설명은 학습 시 **`γ`, `β`를 적용하기 전 정규화 단계**에 대한 것이다. 분모의 작은 보정값이나 원래 분산에 따라 분산이 정확히 1이 아닐 수 있고, 이후 `γ`, `β`까지 적용한 최종 출력은 평균 0·분산 1로 고정되지 않는다. ([PyTorch BatchNorm1d](https://docs.pytorch.org/docs/2.14/generated/torch.nn.BatchNorm1d.html))

---

### 이해 수정: BatchNorm을 ReLU 앞에 두는 이유

처음에는 비선형 함수의 값이 너무 커지는 것을 막기 위해 ReLU 앞에 둔다고 생각했다.

이번 `Linear → BatchNorm → ReLU` 구조에서는 Linear가 만든 출력의 분포를 먼저 정규화·조정한 뒤 ReLU에 전달한다. 단순히 큰 값을 잘라내는 기능이 아니라, 학습을 안정적으로 만드는 방향으로 이해했다.

---

### 이해 수정: BatchNorm과 과적합

처음에는 BatchNorm도 과적합을 해결하는 방법이라고 생각했다.

BatchNorm의 주목적은 **학습 안정화**다. Batch 통계를 사용하면서 Regularization 효과가 생겨 과적합 완화에 도움이 될 수는 있지만, Dropout처럼 과적합 완화 자체를 주목적으로 하는 방법과는 구분했다.
