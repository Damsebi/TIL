# LangChain 앱 구조와 개발 환경

> 학습일: 2026-09-29

## 핵심 정리

- LangChain은 LLM 자체가 아니라 LLM Application을 구성하기 위한 Framework다.
- 작은 Program은 OpenAI SDK로 직접 호출하는 편이 단순할 수 있지만, 단계와 기능이 많아지면 LangChain을 통해 역할을 분리하고 연결하기 쉬워진다.
- LangChain의 기본 흐름은 `Prompt → Model → Parser`로 이해할 수 있다.
- LangChain을 사용한다고 LLM의 지식이나 지능이 높아지는 것은 아니다. Prompt, Model, 출력 처리 등 Code의 경계가 명확해지는 것이다.
- Tool을 연결해도 Model 자체의 지능은 변하지 않지만, 외부 기능을 사용할 수 있으므로 전체 System이 수행할 수 있는 일은 늘어날 수 있다.
- LangChain 구성 요소는 설정, 교체, 상속·Override, Wrapper, 직접 구현 등을 통해 필요한 방식으로 변경할 수 있다.
- `langchain-core`는 공통 구성 요소, `langchain-openai`는 OpenAI Model 연결, `openai`는 OpenAI 공식 SDK를 담당한다.
- `uv`는 LangChain 전용 도구가 아니라 Python Version, Virtual Environment, Package 의존성을 관리하는 도구다.
- API Key는 Code에 직접 작성하지 않고 `.env`에 저장하며, `.env`는 `.gitignore`에 추가한다.
- `ChatOpenAI(...).invoke()`는 일반 문자열이 아니라 `AIMessage`를 반환하며, 필요한 경우 Parser를 통해 원하는 형태로 변환한다.

## 1. LangChain은 무엇인가?

LangChain은 학습된 LLM을 이용해 Application을 구성할 때 반복적으로 필요한 기능을 공통 규격과 Component로 제공하는 Framework다.

```text
LangChain
→ LLM 자체가 아님
→ 새로운 Model을 학습시키는 도구가 아님
→ LLM Application의 구성 요소를 연결하는 Framework
```

간단한 질문 하나를 Model에 전달하는 Program이라면 OpenAI SDK를 직접 사용하는 편이 더 짧고 이해하기 쉬울 수 있다. 반면 Prompt 관리, 출력 변환, Tool, RAG, 상태 관리처럼 단계가 늘어나면 각 역할을 나누고 조합할 수 있는 LangChain의 장점이 커진다.

| 방식 | 적합한 경우 |
| --- | --- |
| OpenAI SDK 직접 호출 | 호출 과정이 단순하고 별도의 추상화가 필요하지 않을 때 |
| LangChain | 여러 단계와 Component를 재사용·교체·연결해야 할 때 |

### 왜 별도의 Framework가 필요한가?

LangChain만의 새로운 Programming 원리가 생긴 것은 아니다. 기존의 모듈화, 추상화, Pipeline 개념을 LLM Application에 맞는 공통 Interface와 Component로 제공한다.

```text
직접 구현
→ 역할별 함수와 Class를 직접 설계
→ 연결 규칙과 공통 형식도 직접 관리

LangChain
→ 반복되는 역할에 공통 Component 제공
→ Component를 일정한 방식으로 연결
```

LangChain은 직접 구현할 수 없던 기능을 갑자기 가능하게 만드는 도구라기보다, 반복되는 구조를 재사용하고 교체하기 쉽게 만드는 도구에 가깝다.

### LangChain은 Model 학습이나 Fine-tuning에 사용하는가?

주요 용도는 아니다.

```text
PyTorch / Transformers / PEFT
→ Model 학습·Fine-tuning

LangChain
→ 학습된 Model을 활용해 LLM Application 구성
```

Fine-tuning한 Model을 LangChain에 연결해 사용하는 것은 가능하지만, LangChain 자체의 중심 역할은 Model 학습이 아니다.

### `Lang`은 사람 이름인가?

사람 이름이 아니라 `Language`에서 온 표현으로 이해했다.

```text
LangChain
→ Language + Chain

LangGraph
→ Language + Graph
```

## 2. 기본 구조: Prompt → Model → Parser

LangChain Application의 기본 흐름은 세 Component로 나누어 볼 수 있다.

```text
사용자 입력
→ Prompt
→ Model
→ Parser
→ Application에서 사용할 결과
```

### Prompt

입력값을 Model에 전달할 Message 형태로 만든다. 고정된 지시문과 사용자가 입력한 값을 결합하고, Message의 역할과 형식을 관리한다.

### Model

Prompt에서 만들어진 Message를 받아 LLM을 호출한다. `ChatOpenAI(...).invoke()`를 호출하면 일반 문자열이 아니라 `AIMessage`가 반환된다.

```text
Prompt가 만든 Message
→ ChatOpenAI
→ LLM 호출
→ AIMessage
```

### Parser

Model의 출력인 `AIMessage`를 문자열이나 구조화된 객체처럼 Application에서 사용하기 좋은 형태로 바꾼다.

```text
AIMessage
→ Parser
→ 문자열 또는 구조화된 결과
```

Parser가 항상 필요한 것은 아니다. `AIMessage` 자체가 필요하다면 그대로 사용할 수 있고, 문자열이나 특정 Schema가 필요할 때 적절한 Parser를 연결한다.

### LangChain을 사용하면 LLM이 더 똑똑해지는가?

Prompt, Model, Parser로 Code를 나눈다고 Model의 지식이나 추론 능력이 자동으로 증가하지는 않는다.

```text
Model 자체의 지능
→ 그대로

Application Code의 구조
→ 역할과 경계가 명확해짐
→ 유지보수·교체·확장이 쉬워짐
```

## 3. 모듈화와 Component 변경

모듈화는 Program의 책임을 역할별로 나누는 설계 방식이다. 함수를 만드는 것은 모듈화를 구현하는 방법 중 하나지만, 함수가 존재한다는 사실만으로 책임이 적절히 분리되었다고 볼 수는 없다.

```text
모듈화
→ 책임과 역할을 나누는 설계 방식

함수 / Class / Module
→ 모듈화를 구현하는 수단
```

LangChain도 Prompt, Model, Parser, Tool처럼 역할을 나누고 이를 Pipeline으로 연결한다.

### 기본 기능을 수정하거나 제거할 수 있는가?

가능하다. 필요하지 않은 Component는 연결하지 않으면 되고, 일부 동작을 바꾸고 싶다면 구현 방식에 따라 다음 방법을 사용할 수 있다.

```text
설정값으로 동작 변경
→ 다른 Component로 교체
→ 상속 후 Override
→ Wrapper로 감싸기
→ 필요한 부분 직접 구현
```

Library 내부 Code를 직접 Monkey Patch하는 것도 기술적으로는 가능하지만 Version 변경에 취약하고 유지보수가 어려워질 수 있다. 공식 설정과 확장 지점을 먼저 사용하는 편이 좋다.

## 4. Tool과 전체 System의 능력

`@tool`은 일반 Python 함수를 LLM Application에서 사용할 수 있는 Tool 형식으로 감싼다. 함수 이름, 설명, 입력 Type 등의 정보를 Model에 제공하면 Model은 상황에 따라 어떤 Tool을 어떤 인자로 호출할지 결정할 수 있다.

```text
LLM
→ Tool 호출 필요 여부 판단
→ Tool 이름과 인자 생성
→ Program이 실제 Python 함수 실행
→ 실행 결과를 LLM에 전달
→ LLM이 결과를 이용해 다음 답변 생성
```

실제 Python 함수를 실행하는 것은 LLM 자체가 아니라 Application Program이다.

### Tool이 추가되면 LLM이 더 똑똑해지는가?

Model 자체의 지능과 전체 System의 수행 능력을 구분해야 한다.

```text
Model 자체의 지능
→ 변하지 않음

사용 가능한 Tool
→ 늘어남

전체 System의 수행 능력
→ 향상될 수 있음
```

계산기, 검색, Database 등의 Tool을 사용할 수 있으면 Model이 새롭게 학습된 것은 아니어도 해결할 수 있는 문제의 범위와 정확도가 커질 수 있다.

Tool이 많다고 항상 결과가 좋아지는 것은 아니다. Model이 적절한 Tool을 선택할 수 있어야 하며, Tool의 설명과 입력 Schema도 명확해야 한다.

## 5. LangChain과 LangGraph

LangChain과 LangGraph는 역할이 다른 같은 생태계의 도구다.

```text
LangChain
→ Model, Prompt, Parser, Tool, Agent 같은 고수준 Component

LangGraph
→ 상태, 분기, 반복이 있는 실행 흐름을 Graph로 제어
```

단순한 순차 Pipeline은 LangChain만으로 구성할 수 있다. 상태에 따라 다른 경로를 선택하거나 특정 단계를 반복해야 한다면 LangGraph를 이용해 실행 흐름을 더 세밀하게 표현할 수 있다.

LangChain의 Agent는 LangGraph를 기반으로 동작하며, LangChain Component를 LangGraph의 Node 안에서 함께 사용할 수 있다.

## 6. LangChain의 주요 기능

대화에서 확인한 주요 기능은 다음과 같다.

```text
Model 연결
Prompt 관리
출력 처리·구조화
Tool
Agent
검색 / RAG 연결
상태·Memory 관리
```

각 함수와 Class의 세부 인자를 전부 외우기보다 Component가 왜 존재하고 어떤 역할을 담당하는지 먼저 이해하는 것이 중요하다.

## 7. Package 구조

LangChain 관련 Package는 공통 규격과 Model 제공자별 연결을 나누어 관리한다.

| Package | 역할 |
| --- | --- |
| `langchain` | Agent 등 LLM Application의 상위 수준 기능 |
| `langchain-core` | Prompt, Message, Parser 등 공통 Component와 Interface |
| `langchain-openai` | OpenAI Model을 LangChain 공통 방식에 연결 |
| `openai` | OpenAI가 제공하는 공식 Python SDK |

`langchain-openai`와 `openai`는 이름이 비슷하지만 같은 Package가 아니다.

```text
langchain-core
→ Model 제공자와 관계없이 사용하는 공통 구조

langchain-openai
→ OpenAI Model 연결 구현

openai
→ OpenAI 공식 SDK
```

공통 구조와 제공자별 연결이 분리되어 있으므로 다른 Model을 사용할 때도 Prompt나 Parser 같은 구조를 유지하면서 Model 연결 부분을 바꿀 수 있다.

## 8. `uv`와 개발 환경

`uv`는 LangChain 전용 도구가 아니다. Python Project에서 Python Version, Virtual Environment, Package 의존성을 관리하는 도구다.

```text
LangChain
→ 설치해서 사용하는 LLM Application Framework

uv
→ Python Project 환경과 Package를 관리하는 도구
```

이번 학습 환경은 다음 기준으로 구성한다.

```text
Python 3.12
uv
.venv
```

`uv` 대신 `pip`나 Poetry 등 다른 Package 관리 방식을 사용할 수도 있다. 중요한 것은 수업과 Project에서 사용하는 Python Version과 의존성을 일관되게 유지하는 것이다.

## 9. API Key와 `.env`

API Key는 Code에 직접 작성하지 않고 `.env` File에 저장한다.

```dotenv
OPENAI_API_KEY=실제_API_KEY
```

`.env`에는 비밀값이 들어 있으므로 Git에 Commit되지 않도록 `.gitignore`에 추가한다.

```gitignore
.env
```

```text
Code
→ 환경 변수 이름만 사용

.env
→ 실제 API Key 저장

.gitignore
→ .env가 Git에 올라가지 않도록 제외
```

환경 변수를 사용하더라도 실제 Key를 Log나 출력에 노출하지 않아야 한다.

## 10. 학습할 때 무엇을 기억해야 하는가?

LangChain의 모든 함수와 Class, 세부 인자를 암기할 필요는 없다.

지금 단계에서는 다음 내용을 우선 이해한다.

- Prompt, Model, Parser가 담당하는 역할
- `invoke()`가 Component를 실행하는 공통 방식이라는 점
- `AIMessage`와 문자열 출력의 차이
- Tool을 실제로 실행하는 주체는 Program이라는 점
- Package마다 담당하는 역할
- 구체적인 인자와 최신 사용법은 개발할 때 공식 문서에서 확인하는 습관

## 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| 함수를 만드는 것 자체가 모듈화다. | 모듈화는 책임을 역할별로 나누는 설계 방식이며, 함수는 이를 구현하는 수단 중 하나다. |
| LangChain을 사용하면 LLM 자체가 더 똑똑해진다. | Model 자체는 그대로이며 Application Code의 역할 분리와 확장이 쉬워진다. |
| Tool을 연결하면 Model이 새 기능을 학습한다. | Model이 학습되는 것은 아니다. Program이 Tool을 실행해 결과를 제공하므로 전체 System의 수행 범위가 넓어질 수 있다. |
| LangChain은 Model을 학습하거나 Fine-tuning하는 도구다. | LangChain의 주된 역할은 학습된 Model을 활용해 LLM Application을 구성하는 것이다. |
| LangChain을 사용하려면 `uv`가 필수다. | `uv`는 여러 Python 환경 관리 도구 중 하나이며, `pip`나 Poetry 등을 사용할 수도 있다. |
