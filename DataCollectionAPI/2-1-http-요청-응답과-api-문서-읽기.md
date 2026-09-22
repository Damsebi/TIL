# HTTP 요청·응답과 API 문서 읽기

> 학습일: 2026-09-21

## 핵심 정리

- Web이나 App에서는 Client가 Server에 HTTP/HTTPS Request를 보내고 Server가 Response를 돌려주는 방식으로 통신한다.
- Browser뿐 아니라 Python과 같은 Code에서도 HTTP Request를 직접 보낼 수 있다.
- API를 사용한다는 것은 API 자체를 다운로드하는 것이 아니라, API 문서에 맞춰 Request를 보내고 필요한 데이터를 Response로 받는 것에 가깝다.
- HTTP Status Code를 통해 요청 처리 결과를 확인하며, `200 OK`는 요청이 정상적으로 처리됐다는 의미다.
- URL은 `scheme → host → base path → endpoint → parameter` 등의 요소로 나누어 읽을 수 있다.
- Path Parameter는 특정 자원을 지정하고, Query Parameter는 검색·필터·페이지 등의 조건을 전달하는 데 주로 사용한다.

## 1. HTTP Request와 Response

Web이나 App에서 Client와 Server는 다음 흐름으로 통신한다.

```text
Client
→ HTTP/HTTPS Request
→ Server
→ Request 처리
→ HTTP Response
→ Client
```

Client는 필요한 자원이나 작업을 Request하고, Server는 요청을 처리한 결과를 Status Code와 Response Body에 담아 돌려준다.

요즘에는 전송 내용을 암호화하는 HTTPS를 주로 사용한다. Browser에서 주소를 입력하는 것뿐 아니라 Python의 `httpx`나 `requests` 같은 Library로도 같은 방식의 Request를 보낼 수 있다.

## 2. API를 사용한다는 의미

API를 사용한다는 것은 보통 API를 File처럼 다운로드하는 것이 아니다. API 문서에서 정한 규칙에 따라 올바른 Request를 보내고 Response를 받는 과정이다.

API 문서에서는 주로 다음 항목을 확인한다.

- Request를 보낼 URL과 Endpoint
- GET, POST 등의 HTTP Method
- Path·Query Parameter
- Header와 인증 방식
- Request Body의 구조
- Response Body의 구조
- Status Code와 오류 형식

```text
API 문서 확인
→ URL·Method 결정
→ 인증 정보와 Parameter 구성
→ Request
→ Status Code 확인
→ Response Body 확인
```

## 3. Status Code 읽기

Server는 Response를 보낼 때 Request 처리 결과를 Status Code로 함께 전달한다.

```text
1xx → 정보 / 처리 중
2xx → 성공
3xx → Redirection
4xx → Client 측 오류
5xx → Server 측 오류
```

`200`은 `2xx` 성공 범위에 속하며, HTTP 표준에서 기본적인 성공 Response인 `200 OK`로 정의되어 있다. 숫자 자체에 별도의 계산 원리가 있는 것은 아니다.

같은 성공 범위 안에서도 Code에 따라 의미가 다르다.

| Status Code | 의미 |
| --- | --- |
| `200 OK` | Request가 정상적으로 처리됨 |
| `201 Created` | Request 처리 결과로 새로운 자원이 생성됨 |
| `204 No Content` | Request는 성공했지만 Response Body가 없음 |

### `200 OK`이면 원하는 데이터를 받았다는 뜻인가?

반드시 그렇지는 않다. `200 OK`는 HTTP Request가 정상적으로 처리됐다는 뜻이다. Response Body가 비어 있거나 원하는 조건의 결과가 없을 수도 있으므로 실제 데이터의 내용과 구조는 별도로 확인해야 한다.

```text
Status Code 확인
→ HTTP 처리 성공 여부 확인
→ Response Body 확인
→ 필요한 데이터와 구조가 맞는지 검증
```

## 4. URL 구성 요소

다음 URL을 요소별로 나누어 볼 수 있다.

```text
https://api.example.org/v1/books?q=python&page=1
```

```text
https             → scheme
api.example.org   → host
/v1               → base path
/books            → endpoint
?q=python&page=1  → query
```

- `scheme`: HTTP 또는 HTTPS와 같은 통신 방식
- `host`: Request를 받을 Server
- `base path`: API의 공통 경로나 Version
- `endpoint`: 접근할 자원의 경로
- `query`: 검색이나 필터에 사용할 조건

### Host는 항상 Domain 이름인가?

아니다. 사람이 읽기 쉬운 Domain 대신 IP Address를 직접 사용할 수도 있다.

```text
https://192.168.0.10:8000/books
```

```text
https          → scheme
192.168.0.10   → host(IP Address)
8000           → port
/books         → path
```

`api.example.org` 같은 Domain 이름은 DNS를 통해 실제 Server의 IP Address와 연결된다. URL Path에 숫자나 영문자가 섞인 값이 들어갈 수도 있으며, Server나 특정 자원을 구분하는 ID로 사용될 수 있다.

## 5. Path Parameter와 Query Parameter

Path Parameter는 URL 경로 안에서 특정 자원을 지정한다.

API 문서에 다음과 같이 표시되어 있다고 가정한다.

```text
/books/{book_id}
```

`book_id`가 `123`이라면 실제 Request Path는 다음과 같다.

```text
/books/123
```

Query Parameter는 `?` 뒤에 붙으며 검색·필터·정렬·페이지 같은 조건을 전달할 때 주로 사용한다.

```text
/books/123?lang=ko
```

```text
123
→ Path Parameter
→ 어떤 책인가?

lang=ko
→ Query Parameter
→ 어떤 조건으로 요청할 것인가?
```

Parameter가 필수인지 선택인지는 HTTP 자체가 아니라 각 API 문서의 정의에 따라 달라진다.
