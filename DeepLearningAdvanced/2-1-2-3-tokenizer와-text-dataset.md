# Tokenizer와 Text Dataset

> 학습일: 2026-09-01

## 핵심 정리

- Tokenizer는 문자열을 토큰으로 나누고, Vocabulary에 정의된 정수 ID로 변환한다. Subword는 단어보다 작은 조각을 재사용해 어휘 크기와 입력 길이 사이의 균형을 잡는다.
- Vocabulary 크기는 등록된 토큰의 종류 수이고, Sequence 길이는 한 입력을 표현하는 데 사용한 토큰 수다. 같은 토큰이 반복되어도 어휘에 중복 등록되는 것은 아니다.
- Vocabulary는 토큰과 ID의 대응 관계를, Embedding Table은 각 ID에 대응하는 학습 가능한 벡터를 저장한다.
- `encode()`는 문자열을 ID로, `decode()`는 ID를 문자열로 변환한다. 토큰화의 `encode`와 Transformer Encoder의 역할은 다르다.
- 길이를 맞춘 배치의 `input_ids`와 `attention_mask`는 일반적으로 `(B, L)`, Embedding 출력은 `(B, L, D)` 형태다.
- Padding은 부족한 위치를 채우고, Truncation은 최대 길이를 넘는 입력을 자른다. `max_length`를 정했다고 모든 입력이 그 길이로 채워지는 것은 아니다.
- `DatasetDict`는 데이터 분할을 묶어 관리하고, `map(batched=True)`는 여러 행을 전처리한다. `DataCollatorWithPadding`은 실제 학습 배치를 구성할 때 동적 Padding을 수행한다.
- 아래의 토큰 분할, ID·벡터 값, 길이 분포 수치는 개념 설명을 위한 예시다. 실제 Tokenizer 출력이나 데이터셋의 측정 결과와 구분한다.

## 1. NLP 데이터 구조와 Token·Subword — 2-1강

### 문자열에서 Token ID까지

모델은 원본 문자열을 그대로 입력받아 계산하는 대신, 토큰화된 정수 ID를 사용한다.

| 개념 | 의미 |
| --- | --- |
| Token | 문자열을 처리하기 위해 나눈 단위 |
| Vocabulary | 토큰과 정수 ID의 대응 관계를 저장한 어휘 사전 |
| Tokenizer | 문자열을 토큰으로 분할하고 ID로 변환하는 도구 |
| Subword | 단어보다 작은 조각을 재사용하는 토큰화 방식 |

Subword는 모든 단어를 각각 등록하는 대신 단어의 일부를 조합해 표현할 수 있게 한다. 이때 어휘에 얼마나 다양한 조각을 등록할지와, 한 입력을 몇 개의 토큰으로 표현할지를 함께 고려한다.

토큰화 전에 데이터의 빈 값, 중복, 잘못된 Label 등을 확인해야 한다. 텍스트를 ID로 바꾸는 것만으로 데이터 품질 문제가 해결되지는 않는다.

### Vocabulary 크기와 Sequence 길이는 어떻게 다른가?

처음에는 문자열을 잘게 나누면 토큰이 많아지므로 Vocabulary도 커지고, Vocabulary가 커질수록 Sequence 길이도 길어진다고 생각했다.

하지만 두 값은 세는 대상이 다르다.

- **Vocabulary 크기**: 사전에 등록된 서로 다른 토큰의 종류 수
- **Sequence 길이**: 특정 입력을 표현하는 데 실제로 사용한 토큰의 개수

`설치파일설치파일`을 나누는 상황을 가정하면 다음과 같다.

| 구분 | Vocabulary A | Vocabulary B |
| --- | --- | --- |
| 등록된 토큰 | `설치`, `파일` | `설치`, `파일`, `설치파일` |
| Vocabulary 크기 | 2 | 3 |
| 토큰화 결과 | `[설치, 파일, 설치, 파일]` | `[설치파일, 설치파일]` |
| Sequence 길이 | 4 | 2 |

이 예시는 긴 토큰을 우선 사용하는 분할 규칙을 가정한다. 다양한 긴 문자열이 어휘에 등록되면 같은 문장을 더 적은 토큰으로 표현할 수 있지만, 실제 결과는 Tokenizer의 알고리즘과 분할 규칙에도 영향을 받는다.

Vocabulary가 크다는 말은 모든 토큰을 무조건 크게 자른다는 뜻이 아니다. 더 다양한 토큰을 등록할 수 있다는 의미다. 또한 이미 학습된 Tokenizer에 새 문장을 입력하는 것만으로 Vocabulary가 일반적으로 바뀌지는 않는다.

### Vocabulary와 입력 길이의 Trade-off

Trade-off는 한쪽의 이득을 얻는 대신 다른 쪽의 비용을 감수하는 관계다. 같은 Embedding 차원 등 다른 조건을 고정했을 때, 어휘 크기와 입력 길이에는 다음과 같은 경향이 있다.

| 구분 | Vocabulary가 작을 때 | Vocabulary가 클 때 |
| --- | --- | --- |
| 등록된 토큰 종류 | 적음 | 많음 |
| 같은 입력의 Sequence 길이 | 길어질 가능성 | 짧아질 가능성 |
| Embedding 파라미터 수 | 적음 | 많음 |
| 어휘 크기에 따른 가중치 메모리 부담 | 상대적으로 적음 | 상대적으로 많음 |

어휘를 크게 하면 입력 길이를 줄일 가능성이 있지만, 저장하고 학습할 파라미터는 늘어난다. 따라서 Vocabulary를 무조건 늘리거나 줄이기보다 모델의 메모리 부담과 Sequence 처리 비용을 함께 고려해야 한다.

### Embedding 파라미터는 왜 늘어나는가?

Vocabulary와 Embedding Table은 서로 다른 구조다. 다음은 설명을 위해 임의로 정한 값이다.

```text
Vocabulary
설치 → 0
파일 → 1
시험 → 2

Embedding Table
ID 0 → [0.2, 0.5, 0.1]
ID 1 → [0.8, 0.1, 0.4]
ID 2 → [0.3, 0.9, 0.2]
```

Embedding Table에는 각 Token ID에 대응하는 학습 가능한 벡터가 저장된다. Vocabulary 크기를 V, Embedding 차원을 D라고 하면 다음과 같다.

$$
\text{Embedding 파라미터 수} = V \times D
$$

예를 들어 `V = 50,000`, `D = 768`이라면 다음과 같다.

- Embedding Table Shape: `(50000, 768)`
- 파라미터 수: `50,000 × 768 = 38,400,000`개

다만 입력을 처리할 때는 해당 Token ID의 벡터를 조회한다. Vocabulary가 커진다고 Embedding 조회 연산량까지 같은 비율로 늘어나는 것은 아니다.

## 2. AutoTokenizer와 모델 입력 필드 — 2-2강

### tokenize·encode·decode 구분

`AutoTokenizer`는 모델의 설정에 맞는 Tokenizer를 불러오는 기능이다.

| 기능 | 역할 |
| --- | --- |
| `tokenizer.tokenize()` | 문자열을 토큰으로 분할 |
| `tokenizer.encode()` | 문자열을 Token ID로 변환 |
| `tokenizer.decode()` | Token ID를 다시 문자열로 변환 |
| `tokenizer()` | `input_ids`, `attention_mask` 등 모델 입력 필드 생성 |

처음에는 `encode()`가 ID를 문장으로 복원하는 함수라고 혼동했다. 문자열을 ID로 바꾸는 것이 `encode()`, ID를 문자열로 되돌리는 것이 `decode()`다. 다만 정규화나 특수 토큰 처리 등에 따라 복원된 문자열이 원문과 완전히 같지는 않을 수 있다.

### Vocabulary와 Embedding Layer의 역할

| 구분 | 저장하거나 수행하는 일 |
| --- | --- |
| Vocabulary | 토큰과 정수 ID의 대응 관계 저장 |
| Tokenizer | 문자열을 Token ID로 변환 |
| Embedding Table | Token ID별 학습 가능한 벡터 저장 |
| Embedding Layer | 입력 ID에 대응하는 벡터를 Table에서 조회 |

```text
원본 문자열
    ↓ Tokenizer: 분할과 ID 변환
Token ID
    ↓ Embedding Layer: 벡터 조회
Embedding 벡터
```

Vocabulary 안에 Embedding 벡터까지 들어 있는 것은 아니다. 벡터는 모델의 Embedding Table에 있으며, 학습 과정에서 값이 조정된다.

### encode와 Transformer Encoder는 같은가?

`encode`는 '인코드', `encoder`는 '인코더'라고 읽지만, 여기서 수행하는 일은 다르다.

- `tokenizer.encode()`: 문자열을 정수 ID로 변환하는 함수
- Transformer Encoder: 입력 벡터들 사이의 관계를 계산해 문맥이 반영된 표현을 만드는 신경망 구조

토큰화가 끝났다고 문맥을 반영하는 신경망 계산까지 끝난 것은 아니다.

### 여러 문장의 토큰화와 Batch Shape

문장 두 개를 배치로 토큰화한다는 것은 두 문장을 이어 붙여 하나로 처리한다는 뜻이 아니다. 각각 토큰화하므로 길이가 다를 수 있다.

```text
문장 A → [101, 200, 300, 102]
문장 B → [101, 400, 102]
```

이를 하나의 배치 텐서로 묶으려면 길이를 맞춰야 한다. PAD ID를 `0`으로 가정하고 짧은 문장에 Padding을 적용하면 다음과 같다.

```text
input_ids:
[
  [101, 200, 300, 102],
  [101, 400, 102,   0]
]

Shape = (2, 4)
```

| 기호 | 의미 |
| --- | --- |
| B | Batch Size, 한 번에 처리하는 입력 수 |
| L | Sequence Length, 길이를 맞춘 뒤 각 입력의 토큰 수 |
| D | Embedding Dimension, 각 토큰 벡터의 차원 |

Embedding 차원이 768이라면 Shape는 다음과 같이 바뀐다.

```text
input_ids:        (2, 4)
    ↓ Embedding
Embedding 출력:   (2, 4, 768)
```

이 `(B, L)` 표기는 길이를 맞춰 배치 텐서로 만든 경우다. Padding 전의 토큰화 결과는 입력별 길이가 다른 리스트일 수 있다.

## 3. Padding·Truncation·Attention Mask — 2-3강

### PAD ID만 넣으면 모델이 알아서 무시하는가?

직접 Padding을 구현할 경우 PAD ID를 넣는 것만으로 모델이 해당 위치를 구분할 수 있는지 질문했다.

`input_ids`는 어떤 토큰인지를 나타내고, `attention_mask`는 어떤 위치가 실제 입력인지를 나타낸다. PAD ID를 `0`으로 가정한 예시는 다음과 같다.

```text
input_ids:
[
  [101, 200, 300, 102],
  [101, 500, 102,   0]
]

attention_mask:
[
  [1, 1, 1, 1],
  [1, 1, 1, 0]
]
```

일반적인 Tokenizer의 Padding Mask에서는 `1`이 실제 토큰, `0`이 PAD 위치를 의미한다. 두 필드는 배치 텐서 기준으로 같은 `(B, L)` 형태를 가진다.

직접 Padding을 구현한다면 원본 Sequence 길이를 기준으로 Mask도 함께 만들어야 한다. 일부 모델이나 도구가 PAD 처리를 자동화할 수 있어도 모든 모델이 PAD ID만 보고 적절히 처리한다고 가정하면 안 된다. Hugging Face의 Tokenizer와 Data Collator는 Padding과 Mask 생성을 편리하게 처리하도록 지원한다.

### max_length를 정하면 항상 잘리는가?

Truncation은 설정한 최대 길이를 초과하는 토큰을 자르는 작업이다. `truncation=True`여도 입력이 충분히 짧으면 실제로 잘리는 부분은 없다.

원본 토큰 길이가 300이라고 가정하면 다음과 같다. 여기서는 특수 토큰 등 추가 조건 없이 길이 제한만 비교한다.

| 설정 | 결과 |
| --- | --- |
| `max_length=128` | 최대 128개로 절단 |
| `max_length=256` | 최대 256개로 절단 |
| `max_length=512` | 절단 없음 |

또한 `max_length=512`를 정했다고 모든 입력을 512개 토큰으로 채우는 것은 아니다. Padding은 별도로 설정한다.

### 동적 Padding과 고정 길이 Padding

- 동적 Padding: 현재 배치에서 가장 긴 Sequence에 맞춰 부족한 위치를 채운다.
- 고정 길이 Padding: 지정한 길이에 맞춰 부족한 위치를 채운다.

Hugging Face Tokenizer에서 `padding=True`는 전달된 배치의 가장 긴 길이에, `padding="max_length"`는 설정한 최대 길이에 맞추는 데 사용한다. `DataCollatorWithPadding`을 사용하면 실제 학습 배치를 구성할 때 동적 Padding을 적용할 수 있다.

데이터셋 전체의 가장 긴 입력 길이와 현재 배치의 가장 긴 입력 길이는 구분해야 한다. 동적 Padding에서는 배치 구성에 따라 L이 달라질 수 있다.

### max_length=512는 데이터의 평균 길이인가?

처음에는 512라는 값이 데이터 대부분의 길이가 512라는 의미인지 궁금했다. 하지만 이 값은 평균 길이가 아니라 입력을 최대 512개 토큰으로 제한한다는 뜻이다.

BERT처럼 최대 512개 토큰을 지원하도록 설계된 모델이 있어 자주 보이지만, 모든 모델의 공통 기본값은 아니다. 다음 조건을 함께 확인해야 한다.

1. 모델이 지원하는 최대 입력 길이
2. 실제 데이터의 토큰 길이 분포
3. 절단되는 정보의 양과 중요성
4. Validation 성능
5. 메모리 사용량과 계산 비용

다음은 학습 데이터의 길이 분포를 설명하기 위해 **가정한 수치**다.

| max_length | 절단되지 않는 데이터 비율 |
| --- | --- |
| 128 | 90% |
| 256 | 98% |
| 512 | 99.5% |

이 가정에서는 256이 데이터의 98%를 절단 없이 보존하면서 최대 입력 길이를 제한하는 후보가 된다. 실제 선택은 잘리는 내용의 중요성과 Validation 성능, 메모리 사용량까지 확인한 뒤 해야 한다.

일반적인 전체 Self-Attention에서 토큰 간 관계를 계산하는 비용은 Sequence 길이의 제곱에 비례한다. 따라서 더 긴 입력을 허용하면 계산 부담도 커질 수 있다.

## 4. Dataset과 전처리·학습 배치 연결 — 2-3강

### Dataset과 DatasetDict

`Dataset`은 개별 데이터셋을 관리하는 객체이고, `DatasetDict`는 여러 Dataset을 딕셔너리 형태로 묶는 자료구조다.

아래는 `train`, `validation`, `test`가 이미 각각의 Dataset으로 준비되어 있다고 가정한 구성 예시다.

```python
from datasets import DatasetDict

dataset = DatasetDict({
    "train": train,
    "validation": validation,
    "test": test,
})
```

`DatasetDict` 자체가 데이터를 자동으로 분할하거나 토큰화하지는 않는다. 이미 분리된 Dataset을 묶어 관리하고 같은 전처리를 적용하기 쉽게 해준다.

### map(batched=True)의 batch["text"]는 무엇인가?

다음은 `tokenizer`가 준비되어 있고 데이터셋에 `text` 열이 있다고 가정한 전처리 함수다.

```python
def preprocess(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding=False,
    )
```

`batch`는 `map()`이 함수에 전달하는 데이터 묶음이다. `batched=True`일 때의 구조를 단순화하면 다음과 같다.

```python
batch = {
    "text": ["금리 인상", "대표팀 결승 진출"],
    "label": [0, 1],
}

batch["text"]
# ["금리 인상", "대표팀 결승 진출"]
```

`batch["text"]`는 특별한 Tokenizer 문법이 아니라 일반적인 Python 딕셔너리 접근 문법이다.

| map 설정 | 전처리 함수에 전달되는 값 |
| --- | --- |
| `batched=True` | 여러 행을 열별 리스트로 묶은 값 |
| `batched=False` | 한 행의 값 |

### 전처리 배치와 학습 배치는 다르다

전처리할 때 여러 행을 묶는 것과, 모델에 한 번에 넣을 학습 배치를 만드는 것은 별개다. 위 객체가 준비되어 있다는 전제에서 연결하면 다음과 같다.

```python
from transformers import DataCollatorWithPadding

tokenized_dataset = dataset.map(preprocess, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
```

```text
DatasetDict: train / validation / test 관리
    ↓ map(batched=True)
여러 행을 묶어 토큰화, 이 단계에서는 padding=False
    ↓ 실제 학습 배치 구성 시 DataCollatorWithPadding 호출
현재 배치의 가장 긴 입력에 맞춰 Padding과 Mask 구성
    ↓
모델 입력
```

Collator 객체를 만드는 것만으로 Padding이 바로 실행되지는 않는다. 실제 배치를 구성하는 DataLoader나 Trainer에 연결해 호출할 때 적용된다. 이 코드는 각 도구의 연결 관계를 보여주는 예시이며, 전체 학습 코드는 아니다.

### Token ID와 Label ID 구분

분류 문제의 정답 클래스도 정수 ID로 표현할 수 있다.

```python
label2id = {
    "경제": 0,
    "스포츠": 1,
    "IT": 2,
}

id2label = {
    0: "경제",
    1: "스포츠",
    2: "IT",
}

id2label[2]
# "IT"
```

- `label2id`: 클래스 이름을 정수 ID로 변환
- `id2label`: 정수 ID를 클래스 이름으로 복원

Token ID는 입력 텍스트의 토큰을, Label ID는 분류 문제의 정답 클래스를 가리킨다. 둘 다 정수로 표현하더라도 서로 다른 ID 체계다.

## 5. Hugging Face 도구의 역할과 의존 범위

### Hugging Face Dataset 없이도 전처리할 수 있는가?

공공데이터셋을 직접 전처리할 수 있는지 질문했다. 데이터 전처리는 Hugging Face에 종속된 작업이 아니다.

| 도구 | 주요 역할 |
| --- | --- |
| Python | 기본적인 데이터 가공 |
| pandas | 표 형태 데이터 정제와 처리 |
| scikit-learn | 데이터 분리, 전처리, 머신러닝 학습과 평가 |
| PyTorch | 텐서 처리와 딥러닝 모델 학습 |
| Hugging Face datasets | 데이터셋 관리와 변환 |

예를 들어 공공데이터를 pandas로 정제하고, scikit-learn으로 분리한 뒤 PyTorch로 학습할 수도 있다. Hugging Face는 이 과정을 편리하게 수행하도록 돕는 선택지 중 하나다.

### 외부 모델 사용과 온라인 서비스 의존성

Hugging Face 외부의 모델을 사용하거나 온라인 서비스가 종료되더라도 기존 기능을 사용할 수 있는지 궁금했다. 이를 이해하려면 서비스, 라이브러리, 파일을 구분해야 한다.

| 구분 | 역할과 의존 범위 |
| --- | --- |
| Hugging Face Hub | 모델과 데이터셋을 공유하는 온라인 서비스 |
| 오픈소스 라이브러리 | 로컬 환경에서도 실행할 수 있는 코드 |
| 모델·Tokenizer 파일 | 내려받아 로컬에 보관할 수 있는 실행 자료 |

필요한 코드와 파일이 로컬에 준비된 기능은 온라인 Hub 접근과 구분해서 생각할 수 있다. 다만 원격 파일을 새로 내려받아야 하는 기능까지 인터넷 없이 동작한다는 뜻은 아니다.

Hugging Face 외부의 모델에도 `datasets`를 활용할 수 있지만, `AutoTokenizer` 등의 사용 여부는 모델과 라이브러리의 호환성에 따라 달라진다. Hugging Face를 사용하지 않더라도 Padding과 Attention Mask 같은 기본 처리는 직접 구현할 수 있다.

## 6. 학습 중 이해 점검

동적 Padding 이해 점검에서는 다음 두 입력에 대한 결과를 올바르게 구했다.

```text
문장 A: [10, 20, 30, 40, 50]
문장 B: [10, 20, 30]
```

현재 배치의 가장 긴 길이는 5이므로 다음과 같다.

- `input_ids.shape = (2, 5)`
- 문장 B의 `attention_mask = [1, 1, 1, 0, 0]`

또한 `label2id`에서 `"IT": 2`로 정의하고 역방향 매핑을 만들었다면 `id2label[2]`는 `"IT"`라는 점을 확인했다.

이 내용은 학습 중 풀이한 이해 점검이며, 실제 모델 학습이나 데이터셋 성능 측정 결과는 아니다.

## 남은 의문

- `max_length`에 128, 256, 512처럼 2의 거듭제곱이 자주 사용되는 기술적 배경은 무엇인가? 질문은 했지만 이번 학습에서는 구체적인 이유까지 정리하지 못했으므로 추가 확인이 필요하다.

## 오답 노트

| 처음 이해하거나 혼동한 내용 | 수정된 이해 |
| --- | --- |
| Vocabulary가 커지면 더 잘게 나누므로 Sequence 길이도 길어진다. | Vocabulary는 토큰의 종류 수다. 긴 토큰을 등록하고 사용하는 경우 같은 입력을 더 적은 토큰으로 표현할 수 있다. 실제 결과는 분할 규칙에도 달려 있다. |
| `encode()`가 ID를 문장으로 바꾼다. | `encode()`는 문자열 → ID, `decode()`는 ID → 문자열 변환이다. |
| Vocabulary에 Token ID와 Embedding 벡터가 함께 저장된다. | Vocabulary는 토큰과 ID를 연결하고, Embedding Table이 ID별 벡터를 저장한다. |
