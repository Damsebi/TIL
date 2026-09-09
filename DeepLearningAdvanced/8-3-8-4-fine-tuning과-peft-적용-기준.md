# Fine-tuning과 PEFT 적용 기준

> 학습일: 2026-09-09

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Fine-tuning은 이미 학습된 모델을 목적에 맞게 추가 학습하는 과정이다

Fine-tuning은 학습이 끝나지 않은 모델을 마저 학습하는 과정이 아니다. 이미 학습된 Base Model을 출발점으로 삼아 특정 task나 서비스 목적에 맞는 최종 모델을 만들기 위해 추가로 학습하는 과정이다.

Prompt-only 방식만으로 원하는 성능을 얻기 어렵더라도 바로 Full Fine-tuning을 선택하지는 않는다. 먼저 학습 데이터의 품질과 양, 평가 기준이 준비되어 있는지 확인하고 추가 학습에 필요한 비용도 고려해야 한다.

```text
Prompt-only Baseline 확인
→ 데이터 품질과 평가 기준 점검
→ Fine-tuning 방식 선택
→ Train
→ Validation / Evaluation
→ 최종 모델 선택
→ Serving
```

Fine-tuning도 일반적인 모델 학습과 마찬가지로 validation과 평가가 필요하다. 학습이 끝났다는 이유만으로 바로 사용자에게 답변하도록 배포하지 않고, baseline보다 실제 성능이 좋아졌는지 확인한 뒤 최종 모델을 선택한다.

### Full Fine-tuning과 PEFT는 학습하는 파라미터의 범위가 다르다

Full Fine-tuning은 Base Model의 전체 파라미터를 학습 대상으로 삼기 때문에 계산량과 메모리 등 비용이 크다.

PEFT는 **Parameter-Efficient Fine-Tuning**의 약자로, Base Model의 대부분을 `Frozen` 상태로 두고 작은 일부 파라미터만 `Trainable`하게 만들어 학습 비용을 줄이는 방식이다. Prompt-only로는 부족하지만 Full Fine-tuning의 비용이 부담스러울 때 중간 선택지로 고려할 수 있다.

```text
Prompt-only
→ parameter 학습 없음

PEFT
→ 대부분 Frozen
→ 작은 일부 parameter만 Trainable

Full Fine-tuning
→ 전체 parameter를 학습
```

### LoRA는 기존 가중치에 작은 보정값을 더한다

LoRA는 기존 가중치 `W`를 직접 다시 학습하지 않고 고정한 채, 학습 가능한 작은 두 행렬 `A`, `B`로 가중치 변화량 `ΔW`를 근사하는 PEFT 방식이다.

```text
ΔW ≈ B × A
```

LoRA를 적용한 계산은 직관적으로 다음과 같이 볼 수 있다.

```text
기존 계산 W x
+ LoRA 보정 B A x
```

즉 LoRA가 새로운 가중치만 사용해 Base Model을 대체하는 것이 아니다. 추론에서도 기존 `W`는 계속 사용되고, 특정 task에 맞게 학습한 보정값 `ΔW`가 추가된다.

### Prompt Tuning도 PEFT에 포함된다

Prompt Tuning은 입력 앞에 붙는 학습 가능한 soft prompt embedding을 학습하는 방식이므로 PEFT에 포함된다. 사람이 자연어 프롬프트 문구를 수정하며 별도의 parameter를 학습하지 않는 Prompt Engineering과는 다르다.

```text
PEFT
├─ LoRA
├─ Prompt Tuning
└─ Adapter 계열

Prompt Engineering
→ 사람이 자연어 prompt 수정
→ parameter 학습 없음

Prompt Tuning
→ soft prompt parameter 학습
→ PEFT
```

### 학습은 가중치를 결정하고 추론은 결정된 가중치를 사용한다

학습 단계에서는 forward 결과로 loss를 계산하고, `backward()`와 `optimizer.step()`을 통해 학습 대상 가중치를 수정한다.

```text
입력
→ forward
→ loss
→ backward
→ optimizer.step()
→ 학습 대상 가중치 수정
```

학습이 끝났다고 해서 가중치가 출력 계산에서 빠지는 것은 아니다. Serving 단계에서는 가중치를 더 이상 수정하지 않을 뿐, 학습으로 결정된 가중치를 사용해 forward를 수행한다.

```text
사용자 입력
→ Tokenizer
→ 학습된 가중치로 forward
→ logits
→ 다음 토큰 선택
→ 다시 forward
→ 다음 토큰 선택 반복
→ 답변 완성
```

이 추론 과정에서는 정답 label로 loss를 계산하거나 gradient를 구하지 않으며, `backward()`와 `optimizer.step()`도 실행하지 않는다.

### Checkpoint를 보존하면 성능이 나빠졌을 때 되돌릴 수 있다

Fine-tuning 결과가 baseline보다 나쁘다면 best checkpoint나 원본 Base Model로 되돌릴 수 있다.

```text
Base checkpoint
→ epoch 1
→ epoch 2: best
→ epoch 3: 성능 하락

→ best checkpoint 또는 Base checkpoint로 rollback
```

Full Fine-tuning은 기존 가중치를 변경하므로 Fine-tuning 전 Base Model이나 이전 checkpoint를 따로 보존해야 한다. 원본을 덮어썼다면 동일한 Base Model과 revision을 다시 받을 수 있어야 복구할 수 있다.

외부 API를 이용할 때는 일반적으로 Base Model과 Fine-tuned Model을 별도로 관리하므로 Fine-tuned Model 대신 Base Model을 다시 선택할 수 있다. 다만 해당 모델과 revision이 제공자에게 계속 제공되는지는 확인해야 한다.

PEFT는 Base Model을 보존하기 쉽지만 데이터 품질의 영향을 피하는 방식은 아니다. 오염된 데이터로 학습하면 adapter의 `ΔW`가 잘못 학습되어 adapter를 적용한 서비스의 성능이 떨어질 수 있다. 이때 문제가 있는 adapter를 제거하면 보존된 Base Model로 돌아갈 수 있다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| Fine-tuning을 마치면 곧바로 사용자에게 출력하는 단계로 넘어간다고 이해했다. | Fine-tuning 뒤에도 validation과 평가로 성능 개선을 확인하고 최종 모델을 선택한 다음 serving한다. |
| Fine-tuning 대상은 아직 학습이 끝나지 않은 모델이라고 이해했다. | Base Model은 이미 학습된 모델이며, 서비스 목적에 맞는 최종 모델을 만들기 위해 추가 학습한다. |
| LoRA는 기존 가중치를 사용하지 않고 새로운 가중치만 사용한다고 이해할 수 있었다. | 기존 `W`를 고정한 채 계속 사용하고, 작은 LoRA 파라미터로 학습한 `ΔW`를 보정값으로 더한다. |
| 학습이 끝나면 가중치는 더 이상 출력에 관여하지 않는다고 볼 수 있었다. | 학습은 가중치를 결정하는 과정이고, 추론은 결정된 가중치를 사용해 출력을 계산하는 과정이다. |
| PEFT는 Base Model을 직접 수정하지 않으므로 오염된 데이터의 영향을 크게 받지 않을 수 있다고 생각했다. | Base Model은 보존되지만 adapter는 오염된 데이터에 맞게 잘못 학습될 수 있어, adapter를 적용한 서비스 성능은 떨어질 수 있다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: PEFT란?

PEFT는 큰 모델 전체를 다시 학습하지 않고 일부 작은 파라미터만 학습하여 Fine-tuning 비용을 줄이는 방식이다.

```text
Prompt-only로는 부족함
→ Full Fine-tuning은 비용이 큼
→ PEFT를 중간 선택지로 고려
```

---

### 질문: Fine-tuning할 때 validation을 거치지 않고 바로 출력하는가?

아니다. Fine-tuning 결과를 validation과 평가로 확인하고 최종 모델을 선택한 뒤 serving한다.

Serving에서는 사용자 입력으로 추론만 수행한다. 정답 label을 사용한 loss 계산, `backward()`, `optimizer.step()`은 학습 과정에 해당하므로 실행하지 않는다.

---

### 질문: Fine-tuning 결과가 baseline보다 나빠지면 되돌릴 수 있는가?

가능하다. Full Fine-tuning 전의 Base Model과 학습 중간의 checkpoint를 별도로 보존하면 best checkpoint 또는 Base checkpoint를 다시 불러올 수 있다.

원본 가중치를 덮어썼다면 동일한 Base Model을 다시 받을 수 있어야 복구할 수 있으므로, 학습 전 원본과 주요 checkpoint를 보존하는 것이 중요하다.

---

### 질문: API나 외부에서 받은 Base Model이면 다시 받아도 되는가?

가능하다. 외부 API에서는 보통 Base Model과 Fine-tuned Model이 별도로 관리되므로 Fine-tuned Model을 사용하지 않고 Base Model을 다시 선택할 수 있다.

가중치를 직접 다운로드한 경우에도 같은 model revision을 다시 받을 수 있다면 원본으로 복구할 수 있다. 다만 제공자가 해당 모델이나 revision을 계속 제공하는지는 확인해야 한다.

---

### 질문: 근사란?

근사는 원래 값이나 구조와 완전히 같지는 않지만 중요한 성질을 유지하도록 비슷하게 표현하는 것이다.

LoRA에서는 큰 가중치 업데이트를 직접 학습하는 대신 작은 두 행렬의 곱으로 표현한다.

```text
ΔW ≈ B × A
```

---

### 질문: Prompt Tuning도 PEFT인가?

그렇다. Prompt Tuning은 학습 가능한 soft prompt parameter를 학습하므로 PEFT에 포함된다.

반면 Prompt Engineering은 사람이 자연어 프롬프트를 수정하며 parameter를 학습하지 않는 방식이므로 PEFT가 아니다.

---

### 질문: LoRA도 이미 학습된 모델을 조금 더 학습하는 것인가?

큰 의미에서는 맞다. 다만 Base Model의 기존 가중치 `W`를 직접 다시 학습하지 않고 `Frozen` 상태로 두며, 작은 LoRA 파라미터 `A`, `B`만 학습한다.

```text
기존 W
→ Frozen

LoRA의 작은 A, B
→ Trainable
```

기존 모델의 능력을 사용하면서 특정 task에 필요한 보정을 추가로 학습하는 방식이다.

---

### 질문: 학습이 끝난 모델에서도 가중치가 출력에 사용되는가?

사용된다. 학습이 끝나면 가중치를 더 이상 수정하지 않을 뿐, 추론에서는 학습된 가중치를 사용해 입력으로부터 logits와 출력을 계산한다.

---

### 질문: ChatGPT처럼 답변을 생성할 때도 학습 때와 같은 경로를 사용하는가?

forward까지는 연결되지만 그 이후 과정이 다르다. 학습에서는 forward 뒤에 loss 계산, 역전파, 가중치 수정이 이어진다.

답변을 생성할 때는 학습된 가중치로 forward를 수행해 다음 토큰을 선택하고, 그 토큰을 입력에 이어 붙여 다시 다음 토큰을 예측한다. 이 과정을 답변이 완성될 때까지 반복하며 gradient 계산이나 가중치 수정은 하지 않는다.

---

### 질문: 오염된 데이터로 PEFT를 하면 어떻게 되는가?

LoRA에서는 Base Model의 가중치가 고정되므로 원본 모델 자체는 보존하기 쉽다. 하지만 오염된 데이터로 학습한 LoRA adapter에는 잘못된 보정값 `ΔW`가 만들어질 수 있다.

```text
Base Model W
→ 그대로 보존

오염된 데이터
→ LoRA Adapter 학습
→ 잘못된 ΔW
→ Adapter 적용 시 서비스 성능 하락
```

따라서 PEFT에서도 데이터 품질은 중요하다.

---

### 이해한 내용: 추가 학습과 Serving의 관계

Fine-tuning과 PEFT는 이미 학습된 모델을 대상으로 serving 전에 수행하는 추가 학습 과정이다.

학습이 끝난 최종 모델은 사용자 입력을 받을 때 gradient를 계산하거나 가중치를 수정하지 않는다. 학습으로 결정된 가중치를 사용해 forward를 반복하며 다음 토큰을 예측하고 답변을 생성한다.
