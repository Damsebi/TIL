# Prompt Template과 ChatModel·Output Parser

> 학습일: 2026-09-29

## 핵심 정리

- `PromptTemplate`은 입력 변수를 받아 하나의 문자열 Prompt를 만들고, `ChatPromptTemplate`은 `system`, `human` 같은 Role이 포함된 Message 구조를 만든다.
- Template은 사용자 요청마다 새로 만드는 것이 아니라 요약, 번역, Code Review처럼 작업 목적이나 기능 단위로 만들어 재사용한다.
- Template은 필수가 아니며, 단순하거나 일회성인 요청은 문자열 또는 Message를 직접 만들어 Model에 전달할 수 있다.
- Template은 답변을 생성하지 않고 Model에 전달할 입력만 준비한다.
- 전체 흐름은 `Prompt → ChatModel → AIMessage → Output Parser → Python 자료형`이다.
- `ChatModel`은 Prompt가 만든 입력을 받아 답변을 생성하고 기본적으로 `AIMessage`를 반환한다.
- `Output Parser`는 Model이 이미 생성한 출력을 읽어 `str`, `list`, `dict` 등 후속 Code가 사용하기 좋은 형태로 변환한다.
- Parser가 원하는 형식으로 해석하려면 Prompt 단계에서 Model에 출력 형식을 명확하게 요청해야 한다.
- JSON Parsing에 성공해도 필요한 Field가 모두 존재하거나 내용이 사실이라는 뜻은 아니므로 별도의 구조 검증과 사실 확인이 필요하다.

## 1. 전체 처리 흐름

LangChain에서 입력을 만들고 결과를 Application Code로 전달하는 흐름은 다음과 같다.

```text
사용자 입력
→ PromptTemplate / ChatPromptTemplate
→ Prompt 또는 Message 생성
→ ChatModel
→ AIMessage
→ Output Parser
→ str / list / dict 등 Python 자료형
```

각 단계의 역할은 분리되어 있다.

| 단계 | 역할 |
| --- | --- |
| Prompt Template | 입력값과 지침을 조합해 Model에 전달할 입력 준비 |
| ChatModel | 준비된 입력으로 LLM을 호출해 답변 생성 |
| AIMessage | Model이 반환한 답변과 부가 정보를 담은 객체 |
| Output Parser | Model 출력을 후속 Code에서 사용할 자료형으로 변환 |

Template과 Parser는 Model을 직접 호출하지 않는다. Template은 호출 전에 입력을 준비하고, Parser는 호출 후에 출력을 해석한다.

## 2. PromptTemplate

`PromptTemplate`은 반복해서 사용할 Prompt의 틀을 만들고, 실행 시점에 `{question}`이나 `{topic}` 같은 입력 변수의 값을 채운다.

```python
template = PromptTemplate.from_template(
    "너는 파이썬 튜터야. "
    "초보자가 알아듣기 쉽게 설명해.\n"
    "질문: {question}"
)
```

`question="PyTorch가 뭐야?"`를 전달하면 최종적으로 다음과 같은 하나의 문자열 Prompt가 만들어진다.

```text
너는 파이썬 튜터야. 초보자가 알아듣기 쉽게 설명해.
질문: PyTorch가 뭐야?
```

`PromptTemplate`의 결과는 Model의 답변이 아니라 Model에 전달할 입력 문자열이다.

### Template은 사용자 요청마다 만들어야 하는가?

사용자 입력마다 새로운 Template을 만들 필요는 없다. 같은 목적의 작업이라면 하나의 Template에 다른 입력값을 넣어 재사용할 수 있다.

```text
서로 다른 사용자 입력
→ 같은 목적의 Template
→ 입력 변수의 값만 변경
```

예를 들어 요약 기능은 요약용 Template, 번역 기능은 번역용 Template, Code Review 기능은 Review용 Template으로 나눌 수 있다. 기능의 목적 자체가 다를 때 별도 Template을 두는 것이다.

### 미리 만들지 않은 요청은 Template이 자동 생성하는가?

`PromptTemplate`이 사용자 요청을 분석해 새로운 Template을 자동으로 만들지는 않는다.

필요하다면 개발자가 조건에 따라 미리 만든 Template을 선택하거나, Code에서 문자열을 동적으로 조합할 수 있다. 다양한 요청을 그대로 받을 수 있는 `{request}` 변수를 가진 범용 Template을 사용하는 방법도 있다.

### Template을 사용하지 않아도 되는가?

가능하다. 단순하거나 한 번만 사용하는 요청은 문자열이나 `SystemMessage`, `HumanMessage`를 직접 만들어 Model에 전달해도 된다.

```text
Template 사용
→ 반복되는 Prompt의 재사용과 관리에 유리

Template 미사용
→ 단순한 요청을 직접 구성
```

Template은 LLM 호출을 가능하게 만드는 필수 요소가 아니라 반복되는 Prompt를 일관되게 관리하기 위한 도구다.

## 3. ChatPromptTemplate과 Message Role

`ChatPromptTemplate`은 `system`, `human`처럼 Role이 포함된 Message 구조를 만든다.

```text
ChatPromptTemplate
├─ system: Model이 따라야 할 지침
└─ human: 사용자의 요청
```

Message의 `content` 자체는 여전히 문자열이다. 문자열을 없애는 것이 아니라 문자열에 Role과 부가 정보를 붙여 Message 객체로 관리하는 것이다.

### PromptTemplate 문자열에 `system:`이라고 쓰면 같은가?

`PromptTemplate` 안에 다음처럼 작성할 수는 있다.

```text
system: 너는 친절한 튜터야.
human: {question}
```

하지만 여기서 `system:`과 `human:`은 문자열에 포함된 글자일 뿐 실제 Message Role이 아니다. Model이 문맥을 보고 지침과 질문처럼 해석할 수는 있지만 구조적으로 Role이 지정된 것은 아니다.

```text
PromptTemplate의 "system:"
→ 문자열의 일부

ChatPromptTemplate의 system
→ Message 구조에 지정된 실제 Role
```

### GPT의 지침과 Template은 같은가?

GPT의 지침은 `ChatPromptTemplate`의 `system` Message와 비슷하게 Model이 따라야 할 규칙을 전달한다.

다만 지침은 Model의 행동 규칙이고, Template은 지침과 사용자 입력을 일정한 구조로 조립하고 재사용하는 틀이다.

## 4. ChatModel과 AIMessage

`ChatModel`은 Prompt가 만든 문자열이나 Message를 받아 LLM을 호출하고 답변을 생성한다.

```text
Prompt 또는 Message
→ ChatModel
→ LLM 호출
→ AIMessage
```

`AIMessage`는 Model이 반환한 원본 Response 객체에 가깝다.

```text
AIMessage
├─ content: 실제 Model 답변
├─ metadata 등의 부가 정보
└─ 기타 Model 관련 정보
```

`AIMessage` 자체가 답변 문자열인 것은 아니다. 실제 답변 내용은 `content`에 들어 있으며, 객체에는 사용량이나 Model 관련 정보처럼 추가 데이터가 포함될 수 있다.

## 5. Output Parser의 역할

Parser는 데이터를 읽고 구조를 해석해 Program이 사용할 수 있는 형태로 변환한다.

예를 들어 다음 문자열을

```text
"Prompt, Model, Parser"
```

다음과 같은 Python List로 바꿀 수 있다.

```python
["Prompt", "Model", "Parser"]
```

LangChain의 `Output Parser`는 특히 Model이 생성한 Output을 해석한다.

```text
Prompt
→ 원하는 출력 형식을 Model에 요청

Model
→ 해당 형식의 답변 생성

Output Parser
→ 생성된 답변을 읽어 Python 자료형으로 변환
```

Parser는 Model의 출력을 직접 생성하지 않는다. 이미 만들어진 출력을 나중에 읽고 해석하는 단계다.

### Parser는 화면 표시 방식을 정하는가?

화면에 표시할 값을 만드는 데도 사용할 수 있지만 핵심 목적은 후속 Application Code가 필요한 자료형으로 변환하는 것이다.

```text
사람이 읽을 일반 답변·요약
→ str

키워드·Tag 목록
→ list

각 값을 조건 처리·DB 저장·알림에 사용
→ dict / list
```

Parser는 최종 화면 모양보다 다음 Code가 데이터를 어떻게 사용할지를 기준으로 선택한다.

## 6. StrOutputParser

`StrOutputParser`는 `AIMessage`에서 최종 답변 내용을 일반 문자열로 사용할 수 있게 처리한다.

```text
AIMessage
→ StrOutputParser
→ str
```

`AIMessage.content`는 처음부터 문자열이다. `StrOutputParser`가 Message를 다시 문자열 방식으로 되돌리는 것이 아니라, Message 객체에서 최종 답변 문자열을 꺼내 LangChain Pipeline의 다음 단계로 전달하기 쉽게 만드는 것이다.

`ai_message.content`를 직접 사용할 수도 있지만 Parser를 사용하면 Chain의 한 단계로 일관되게 연결할 수 있다.

`StrParser`가 아니라 `StrOutputParser`라는 이름을 사용하는 이유는 Model의 Output을 처리하는 Parser이기 때문이다.

## 7. CommaSeparatedListOutputParser

`CommaSeparatedListOutputParser`는 쉼표로 구분된 Model 출력을 `list[str]`로 변환한다.

```text
"매출 감소, 이탈률 상승, 계약 종료"

→

["매출 감소", "이탈률 상승", "계약 종료"]
```

Keyword나 Tag처럼 단순한 항목 목록에 적합하다. 항목 자체에 쉼표가 포함되는 복잡한 데이터에는 적합하지 않을 수 있다.

Parser가 쉼표를 기준으로 정확히 나누려면 Prompt에서 Model에 쉼표로 구분된 형식으로 답하도록 요청해야 한다.

## 8. JsonOutputParser

`JsonOutputParser`는 JSON 형식의 Model 출력을 Python의 `dict` 또는 `list`로 변환한다.

```text
'{"risk": "high", "churn_rate": 5.2}'

→

{
    "risk": "high",
    "churn_rate": 5.2
}
```

사람에게 읽히는 보고서보다 각각의 값을 Code에서 꺼내 조건 처리, Database 저장, 알림 등에 사용할 때 유용하다.

### Parser가 기대하는 형식은 어떻게 Model에 전달하는가?

JSON Parser를 연결했다고 Model이 자동으로 항상 올바른 JSON을 만드는 것은 아니다. Prompt에서 Model에 필요한 출력 형식을 미리 요청해야 한다.

`get_format_instructions()`를 사용하면 Parser가 기대하는 형식에 대한 지침을 Prompt에 포함할 수 있다.

```text
Parser가 기대하는 형식 확인
→ Format Instruction을 Prompt에 포함
→ Model이 지정된 형식으로 답변 생성
→ Parser가 결과 해석
```

Prompt의 출력 지시와 Parser의 해석 규칙이 서로 맞아야 한다.

## 9. Parsing과 검증의 차이

JSON Parsing에 성공했다고 필요한 Field가 모두 존재하는 것은 아니다.

예를 들어 다음 결과는 올바른 JSON이므로 Parsing에는 성공할 수 있다.

```python
{
    "risk": "high"
}
```

하지만 이후 Code가 `result["reason"]`을 요구하면 `reason` Key가 없으므로 `KeyError`가 발생할 수 있다.

```text
JSON Parsing 성공
≠ 필요한 Field가 모두 존재함
≠ 값의 Type과 범위가 올바름
≠ 내용이 사실임
```

따라서 Parsing 후에도 필요한 Key, Type, 값의 범위를 별도로 검증해야 한다. Parser는 출력 형식을 변환할 뿐 Model 답변의 사실성을 확인하지 않는다.

## 10. Parser 선택 기준

어떤 Parser를 사용할지는 Model 답변을 최종적으로 어떻게 활용할지에 따라 달라진다.

| 필요한 결과 | 적합한 형태 | 예시 |
| --- | --- | --- |
| 사람이 읽을 답변이나 요약 | `str` | 보고서 문장, 설명 |
| 단순한 Keyword나 Tag | `list[str]` | 분류 Tag, 핵심어 목록 |
| Code에서 Field별로 처리할 데이터 | `dict` 또는 `list` | 조건 분기, DB 저장, 알림 |

```text
후속 Code가 필요한 자료형 결정
→ 적절한 Parser 선택
→ Parser의 Format Instruction을 Prompt에 반영
→ Model 호출
→ Parsing
→ 구조와 내용 검증
```

## 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| `PromptTemplate` 문자열에 `system:`, `human:`을 쓰면 실제 Role이 지정된다. | 문자열에 적힌 글자일 뿐이다. `ChatPromptTemplate`을 사용해야 Message 구조에 Role이 지정된다. |
| `ChatPromptTemplate`은 문자열을 사용하지 않기 위해 Message 객체를 사용한다. | Message의 `content`는 여전히 문자열이며, 문자열에 Role과 부가 정보를 붙여 객체로 관리한다. |
| `StrOutputParser`는 다시 문자열 방식으로 되돌아가는 과정이다. | `AIMessage.content`는 원래 문자열이다. 최종 답변 문자열을 꺼내 Pipeline에서 사용하기 쉽게 만드는 과정이다. |
| Parser는 주로 사용자 화면 표시 형식을 정한다. | 핵심 목적은 Model 출력을 후속 Code가 사용할 `str`, `list`, `dict` 등의 형태로 변환하는 것이다. |
| JSON Parsing에 성공하면 결과가 완전하고 정확하다. | Parsing 성공은 문법적 변환에 성공했다는 뜻일 뿐 Field 존재 여부와 사실성은 별도로 검증해야 한다. |
