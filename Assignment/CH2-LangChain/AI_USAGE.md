# AI 사용 기록

허용 범위는 개념 질문과 자신이 작성한 코드의 디버깅입니다. 과제 함수의 정답이나 전체 구현을 대신 생성하게 해서는 안 됩니다. 먼저 현재 단계 검사를 실행하세요.

사용하지 않았다면 아래에 사용하지 않았다고 적습니다. 사용했다면 질문마다 기록합니다. API 키, 개인 이메일, 실제 회사 데이터는 입력하지 않습니다.

| 구분 | 질문 요약 | 공유한 자기 코드와 오류 범위 | 이해한 내용 | 직접 수정하고 검증한 결과 |
|---|---|---|---|---|
| 개념(빈칸 힌트) | 필수 1 문서 검색 진행 방법 | 없음 (제공 코드 기준 질문) | Document의 page_content와 metadata 구분, allowed로 후보를 먼저 제한, 키워드 일치 개수로 점수 계산, search_query 연결, RunnableParallel로 입력 보존과 검색을 병렬 준비 | main.py to_documents, search_documents, build_context_chain 직접 작성 (점수는 반복문으로 작성) / check search 7/7 통과 |
| 개념(빈칸 힌트) | 필수 2 기본 체인 진행 방법 | 없음 | PydanticOutputParser와 MessagesPlaceholder 역할, 출처 검사 3조건(중복, 검색 밖, 근거 없는데 담당자 불필요), 프롬프트·모델·파서를 파이프 연산자로 순차 연결, 문서 없음 분기 | main.py build_prompt_and_parser, validate_sources, build_primary_chain, build_answer_chain 직접 작성 (검색 밖 출처는 issubset으로 작성) / check chain 13/13 통과 |
| 디버깅 | check chain만 TODO 미구현으로 실패한 원인 | main.py 전체와 check chain 실패 출력(11개 항목 "현재 단계의 TODO를 먼저 구현하세요") | 코드에는 남은 todo가 없고, 같은 코드로 실행하면 통과하므로 저장 전 실행했을 가능성 | 저장 후 check chain 재실행 [결과 직접 작성] |
| 개념(빈칸 힌트) | 필수 3 대화 이력 진행 방법 | 없음 | 세션마다 InMemoryChatMessageHistory를 따로 보관, primary가 아니면 저장하지 않음, HumanMessage 다음 AIMessage 순서로 저장 | main.py get_history, commit_history 직접 작성 / check history 4/4 통과 |
| 개념(빈칸 힌트) | 필수 4 실패 복구 진행 방법 | 없음 | with_retry로 허용 오류만 최대 2회 시도, with_fallbacks로 계속 실패하면 fallback 응답 | main.py build_resilient_chain 직접 작성 / check recovery 13/13 통과 |
| 개념(빈칸 힌트) | 필수 5 스트리밍과 실행 기록 진행 방법 | 없음 | delta, final, reset 이벤트 형식, delta 전 첫 시도만 재시도, 검증 실패 시 reset 후 fallback, TraceHandler의 시작 시각·경과 밀리초·오류 이름·청크 수 계산 | main.py stream_answer, TraceHandler 직접 작성 / check stream 19/19 통과 |

도구와 모델 이름: Claude Code (claude.ai 클라우드 세션), Claude Opus 5.5, chatGPT

추가로 지피티를 이용해서 코드에 관해서 질문하고 수정하는 과정을 거침

AI의 설명이 틀렸거나 그대로 적용하지 않은 부분: 키워드 점수는 sum 표현 대신 반복문으로, 검색 밖 출처 검사는 any 대신 issubset으로, MessagesPlaceholder는 variable_name 인자를 써서 직접 바꿔 작성했다. 힌트에는 빈칸별 코드 표현이 포함되어 있었다.
