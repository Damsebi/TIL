# CH2 과제: KANT NEXT DevDesk

프롬프트 엔지니어링 / 데이터 수집 & API 서버 구축 / LangChain 과제 발제 (1)

| 항목 | 내용 |
| --- | --- |
| 제출 기간 | 10/13(화) ~ 11/2(월) (10/27에서 연장) |
| 제출 파일 | 과목별 구현 파일(`main.py` 또는 `app.py`) + `AI_USAGE.md` |
| 실행 환경 | VS Code + uv + Python 3.12 |
| 과제 사이트 | [DevDesk 과제 웹사이트](https://private-llm-assignment.vercel.app/) · [과제 목록](https://private-llm-assignment.vercel.app/assignments/) · [제출 안내](https://private-llm-assignment.vercel.app/submission/) |


## 폴더 구성

과목별 학생용 ZIP을 `Assignment/`에 풀고, 생긴 폴더(`kant-next-...-student/`) 이름을 아래처럼 바꿔서 작업합니다.

| 폴더 | 과목 | 구현 파일 |
| --- | --- | --- |
| `CH2-PromptEngineering/` | 프롬프트 엔지니어링 | `main.py` |
| `CH2-DataCollectionAPI/` | 데이터 수집 & API 서버 구축 | `app.py` |
| `CH2-LangChain/` | LangChain | `main.py` |

`.gitignore` 설정으로 과목 폴더에서는 직접 작성한 구현 파일(`main.py` / `app.py`)과 `AI_USAGE.md`만 커밋됩니다. 제공 코드, `data/`, `artifacts/`, `.env`, `.venv/`는 자동으로 제외됩니다.


## 공통 실행 흐름

```bash
uv sync --frozen
cp .env.example .env                  # OPENAI_API_KEY 입력
uv run --frozen python main.py demo   # 데이터 수집 & API 과제는 app.py
```

기능 구현 → `run 기능명` → `artifacts/` 결과 확인 → `check 기능명` → 필요한 기능만 `--live`

- `check`에는 `--live`를 붙이지 않는다.
- `support.py`, `checks.py`, `data/`는 수정하지 않는다.

아래 체크리스트의 괄호 안은 `run` / `check` 기능명입니다.


## 1. 프롬프트 엔지니어링

[과제 본문](https://private-llm-assignment.vercel.app/assignments/prompt-engineering/brief/) · [시작 안내](https://private-llm-assignment.vercel.app/assignments/prompt-engineering/guide/) · [AI 사용 기준](https://private-llm-assignment.vercel.app/assignments/prompt-engineering/ai-policy/) · [학생용 ZIP](https://private-llm-assignment.vercel.app/downloads/prompt-engineering/kant-next-prompt-student.zip)

- [ ] 필수 1. 정책 프롬프트와 두 조건 비교 (`policy`)
- [ ] 필수 2. 답변 형식, 검증, 한 번의 수정 (`answer`)
- [ ] 필수 3. 티켓 조회, 이미지, 재시도, 사용량과 비용, 전체 연결 (`tools`, `image`, `retry`, `usage`, `pipeline`)
- [ ] 선택 심화 1. 대상별 설명과 정책 일치 검사 (`challenge`)
- [ ] 마무리: `check all` → `compare --live` → `export`


## 2. 데이터 수집 & API 서버 구축

[과제 본문](https://private-llm-assignment.vercel.app/assignments/data-api/brief/) · [시작 안내](https://private-llm-assignment.vercel.app/assignments/data-api/guide/) · [제공 자료](https://private-llm-assignment.vercel.app/assignments/data-api/data/) · [AI 사용 안내](https://private-llm-assignment.vercel.app/assignments/data-api/ai-policy/) · [학생용 ZIP](https://private-llm-assignment.vercel.app/downloads/data-api/kant-next-api-student.zip)

- [ ] 필수 1. 공개 자료 수집과 저장 (`collect`)
- [ ] 필수 2. 품질 점검과 문서 구성 (`documents`)
- [ ] 필수 3. 문서 API (`document-api`)
- [ ] 필수 4. 질문 API: 모델 연결, 실패 처리, 요청 제한과 기록 (`query`, `retry`, `observe`)
- [ ] 선택 심화 1. 두 시점의 문서 변경 내역 (`challenge`)
- [ ] 마무리: `check all`


## 3. LangChain

[과제 본문](https://private-llm-assignment.vercel.app/assignments/langchain/brief/) · [환경 준비 및 실행 안내](https://private-llm-assignment.vercel.app/assignments/langchain/guide/) · [AI 사용 안내](https://private-llm-assignment.vercel.app/assignments/langchain/ai-policy/) · [예제 자료](https://private-llm-assignment.vercel.app/assignments/langchain/data/) · [학생용 ZIP](https://private-llm-assignment.vercel.app/downloads/langchain/kant-next-langchain-student.zip)

- [ ] 필수 1. 관련 문서를 찾아 실행 입력 준비 (`search`)
- [ ] 필수 2. 기본 체인과 문서 없음 분기 (`chain`)
- [ ] 필수 3. 세션별 후속 질문 이어가기 (`history`)
- [ ] 필수 4. 실패를 구분해 제한된 복구 적용 (`recovery`)
- [ ] 필수 5. 생성 중 청크 전달과 실행 관측 (`stream`)
- [ ] 선택 심화 1. 답변 초안 검토 후 한 번 개선 (`challenge`)
- [ ] 마무리: `check all`
