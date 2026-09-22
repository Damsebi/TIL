# Python API 호출과 인증·환경변수

> 학습일: 2026-09-21

## 핵심 정리

- API 호출은 `환경 변수에서 API Key 읽기 → headers/params 구성 → GET Request → Status Code 확인 → raise_for_status() → JSON Parsing → 데이터 구조 확인` 순서로 진행한다.
- API Key는 Code에 직접 적지 않고 환경 변수에 저장한 뒤 Python에서 `os.getenv()`로 읽는다.
- `headers`는 인증 같은 부가 정보를, `params`는 검색어 같은 Query Parameter를 전달한다.
- `response.raise_for_status()`는 4xx·5xx Response를 정상 데이터와 구분해 HTTP 오류가 발생한 위치에서 바로 실패하게 만든다.
- `response.json()`은 JSON Response를 Python 자료형으로 바꾼다.
- `timeout`은 Network가 무기한 대기하지 않도록 제한하며, 너무 짧으면 Response를 받기 전에 실패할 수 있다.
- `MockTransport`와 Fixture를 사용하면 실제 Internet이나 API Server 없이 고정된 Request와 Response로 Test할 수 있다.

## 1. Python API 호출의 전체 흐름

```text
환경 변수에서 API Key 읽기
→ headers 구성
→ params 구성
→ GET Request
→ Status Code 확인
→ raise_for_status()
→ JSON Parsing
→ 필요한 데이터 구조 확인
```

API 호출은 URL에 접속하는 것만으로 끝나지 않는다. 인증 정보와 검색 조건을 API가 요구하는 형식으로 전달하고, Server가 돌려준 HTTP 상태와 데이터 구조를 단계별로 확인해야 한다.

## 2. API Key와 환경 변수

API Key를 Code에 직접 작성하면 Git Repository, Notebook 공유, 화면 캡처, Log 등을 통해 노출될 수 있다. 환경 변수에 비밀값을 저장하고 Code에서는 변수 이름으로 읽어오면 Code와 비밀값을 분리할 수 있다.

```python
import os

api_key = os.getenv("KAKAO_REST_API_KEY")

if not api_key:
    raise RuntimeError("KAKAO_REST_API_KEY 환경변수를 설정하세요.")
```

환경 변수를 사용하더라도 실제 Key를 출력하거나 Log에 남기면 안 된다.

SSH Session에서 임시로 설정한 환경 변수는 Session이 종료된 뒤 사라질 수 있다. 새 Session에서는 다시 설정하거나, 안전한 환경 변수 관리 방법을 별도로 구성해야 한다.

## 3. `headers`와 `params`

`headers`에는 인증 정보나 Content Type처럼 Request에 필요한 부가 정보를 담는다. `params`에는 검색어, 페이지, 정렬 방식 같은 Query Parameter를 담는다.

```text
headers
→ 인증 정보와 Request 부가 정보

params
→ URL의 Query Parameter
→ 검색·필터·페이지 조건
```

`params` 자체가 모든 GET Request에 필수인 것은 아니다. 어떤 Query Parameter가 필수인지는 각 API 문서에서 정한다.

## 4. Response 확인과 JSON Parsing

Request를 보낸 뒤에는 Status Code부터 확인한다.

```text
Response 수신
→ Status Code 확인
→ raise_for_status()
→ response.json()
→ 데이터 구조 검증
```

`response.raise_for_status()`는 4xx나 5xx가 반환됐을 때 `HTTPStatusError`를 발생시킨다. 오류 Response를 정상 데이터처럼 처리하지 않고 HTTP 오류가 발생한 위치에서 실행을 멈추게 한다.

`response.json()`은 Server가 보낸 JSON을 Python의 `dict`와 `list` 같은 자료형으로 변환한다.

카카오 검색 API에서 확인한 Response는 대략 다음 구조였다.

```python
payload = {
    "documents": [
        {
            "title": "...",
            "contents": "...",
            "url": "...",
            "datetime": "..."
        }
    ],
    "meta": {
        # 검색 요청 전체에 대한 정보
    }
}
```

- `payload`: Response 전체를 담은 변수
- `dict`: `payload`의 Python 자료형
- `documents`: 검색 결과 목록
- `documents[0]`: 검색 결과 한 건
- `title`, `url`, `datetime`: 각 검색 결과를 설명하는 Field
- `meta`: 검색 요청 전체에 대한 부가 정보

`documents` 안의 Field와 최상위 `meta`는 구조상 같은 위치가 아니다. 다만 넓은 의미에서 `title`, `url`, `datetime`도 데이터를 설명하는 Metadata 성격을 가질 수 있다.

## 5. 실제 실습에서 확인한 오류

### 환경 변수 누락

SSH Session이 끊긴 뒤 환경 변수를 다시 설정하지 않았을 때 API Request를 보내기 전에 Python Code에서 오류가 발생했다.

```text
RuntimeError: KAKAO_REST_API_KEY 환경변수를 설정하세요.
```

환경 변수 검사는 인증 정보가 없는 상태로 불필요한 Request를 보내기 전에 설정 문제를 알려준다.

### 잘못된 API Key

일부러 잘못된 Key를 사용했을 때 Server가 `401 Unauthorized`를 반환했다.

```text
잘못된 인증 정보
→ Server까지 Request 도착
→ Server가 401 Response
→ raise_for_status()
→ HTTPStatusError
```

`401`은 Network 연결 자체의 실패가 아니라 Server가 Request를 받은 뒤 인증에 실패했다고 응답한 경우다.

### `raise_for_status()`를 제거했을 때

`401` Response Body도 JSON이므로 `response.json()` 자체는 성공했다.

```text
Key 목록: ['errorType', 'message']
```

그러나 정상 Response에 있어야 할 `documents`가 없기 때문에 이후 구조 검사에서 `ValueError`가 발생했다. `raise_for_status()`는 이 문제를 더 이른 위치에서 HTTP 오류로 구분한다.

### Response 구조 검사까지 제거했을 때

`documents`가 없는 Response에서 다음 값은 `None`이 된다.

```python
documents = payload.get("documents")
```

그 상태에서 `len(documents)`를 실행하면 사실상 `len(None)`이 되어 다음 오류가 발생한다.

```text
TypeError: object of type 'NoneType' has no len()
```

Response 구조 검사는 뒤에서 발생할 오류를 더 정확한 위치와 메시지로 알려주는 역할을 한다.

### Query Parameter를 제거했을 때

카카오 검색 API 문서에서는 `query`가 필수이지만, 실습에서 `query` 없이 요청했을 때는 `400`이 아니라 `200`과 빈 `documents`가 반환됐다.

```text
Request URL
→ https://dapi.kakao.com/v2/search/web

Status Code
→ 200

검색 결과
→ 0건
```

필수 Parameter가 빠지면 400번대 오류가 발생하는 경우가 많지만 절대적인 규칙은 아니다. API 문서의 조건을 따르되 실제 Server Response도 확인하고, 필요하면 Client Code에서 필수 값 검사를 추가한다.

### Timeout을 매우 짧게 설정했을 때

```python
httpx.Client(timeout=0.000001)
```

연결 제한 시간이 먼저 끝나 다음 오류가 발생했다.

```text
httpx.ConnectTimeout: timed out
```

```text
ConnectTimeout
→ HTTP Response를 받기 전 Network 단계에서 실패

HTTPStatusError
→ Server Response는 받았지만 Status Code가 4xx/5xx
```

`timeout`은 Network가 무기한 대기하는 것을 막지만, 지나치게 짧으면 정상적인 Server에도 연결하기 전에 실패할 수 있다.

## 6. EC2 실습 환경 이해

이번 실습에서는 EC2에 API Server를 만든 것이 아니라 EC2를 원격 Python Computer처럼 사용했다.

```text
Windows
→ SSH
→ AWS EC2 Ubuntu
→ Python + httpx
→ 카카오 API 호출
```

EC2 Instance 안에 Project Folder와 Virtual Environment를 만들고 `httpx`로 외부 API를 호출했다.

### SSH

SSH는 다른 Computer에 원격으로 접속해 Shell 명령을 실행하는 방식이다.

```text
내 Windows PowerShell
→ SSH
→ EC2의 Linux Shell
```

`first_key_pair.pem`은 SSH 접속에 사용하는 Private Key 역할을 했다.

### Linux와 Ubuntu

Ubuntu는 Linux 계열 Operating System의 한 Distribution이다.

```text
Linux
├─ Ubuntu
├─ Debian
├─ Fedora
└─ Amazon Linux
```

Ubuntu는 Linux이지만 모든 Linux가 Ubuntu인 것은 아니다.

### Shell과 Terminal

- Shell: 사용자의 명령을 해석해 Operating System에 전달하는 Program
- Terminal: Shell을 실행하고 명령과 결과를 보여주는 화면 또는 Program
- SSH: `Secure Shell`의 약자로 원격에서 안전하게 Shell을 사용하는 방식

## 7. `httpx`와 FastAPI의 역할

`httpx`는 API Request를 보내는 Client Library이고, FastAPI는 Python으로 API Server를 만드는 Framework다.

```text
httpx
→ API Request를 보내는 Client

FastAPI
→ API Request를 받는 Server 구현
```

이번 실습에서는 `httpx`로 카카오 API를 호출하는 Client 역할을 확인했다. FastAPI는 이후 API 요청을 받는 Server를 구현할 때 사용한다.

## 8. 실제 API 없이 Test하기

`MockTransport`는 실제 Internet이나 API Server를 사용하지 않고, Request에 대해 미리 정한 Response를 반환하도록 만드는 `httpx`의 Test 도구다.

Fixture는 Test에서 반복해서 사용하는 고정 데이터나 준비된 실행 환경이다.

```text
Test Request
→ MockTransport
→ 미리 정한 Response
→ Parsing·오류 처리 Logic 검증
```

이를 사용하면 실제 API Key, Network 상태, 외부 Server의 데이터 변화에 영향을 받지 않고 Client Logic을 반복해서 Test할 수 있다.

## 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| `params`는 GET Request에서 항상 필수다. | `params` 자체가 항상 필요한 것은 아니다. 필요한 Query Parameter는 API마다 다르다. |
| 필수 Parameter가 빠지면 반드시 400번대 오류가 발생한다. | 흔한 설계이지만 절대 규칙은 아니다. 실습한 카카오 검색 API에서는 `200`과 빈 `documents`가 반환됐다. |
| `documents` 안의 Field 전체가 최상위 `meta`에 해당한다. | `documents`는 검색 결과 목록이고, 내부 Field는 결과 한 건을 설명한다. 최상위 `meta`는 검색 요청 전체의 정보다. |
| 오류 처리는 오류를 없애는 기능이다. | 오류 처리는 문제가 발생한 단계를 구분하고 원인을 더 정확하게 확인하도록 돕는 과정이다. |
