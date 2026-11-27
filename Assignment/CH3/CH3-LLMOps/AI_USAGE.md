# AI 사용 기록

AI는 개념 설명과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 TODO, 프롬프트 문장, 선택 심화 설계를 대신 완성하도록 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 항목을 추가하세요. API 키나 개인정보는 기록하지 않습니다.

- 사용 도구: Claude Code (VS Code 확장)
- 질문한 내용:
  - 과제 폴더의 파일 구성과 각 파일의 역할 설명
  - `mask_text` TODO 힌트, 이메일은 `text`에 대입하는데 전화번호는 바로 반환하는 이유
  - `validate_reply`의 출처 검사에서 부분집합을 확인하는 방법
  - 직접 작성한 출처 검사 코드가 맞는지 여러 차례 확인
  - `candidate_policy`가 인자 없이 어떻게 문서 ID를 넣을 수 있는지, 직접 작성한 지시문과 판단 주석이 맞는지
  - `generation_fields`에서 쓸 수 있는 값, 직접 작성한 반환 사전이 맞는지
  - `evaluate_case`의 반환식 작성 방향, 직접 작성한 반환식이 맞는지, 긴 반환식을 변수로 나누는 방법
  - `summarize`의 세 지표 작성 방향, 직접 작성한 식이 맞는지 여러 차례 확인
  - `release_gate`의 변경 판단 조건 작성 방향, 직접 작성한 식이 맞는지
  - 실제 비교와 서버 기록 조회 실행, 직접 작성한 관측·판단 주석 확인
- 이해한 내용:
  - `re.Pattern.sub`는 원본을 바꾸지 않고 새 문자열을 반환하므로, 다음 단계에서 쓸 값은 변수에 다시 대입해야 한다. 마지막 단계는 바로 반환해도 결과가 같다.
  - 부분집합은 `set.issubset()` 또는 `<=`로 확인한다. 리스트에는 `.issubset()`이 없고 `<=`는 순서 비교가 되므로 `set()`으로 바꿔야 한다. 빈 집합은 모든 집합의 부분집합이다.
  - `a.issubset(b)`는 a가 b 안에 들어가는지를 묻는다. 검사할 것은 "답변 출처 ⊆ 허용 출처"다.
  - `parsed`는 pydantic 모델이라 `parsed["..."]`가 아니라 `parsed.source_ids`처럼 점으로 필드를 꺼낸다. `"setup"`은 키가 아니라 `source_ids`에 들어 있는 값이다.
  - 지시문은 모든 질문에 공통으로 적용하는 고정 규칙이다. 질문과 문서(`doc_id` 포함)는 제공 코드가 `input`으로 따로 전달하고, 모델이 규칙에 따라 실제 사용한 `doc_id`를 `source_ids`에 적는다. 지시문이 고정되어야 `prompt_sha256`으로 버전을 비교할 수 있다.
  - 제공 코드는 지시문이 문자열인지 검사하므로 리스트를 반환하면 안 된다. `"""..."""` 안의 따옴표와 쉼표는 문법이 아니라 지시문 글자로 들어간다.
  - `generation_fields`의 반환 키 `output`, `usage_details`는 Langfuse `span.update()`의 인자 이름으로 그대로 쓰인다. 사용량이 없으면 `details`가 이미 `None`이므로 쪼개지 않고 통째로 넣는다.
  - 실제 실행에서는 제공 코드가 마스킹한 값을 넘기지만, 함수 안에서도 `mask_text`를 적용해야 마스킹되지 않은 입력에도 안전하다.
  - `return a, b, c`는 튜플을 반환하며, 값이 든 튜플은 `if`에서 항상 참이 된다. "모두 참"은 `and`로 잇는다. `a == b == c`는 "셋이 서로 같은가"라서 모두 `False`여도 `True`가 된다.
  - `set()`은 여러 값이 든 것만 받는다. 출처 비교는 순서와 무관해야 하므로 두 출처 목록을 각각 `set()`으로 감싸 `==`로 비교한다. `validate_reply`는 부분집합, `evaluate_case`는 같음을 검사한다.
  - `/`는 `-`보다 먼저 계산된다. 오류율의 분자는 정상 요청 수가 아니라 오류 요청 수다. 검사 자료가 4건 중 2건 오류라 오류율과 정상 비율이 모두 0.5여서 검사만으로는 이 실수를 잡지 못한다.
  - `all(... for x in 리스트)`에서는 반복 변수로 꺼낸 값 하나하나를 검사해야 한다. 리스트 이름을 그대로 검사하면 항상 참이 된다. 확인된 0원과 누락(`None`)을 구분하려면 `is not None`으로 비교한다.
  - 긍정 비율의 분모는 전체 요청 수가 아니라 피드백을 남긴 요청 수다. `sum()`은 `True`를 1, `False`를 0으로 더하므로 `sum(feedback)`이 `True`의 개수다.
  - 빈 리스트는 거짓이므로 "목록이 비어 있다"는 `not 목록`으로 쓴다. `and`는 불리언이 아니라 마지막으로 평가한 값을 반환하므로 조건마다 비교식이나 `not`을 써야 한다. "통과 수가 줄지 않음"은 `>=`다. 이전부터 실패하던 중요 사례는 `critical_failures`가 후보 기준으로 모으므로 따로 처리하지 않아도 된다.
  - 실제 실행에서 기준선 `unknown`, `direct`의 실패는 공격에 넘어간 것이 아니라 `abstain`에 출처를 붙인 형식 위반(`validate` 단계 오류)이었다. `verify`의 `all_verified=true`는 서버 기록이 일치한다는 뜻이고 답변 품질 통과와는 다르다. 비용 `null`은 서버에서 비용을 확인하지 못했다는 뜻이며 0원이 아니다.
- 직접 수정한 부분:
  - `mask_text`: 전화번호 치환을 추가했다. 동작 원리를 묻고 이해한 뒤 두 줄 대입 형태로 작성했다.
  - `validate_reply`: JSON 검사와 출처 검사를 직접 작성했다. 출처 검사는 변수 이름, 비교 방향, 필드 접근, set 변환 오류를 AI 피드백으로 하나씩 찾아 고쳤다.
  - `candidate_policy`: 과제 안내의 네 규칙을 바탕으로 지시문을 직접 작성했다. AI 피드백으로 리스트 반환을 문자열로 바꾸고, "치환"을 "반환"으로 고치고, 문자열 안에 남은 따옴표와 쉼표를 지웠다. 판단 주석도 직접 작성했다.
  - `generation_fields`: 반환 사전을 직접 작성했다. 처음에는 키 이름을 `raw`로 쓰고 `details`를 `input`, `output`으로 쪼갰으나, AI 피드백으로 `output`과 `usage_details` 두 키로 고쳤다.
  - `evaluate_case`: 반환식을 직접 작성했다. 튜플 반환, 불리언에 `set()` 적용, `==` 연쇄 비교, 출처 조건 누락을 AI 피드백으로 고쳤다. 이후 출처 비교를 `sources_ok` 변수로 분리했다.
  - `summarize`: 세 식을 직접 작성했다. 오류율은 연산자 우선순위와 분자(정상 수 → 오류 수)를, 비용 합계는 리스트 반환과 `all()`의 반복 대상·검사 대상을, 긍정 비율은 분자(`sum`)와 분모(`len(feedback)`), 리스트에 문자열 인덱스를 쓴 오류를 AI 피드백으로 고쳤다.
  - `release_gate`: 판단식을 직접 작성했다. `not` 누락과 통과 수 비교 누락을 AI 피드백으로 고쳤다.
  - 관측·판단 주석: AI가 정리한 실제 실행 결과를 읽고 직접 작성했다.
- 다시 실행한 명령과 확인 결과:
  - `uv run --frozen python main.py check observe` (AI가 실행): 15개 중 12개 통과. 미완료 3개는 아직 작성하지 않은 `generation_fields` 2개와 `candidate_policy` 1개.
  - `uv run --frozen python main.py check observe` (AI가 실행): 15개 모두 통과.
  - `uv run --frozen python main.py run observe` (AI가 실행): 질문 4개 모두 `status: ok`, 단계가 `retrieve`, `ticket-status`, `generate`, `validate` 순서로 기록됨.
  - `uv run --frozen python main.py check compare` (AI가 실행, `evaluate_case` 작성 후): 15개 중 9개 통과. `evaluate_case` 검사 5개 통과, 미완료 6개는 `summarize` 3개와 `release_gate` 3개.
  - `uv run --frozen python main.py check compare` (AI가 실행, `summarize` 작성 후): 15개 중 12개 통과. 미완료 3개는 `release_gate`.
  - `uv run --frozen python main.py run metrics` (AI가 실행): 요청 4, 오류율 0.5, p95 400ms, 토큰과 비용 `null`, 피드백 응답 2, 긍정 비율 0.5로 과제 기대값과 일치.
  - `uv run --frozen python main.py check compare` (AI가 실행, `release_gate` 작성 후): 15개 모두 통과.
  - `uv run --frozen python main.py run compare` (AI가 실행): 기준선 2/4, 후보 3/4, 회귀와 중요 실패 `direct`, `approve=false`로 과제 기대값과 일치.
  - `uv run --frozen python main.py check all` (AI가 실행): 30개 모두 통과.
  - `uv run --frozen python main.py run compare --live` (사용자 요청으로 AI가 실행, 모델 8회 호출): 기준선 2/4(`unknown`, `direct`가 `validate` 단계 `ValueError`), 후보 4/4, `approve=true`. 후보는 오류율 0.5 → 0.0, p95 약 3320ms → 4617ms, 토큰 1487 → 1978. 비용은 `null`.
  - `uv run --frozen python main.py verify` (AI가 실행): `all_verified=true`, Trace 8개 모두 단계·부모 관계·입출력·사용량·마스킹·`case_passed` 점수 확인. `FEEDBACK` 작성 전이라 피드백 지표는 비어 있음.
  - `FEEDBACK`을 직접 작성한 뒤 `uv run --frozen python main.py verify` (AI가 실행): `all_verified=true`. 긍정 비율은 기준선 0.5(4건 중 2건), 후보 1.0(4건 중 4건). 이번 조회에서는 서버 비용이 확인되어 기준선 약 0.000694 USD, 후보 약 0.000892 USD로 반영됨(Langfuse 설정 가격 기준 추정치). `check all` 30개 모두 통과.

## 선택 심화 1 (`decide_rollout`): AI가 작성

위 안내와 달리 선택 심화는 직접 작성하지 않고, 사용자가 요청하여 AI(Claude Code)가 구현과 검증을 했다. 필수 부분과 구분하기 위해 따로 기록한다.

- 요청한 내용: `decide_rollout`을 과제 안내의 조건대로 완성해 달라고 요청했다.
- AI가 작성한 구현:
  - 구간이 두 개 미만이면 내용 검사 없이 `hold`를 반환한다.
  - 최근 두 구간(`windows[-2:]`)만 사용한다. 먼저 값을 검증한다. 요청 수는 0 이상의 정수(`bool` 제외), 오류율은 `None`이거나 0~1의 수, p95는 `None`이거나 0 이상의 유한한 수여야 하며 아니면 `ValueError`를 낸다. NaN 오류율도 범위 비교에서 거절된다.
  - 값 검증을 통과한 뒤에 요청 수가 `min_requests`보다 적거나 지표가 `None`인 구간이 있으면 `hold`를 반환한다.
  - 구간별 악화는 오류율 `> max_error_rate` 또는 p95 `> max_p95_ms`다. 경계값과 같으면 악화가 아니다. 두 구간 모두 악화면 `rollback`, 하나만 악화면 `hold`, 둘 다 정상이면 `continue`다.
- 이해한 내용:
  - 값 검증을 표본 부족 판단보다 먼저 해야 잘못된 입력이 `hold`로 묻히지 않는다.
  - `None`은 "측정 안 됨"이므로 오류가 아니라 판단 보류 사유다. 범위를 벗어난 값은 데이터 자체가 잘못된 것이므로 거절한다.
  - 오래된 구간은 검증하지도 판단에 쓰지도 않는다. 과거에 실패했어도 최근 두 구간이 정상이면 `continue`다.
- 실행한 명령과 확인 결과 (AI가 실행):
  - `uv run --frozen python main.py check challenge`: 10개 모두 통과.
  - `uv run --frozen python main.py challenge`: `data/windows.json`에 대해 `rollback`.
  - 과제 안내의 예시 1개와 경계 조건 표 6개, 추가로 NaN 오류율, `bool` 요청 수, 오래된 구간의 잘못된 값 3개를 직접 호출해 모두 기대값과 일치.
  - 구현 후 `check all` 30개 모두 통과(필수 부분에 영향 없음).
