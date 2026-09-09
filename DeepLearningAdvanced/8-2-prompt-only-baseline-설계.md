# Prompt-only Baseline 설계

> 학습일: 2026-09-09

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Prompt-only Baseline은 프롬프트만으로 만드는 기준점이다

Prompt-only Baseline은 사전학습된 LLM의 parameter를 추가로 학습하지 않고, 프롬프트만 설계해 성능을 확인하는 기준점이다. 분류 문제에서는 프롬프트에 **허용된 label, 각 label의 의미, 출력 형식**을 명확히 적어야 안정적인 예측을 얻을 수 있다.

```text
분류 대상
+ 허용된 label
+ label의 의미
+ 출력 형식
→ Prompt-only Baseline
```

사람이 프롬프트 문구나 예시를 직접 수정하는 것은 **Prompt Engineering** 또는 **Prompt Template 개선**에 가깝다. 이는 모델 본체는 고정하되 학습 가능한 soft prompt parameter를 데이터로 학습하는 **Prompt Tuning**과 구분해야 한다.

### Label-only 출력은 평가를 위한 약속이다

LLM은 각 입력에 대해 `payment`, `refund` 같은 개별 예측 label을 출력한다. 모델이 Accuracy나 F1 같은 최종 성능 수치를 직접 출력하는 것이 아니라, 평가 코드가 예측 label과 정답 label을 비교해 수치를 계산한다.

```text
입력 데이터
→ LLM이 label 예측
→ Parser가 출력 형식 검증
→ 정답 label과 비교
→ Accuracy·F1 계산
```

따라서 `label-only` 형식은 단순히 사람이 읽기 편하게 만들기 위한 규칙이 아니다. 평가 코드가 모델 출력을 일관된 값으로 처리할 수 있도록 만드는 약속이다.

### Parser는 출력 전체가 규칙에 맞는지 검증한다

Parser는 LLM의 원본 출력을 받아 평가에 사용할 수 있는 형식인지 검사한다. `parse_label_only()`는 설명문 속에서 label을 억지로 찾아내는 함수가 아니라, **출력 전체가 허용된 label 하나와 일치하는지 확인**하는 함수다. 형식이 맞지 않으면 `None`을 반환한다.

허용된 label이 다음과 같다고 가정한다.

```text
refund
payment
shipping
```

다음 출력은 허용된 label 하나만 포함하므로 평가에 사용할 수 있다.

```text
payment
```

반면 다음 출력은 설명문이 함께 있으므로 label-only 형식에 맞지 않는다.

```text
The label is payment.
```

### Prompt Template을 구체적으로 작성해야 하는 이유

단순히 다음과 같이 요청하면 분류 기준과 출력 규칙이 불명확하다.

```text
Classify this message.
```

어떤 label 중에서 선택해야 하는지, 각 label을 어떤 의미로 사용해야 하는지, 어떤 형식으로 답해야 하는지를 프롬프트에 명시해야 한다. 이렇게 Prompt Template을 개선하면 모델을 추가로 학습하지 않는 환경에서도 출력을 안정적으로 얻고 같은 기준으로 평가할 수 있다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| 사람이 프롬프트 문장을 수정하는 것을 Prompt Tuning이라고 이해했다. | 이번 방식은 Prompt Engineering 또는 Prompt Template 개선에 가깝다. Prompt Tuning은 학습 가능한 soft prompt parameter를 데이터로 학습하는 별도의 기법이다. |
| 모델 성능은 숫자로 비교하므로 LLM이 처음부터 성능 수치를 출력해야 한다고 생각했다. | LLM은 각 데이터의 label을 예측하고, 평가 코드가 예측 label과 정답 label을 비교해 최종 성능을 수치로 계산한다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Parsing이란?

Parsing은 들어온 데이터를 정해진 규칙에 따라 해석해 프로그램이 사용할 수 있는 형태로 처리하는 과정이다.

이번 강의에서는 LLM의 원본 출력이 허용된 label 형식인지 검사하는 과정으로 사용한다.

```text
LLM 출력
→ Parser로 형식 검증
→ 예측 label
→ 정답 label과 비교
→ 성능 수치 계산
```

---

### 질문: Label-only 출력 형식을 고정한다는 것은 무슨 의미인가?

모델이 허용된 label 중 하나만 출력하도록 프롬프트를 설계한다는 뜻이다. 예를 들어 `payment`는 유효하지만, `The label is payment.`처럼 설명이 붙은 출력은 label-only 형식에 맞지 않는다.

`parse_label_only()`는 형식이 맞지 않는 출력을 임의로 보정하지 않고 `None`으로 처리한다. 그래야 평가 과정에서 어떤 출력이 규칙을 지키지 않았는지 분명하게 확인할 수 있다.

---

### 질문: Prompt Template을 왜 개선하는가?

분류 대상만 제시하면 모델이 선택할 수 있는 label과 판단 기준, 출력 형식을 알기 어렵다. 프롬프트에 다음 정보를 명확히 넣어야 한다.

```text
분류 대상
+ 허용된 label
+ label의 의미
+ 출력 형식
```

이를 통해 Prompt-only 환경에서도 모델의 예측을 일관된 형식으로 받아 평가할 수 있다.

---

### 이해한 내용: Label 예측부터 성능 계산까지의 흐름

Prompt-only Baseline에서는 모델을 추가로 학습시키지 않고 프롬프트를 설계해 각 입력의 label을 예측한다.

Label-only 출력과 parsing의 핵심 목적은 결과를 보기 좋게 만드는 것이 아니라, 모델 출력을 일관된 label로 검증하는 것이다. 검증된 예측 label을 정답과 비교한 뒤 평가 코드가 Accuracy와 F1 같은 최종 성능 수치를 계산한다.
