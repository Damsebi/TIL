# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 디버깅에만 사용할 수 있습니다. 사용하지 않았다면 아래에 `사용하지 않음`이라고 적습니다. 사용량을 늘릴 필요는 없습니다.

| 허용되는 도움 | 예시 |
|---|---|
| 개념 이해 | HTTP 404와 422의 차이, await의 의미를 다른 예시로 설명해 달라고 질문 |
| 자신의 코드 디버깅 | 직접 작성한 짧은 함수와 오류를 보여 주고 원인과 확인 방법을 질문 |

과제 전체 풀이, TODO의 완성 코드, 참고 답안을 요청하지 않습니다. 디버깅 답변도 이해한 원인과 수정 내용을 자신의 말로 기록하고 다시 실행합니다. API 키, `.env`와 인증 헤더를 질문에 포함하지 않습니다.

## 사용 여부

- 사용 여부: 사용함
- 사용 도구, 모델: Claude Code (claude.ai 클라우드 세션), Claude Opus 5.5

## 도움 기록

도움을 받은 건마다 표의 행을 추가합니다. 대화 전문보다 질문과 직접 확인한 결과를 구체적으로 적습니다.

| 날짜, 단계 | 질문 원문 | 받은 설명의 요지 | 직접 수정한 파일, 함수와 이유 | 다시 실행한 검사, 결과 |
|---|---|---|---|---|
| 11/01 필수1 | collect_releases 빈칸 4개와 작성 메모 힌트 (params dict, raise_for_status, "next" in response.links, 저장할 변수 value) | app.py collect_releases를 직접 작성. 페이지 단위로 수집하고 HTTP 오류와 다음 페이지 여부를 확인하려고 | check collect 9/9 통과 |
| 11/01 필수2 | (같은 요청) | normalize_releases 빈칸 6개와 작성 메모 힌트 (bool 타입 검사, 제목 대체 조건식, 빈 본문, 중복 ID, 문서 값 변수) | app.py normalize_releases를 직접 작성. 잘못된 자료는 격리, 초안·사전 릴리스는 제외하고 유효한 문서만 남기려고 | check documents 22/22 통과 |
| 11/01 필수3 | "이것도 해야하는거지?", "support.todo(…) 이거는 뭐야?", "이러면 되나?" | Pydantic 필드 선언 문법과 필드별 타입·길이 제한, support.todo 줄을 지우는 이유, list[DocumentId]와 Field 값 보완, 중복 URL 반복문 확인 | app.py Document, QueryRequest, QueryReply 필드와 response_models, find_document, register_document를 직접 작성. 입력 형식을 검증하고 없는 문서는 404, 중복은 409로 처리하려고 | check document-api 7/7 통과 |
| 11/01 필수3 메모 | "작성 메모: GET/POST의 입력 위치와 없는 ID/잘못된 입력의 차이를 1~2줄로 적으세요." | GET/POST 입력 위치와 404/422 차이의 문장 틀 | app.py find_document 작성 메모를 직접 작성 | 해당 없음 (주석) |
| 11/02 필수4 모델 연결 | "어제에 했던거에 이어서 필수 4하자", "이거부터 하는거 맞지?" | build_prompt dict, json.loads(text), 선택 밖 출처 검사(any … not in …) 힌트 | app.py build_prompt, call_model_once를 직접 작성. 선택한 문서만 모델에 보내고 선택 밖 출처는 거부하려고 | check query 6/6 통과 |
| 11/02 필수4 실패 처리 | 작성한 query_with_retry 코드 검토 요청 | 첫 시도 조건, 500~599 범위, 공급자 429를 503으로 반환하는 힌트와 작성 코드 확인, 작성 메모 문장 틀 | app.py query_with_retry 조건 3개와 작성 메모를 직접 작성. 첫 시도의 timeout과 5xx만 재시도하고 공급자 429를 구분하려고 | check retry 17/17 통과 |
| 11/02 필수4 요청 제한·기록 | "다음 은 def admit_query…야?" | 구간 갱신, 한도 확인, 요청 수 증가, 로그 필드 5개 dict 힌트 | app.py admit_query, request_logging을 직접 작성. 60초에 30회로 제한하고 민감정보 없이 로그를 남기려고 | check observe 6/6 통과 |
