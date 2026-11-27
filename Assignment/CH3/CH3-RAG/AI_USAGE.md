# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인을 확인할 때 사용할 수 있습니다. 미작성 빈칸, 과제 전체, 평가 사례나 선택 심화의 설계를 대신 완성해 달라고 요청하지 않습니다. 실제 실행 결과를 만들거나 고쳐 달라고 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적으세요. 사용했다면 필요한 만큼 기록하세요. API 키나 원문 개인정보를 대화에 넣지 않습니다.

사용 도구: Claude Code (VS Code 확장, Claude Opus 5.5)

질문과 관련 함수:

`prepare_chunks` (1-14번)

1. 문단의 연속 공백을 찾는 코드가 뭘까
2. `join`은 `.` 앞에 있는 것을 합치고 인자로 넣는 게 합칠 문장들인지, `split`에 인자를 안 넣으면 공백 기준으로 잘리는지
3. chunk를 만드는 방식이 맞는지, `paragraphs`가 무엇인지, 문서 정보 5개와 chunk_id, text를 담은 사전으로 만들면 되는지(정답 대신 힌트만 달라고 요청)
4. 문서 정보 5개가 id, title, category, status, source, file인지
5. status, category, source, chunk_id인지, 그리고 document_id가 아니라 chunk_id인지
6. `prepare_chunks`를 참조하는 곳을 찾아봐도 없는 이유, 원래 이렇게 찾는 게 아닌지
7. support.py의 `prepare_chunks` 호출 부분이 맞는지
8. 문서 정보 5개가 title, status, category, source, document_id인지
9. 검사 실행 명령
10. 직접 작성한 chunk 사전이 맞는지 (chunk_id를 세 번 고치며 매번 확인 요청)
11. 문단을 유지해야 하는 이유가 청킹하기 쉬워서인지
12. 청킹 방식이 문단과 글자 수 말고 다른 것도 있는지
13. 직접 작성한 `# 이유:` 주석이 맞는지 (두 번 확인 요청)
14. 두 번 시도한 뒤 `# 이유:` 주석의 답을 알려 달라고 요청 (→ AI가 주석 예시 문장을 답함)

`build_index` (15-18번)

15. 정규화된 문서 벡터로 바꾸려면 인자로 받은 embedder로 무엇을 해야 하는지, 사용할 수 있는 라이브러리가 무엇인지
16. 직접 작성한 `embedder.encode(...)` 줄이 맞는지
17. Qdrant point에 연결하는 특별한 함수가 있는지
18. `Payload(i, vector, row)`처럼 쓰면 되는지, 그리고 직접 작성한 `PointStruct` 줄이 맞는지

`search` (19-24번)

19. 필터도 `models.`으로 시작하는 모양인지
20. key에 넣을 값이 보이지 않는데 vector 안에서 키를 가져와야 하는지
21. `search`는 `build_index`를 호출하지 않는데 어떻게 저장된 데이터를 받아올 수 있는지
22. 직접 작성한 필터 코드가 맞는지 (두 번 확인 요청)
23. key 값만 정답을 알려 달라고 요청 (→ AI가 `"status"`, `"category"`를 답함)
24. 고친 필터 코드가 맞는지 (세 번 확인 요청)

`rewrite_query` (25-27번)

25. 직접 작성한 `alias.replace(formal_name)`이 맞는지
26. `question.replace(alias, formal_name)`으로 고친 것이 맞는지
27. `rewritten.replace(alias, formal_name)`으로 고친 것이 맞는지

`answer_question` (28-37번)

28. `context`를 `"\n".join(question, rows, generate)`로 만든 것이 맞는지
29. `rows["chunk_id"] + generate`로 고친 것이 맞는지
30. 94번 줄이 완성된 것인지 (파일이 저장되지 않아 이전 상태였음)
31. 반복문으로 `[chunk_id] 본문` 문자열을 만들어 리스트에 담은 코드가 맞는지
32. `" ".join(context)`로 고친 것이 맞는지
33. `"\n".join(context)`로 고친 것이 맞는지 (→ AI가 빈 줄 구분자는 `"\n\n"`이라고 답함)
34. `context`가 맞는지 확인하고, 출처 검사 TODO 힌트 요청
35. `reply["citations"] not in all(reply)`로 작성한 것이 맞는지
36. `for` 반복문 안에 `any(term not in allowed)`를 쓴 것이 맞는지 (→ AI가 `any`를 빼면 된다고 완성된 모양을 보여 줌)
37. `any`를 뺀 최종 코드가 맞는지

`make_golden` (38-44번, 사례 내용은 직접 작성하고 규칙에 맞는지만 확인 요청)

38. 다음 TODO가 `make_golden`인지, if문으로 하나를 리턴하고 else로 나머지를 리턴하면 안 되는지
39. 리스트 안에 사전 두 개를 넣고 `question_id`에 `data/golden.json["question_id"]`를 쓴 구조가 맞는지
40. golden.json에 이미 있는 사례를 가져와도 되는지
41. 직접 작성한 첫 번째 사례(VPN)가 맞는지
42. 질문에 별칭 `초록문`을 넣고 확인 문구를 `승인`으로 고친 첫 번째 사례가 맞는지
43. 확인 문구를 `보안팀에 승인 요청`으로 바꾸고 두 번째 사례(`overseas`)를 작성한 것이 맞는지
44. 확인 문구를 단어별로 나누고 두 번째 사례의 질문과 참고 답변을 고친 것이 맞는지

`measure` (45-48번)

45. `recall = int(expected - (expected - found)) / 100`으로 작성한 것이 맞는지
46. `len(...) / len(expected)`로 고친 것이 맞는지, 그리고 `if len(expected) is not None:`으로 조건을 붙인 것이 맞는지
47. `if expected:` / `else: recall : None`으로 고친 것이 맞는지
48. `recall = None`으로 고친 최종 코드가 맞는지

이해한 내용:

- `split()`은 인자가 없으면 연속된 공백(스페이스, `\n`, `\t`)을 한 덩어리로 보고 자르며 빈 조각을 버린다. `"구분자".join(리스트)`는 리스트 조각 사이에 구분자를 넣어 잇는다.
- `paragraphs`는 `load_documents()`가 TXT는 빈 줄, HTML은 문단 기준으로 나눈 문자열 리스트다.
- `document_id`는 청크가 어느 문서에서 왔는지(문서마다 같음), `chunk_id`는 청크 하나를 구분하는 값(`문서ID:번호`)이다.
- 문자열과 정수는 `+`로 바로 이을 수 없어 `str()`로 바꿔야 한다.
- main.py 함수는 `globals()`로 넘겨져 `api["prepare_chunks"]`처럼 문자열 키로 호출되므로 IDE 참조 찾기에 나오지 않고, 전체 텍스트 검색으로 찾아야 한다.
- 청킹 방식에는 고정 길이, 문장, 재귀 분할, 문서 구조, 의미 기반, 부모-자식 등이 있고 데이터 생김새에 따라 고른다. 이 과제는 데이터가 이미 문단으로 나뉘고 문단이 512토큰보다 짧아 문단 단위가 적절하다.
- 메타데이터 용도: title은 임베딩 시 문서 주제를 더해 검색 정확도를 높이고, status·category는 검색 필터, source·chunk_id는 출처 표시, document_id는 문서 Recall 평가에 쓰인다.
- `embedder`는 `SentenceTransformer` 모델이고, `encode(텍스트 리스트, normalize_embeddings=True)`로 정규화된 벡터를 만든다. 질문은 하나라 `[0]`으로 꺼내지만, 문서는 여러 개라 `[0]`을 붙이면 첫 벡터만 남는다.
- Qdrant point는 `models.PointStruct(id=, vector=, payload=)`로 만들고, 인자는 이름을 붙여 넘긴다. payload에 청크 사전을 넣어 두면 검색 결과로 그대로 돌아온다.
- 필터는 `models.Filter(must=[models.FieldCondition(key=, match=models.MatchValue(value=)), ...])` 구조다. `must`는 모든 조건을 만족해야 하고, `FieldCondition` 하나에 조건 하나가 들어간다.
- 필터의 `key`는 payload 필드 이름을 문자열로 적는 것이고, 값을 어딘가에서 꺼내 오는 것이 아니다. 고정 값은 따옴표로 쓰고, 함수 인자 같은 변수는 따옴표 없이 쓴다.
- `build_index`와 `search`는 서로 호출하지 않고 `client`(Qdrant DB)로 이어진다. `build_index`가 저장하고 돌려준 `client`를 호출하는 쪽이 `search`에 넘기며, 필터는 SQL의 `WHERE`처럼 DB에 조건을 보내는 것이다.
- `문자열.replace(찾을 글자, 바꿀 글자)`는 인자 두 개를 받는다. 반복문에서 여러 별칭을 차례로 바꾸려면 매번 원래 질문이 아니라 직전 결과(`rewritten`)에서 시작해야 한다.
- `rows`는 딕셔너리 여러 개가 든 리스트라 `rows["chunk_id"]`처럼 키로 접근할 수 없고, `for row in rows`로 꺼낸 `row`에서 키를 꺼내야 한다. `generate`는 문자열이 아닌 함수이고, `question`과 `context`는 따로 넘어간다.
- 리스트를 모아 문자열로 만들 때는 빈 리스트를 반복문 밖에서 한 번 만들고, 반복하며 `append`하고, 반복문이 끝난 뒤 `join`한다. 리스트를 반복문 안에서 만들면 매번 초기화된다.
- 빈 줄은 `"\n\n"`이다. 첫 `\n`이 줄을 끝내고 두 번째 `\n`이 빈 줄을 만든다.
- `any`는 여러 값의 묶음을 받아 하나라도 참인지 보고, `all`은 모두 참인지 본다. `True`/`False` 하나만 넣으면 오류가 난다. `any(c not in allowed for c in 리스트)`와 `for` 안의 `if c not in allowed:`는 같은 일을 한다.
- 출처 검사는 LLM이 검색 결과에 없는 출처를 지어내는 것을 막기 위한 것이다.
- `make_golden`은 인자가 없어 if/else로 나눌 것이 없고, `return`은 한 번만 실행되므로 사례 두 개를 리스트 하나에 담아 돌려준다.
- `data/golden.json["question_id"]`는 파일을 읽는 코드가 아니라 변수 나눗셈으로 해석된다. 평가 사례 값은 직접 문자열로 적는다.
- 제공 사례와 `question_id`나 질문이 겹치면 `run evaluate`에서 실패한다. `check evaluate`는 사례 규칙만 검사해 이 중복은 잡지 않는다.
- 답이 있는 사례는 질문에 별칭(`초록문`, `임시열쇠`)이 있어야 하고, 확인 문구는 참고 답변과 근거 원문에 글자 그대로 들어 있어야 한다(`in` 검사라 조사 하나만 달라도 실패). 흔한 단어 하나보다 구체적인 문구가 평가를 엄격하게 만든다.
- 자료가 없는 사례는 `overseas` 분류에 빈 리스트를 쓰고, 문서와 무관한 질문이어야 한다. 참고 답변은 답을 지어내지 않고 담당자 확인으로 넘기는 응답이어야 한다.
- `expected - (expected - found)`는 필요한 문서 중 실제로 찾은 문서(교집합)다. 결과는 집합이라 `int()`로 바꿀 수 없고 `len()`으로 개수를 센다.
- Recall은 `찾은 개수 / 필요한 개수`인 0~1 사이 비율이고, 100으로 나누는 퍼센트가 아니다.
- `len()`은 빈 집합에도 `None`이 아니라 `0`을 돌려준다. 비어 있는지는 `if expected:`로 확인하고, 비었을 때는 0으로 나누지 않도록 `None`을 넣는다. if에서 값을 넣으면 else에서도 값을 넣어야 변수가 항상 만들어진다.
- `recall : None`은 값을 넣지 않는 타입 표시(annotation)라 문법 오류 없이 지나가지만 변수가 만들어지지 않는다. 값을 넣으려면 `=`를 써야 한다.

직접 수정한 부분:

- main.py 19번 줄: 연속 공백 정리 코드
- main.py 24-32번 줄: chunk 사전. chunk_id는 `"vpn:"+number` → `"vpn:"+document["document_id"]` → `document["document_id"] + number` → `document["document_id"] + ":" + str(number)` 순서로 힌트를 받으며 직접 고침
- main.py 35-37번 줄: `# 이유:` 주석을 직접 작성하고 두 번 고침
- main.py 45번 줄: 문서 벡터 생성. `search`의 질문 벡터 줄을 참고해 작성하고, 처음에 붙였던 `[0]`을 힌트를 받아 뗌
- main.py 50번 줄: `models.PointStruct(id=i, vector=vector, payload=row)`. AI가 준 빈칸 틀(`id=___, vector=___, payload=___`)에 값을 직접 채움
- main.py 61-66번 줄: 현행 문서와 지정 category 필터. key 값은 AI 답을 받고, value는 `"category"` 문자열 → 빈칸 → `category` 변수 순서로 직접 고침
- main.py 82번 줄: 별칭 치환. `alias.replace(formal_name)` → `question.replace(alias, formal_name)` → `rewritten.replace(alias, formal_name)` 순서로 힌트를 받으며 직접 고침
- main.py 94-98번 줄: `context` 만들기. AI가 준 `"[" + row["chunk_id"] + "] " + row[___]` 틀을 참고해 반복문으로 작성하고, 리스트 초기화 위치와 `join` 구분자(`" "` → `"\n"` → `"\n\n"`)를 힌트를 받으며 고침. `"\n\n"`은 AI 답을 받음
- main.py 102-104번 줄: 출처 검사. `all` 사용 → `for` 안에서 `any` 사용 → AI 답을 받아 `any`를 뺀 `if term not in allowed:`로 고침
- main.py 110-129번 줄: `make_golden` 평가 사례 두 개. 질문, 참고 답변, 근거 문서, 확인 문구를 직접 정하고, AI가 짚은 규칙 위반(별칭 없음, 확인 문구가 원문에 없음, 자료 없는 사례가 실제 문서와 겹침, 참고 답변이 답을 지어냄)을 보고 직접 고침
- main.py 136-139번 줄: Recall 계산. 교집합 식(`expected - (expected - found)`)은 직접 작성하고, `int` → `len`, `/ 100` → `/ len(expected)`, 빈 집합 조건(`is not None` → `if expected:`), else의 `:` → `=` 순서로 힌트를 받으며 직접 고침. AI가 if/else 빈칸 틀을 보여 줌

다시 실행한 명령과 확인 결과:

- `.venv\Scripts\python.exe main.py check index` (AI가 실행): 3개 중 1개 통과. "TXT/HTML 정제와 문단 청킹" 통과, 나머지 2개는 `build_index`의 TODO가 남아 미완료.
- 같은 명령, `build_index` 작성 후 (AI가 실행): 3개 중 2개 통과. "현행/분류 필터와 검색 개수"는 `search`의 필터 TODO가 남아 미완료.
- 같은 명령, `search` 필터 작성 후 (AI가 실행): 3개 중 3개 통과.
- numpy 벡터를 `PointStruct`에 넣으면 리스트로 바뀌는지 확인하는 한 줄 코드 (AI가 실행): 자동으로 리스트로 바뀌어 `list()` 변환이 필요 없음을 확인.
- `.venv\Scripts\python.exe main.py check answer`, `rewrite_query` 작성 후 (AI가 실행): 2개 중 1개 통과. "출처 답변과 자료 없음 처리"는 `answer_question`의 TODO가 남아 미완료.
- 같은 명령, `answer_question` 작성 후 (AI가 실행): 2개 중 2개 통과.
- `.venv\Scripts\python.exe main.py check evaluate`, 확인 문구를 `보안팀에 승인 요청`으로 쓴 상태 (AI가 실행): 3개 중 0개 통과. "확인 문구는 참고 답변과 근거 원문에 모두 있어야 합니다" 오류.
- 같은 명령, 사례 수정 후 (AI가 실행): 3개 중 1개 통과. "직접 작성한 평가 사례" 통과, 나머지 2개는 `measure`의 Recall TODO가 남아 미완료.
- 같은 명령, `measure` 작성 후 (AI가 실행): 3개 중 3개 통과.

---

## 선택 심화 1: `fuse_rankings` (AI가 작성한 코드)

이 부분은 위의 힌트 기반 작업과 다르게, 직접 구현하기 어렵다고 판단해 AI에게 코드 작성을 요청했습니다. 과제 규칙(선택 심화 설계를 대신 완성해 달라고 요청하지 않음)에 어긋나는 사용임을 알고, 숨기지 않고 따로 기록합니다.

요청 내용:

- `fuse_rankings`를 AI가 작성하고, 작성된 코드를 보며 직접 분석하는 방식으로 진행

AI가 작성한 부분:

- main.py `fuse_rankings` 함수 본문 전체 (`top_k` 검사, 목록별 중복 제거와 순위 매기기, `1 / (60 + 순위)` 점수 합산, 점수 내림차순·`chunk_id` 오름차순 정렬, 새 사전으로 `score`를 넣어 `top_k`개 반환). 코드 안에도 `(AI 작성)` 주석으로 표시함

직접 한 부분:

- (코드 분석 후 이해한 내용을 여기에 직접 작성)

실행한 명령과 확인 결과 (AI가 실행):

- `.venv\Scripts\python.exe main.py check challenge`: 1개 중 1개 통과.
- ASSIGNMENT.md의 작은 예시 입력: `guide:1`(2/62), `guide:0`(1/61), `policy:0`(1/61) 순서로 반환되어 문서의 예시와 일치.
- `top_k`에 `True`, `0`, `6`, `2.0`을 넣으면 모두 `ValueError`가 나는 것을 확인.
