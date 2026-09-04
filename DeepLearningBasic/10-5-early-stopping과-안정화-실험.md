# Early Stopping과 안정화 실험

> 학습일: 2026-08-28

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

Early Stopping은 **Validation 성능이 더 이상 충분히 좋아지지 않으면 학습을 멈추는 방법**이다. 무조건 정해진 Epoch까지 학습하기보다, 과도한 학습과 과적합을 줄이기 위해 사용한다.

이번에는 Validation Loss를 기준으로 판단하며, 매 Epoch가 끝날 때 한 번 확인한다. 개선되면 best를 갱신하고 기다린 횟수를 초기화한다. 개선되지 않으면 기다린 횟수를 늘린다.

```text
Validation Loss 확인
├─ min_delta 기준을 만족하는 개선
│  → best_loss 갱신
│  → best checkpoint 즉시 저장
│  → counter = 0
└─ 개선 없음
   → counter += 1
   → counter >= patience이면 학습 종료
```

여기서 best는 **`min_delta` 기준으로 충분한 개선이 인정된 상태**를 뜻한다. Loss가 조금 낮아졌더라도 기준을 충족하지 못하면 best를 갱신하지 않는다. 따라서 기록된 Loss 중 단순한 최솟값과 다를 수 있다.

마지막으로 학습한 Epoch가 가장 좋은 Epoch라는 보장은 없다. 학습을 종료한 뒤에는 마지막 모델을 그대로 쓰는 것이 아니라, 선택해 둔 best checkpoint의 모델 상태를 불러와 사용한다.

### 안정화 실험 비교

Baseline은 절대적으로 아무 기법도 없는 모델이 아니라 **이번 실험에서 비교 기준으로 삼은 모델**이다.

| 실험 조건 | 확인할 내용 |
| --- | --- |
| Baseline | 비교 기준이 되는 Validation 성능과 학습 곡선 |
| Baseline + Dropout | 특정 뉴런·특징 조합에 대한 의존을 줄였을 때 과적합이 완화되는지 |
| Baseline + BatchNorm | 중간 출력의 분포를 조정했을 때 학습이 안정적으로 진행되는지 |
| Baseline + Dropout + BatchNorm | 각각 단독으로 적용한 경우와 비교해 함께 사용한 효과가 있는지 |
| 비교할 모델 구성 + Early Stopping | 같은 구성에서 중단 기준을 적용했을 때 선택된 모델과 종료 시점이 어떻게 달라지는지 |

위 조건은 앞 단계에 무조건 하나씩 덧붙여야 한다는 순서가 아니라 비교할 실험들이다. 비교하려는 조건 외에는 최대한 같게 유지하고, 한 번에 하나씩 바꾸어 효과를 확인한다.

예를 들어 BatchNorm의 효과를 보고 싶다면 Baseline에서는 BatchNorm을 제외한다. Dropout+BatchNorm 조합도 단독 적용 결과와 함께 비교해야 어떤 추가 효과가 있었는지 판단하기 쉽다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `patience`는 오차 범위 안에서 얼마나 더 학습할지를 의미하는가?

처음에는 개선의 크기와 기다리는 기간을 함께 생각했지만, 두 설정의 역할이 다르다.

```text
min_delta
→ 얼마나 좋아져야 개선으로 인정할 것인가

patience
→ 개선이 없어도 몇 번까지 기다릴 것인가
```

이번 메모의 기준에서 `min_delta=0.01`, `patience=3`이라면 best loss보다 최소 0.01 이상 좋아지지 않은 상태가 3 Epoch 연속될 때 중단한다. 중간에 충분한 개선이 있으면 `counter`는 다시 0이 된다.

이는 매 Epoch마다 Validation을 한 번 수행할 때의 설명이다. 기다리는 횟수는 실제로 Early Stopping을 판단하는 주기와 함께 읽어야 한다.

---

### 이해한 내용: `improved`와 `should_stop`

두 값은 서로 다른 질문에 대한 답이다.

```text
improved
→ 이번 결과가 충분히 좋아졌는가?

should_stop
→ 이제 학습을 멈춰야 하는가?
```

`improved=True`이면 best를 갱신하고 checkpoint를 저장한다. `improved=False`라도 아직 `counter`가 `patience`에 도달하지 않았다면 계속 학습한다.

`should_stop=True`가 되었을 때 학습 루프에서 `break`하여 종료한다.

---

### 질문: Best Checkpoint는 학습이 모두 끝난 뒤 저장하는가?

아니다. 새로운 best로 인정되는 **그 시점의 모델을 바로 저장**한다.

각 감소가 개선 기준을 충족했다면 다음과 같이 남는다.

```text
Epoch 1 → 0.50 → best 저장
Epoch 2 → 0.43 → best 갱신
Epoch 3 → 0.39 → best 갱신
Epoch 4 → 0.41 → 갱신하지 않음
Epoch 5 → 0.42 → 갱신하지 않음
```

학습이 더 진행되어 현재 모델이 바뀌어도 best checkpoint에는 Epoch 3의 모델 상태가 남는다. 종료 후 마지막 모델을 저장하는 것과는 다르다고 이해했다.

---

### 질문: 일반 Checkpoint와 Best Checkpoint는 어떻게 다른가?

저장 목적이 다르다.

```text
Best Checkpoint
→ 설정한 Validation 개선 기준으로 선택한 모델 보관
→ 최종 모델 선택용

일반 / Latest Checkpoint
→ 현재까지 진행한 학습 상태 보관
→ 학습 재개용
```

Latest checkpoint에는 현재 Epoch, 모델과 Optimizer 상태, Early Stopping의 `best_loss`·`counter` 같은 진행 상태도 담을 수 있다. 구체적인 저장 항목은 구현에 따라 달라진다.

일반 checkpoint를 매 Epoch 저장하는 것은 Early Stopping 자체의 필수 조건이 아니다. 중단 시점의 최신 상태까지 보관할지는 별도의 저장 정책이다.

---

### 이해 수정: `patience=5`인 경우

`patience=5`는 전체 학습의 5 Epoch에서 멈춘다는 뜻이 아니다. **마지막으로 충분히 개선된 뒤, 개선 없이 기다린 횟수가 5가 되면 멈춘다.**

Best Epoch가 3이고 그 뒤로 개선이 없다면 다음과 같다.

```text
Epoch 3 → BEST      → counter = 0
Epoch 4 → 개선 없음 → counter = 1
Epoch 5 → 개선 없음 → counter = 2
Epoch 6 → 개선 없음 → counter = 3
Epoch 7 → 개선 없음 → counter = 4
Epoch 8 → 개선 없음 → counter = 5 → should_stop = True → break
```

Best checkpoint는 Epoch 3의 모델이고, 실제로 학습을 중단한 시점은 Epoch 8이다. 이 시점의 latest checkpoint도 따로 저장하도록 구현했다면 Epoch 8의 학습 상태를 보관할 수 있다. Epoch 9는 실행하지 않는다.
