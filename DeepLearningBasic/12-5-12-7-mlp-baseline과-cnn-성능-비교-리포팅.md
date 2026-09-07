# MLP Baseline과 CNN 성능 비교·리포팅

> 학습일: 2026-08-31

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Baseline은 실험의 기준점이다

Baseline은 정해진 모델 이름이 아니라 **이번 실험에서 비교 기준으로 선택한 모델**이다.

이번에는 이미지의 공간 구조를 사용하지 않는 MLP를 baseline으로 두고, 공간 구조를 활용하는 CNN과 비교한다. 반면 filter 수나 kernel size처럼 CNN 내부 설정을 비교할 때는 기존 CNN을 baseline으로 둘 수 있다.

```text
MLP를 baseline으로 사용
→ MLP와 CNN의 구조 차이 비교

기존 CNN을 baseline으로 사용
→ filter·kernel·layer 변경 효과 비교
```

### MLP와 CNN의 입력 처리 방식

CIFAR-10 이미지의 Shape는 `(N, 3, 32, 32)`이다. MLP는 이미지를 처음부터 펼쳐 샘플당 `3 × 32 × 32 = 3072`개의 feature로 만든다.

```text
MLP
(N, 3, 32, 32)
→ Flatten
→ (N, 3072)
→ Linear → ReLU → Linear
→ (N, 10)
```

CNN은 이미지의 C, H, W 구조를 유지한 상태에서 지역 특징을 먼저 찾은 뒤 펼친다.

```text
CNN
(N, 3, 32, 32)
→ Conv2d → ReLU → Pooling
→ Feature Map
→ Flatten → Linear
→ (N, 10)
```

두 모델의 내부 처리 방식은 다르지만 같은 10개 class를 분류하므로 최종 logits의 Shape는 모두 `(N, 10)`이다.

MLP는 펼친 모든 입력을 Linear와 연결하므로 parameter가 많아질 수 있다. CNN은 작은 지역을 살펴보고 같은 filter를 여러 위치에서 공유한다. 이번 실험에서는 MLP의 `hidden_dim`을 줄여 SmallCNN과 parameter 수를 비슷하게 맞춘 뒤 구조 차이를 비교한다.

### 같은 조건에서 학습 과정까지 비교하기

두 모델의 차이를 보려면 모델 구조를 제외한 조건을 같게 맞춰야 한다.

```text
같은 dataset과 split
+ 같은 preprocessing
+ 같은 seed
+ 같은 epoch와 batch size
+ 같은 optimizer와 learning rate
+ 같은 metric 계산 방식
```

각 epoch의 `train/valid loss`와 `train/valid accuracy`를 history에 남기면 마지막 결과뿐 아니라 학습 과정도 비교할 수 있다. Learning Curve를 통해 train만 좋아지는 과적합이나 train과 validation이 모두 충분히 좋아지지 않는 과소적합도 확인한다.

Best epoch는 기준을 하나 정해서 선택한다. 이번 실험에서는 validation loss가 가장 낮은 epoch를 고르고, **같은 epoch의** loss와 accuracy를 함께 기록한다.

### 실험 결과는 조건과 한계를 함께 적는다

리포트는 단순히 어느 모델의 accuracy가 높았는지만 적지 않는다.

```text
실험 설정
→ 모델 구조
→ 학습 결과
→ 두 모델 비교
→ 결과 해석
→ 다음 실험 제안
```

결과에는 모델 이름, parameter 수, best epoch, validation loss·accuracy, history와 실험 조건을 남긴다. CSV나 그래프를 저장하는 세부 구현은 실제 실습에서 확인하고, 현재는 **무엇을 기록하고 어떤 기준으로 해석할지**에 집중한다.

결과는 dataset, seed, 모델 크기와 학습 조건의 영향을 받는다. 따라서 `CNN이 항상 MLP보다 좋다`고 일반화하지 않고 **이번 실험 조건에서 나온 결과**라고 표현한다.

Accuracy 외에도 문제의 목적에 따라 F1 Score, Precision, Recall, PR-AUC 등을 사용할 수 있다. Validation loss가 계속 감소한다면 epoch를 늘리는 실험을, 다시 상승한다면 Early Stopping을 적용하는 실험을 다음 단계로 고려할 수 있다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 여기서만 MLP를 Baseline으로 두는 것인가? 보통 같은 CNN끼리 비교하지 않나?

둘 다 가능하며 실험 목적에 따라 달라진다.

```text
이미지 처리 구조의 차이를 확인
→ MLP와 CNN 비교
→ MLP를 baseline으로 선택 가능

CNN 내부 설정의 효과를 확인
→ 기존 CNN과 변경한 CNN 비교
→ 기존 CNN을 baseline으로 선택 가능
```

즉 baseline은 항상 같은 모델이 아니라, 이번 실험에서 변화의 기준으로 삼은 모델이다.

---

### 질문: Loss와 Accuracy 중에서는 Loss를 우선해 Best Epoch를 고르는가?

이번 강의에서는 validation loss가 가장 낮은 epoch를 선택한다. 하지만 loss가 언제나 accuracy보다 절대적으로 우선하는 것은 아니며, 실험 목적에 따라 validation accuracy나 다른 metric을 기준으로 정할 수도 있다.

중요한 것은 선택 기준을 미리 정하고 서로 다른 epoch의 결과를 섞지 않는 것이다.

```text
validation loss가 가장 낮은 epoch 선택
→ 그 epoch의 validation loss 기록
→ 같은 epoch의 validation accuracy 기록
```

최소 loss가 나온 epoch와 최대 accuracy가 나온 epoch가 다르다면 두 값을 하나의 모델 결과처럼 합쳐 적지 않는다.

---

### 이해한 내용: 결과 기록과 AI 해석

실험 결과를 해석하고 문장으로 정리하는 일에는 AI를 활용할 수 있다. 다만 AI가 해석하더라도 근거가 되는 결과는 구조화해 남겨야 한다.

```text
model
parameter 수
best epoch
validation loss
validation accuracy
history
실험 조건
```

즉 **결과 데이터는 직접 보존하고, 그 결과를 비교하거나 설명하는 과정에 AI를 활용한다**고 이해했다.

---

### 이해한 내용: 리포트의 세부 구현 범위

CSV 저장 코드, 그래프 저장 방법, 세부 표 작성은 개념 설명만 길게 남기기보다 실제 실험을 수행하면서 확인하는 것이 적절하다고 판단했다.

현재 단계에서는 어떤 조건과 결과를 기록해야 하는지, 그리고 결과를 과도하게 일반화하지 않고 어떻게 설명해야 하는지가 핵심이다.

---

### 질문: 후속 실험은 별도 보고서로 작성해야 하나, 기존 보고서에 이어서 작성해야 하나?

실험 기록은 변경한 조건이 섞이지 않도록 각각 분리하고, 최종 보고서에서는 여러 실험을 하나의 이야기로 연결하는 방식이 명확하다.

```text
실험 1: MLP와 CNN 비교
→ 이번 조건에서 CNN의 결과가 더 좋음
→ 과적합 징후 확인

실험 2: CNN에 Early Stopping 적용
→ 기존 CNN 결과와 비교

실험 3: CNN filter 수 변경
→ filter 수 변화의 영향 비교
```

최종 보고서에서는 다음 흐름으로 연결한다.

```text
이전 실험 결과
→ 발견한 문제
→ 후속 실험에서 바꾼 조건
→ 새 결과와 해석
```
