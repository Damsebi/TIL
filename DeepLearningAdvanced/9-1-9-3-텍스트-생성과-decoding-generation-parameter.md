# 텍스트 생성과 Decoding·Generation Parameter

> 학습일: 2026-09-09

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Forward pass는 입력으로부터 출력을 계산하는 과정이다

Forward pass는 모델의 학습 완료 상태를 뜻하지 않는다. 입력이 모델의 계산 구조를 한 번 통과해 logits 같은 출력값을 만드는 **한 번의 순전파 과정**이다. 따라서 학습, Fine-tuning, 추론에서 모두 사용된다.

PyTorch의 `forward()`는 입력으로부터 출력을 계산하는 방법을 정의하는 메서드다. 실제로 `model(x)`를 호출하면 내부적으로 `forward()`가 실행되며 forward pass가 수행된다.

```text
forward()
→ 계산 구조를 정의

model(x)
→ 정의된 계산을 실제로 실행
→ forward pass 수행
```

학습과 생성은 모두 forward pass를 사용하지만 그 뒤의 과정이 다르다.

```text
학습
forward
→ loss
→ backward
→ parameter update

생성
forward
→ 다음 토큰 선택
→ 선택한 토큰을 입력에 추가
→ 다시 forward
```

### `generate()`는 학습이 아니라 텍스트 생성을 위한 기능이다

`generate()`는 학습 루프의 핵심 구성 요소가 아니다. 학습된 모델로 텍스트를 만들 때 forward pass와 다음 토큰 선택을 반복하도록 묶어 둔 생성 기능이다.

학습 중 결과 확인이나 평가 목적으로 `generate()`를 호출할 수는 있지만, 일반적인 학습 루프는 `forward → loss → backward → update`로 구성된다.

```text
입력 토큰
→ 모델 forward
→ 다음 토큰 선택
→ 입력 뒤에 추가
→ 다시 forward
→ 종료 조건까지 반복
```

`max_new_tokens`는 이 과정에서 **새로 생성할 토큰의 최대 개수**를 사용자가 지정하는 generation parameter다. 모델이 처리할 수 있는 전체 최대 context 길이와는 별개의 설정이지만, 실제 생성에서는 입력 토큰과 새 토큰을 합친 길이가 모델이 지원하는 범위를 넘지 않아야 한다.

### 추론에서도 필요에 따라 Batch와 Padding을 사용한다

Batch와 Padding은 학습 전용 개념이 아니다. 여러 입력을 효율적으로 추론하려면 batch로 묶을 수 있고, 입력 길이가 서로 다르면 padding으로 길이를 맞출 수 있다.

```text
단일 입력
→ 반드시 batch로 묶을 필요 없음

여러 입력
→ Batch Inference 가능
→ 길이가 다르면 Padding 사용 가능
```

`SEP` 같은 구분 토큰의 사용 여부는 모델 구조와 tokenizer의 규칙에 따라 달라진다.

### Decoding Strategy가 다음 토큰의 선택 방식을 정한다

모델은 vocabulary 전체에 대한 다음 토큰 logits를 계산한다. 그다음 어떤 후보를 실제 다음 토큰으로 선택할지 정하는 규칙이 decoding strategy다.

```text
Greedy Decoding
→ 매 단계에서 점수가 가장 높은 토큰 하나 선택

Beam Search
→ 점수가 좋은 여러 후보 경로를 유지하며 비교

Sampling
→ 확률 분포에 따라 다음 토큰 선택
```

Greedy Decoding은 매번 가장 높은 점수의 토큰을 선택하므로 같은 조건에서 결과가 일관적이다. Sampling은 확률적으로 토큰을 선택하므로 같은 입력에서도 다양한 결과가 나올 수 있다.

기본 Beam Search는 Greedy와 Sampling을 동시에 사용하는 방식이 아니다. 랜덤하게 토큰을 뽑기보다 점수가 좋은 여러 경로를 결정적으로 유지하며 비교한다. Sampling과 Beam을 결합한 별도의 방식도 있지만 기본 Beam Search와는 구분해야 한다.

### Temperature와 Top-k는 Sampling 후보 분포를 조절한다

`temperature`, `top_k`, `top_p`는 모델을 다시 학습시키는 값이 아니라 생성 단계에서 사용하는 generation parameter다.

Temperature를 낮추면 확률이 높은 후보에 더 집중하고, 높이면 여러 후보가 선택될 가능성이 커진다. Greedy는 가장 높은 점수의 토큰을 선택하므로 temperature를 적용해도 토큰의 순위가 바뀌지 않는다. 이번 강의에서는 temperature를 확률 분포를 사용하는 Sampling과 연결해 이해한다.

Top-k는 모델이 계산한 vocabulary 전체의 후보 중 점수가 높은 상위 `k`개만 남기고 그 안에서 sampling하는 방식이다. 수업 예제에 후보가 몇 개만 등장한 것은 설명을 단순화한 것이며, 실제 후보가 처음부터 그 개수로 제한된 것은 아니다.

```text
현재 입력
→ vocabulary 전체의 다음 토큰 logits
→ Top-k로 상위 k개만 남김
→ 남은 후보 안에서 Sampling
```

기본 Beam Search는 높은 점수의 경로를 유지하는 방식이므로 이번 강의에서는 temperature를 Sampling parameter로 구분한다. Sampling과 Beam을 결합한 설정에서는 temperature를 함께 사용할 수 있다.

### Generation Parameter는 재학습 없이 비교할 수 있다

Learning rate, batch size, epoch는 Fine-tuning 방법을 정하는 **학습 hyperparameter**다. 값을 바꾸면 모델을 다시 학습해야 하므로 모든 조합을 시험하는 데 큰 비용이 든다.

Weight와 bias는 학습 과정에서 값이 바뀌는 **model parameter**다. Temperature, `top_k`, `top_p`는 학습이 끝난 모델의 생성 방식을 조절하는 **generation parameter**다.

```text
learning rate, batch size, epoch
→ Fine-tuning hyperparameter

weight, bias
→ Model parameter

temperature, top_k, top_p
→ Generation parameter
```

Generation parameter는 같은 모델을 다시 학습하지 않고 값을 바꾸며 여러 출력을 비교할 수 있어 학습 hyperparameter 실험보다 비용이 작다. 개발 단계에서 task에 적절한 설정을 찾고, 서비스에서는 이를 기본값이나 task별 설정으로 사용할 수 있다.

```text
Fine-tuning 완료
→ Generation parameter를 바꾸며 결과 비교
→ Task에 적절한 설정 선택
→ 서비스 기본값 또는 Task별 설정으로 적용
→ 실제 사용자 요청에 사용
```

자유 생성은 정답 문장이 하나로 고정되지 않는 경우가 많아 단순 Accuracy만으로 평가하기 어렵다. 출력의 일관성, 다양성, 반복, 사실성 같은 여러 기준을 살피며 사람 평가와 자동 평가를 함께 사용할 수 있다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| Forward pass를 Fine-tuning이 끝난 상태라고 이해했다. | Forward pass는 학습 완료 여부가 아니라 입력으로부터 출력을 계산하는 과정이며 학습, Fine-tuning, 추론에서 모두 사용된다. |
| Training loop 안에 `generate()`가 포함된다고 이해했다. | 일반적인 학습 루프는 `forward → loss → backward → update`이고, `generate()`는 별도의 생성 과정에서 forward를 반복해 사용한다. |
| Beam Search를 Greedy와 Sampling의 가능성을 모두 열어 두는 방식이라고 이해했다. | 기본 Beam Search는 랜덤하게 sampling하지 않고 점수가 좋은 여러 후보 경로를 유지하며 비교하는 방식이다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Forward pass가 무엇인가?

입력이 모델의 계산 구조를 한 번 통과해 logits 등의 출력을 만드는 과정이다. 학습이 완료됐다는 상태가 아니라 실제 계산이 수행되는 한 번의 흐름을 뜻한다.

---

### 이해한 내용: `forward()`와 Forward pass의 관계

PyTorch의 `forward()`는 계산 구조를 정의하고, `model(x)`를 실행해 그 계산이 실제로 수행되는 과정을 forward pass라고 이해했다.

---

### 질문: `generate()`는 학습 루프에서 사용하는가?

일반적인 학습에서는 직접 사용하지 않는다. 학습 루프의 핵심은 forward, loss 계산, backward, parameter update다.

학습 도중 생성 결과를 확인하거나 평가하기 위해 사용할 수는 있지만, 이 경우에도 `generate()`가 parameter를 업데이트하는 학습 과정 자체를 대신하는 것은 아니다.

---

### 이해한 내용: `generate()`의 용도

`generate()`는 학습보다는 학습된 모델이 실제 텍스트를 생성할 때 주로 사용한다. 다음 토큰을 고르고 입력에 추가한 뒤 다시 forward하는 과정을 반복한다.

---

### 질문: 최대 토큰 수는 사용자가 지정하는가?

`max_new_tokens`는 사용자가 생성할 때 지정하는 값이며 새로 생성할 토큰 수의 상한이다.

모델에는 별도로 처리 가능한 최대 context 길이가 있다. 두 값은 같은 개념은 아니지만 입력과 생성 결과의 전체 길이는 모델이 지원하는 범위 안에 있어야 한다.

---

### 질문: Padding과 SEP는 학습에서만 사용하는가?

둘 다 학습 전용 개념은 아니다. Padding은 추론에서도 길이가 다른 여러 입력을 batch로 묶을 때 사용할 수 있다. `SEP`의 사용 여부와 의미는 모델 구조와 tokenizer에 따라 달라진다.

---

### 질문: 추론에서도 반드시 batch로 묶어야 하는가?

아니다. 단일 입력은 그대로 추론할 수 있다. 여러 입력을 효율적으로 처리하려는 경우 Batch Inference를 사용할 수 있다.

---

### 질문: Beam Search는 Greedy와 Sampling을 동시에 사용하는 방식인가?

아니다.

```text
Greedy
→ 가장 좋은 경로 하나 유지

Beam Search
→ 점수가 좋은 여러 경로 유지

Sampling
→ 확률적으로 토큰 선택
```

Sampling과 Beam을 결합한 별도의 방식은 존재하지만 기본 Beam Search와는 구분해서 이해해야 한다.

---

### 질문: Temperature는 Sampling에서만 사용하는가?

이번 강의에서는 Sampling과 연결해서 이해하면 된다.

Greedy는 가장 높은 점수의 토큰을 선택하므로 temperature로 분포를 조절해도 토큰의 순위는 바뀌지 않는다. Sampling은 확률 분포를 직접 사용하므로 temperature의 영향을 받는다.

---

### 질문: Beam Search에서도 Temperature가 의미 있지 않은가?

기본 Beam Search는 점수가 높은 경로들을 유지하는 결정적 방식이므로 이번 강의에서는 temperature를 Sampling parameter로 구분한다.

Sampling과 Beam을 결합한 방식에서는 temperature를 함께 사용할 수 있지만 기본 Beam Search와는 별개다.

---

### 질문: 후보 수가 원래 정해져 있는데 왜 Top-k가 필요한가?

예제에서 후보를 몇 개만 보여 준 것은 설명을 단순화한 것이다. 실제 모델은 vocabulary 전체의 다음 토큰 후보에 대해 logits를 계산한다.

Top-k는 이 전체 후보 중 상위 `k`개만 남기고, 남은 후보 안에서 sampling하기 위해 사용한다.

---

### 질문: Fine-tuning에서 고려할 설정이 많은데 전부 테스트하면 너무 오래 걸리지 않는가?

맞다. Learning rate, batch size, epoch 같은 학습 hyperparameter를 바꾸면 모델을 다시 학습해야 하므로 모든 조합을 전부 실험하기 어렵다.

반면 generation parameter는 학습된 모델을 그대로 둔 채 출력만 다시 생성하면 되므로 상대적으로 실험 비용이 작다.

---

### 질문: Fine-tuning parameter가 무엇인가?

대화에서 사용한 Fine-tuning parameter는 정확히는 **Fine-tuning hyperparameter**를 뜻한다.

```text
learning rate, batch size, epoch 등
→ 학습 방법을 정하는 hyperparameter

weight, bias 등
→ 학습으로 값이 바뀌는 model parameter

temperature, top_k, top_p 등
→ 생성 방식을 정하는 generation parameter
```

---

### 질문: Generation parameter는 테스트할 때 쓰는가, 실제 사용자가 이용할 때 쓰는가?

둘 다 사용한다. 개발자는 학습이 끝난 모델에 여러 generation 설정을 적용해 결과를 비교하고, 서비스에서는 선택한 설정으로 실제 사용자 요청의 출력을 생성한다.

---

### 이해한 내용: Generation Parameter 설정과 Serving

Fine-tuning을 마친 뒤 generation parameter 값을 바꾸며 결과를 비교하고 task에 맞는 설정을 선택한다. 서비스에서는 선택한 값을 기본 설정이나 task별 설정으로 적용한다.

하나의 값을 영구적으로 고정할 필요는 없으며 목적에 따라 서로 다른 설정을 사용할 수 있다고 이해했다.

---

### 질문: 생성 결과는 Accuracy처럼 수치화하기 어려운데 사람이 직접 평가해야 하는가?

자유 생성은 하나의 정답 문장이 존재하지 않는 경우가 많아 단순 Accuracy만으로 평가하기 어렵다.

실제 출력의 일관성, 다양성, 반복, 사실성 등을 여러 기준으로 평가해야 하며 사람 평가와 자동 평가 방법을 함께 사용할 수 있다.
