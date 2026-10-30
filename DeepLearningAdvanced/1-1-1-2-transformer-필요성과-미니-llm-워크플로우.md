# RNN·LSTM에서 Transformer로, 미니 LLM 개발 흐름

> 학습일: 2026-09-01

## 핵심 정리

- RNN과 LSTM은 이전 시점의 상태에 의존하므로 시간축의 병렬 처리에 제약이 있다. LSTM은 장기 의존성 문제를 완화하지만 완전히 해결하지는 않는다.
- Transformer는 Self-Attention으로 입력 위치 사이의 관계를 계산한다. 학습 시 입력 위치들을 병렬로 처리할 수 있지만, 자기회귀 생성은 다음 토큰을 순차적으로 만든다.
- 미니 LLM 개발은 `문제 정의 → 데이터 분할 → 토큰화 → 모델 준비 → 학습 → 평가 → 저장`의 흐름으로 이해한다.
- 실습의 `validate_workflow()`는 필수 단계의 누락, 미등록 단계, 중복, 순서를 구분해 검사한다.
- 분류와 생성은 Tokenizer를 공유할 수 있지만 Model Head, 출력 Shape, 평가 기준은 다르다.
- 모델·데이터·Seed·평가 지표·실행 환경을 Manifest에 기록하면 실험 설정과 결과를 함께 추적하기 쉽다.
- 설정을 일정한 방식의 JSON으로 직렬화하고 SHA-256으로 해싱하면 설정 식별자를 만들 수 있다.
- 같은 설정 해시가 실제 학습 결과의 동일성을 보장하지는 않는다. 데이터·모델 버전과 실행 환경도 관리해야 한다.

## 1. RNN·LSTM의 한계와 Transformer의 필요성

기초 13장에서 RNN의 장기 의존성과 LSTM의 Cell State를 학습했다. RNN은 매 시점의 입력과 이전 Hidden State를 이용해 새 상태를 만들기 때문에 오래된 정보가 여러 갱신을 지나면서 영향력을 유지하기 어려울 수 있다.

역전파에서도 미분값이 반복해서 곱해져 Gradient가 지나치게 작아지거나 커질 수 있다. LSTM은 Cell State와 Gate로 기억을 유지·갱신하는 경로를 만들어 이 문제를 완화한다.

하지만 LSTM도 이전 시점의 계산 결과가 있어야 다음 시점을 처리할 수 있다.

```text
RNN / LSTM
이전 상태
→ 현재 상태
→ 다음 상태
→ 시간축의 순차 의존성
```

Transformer는 Self-Attention으로 여러 입력 위치 사이의 관계를 계산한다. RNN처럼 이전 시점의 상태 계산이 끝나야 다음 위치를 처리하는 순환 구조에 의존하지 않아, 학습 시 주어진 입력의 여러 위치를 병렬로 계산할 수 있다.

다만 자기회귀 생성에서는 지금까지의 토큰으로 다음 토큰을 정하고 그 결과를 이어 사용한다. 학습 중 입력 처리의 병렬성과 답변 생성의 순차성은 구분해야 한다.

RNN·LSTM의 세부 기억 구조는 [장기 의존성과 LSTM·Transformer 등장 배경](../DeepLearningBasic/13-3-13-5-장기-의존성과-lstm-transformer-등장-배경.md)에 정리했다.

## 2. 미니 LLM 워크플로우와 단계 검증

```text
문제 정의
→ 데이터 분할
→ 토큰화
→ 모델 준비
→ 학습
→ 평가
→ 저장
```

실습의 `validate_workflow()`는 개발 과정의 단계 구성을 검사한다.

| 검사 항목 | 의미 |
| --- | --- |
| `missing` | 필수 단계 중 빠진 항목 |
| `unknown` | 등록된 단계 이름에 없는 항목 |
| `duplicates` | 중복으로 등장한 단계 |
| `order_ok` | 단계가 기준 순서에 맞게 배치되었는지 |

각 항목은 다른 문제를 확인한다. 순서가 맞는지 확인하는 것만으로 단계 누락이나 미등록 항목까지 검증되는 것은 아니다.

### 리스트 컴프리헨션은 입력 순서를 유지한다

다음은 데이터 분할과 토큰화의 위치가 바뀐 예시다.

```python
REQUIRED = [
    "문제 정의",
    "데이터 분할",
    "토큰화",
    "모델 준비",
    "학습",
    "평가",
    "저장",
]

stages = [
    "문제 정의",
    "토큰화",
    "데이터 분할",
    "모델 준비",
    "학습",
    "평가",
    "저장",
]

projected = [
    stage for stage in stages
    if stage in REQUIRED
]
```

일반 반복문으로 풀면 다음과 같다.

```python
projected = []

for stage in stages:
    if stage in REQUIRED:
        projected.append(stage)
```

`stages`를 순회하면서 등록된 단계만 골라 넣는다. 정렬하는 코드가 아니므로 원래 `stages`의 순서를 유지한다.

기준 순서인 `REQUIRED`에서 현재 등장한 단계만 골라 `expected_present`를 만들면 두 순서를 비교할 수 있다.

```python
expected_present = [
    stage for stage in REQUIRED
    if stage in stages
]

order_ok = projected == expected_present
assert not order_ok
```

이 비교에서는 등장한 단계들의 순서만 확인하므로, 필수 단계의 존재 여부는 `missing` 검사로 따로 확인해야 한다.

## 3. 분류와 생성의 모델·평가 차이

분류와 생성은 입력 텍스트를 토큰화한다는 공통점이 있다. 같은 계열의 모델에서는 Tokenizer를 공유할 수 있지만, 각 모델의 어휘와 입력 규격에 맞아야 한다.

| 구분 | 분류 | 생성 |
| --- | --- | --- |
| 모델 클래스 | `AutoModelForSequenceClassification` | `AutoModelForCausalLM` |
| 출력 역할 | 입력 전체의 클래스 점수 | 각 위치의 다음 토큰 점수 |
| Logits Shape | `[B, C]` | `[B, L, V]` |
| 평가 관점 | Accuracy, Macro-F1 | 생성 품질, Latency |

- B: Batch Size
- C: 클래스 수
- L: 시퀀스 길이
- V: 어휘 크기

Tokenizer가 같더라도 Model Head가 해결하는 문제와 출력 구조가 다르다. 분류의 클래스 점수를 생성 결과처럼 해석하거나 같은 평가 지표를 그대로 적용하면 안 된다.

`[B, L, V]`는 Causal LM의 Forward에서 얻는 Logits Shape다. 이를 이용해 토큰을 선택하는 생성 과정과 최종 토큰 ID 출력은 별도로 구분한다.

## 4. Manifest와 누적 산출물

실험을 다시 확인하려면 모델 파일만 저장하는 것으로는 부족하다. 어떤 조건으로 학습하고 어떤 기준으로 평가했는지도 함께 남겨야 한다.

Manifest는 실험의 설정, 환경, 결과를 추적하기 위한 기록이다.

| 기록 항목 | 확인할 내용 |
| --- | --- |
| 모델 | 모델 이름, 사용한 버전·Revision |
| 데이터 | 데이터셋과 버전, 분할 정보 |
| Seed | 실험에 사용한 난수 설정 |
| 학습 설정 | 비교와 재실행에 필요한 하이퍼파라미터 |
| 평가 | 사용 지표와 측정 결과 |
| 실행 환경 | Python, 라이브러리, 하드웨어 등의 환경 |
| 설정 식별자 | Config Hash와 원본 설정 |

개발 단계별로 남길 수 있는 산출물은 다음과 같다.

| 단계 | 산출물 예시 |
| --- | --- |
| 문제 정의 | 해결할 문제와 평가 목표 |
| 데이터 분할 | Train·Validation·Test 구성 기록 |
| 토큰화 | Tokenizer와 입력 처리 설정 |
| 모델 준비·학습 | 모델 설정과 Checkpoint |
| 평가 | 지표별 결과와 실행 조건 |
| 저장 | 모델·Tokenizer와 Manifest |

산출물을 누적한다는 것은 이전 단계를 덮어 잊는 대신, 마지막 결과가 어떤 데이터와 설정에서 나온 것인지 연결해 보관한다는 의미다.

## 5. 설정 직렬화와 Config Hash

### sort_keys=True의 역할

`json.dumps()`의 `sort_keys=True`는 딕셔너리 Key를 정렬한 JSON 문자열을 만든다.

```python
import json

config = {"seed": 42, "model": "GPT"}

print(json.dumps(config))
# {"seed": 42, "model": "GPT"}

print(json.dumps(config, sort_keys=True))
# {"model": "GPT", "seed": 42}
```

원본 딕셔너리의 순서를 바꾸는 것은 아니다. 입력 순서가 다른 딕셔너리도 같은 Key·값과 직렬화 옵션을 사용하면 같은 JSON 문자열로 만들기 위한 처리다.

여기서 `"GPT"`는 설정 구조를 설명하기 위한 모델 이름 예시다.

### SHA-256 생성 코드

```python
import hashlib

canonical = json.dumps(config, sort_keys=True)
config_hash = hashlib.sha256(
    canonical.encode("utf-8")
).hexdigest()[:12]
```

| 코드 | 역할 |
| --- | --- |
| `canonical` | 일정한 Key 순서로 직렬화한 설정 문자열 |
| `.encode("utf-8")` | 문자열을 UTF-8 바이트 데이터로 변환 |
| `hashlib.sha256()` | 바이트 데이터를 SHA-256으로 해싱 |
| `.hexdigest()` | 해시를 16진수 문자열로 표현 |
| `[:12]` | 앞 12글자를 짧은 설정 식별자로 사용 |

UTF-8은 문자를 바이트로 표현하는 인코딩 방식이다. SHA-256은 바이트를 입력받으므로 문자열을 먼저 인코딩한다.

```text
실험 설정 Dictionary
→ json.dumps(sort_keys=True)
→ 정렬된 JSON 문자열
→ encode("utf-8")
→ 바이트 데이터
→ SHA-256
→ 256비트 Hash
→ hexdigest()
→ 64글자의 16진수 문자열
→ [:12]
→ 12글자의 Config Hash
```

### SHA-256의 256은 글자 수가 아니다

256은 해시의 비트 수다.

```text
256비트 = 32바이트
16진수 한 글자 = 4비트
256 ÷ 4 = 64글자
```

```python
import hashlib

text = "abc"
encoded = text.encode("utf-8")
hashed = hashlib.sha256(encoded)
hash_string = hashed.hexdigest()
config_hash = hash_string[:12]

assert len(hash_string) == 64
assert config_hash == "ba7816bf8f01"
print(config_hash)
```

출력은 `ba7816bf8f01`이다. `[:12]`는 256비트 해시 전체가 아니라 16진수 표현 중 앞 12글자만 가져오는 처리다.

### 설정이 같을 때와 바뀔 때

```python
config1 = {"model": "GPT", "seed": 42}
config2 = {"seed": 42, "model": "GPT"}
config3 = {"model": "GPT", "seed": 7}

canonical1 = json.dumps(config1, sort_keys=True)
canonical2 = json.dumps(config2, sort_keys=True)
canonical3 = json.dumps(config3, sort_keys=True)

assert canonical1 == canonical2
assert canonical1 != canonical3
```

같은 알고리즘에 같은 바이트를 입력하면 같은 해시가 나온다. Key 입력 순서만 다른 두 설정은 같은 해시를 만들고, 위 예시처럼 Seed를 바꾸면 직렬화된 입력과 해시가 달라진다.

암호학적 해시는 결과만으로 원본을 복원하기 어렵도록 설계되지만, 서로 다른 입력이 같은 해시를 갖는 충돌은 이론적으로 가능하다.

특히 12글자로 자른 값은 전체 SHA-256보다 충돌 가능성이 높아 고유성을 보장하지 않는다. 짧은 식별자로 설정을 구분하더라도 원본 설정과 전체 해시를 함께 확인할 수 있어야 한다.

### 같은 Hash면 학습 결과도 같은가?

Config Hash는 해싱에 포함한 설정을 식별하는 값이다. 기록하지 않은 데이터 버전이나 실행 환경의 차이를 알려주지는 못한다.

같은 설정과 Seed라도 실제 실행 환경이나 비결정적 연산 등에 따라 결과가 달라질 수 있으므로, 해시를 학습 결과의 동일성 보장 수단으로 사용해서는 안 된다.

이번 실습의 해시는 암호화나 모델 성능 측정이 아니라 실험 설정의 식별에 사용한다.

## 6. 비트·바이트와 용량 단위

| 단위 | 의미 |
| --- | --- |
| 1 Byte | 8 bit |
| 16진수 한 글자 | 4 bit 표현 |
| 1 KB | 1,000 Byte |
| 1 MB | 1,000 KB |
| 1 GB | 1,000 MB |
| 1 KiB | 1,024 Byte |
| 1 MiB | 1,024 KiB |
| 1 GiB | 1,024 MiB |

4비트는 1바이트가 아니라 반 바이트이며, 16진수 한 글자로 표현할 수 있다. 1,000 기준의 십진 단위와 1,024 기준의 이진 단위는 구분한다.

## 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| SHA-256은 결과 문자열이 256글자다. | 결과는 256비트이며 16진수 문자열로는 64글자다. |
| 4비트가 1바이트이고 4바이트가 1메가바이트다. | 8비트가 1바이트다. KB·MB·GB는 1,000 기준, KiB·MiB·GiB는 1,024 기준이다. |
| 리스트 컴프리헨션으로 골라내면 단계가 정렬된다. | 조건을 만족하는 값만 골라 원래 입력 순서를 유지한다. |
| `sort_keys=True`는 원본 딕셔너리의 순서를 바꾼다. | 정렬된 Key 순서의 JSON 문자열을 생성하며 원본은 변경하지 않는다. |
| 설정 Hash가 같으면 학습 결과도 같다. | 해시는 포함한 설정의 식별자다. 결과 재현에는 데이터·환경 등 추가 조건을 관리해야 한다. |
