# Chat Template과 입력 디버깅

> 학습일: 2026-09-09

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Chat Model의 입력은 대화 구조로 관리한다

많은 Chat Model은 Causal LM을 기반으로 한다. 내부에서는 이전 토큰을 보고 다음 토큰을 예측하지만, 대화와 지시를 잘 따르도록 추가 학습되어 Chat Model로 사용된다. Causal LM과 Chat Model은 서로 반대되는 개념이 아니다.

```text
Causal LM
→ 이전 토큰으로 다음 토큰 예측

Chat Model
→ Causal LM 기반
→ 대화와 지시 형식에 맞게 추가 학습
```

프로그램에서는 대화를 `role`과 `content`를 가진 message 목록으로 관리한다.

```python
messages = [
    {"role": "system", "content": "짧게 답하세요."},
    {"role": "user", "content": "Causal LM이 뭐야?"},
]
```

`role`은 누가 말한 메시지로 처리할지를 나타내고, `content`는 실제 발화 내용이다.

```text
system
→ 모델의 행동 지침

user
→ 사용자의 요청

assistant
→ 모델의 이전 답변
```

새로운 첫 질문에는 이전 모델 답변이 없으므로 `assistant` message가 필요하지 않다. 멀티턴 대화에서는 이전 `user` 질문과 `assistant` 답변을 시간 순서대로 messages에 포함해야 모델이 앞선 대화를 문맥으로 사용할 수 있다.

### Chat Template은 Messages를 모델이 익힌 입력 형식으로 바꾼다

모델이 Python의 message 객체 자체를 이해하는 것은 아니다. Chat Template은 `role + content` 구조의 messages를 모델이 학습할 때 사용한 대화 입력 형식으로 변환한다.

```text
messages
→ Chat Template
→ 모델별 특수 토큰이 포함된 문자열
→ tokenize
→ input_ids
→ model
```

Chat Template은 입력 내용을 분석해 비슷한 기능을 검색하지 않는다. Tokenizer에 정의된 규칙에 따라 `system`, `user`, `assistant`를 해당 모델의 특수 토큰 형식으로 배치한다.

모델마다 대화 형식과 특수 토큰이 다르므로 직접 문자열을 조합하면 실수하기 쉽다. `apply_chat_template()`을 사용하면 tokenizer에 저장된 template에 따라 모델이 기대하는 형식으로 입력을 만들 수 있다.

Template이 기대하지 않는 role 이름을 사용하면 적용 과정에서 오류가 발생하거나 예상과 다른 결과가 나올 수 있다. 직접 만든 문자열도 모델이 토큰으로 받을 수는 있지만 학습 때 익힌 대화 형식과 다르면 성능이 떨어질 수 있다.

### Chat Template은 Decoding보다 앞에서 입력을 준비한다

9-2~9-3에서 다룬 Greedy, Sampling, Temperature, Top-k, Top-p는 모델이 logits를 계산한 뒤 다음 토큰을 고르는 방법이다. Chat Template은 그보다 앞에서 Chat Model에 넣을 입력을 준비한다.

```text
messages / Chat Template
→ tokenize
→ model forward
→ logits
→ Greedy / Sampling
→ temperature / top-k / top-p
```

### Tokenizer와 Embedding은 서로 다른 단계다

Chat 입력은 다음 순서로 처리된다.

```text
messages
→ formatted text
→ input_ids
→ generate()
```

이 과정에서 tokenizer는 문자열을 token id로 바꾸고, Embedding Layer는 token id를 vector로 바꾼다. Tokenizer 자체가 embedding을 만드는 것은 아니다.

```text
문자열
→ Tokenizer
→ token ids
→ Embedding
→ vector
→ Transformer
```

`apply_chat_template(tokenize=False)`를 사용하면 token id로 변환하지 않고 Chat Template만 적용한 formatted text 문자열을 받을 수 있다. 모델 실행 전에 role 순서와 특수 토큰이 의도한 형식으로 들어갔는지 눈으로 확인하는 데 유용하다.

### `add_generation_prompt`는 입력의 끝 모양을 정한다

`add_generation_prompt=True`는 실제 assistant 답변을 생성하는 옵션이 아니다. 지원하는 Chat Template에서 입력 마지막에 **다음 assistant 답변이 시작될 위치를 나타내는 형식**을 추가한다.

```text
add_generation_prompt=False
→ 현재 messages까지만 포맷

add_generation_prompt=True
→ 현재 messages를 포맷
→ 다음 assistant 답변 시작 표시 추가
```

예를 들어 다음 messages가 있다고 가정한다.

```text
system: 짧게 답변하라
user: 질문
```

`True`를 적용한 결과는 개념적으로 다음처럼 끝난다.

```text
<system>
짧게 답변하라
<user>
질문
<assistant>
```

마지막 `<assistant>`는 실제 답변이 아니다. 이 위치부터 assistant의 답변을 생성하라는 시작 표시이며, 답변 자체는 이후 `generate()`가 만든다.

`False`로 설정해도 `generate()`를 호출할 수는 있다. 이 경우 모델은 입력의 마지막 토큰 뒤에서 생성을 이어 간다. 다만 새 Chat 응답을 생성할 때는 assistant 차례를 명확히 표시하는 `True`가 더 적합한 경우가 많다.

이미 assistant 답변까지 포함된 완성된 대화를 포맷하거나 학습 데이터를 전처리할 때는 새로운 assistant 시작 표시가 필요하지 않을 수 있으므로 `False`를 사용한다. 이 옵션은 생성 도중이 아니라 `generate()`를 호출하기 전에 입력을 준비하면서 결정한다.

### 대화 이력 구성과 Template 적용은 별개의 과정이다

Chat Template이 이전 대화를 자동으로 가져오는 것은 아니다. 어떤 대화를 포함할지는 먼저 messages를 어떻게 구성했는지에 달려 있고, Chat Template은 전달받은 messages만 모델별 형식으로 변환한다.

```text
첫 user 질문
→ Chat Template 적용
→ assistant 시작 표시
→ generate()
→ 실제 assistant 답변을 대화 이력에 추가

두 번째 user 질문
→ 이전 대화와 새 질문으로 messages 구성
→ Chat Template 다시 적용
→ 새로운 assistant 시작 표시
→ generate()
```

따라서 대화 이력 저장과 Chat Template 적용은 같은 작업이 아니다.

```text
저장된 대화 이력
→ 새 요청 시 messages 구성
→ Chat Template 적용
→ tokenize
→ generate()
```

출력이 이상하면 decoding parameter부터 바꾸기 전에 messages의 role과 순서, `tokenize=False`로 확인한 formatted text, tokenized input이 의도한 형태인지 먼저 점검한다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| Tokenizer를 Embedding이라고 이해했다. | Tokenizer는 문자열을 token id로 변환하고, Embedding Layer가 token id를 vector로 변환한다. |
| 포맷한다는 것을 이전 대화를 가져오지 않는다는 의미로 이해했다. | 이전 대화의 포함 여부는 messages 구성에 달려 있고, formatting은 준비된 messages를 모델이 기대하는 형식으로 변환하는 과정이다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: Sampling 뒤에 갑자기 Chat Template이 나오는 이유는 무엇인가?

9-2~9-3은 모델이 logits를 만든 뒤 어떤 토큰을 선택할지를 다뤘다. 9-4는 그보다 앞에서 Chat Model의 입력을 어떻게 구성할지를 다룬다.

```text
입력 구성
→ tokenize
→ forward
→ logits
→ Decoding
```

---

### 질문: Chat Model의 입력이 Message라는 것은 무슨 뜻인가?

모델이 message 객체 자체를 이해한다는 뜻이 아니다. 프로그램에서 대화를 `role`과 `content`를 가진 구조로 관리하고, 이 구조를 Chat Template과 tokenizer를 통해 실제 모델 입력으로 바꾼다는 뜻이다.

---

### 질문: Causal LM과 Chat Model은 다른 것인가?

서로 반대되는 개념이 아니다. 많은 Chat Model은 다음 토큰을 예측하는 Causal LM을 기반으로 하며, 대화와 지시 형식에 맞게 추가 학습된 형태다.

---

### 질문: `role`은 무엇인가?

Message를 누가 말한 것으로 처리할지 나타내는 정보다. `system`은 모델의 행동 지침, `user`는 사용자의 요청, `assistant`는 모델의 이전 답변을 나타낸다. 실제 발화 내용은 `content`에 담는다.

---

### 질문: `assistant` Role은 항상 필요한가?

아니다. 새로운 첫 질문에는 이전 assistant 답변이 없으므로 필요하지 않다. 멀티턴 대화에서는 이전 모델 답변을 문맥으로 전달하기 위해 기존 `assistant` message를 포함한다.

---

### 질문: Chat Template은 무엇을 하는가?

`role + content` 구조의 messages를 모델이 학습할 때 사용한 대화 문자열 형식으로 바꾼다. 이 과정에서 모델별 role 표시와 특수 토큰이 적용된다.

---

### 이해한 내용: Chat Template의 작동 방식

Chat Template은 입력 내용을 분석해 비슷한 기능을 찾는 것이 아니다. Tokenizer에 정의된 규칙에 따라 messages를 모델별 특수 토큰 형식으로 변환한다.

즉 학습할 때 사용한 대화 입력 형식을 추론에서도 맞춰 주는 역할이라고 이해했다.

---

### 질문: 약속된 Role이나 형식을 잘못 사용하면 어떻게 되는가?

Template이 기대하는 role 이름과 다르면 적용 중 오류가 발생하거나 예상과 다른 입력이 만들어질 수 있다.

직접 문자열을 구성한 경우 모델이 토큰을 받을 수는 있지만, 학습 때 사용한 대화 형식과 달라지면 성능이 떨어질 수 있다.

---

### 질문: 왜 직접 문자열을 만들지 않고 `apply_chat_template()`을 사용하는가?

모델마다 대화 형식과 특수 토큰이 달라 직접 관리하기 어렵고 실수하기 쉽기 때문이다. Tokenizer에 저장된 template을 사용하면 해당 모델이 기대하는 role과 특수 토큰 형식에 맞춰 입력을 구성할 수 있다.

---

### 질문: `tokenize=False`로 하면 무엇이 나오는가?

Token id로 변환하지 않고 Chat Template이 적용된 formatted text 문자열을 반환한다.

```text
messages
→ apply_chat_template(tokenize=False)
→ formatted text
```

모델을 실행하기 전에 role과 특수 토큰이 의도한 형태로 들어갔는지 확인하는 디버깅에 사용할 수 있다.

---

### 질문: `add_generation_prompt=False`와 `True`의 차이는 무엇인가?

핵심은 입력 끝에 새로운 assistant 답변의 시작 표시를 추가하는지다. `False`는 현재 messages까지만 포맷하고, `True`는 지원하는 template에서 다음 assistant 답변이 시작될 형식을 덧붙인다.

`generate()`를 실제로 실행할지는 이 옵션과 별개다.

---

### 질문: `True`로 하면 실제로 Assistant가 생기는가?

아니다. 입력 마지막에 붙은 assistant 표시는 답변 내용이 아니라 다음 답변의 시작 위치다. 실제 답변은 이 입력을 받은 `generate()`가 생성한다.

---

### 이해한 내용: 멀티턴에서의 반복 흐름

첫 번째 답변을 생성한 뒤 실제 assistant 답변을 대화 이력에 추가한다. 사용자가 다시 질문하면 이전 대화와 새 질문으로 messages를 구성하고 Chat Template과 assistant 시작 표시를 다시 적용한 뒤 `generate()`를 호출한다.

즉 매 요청마다 현재 대화 이력을 모델의 입력 형식으로 다시 준비할 수 있다고 이해했다.

---

### 질문: `False`여도 답변을 생성할 수 있는가?

가능하다. `False`는 생성 자체를 끄는 옵션이 아니라 assistant 시작 표시를 추가하지 않는 설정이다. `generate()`를 호출하면 모델은 입력의 마지막 토큰 뒤에서 생성을 이어 간다.

다만 일반적인 새 Chat 응답에서는 assistant 차례를 분명하게 알리는 `True`가 더 적합할 수 있다.

---

### 질문: `True`와 `False`를 굳이 옵션으로 나눈 이유는 무엇인가?

Chat Template을 새 답변 생성에만 사용하지 않기 때문이다.

```text
새 assistant 답변 생성
→ True

이미 답변까지 포함된 학습 데이터 전처리
→ False

완성된 대화 자체를 포맷
→ False
```

이 값은 생성 중에 바꾸는 것이 아니라 생성 전에 입력을 준비할 때 정한다.

---

### 질문: 완성된 대화란 무엇인가?

User 질문뿐 아니라 assistant 답변까지 이미 포함된 데이터다.

```text
system: 짧게 답변하라
user: Causal LM이 뭐야?
assistant: 이전 토큰을 보고 다음 토큰을 예측하는 언어 모델이야.
```

이미 assistant 답변이 있으므로 새로운 답변의 시작 표시를 추가할 필요가 없다. 이런 형태는 학습 데이터 전처리 등에 사용할 수 있다.

---

### 이해한 내용: 대화 저장과 Chat Template 적용은 별개

사용자의 대화가 처음부터 Chat Template 문자열 그대로 저장된다고 보기보다, 필요한 대화 이력을 가져와 messages로 구성한 뒤 요청 시점에 모델 입력 형식으로 변환한다고 이해했다.

```text
대화 이력 저장
≠ Chat Template 적용
```
