# AI 사용 안내, 기록

이 과제에서는 **개념 질문과 자신이 작성한 코드의 디버깅**에 AI를 사용할 수 있습니다. 필수문제와 선택 심화문제에 같은 기준을 적용합니다.

## 사용할 수 있는 질문

- JSON Schema의 타입 검증과 출처 ID 검사는 무엇이 다른가요?
- Reasoning 프롬프팅과 Self-Consistency의 적용 상황을 비교해 주세요.
- 제가 작성한 이 반복문은 마지막 실패 뒤에도 대기합니다. 어떤 조건을 확인해야 하는지 설명해 주세요.
- 이 코드는 제가 작성했습니다. 예상 결과와 실제 오류를 보고 원인을 설명해 주세요.

디버깅을 요청할 때에는 직접 작성한 코드의 필요한 부분, 기대한 동작, 실제 오류, 이미 확인한 사항을 함께 제시하세요. 설명을 이해한 뒤 직접 수정하고 해당 단계 검사를 다시 실행합니다.

## 사용할 수 없는 요청

- 과제 전체 또는 아직 작성하지 않은 TODO 함수를 완성해 달라는 요청
- baseline/reasoning/대상별 프롬프트를 대신 작성해 달라는 요청
- 다른 과제라는 이름으로 같은 요구사항의 완성 코드를 생성하는 요청
- 실행하지 않은 결과, 비용, 캐시 적중 수치를 만들어 달라는 요청
- 심화문제 설계를 대신 작성해 달라는 요청

AI 답변에 완성 풀이가 포함되었다면 그대로 제출하지 말고, 필요한 개념 설명으로 질문 범위를 좁히세요. API 키나 실제 개인정보는 대화에 넣지 않습니다. 과제 담당자에게 질문할 때에도 현재 단계와 관찰한 오류를 함께 전달하면 도움이 됩니다.

## 사용 기록

AI를 사용하지 않았다면 아래에 `사용하지 않음`이라고 적으세요. 사용했다면 질문별로 행을 추가합니다. API 키와 개인정보를 제외하고, 질문 원문과 받은 설명의 요지를 남깁니다.

- 사용 여부: 사용함
- 사용 도구, 모델: Claude Code (VS Code 확장), Claude Opus 5.5 / Claude Code (claude.ai 클라우드 세션), Claude Opus 5.5 / ChatGPT (모델명: 직접 작성). 표의 "날짜, 단계"에 [도구] 표시가 없는 행은 VS Code 확장 기록입니다.

| 날짜, 단계 | 질문 원문 | 받은 설명의 요지 | 직접 수정한 파일, 함수와 이유 | 다시 실행한 검사, 결과 |
|---|---|---|---|---|
| 2026-11-02, 필수 1 build_instructions | @ASSIGNMENT.md 문제 1 기준으로, 선택한 build_instructions의 두 문자열(기본 정책, reasoning 추가 지시)과 이유: 주석에 각각 꼭 들어가야 하는 항목을 체크리스트로만 정리해줘. 문장 예시는 쓰지 마. | ASSIGNMENT.md 필수 1 조건과 checks.py 검사(KANT NEXT 포함, baseline과 reasoning 문자열 차이, 문서 순서와 무관한 고정 지시문)를 바탕으로 기본 정책, reasoning 추가 지시, 이유 주석에 들어갈 항목을 문장 예시 없이 체크리스트로 정리함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 역할은 당신은 개발 업무를 지원하는 역할입니다 이정도면 될까? | 문장을 대신 쓰지 않고, checks.py가 요구하는 KANT NEXT가 빠져 검사에 실패한다는 점과 소속 팀, 상대하는 사용자, 수행하는 일(근거 있는 안내와 담당자 연결)이 드러나지 않는다는 점을 짚고 스스로 점검할 질문을 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 당신은 KANT NEXT의 개발 지원팀에서 다른 개발자들의 어려움을 도와주는 안내 챗봇입니다. | 회사명, 소속, 상대, 안내 역할이 드러나 역할 문장으로는 적절하지만 "어려움을 도와주는"은 범위가 넓어 근거 없는 답을 유도할 수 있으니, 근거와 담당자 연결 경계를 역할이나 업무 범위, 제약 항목에 분명히 하고 run policy --live의 출장비 사례로 확인하라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 당신은 KANT NEXT의 개발 지원팀에서 다른 개발자들이 개발을 하는데 있어서 필요한 정보들을 안내해주는 챗봇입니다. | "정보를 안내"와 "개발"로 역할과 주제가 좁혀져 나아졌지만 정보의 출처(제공 문서)가 한정되지 않아 일반 지식으로 답할 수 있으니, 역할이나 근거 원칙 항목에 출처 한정을 담고 run policy --live에서 policy-python 출처를 대조하라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 당신은 KANT NEXT의 개발 지원팀에서 다른 개발자들이 개발을 하는데 있어서 필요한 정보들을 사내문서에서 검색한 후 판단하고 검증한 자료를 안내해주는 챗봇입니다. | 출처를 사내문서로 한정한 점은 좋지만, 문서는 검색이 아니라 지시문의 reference_documents에 제공되므로 "검색"은 실제 동작과 다르고, "판단하고 검증"은 reasoning 조건에만 넣을 점검 지시와 겹쳐 두 조건의 비교를 흐리므로 점검 절차를 reasoning 문자열로 옮길지 검토하라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 근데 documents.json 이것도 결국 사내문서 아닌가? | documents.json이 사내문서인 것은 맞고 문제는 "검색"이라는 동작이며, 문서는 정렬된 JSON으로 지시문의 reference_documents 블록에 이미 포함되므로 모델은 검색하지 않고 근거를 고르기만 한다고 설명하고, 정책의 "사내문서"가 그 블록을 가리키는지 export로 확인하라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 당신은 KANT NEXT의 개발 지원팀에서 다른 개발자들이 개발을 하는데 있어서 필요한 정보들을 사내문서에서 자료를 안내해주는 챗봇입니다. | 검색과 검증 표현을 뺀 방향은 맞지만 "정보들을 … 자료를"처럼 목적어가 겹쳐 안내 대상이 모호하다는 점과, "사내문서"가 지시문의 reference_documents 블록을 가리킨다는 연결을 prompt-baseline.txt에서 확인하라고 안내함(문장은 대신 쓰지 않음). | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 시간이 없어. 문장 다듬기나 표현 개선은 지적하지 말고, 발제문 요구사항이 빠졌거나 check가 실패할 문제만 알려줘. | 현재 main.py 정책 문자열이 자리표시자뿐이라 KANT NEXT 검사에서 실패하고 나머지 policy 검사는 구조상 통과 조건임을 설명하고, check가 내용은 검사하지 않으므로 답변 형식(네 필드, 타입, needs_human 조건), 이유 주석, 자리표시자 채우기가 요구사항상 빠져 있다고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | # 업무 범위 적었어 | 작성한 업무 범위가 policy-support 문서의 지원 범위와 범위 밖 목록과 일치해 요구사항 누락이나 check 실패 요인은 없고, 남은 check 실패 요인은 KANT NEXT 미포함뿐이라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 칸트 넥스트 집어넣었어 | 정책 문자열의 역할과 업무 범위에 영문 KANT NEXT가 들어가 checks.py의 문자열 비교 조건을 충족하며(한글 표기면 실패), 구조상 남은 실패 원인은 없으니 check policy를 직접 실행해 확인하라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 규칙도 적었어 | 규칙 항목은 근거 원칙, 추측 금지, 실제 문서 ID 출처, 비밀정보 제약을 담아 요구사항 누락이나 check 실패 요인이 없고, 남은 필수 항목은 특수 상황, 답변 형식, 성공 기준, reasoning 점검 지시, 이유 주석이라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 특수상황도 적었어 | check 실패 요인은 없지만 비밀정보 요청 항목에 실제 처리 기준이 없고(policy-secret 문서 참고), 규칙 무시 지시 항목이 문서 안의 지시 경우를 다루지 않으며, "담당자 확인으로 연결"을 needs_human=true로 잇는 내용은 답변 형식 항목에서 다뤄야 한다고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 다 적었어 | check 실패 요인은 없지만 reasoning 점검 지시가 자리표시자 그대로이고(check는 통과해도 조건 3 미충족), policy 단계 요청에는 응답 스키마가 붙지 않으므로 답변 형식에 네 필드, 타입, category 허용값, needs_human=true 조건이 필요하며, 이유 주석도 미작성이라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | (reasoning 추가 문자열 코드 붙여넣음: 요구한 정보가 전부 문서에 있는지, 정책에 맞는지 확인한 뒤 답하고 확인 과정은 답변에 쓰지 않는다는 2줄) 이렇게 적으면 되나? | 요청 조건과 근거 점검, 사고 과정 비공개를 담아 조건 3을 충족하고 check 실패 요인(문법 포함)도 없으며, 남은 것은 답변 형식의 네 필드, 타입, needs_human 조건과 이유 주석이라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 build_instructions | 실행해줘봐 | AI가 check policy를 실행해 검사 항목 1개 중 1개 통과 출력을 전달하고, run policy --live는 API 비용이 발생하므로 확인 후 실행하겠다고 하며 답변 형식을 먼저 채우는 것이 낫다고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 answer_format (필수 1 build_instructions 포함) | 다음 필수2로 넘어가자 (answer_format의 properties 코드 붙여넣음: answer string, source_ids string 배열, needs_human boolean, category string과 enum [...]) 수정했어 | 필수 1에서 raise ValueError 줄이 이유 문자열로 바뀌어 잘못된 variant 거부 검사가 실패하고 이유는 # 주석이어야 하며 답변 형식의 네 필드 정의가 아직 없다고 짚음. answer_format의 enum [...]은 Ellipsis 값이라 정상 category를 거부하고 JSON 변환도 실패하니 ASSIGNMENT.md의 네 값을 확인하라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 answer_format, validate_answer, finish_answer | python main.py check answer 헸는데 18개중에 10개 통과했네 | checks-answer.json을 읽어 실패 8개가 모두 오류가 아닌 미완료(_todo의 NotImplementedError)이며 validate_answer 첫 조건과 finish_answer의 validate_answer 호출 지점에서 멈춘 것이고, rules 리스트가 _todo를 순서대로 실행해 첫 조건 이름만 보인다고 설명함. answer_format 관련 검사는 통과함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 validate_answer | rules 제대로 들어갔는지 확인해봐 | 빈 답변과 중복 출처 조건은 맞지만, 없는 출처 조건은 boolean인 needs_human에 in을 써서 TypeError가 나므로 함수가 받는 문서 ID 목록과 비교해야 하고, 근거 없는 답변 조건은 항상 값이 있는 category를 검사해 작동하지 않으니 담당자 확인 여부 필드를 봐야 한다고 원인만 설명함(수정 코드는 주지 않음). | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 validate_answer, finish_answer | 수정했어 다음은 뭐야? | 수정한 validate_answer의 네 조건이 요구사항과 맞다고 확인하고, 다음 단계인 finish_answer의 세 TODO(응답 dict에서 본문을 꺼내 known_ids와 함께 검증, 세 오류 유형에 서로 다른 안내를 주되 예외 원문 금지, 수정 안내가 붙은 request를 send로 한 번 전송)에 대해 checks.py가 확인하는 조건과 참고 위치만 안내함(코드는 주지 않음). | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 finish_answer | answer = validate_answer(send, known_ids) 이거 맞아? | known_ids는 맞지만 send는 요청 전송 함수라 json.loads에서 TypeError가 나고 except에도 잡히지 않으며, 검증 대상은 상태를 검사하는 응답 dict의 본문 문자열(키는 support.fixture_response 참고)이고 이 변수는 수정 요청 뒤 새 응답으로 바뀐다고 설명함(코드는 주지 않음). | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 finish_answer | response구나 | 검증 대상이 response인 것은 맞지만 response는 dict라 그대로 넘기면 json.loads에서 같은 TypeError가 나므로 모델 답변 문자열이 담긴 키를 support.fixture_response에서 찾으라고 안내하고, 파일에는 아직 send가 남아 있다고 알림. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 finish_answer | 타입 수정했어 다음은 hint인데 여기는 뭐 넣어야해? | validate_answer 호출이 맞다고 확인하고, hint는 append_repair_input이 직전 출력 뒤에 붙이는 user 메시지이며 비어 있지 않은 str이고 invalid_json, schema_error, unknown_source 안내가 서로 달라야 하고 예외 원문 대신 error_kind와 field만 쓰며 business_rule 같은 예상 밖 종류의 기본값도 고려하라는 조건만 설명함(안내 문장은 주지 않음). | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 finish_answer | hint 수정했는데 ㅓㅇ때 | 오류 종류별 안내 dict와 기본값이 check 조건(세 종류 서로 다름, 비어 있지 않음, 예외 원문 없음)을 충족하지만, unsupported_answer 안내가 근거 없는 경우에도 출처 표기를 요구해 관련 없는 출처를 붙이게 할 수 있고 담당자 연결이 needs_human 값으로 드러나지 않는다고 지적하고, send 호출 TODO가 남았다고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 finish_answer | 다시 수정햇어 | unsupported_answer 안내가 근거 유무로 나뉘어 규칙에 맞게 됐고, 담당자 확인이 needs_human=true로 이어지려면 필수 1 답변 형식에 그 조건이 필요하며, 남은 것은 수정 안내를 붙인 request를 send로 보내는 TODO라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 티켓 조회 (tool_schema, execute_tool, tool_roundtrip) | 다 통과했어 다음으로 넘어가자 | 필수 1 답변 형식(네 필드, 타입, needs_human 조건)이 아직 비어 있다고 다시 알리고, 티켓 조회 세 함수의 TODO별로 발제문 조건(스키마 제약, 허용 함수 이름, 키 집합 검사, 사본 반환 이유, output 전체 연결, call 항목의 키, call_id 연결)과 이유 주석에 쓸 내용의 방향만 안내함(코드는 주지 않음). | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 tool_schema | (tool_schema의 parameters 코드 붙여넣음: object, ticket_id string과 pattern ^IT-[0-9]{4}$, required, additionalProperties False) | 발제문 조건 네 가지를 모두 충족하고 checks.py의 정상값과 거부값(빈 객체, 숫자, 패턴 불일치, 추가 키)이 각각 type, pattern, required, additionalProperties로 처리되어 check 실패 요인이 없다고 확인하고, 다음은 execute_tool이라고 안내함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 execute_tool | 코드는 ai가 적어줬고, 해석했어 (execute_tool 전체 코드 붙여넣음) | execute_tool의 TODO를 이 대화가 아닌 다른 AI가 채운 코드라고 밝혀, 과제 규칙상 허용되지 않으므로 정답 여부는 검토하지 않고, 직접 다시 작성하거나 사용 도구와 질문 원문을 사실대로 기록하라고 안내하며 이해 점검 질문을 제시함. | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 전체 (tool_roundtrip, image_content, call_with_retry, cache_settings, usage_record, run_pipeline) | todo 다 적었어 코드는 ai가 적어줬고, 그걸 보고 해석해서 컴프리핸션된걸 풀어서 내가 재작성했어 | 다른 AI 코드를 바탕으로 재작성한 것도 AI 풀이 사용에 해당하니 도구, 질문, 함수, 재작성 사실을 기록하고 담당자 확인을 권함. call_with_retry의 status == 408 or 409 or 429가 항상 참이라 401도 재시도하는 check 실패 원인을 설명하고, 필수 1 답변 형식, image_content와 call_with_retry 이유 주석, usage_record 관측값 주석이 빠졌다고 안내함. | (직접 작성) | (직접 작성) |
| (날짜 직접 작성), 필수 3 TODO [ChatGPT] | (직접 작성) | 필수 3 TODO 코드를 코드 형태로 받음. 받은 코드를 분석하고 컴프리헨션을 풀어서 다시 작성함(사용자 설명 기준이며, 받은 함수 범위는 직접 작성). | (직접 작성) | (직접 작성) |
| 2026-11-02, 환경 [Claude Code 클라우드 세션] | uv sync frozen에 대해서 설명해줘 | uv.lock 기준 설치, --frozen은 lock을 갱신하지 않는다는 개념 설명 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 [Claude Code 클라우드 세션] | 형식만 알려줘 어떻게 적는지 보통 / 그대로 가져다안쓸테니까 보여줘봐 | 정책 프롬프트 섹션 틀(역할, 범위, 규칙, 특수 상황, 형식, 성공 기준)과 다른 주제(카페 주문) 예시 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 [Claude Code 클라우드 세션] | 제공된 참고문서가 이거야? / 사내 챗봇인데 사내문서 검색이 아니라고? | 문서 6개는 코드가 reference_documents로 붙이며 모델이 검색하는 게 아니라는 설명 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 [Claude Code 클라우드 세션] | 역할만 알려달라고 | 직접 쓴 역할 문장에서 "검색한 후 판단하고 검증한 자료를" 삭제, "제공된 참고 문서를 근거로"로 교체 제안 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 [Claude Code 클라우드 세션] | 다루는 문의와 다루지 않는 문의에 대한 목록을 적어줘 / 규칙에 대해서도 적어줘 / 나머지 특수상황도 다 줘 | documents.json과 evaluation_cases.json 기대값에서 업무 범위, 규칙, 특수 상황별 근거 문장 정리 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 [Claude Code 클라우드 세션] | 작성한 특수 상황과 프롬프트 검토 요청 | 비밀정보 줄에 담당자 연결 추가, 규칙 무시 기준 보완, 이미지 관찰과 추측 구분, 대괄호와 "필수 3" 표현 제거 지적 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 1 이유 [Claude Code 클라우드 세션] | 이유 주석 관련 질문 | Few-shot, Self-Consistency 개념과 Reasoning 한계 힌트(발제문 문장), 지워진 raise 줄 복구와 # 주석 형식 안내 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 [Claude Code 클라우드 세션] | answer_format 어떻게 시작해? / 카테고리 뭐있는데? | JSON Schema 문법 4종 설명, properties 틀 제시, 바뀌어 들어간 source_ids와 needs_human 타입 교정 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 [Claude Code 클라우드 세션] | 필드 찾아줘 / 조건식 검토 요청 | 파이썬 일반 문법(strip, any, set 길이 비교, not … and not …)과 필드명 안내, 잘못 넣은 변수 2개 교정 위치 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 [Claude Code 클라우드 세션] | 여기는 뭐 넘기는데? | validate_answer에 response["output_text"]와 known_ids를 넘긴다는 설명과 호출 줄 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 2 [Claude Code 클라우드 세션] | 이게뭔소리야 (hint 관련) | hint 조건과 오류 종류 6개 의미, dict 틀 제시, unsupported_answer와 기본 안내 문장 수정 제안 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 [Claude Code 클라우드 세션] | 코드쪽은 그냥 적어줘(거절됨) / r붙이는건 뭔데 | tool_schema 틀과 채울 위치 안내, raw string 개념 설명 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 [Claude Code 클라우드 세션] | tool_roundtrip 오류 질문 | 두 함수 내용이 섞인 원인 설명, execute_tool 호출 줄과 인자 검사 조건 위치 안내 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 이유 [Claude Code 클라우드 세션] | 이유 주석 2개 "알려줘" | 토큰 포함 관계와 비용, 지연 차이를 단정할 수 없는 이유, 도구 실행 주체와 call_id 역할 설명 | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 [Claude Code 클라우드 세션] | VS Code Claude 리뷰 내용 전달 | 제출 코드로 check all 실행(41/45, 클라우드 세션이 보고한 수치), 재시도 조건 버그 확인과 수정 줄 제시(수정 후 45/45, 클라우드 세션이 보고한 수치) | (직접 작성) | (직접 작성) |
| 2026-11-02, 필수 3 [Claude Code 클라우드 세션] | run usage --live 결과 전달 | 명령 앞부분 안내, 측정값 표 정리와 비용 검산, 해석 포인트 | (직접 작성) | (직접 작성) |
| 2026-11-02, 주석 [Claude Code 클라우드 세션] | 문장 어떻게 써야할지만 구성해서 알려줘봐 | usage, image, retry 이유 주석의 문장 틀 제공 | (직접 작성) | (직접 작성) |
| 2026-11-02, 위 클라우드 세션 중 코드 형태로 받은 부분 [Claude Code 클라우드 세션] | (위 행들의 질문) | 설명이 아니라 코드 형태로 받은 부분: finish_answer의 validate_answer(response["output_text"], known_ids) 호출 / tool_roundtrip의 result = execute_tool(call["name"], call["arguments"], tickets) 호출 / execute_tool의 인자 검사 조건 한 줄(isinstance와 set(args) 비교) / validate_answer의 변수 2개 교체 위치(known_ids, answer["needs_human"]) / call_with_retry의 status == 408 or status == 409 or status == 429 수정 줄 | (직접 작성) | (직접 작성) |
| 2026-11-02, AI 사용 기록 정리 | (다른 Claude Code 세션이 정리한 사용 기록 붙여넣음) / 추론 등급 높였어 다시 작성해줘 | 사용 도구에 클라우드 세션과 ChatGPT를 추가하고, ChatGPT 사용 행과 클라우드 세션 기록 17행, 코드 형태로 받은 부분 행을 표에 옮김. 붙여넣은 기록상 프롬프트의 업무 범위, 규칙, 특수 상황 근거 문장과 역할 교체 문구, 이유 주석 문장 틀도 AI에게 받은 것이므로 "프롬프트는 직접 다 작성"과 다르다고 짚음. | (직접 작성) | (직접 작성) |

## 제출 전 확인

- [ ] 제출한 함수의 입력, 분기, 반환값을 직접 설명할 수 있습니다.
- [ ] 프롬프트 문장과 비교 실험의 선택 이유를 직접 설명할 수 있습니다.
- [ ] AI를 사용한 부분과 사용하지 않은 부분을 사실대로 기록했습니다.
- [ ] API 키, `.env` 내용, 실제 개인정보를 기록에 포함하지 않았습니다.
