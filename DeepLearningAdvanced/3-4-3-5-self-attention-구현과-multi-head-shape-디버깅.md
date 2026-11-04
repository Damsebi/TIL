# Self-Attention 미니 구현과 Multi-Head Shape 디버깅

> 학습일: 2026-09-02

## 핵심 정리

- Self-Attention의 기본 계산은 `QKᵀ → Scaling → Softmax → Weight × V`다. 교육용 단순 구현에서는 `Q = K = V = X`로 둘 수 있고, 일반적인 Transformer에서는 각각의 Linear Projection으로 Q·K·V를 만든다.
- `transpose(-2, -1)`은 마지막 두 차원을 교환한다. 차원이 하나 늘어나도 Q와 K의 내적에 필요한 K의 마지막 두 축을 바꿀 수 있다.
- PyTorch Tensor에서 `@`와 `torch.matmul()`은 같은 행렬곱 연산을 표현한다. `*`는 원소별 곱셈이다.
- 이 문서처럼 두 입력이 모두 2차원 이상이면 `matmul()`은 마지막 두 차원을 행렬곱 대상으로 사용한다. 앞의 차원은 배치 차원으로 취급하며, 호환되는 경우 Broadcasting을 적용한다.
- 일반적인 동일 차원 Multi-Head Attention에서는 `D_head = D_model / H`다. 따라서 D_model이 Head 개수 H로 나누어떨어져야 한다.
- Head 분리 후 `[B, L, H, D_head]`를 `[B, H, L, D_head]`로 바꿔야 각 Head가 토큰 사이의 관련도 `[L, L]`을 계산한다.
- Head별 Context를 토큰 순서에 맞게 다시 합치면 `[B, L, D_model]`이 되고, 이후 Output Projection으로 Head들의 정보를 혼합한다.
- 디버깅에서는 Shape뿐 아니라 각 축의 의미, Softmax 방향, Head를 합치는 순서도 함께 확인한다.

3-4강의 Tensor 미니 구현과 3-5강의 Multi-Head 차원 흐름을 통합했다. Q·K·V의 역할과 기본 계산은 [3-1~3-3강 정리](3-1-3-3-self-attention-계산과-context-vector.md)에 이어서 읽을 수 있다. 아래 Shape과 코드는 개념을 연결하기 위한 설명용 예시다.

## 1. Tensor로 Self-Attention 미니 구현 — 3-4강

### 가장 단순한 Q = K = V = X

Self-Attention은 Q와 K의 관련도를 계산하고, 그 비율로 V를 가중합하는 연산이다. 우선 입력 X를 Q·K·V로 그대로 사용하는 단순 구현으로 계산 흐름을 확인할 수 있다.

아래는 자료에서 붙어 있던 계산 코드를 줄 단위로 복원하고, 입력을 받는 함수로 묶은 예시다. x는 `[B, L, D]` 형태의 실수 Tensor라고 가정한다.

```python
import torch


def simple_self_attention(x):
    q = k = v = x
    d_k = q.shape[-1]

    scores = q @ k.transpose(-2, -1)
    scores = scores / (d_k ** 0.5)
    weights = torch.softmax(scores, dim=-1)
    context = weights @ v

    return context, weights
```

이 함수는 Mask 없이 Attention의 기본 연산만 보여준다. Q·K·V를 만드는 별도의 학습 가능한 변환은 생략했다. 일반적인 Transformer에서는 서로 다른 Linear Projection으로 Q·K·V를 만든다.

| 단계 | Shape | 의미 |
| --- | --- | --- |
| 입력 및 Q·K·V | `[B, L, D]` | 배치별 L개 토큰, 각 토큰은 D차원 |
| K 전치 | `[B, D, L]` | 내적할 특징 차원의 위치 조정 |
| QKᵀ | `[B, L, L]` | 각 Query와 각 Key의 관련도 |
| Scaling·Softmax | `[B, L, L]` | Key 방향의 참고 비율 |
| Weight × V | `[B, L, D]` | Query마다 만든 Context Vector |

이 단순 구현에서는 Value의 차원을 입력과 같은 D로 두었기 때문에 Context도 입력과 같은 Shape을 갖는다.

### transpose(-2, -1)은 무엇을 바꾸는가?

음수 인덱스는 Tensor의 차원을 뒤에서부터 지정한다.

- `-1`: 마지막 차원
- `-2`: 뒤에서 두 번째 차원

따라서 마지막 두 축을 교환하면 다음과 같다.

```text
[B, L, D]
    ↓ transpose(-2, -1)
[B, D, L]
```

3차원 Tensor에서는 `transpose(1, 2)`와 결과가 같다. 하지만 Head 차원이 추가된 4차원 Tensor에서는 축 번호의 의미가 달라진다.

```text
[B, H, L, D_head]
    ↓ transpose(-2, -1)
[B, H, D_head, L]
```

이 경우 마지막 두 축은 `2`, `3`이다. `transpose(1, 2)`를 쓰면 Head와 토큰 축을 교환하게 된다. 음수 인덱스를 사용하면 Tensor의 차원 수가 바뀌어도 마지막 두 축을 지정할 수 있다.

### @ 대신 torch.matmul()을 쓰는 이유가 있는가?

PyTorch Tensor에서는 다음 두 표현이 같은 행렬곱을 수행한다.

```python
scores_with_operator = q @ k.transpose(-2, -1)
scores_with_function = torch.matmul(q, k.transpose(-2, -1))
```

차이는 주로 표현 방식이다.

| 표현 | 의미 |
| --- | --- |
| `q @ k_transposed` | 수식처럼 간결하게 행렬곱 표현 |
| `torch.matmul(q, k_transposed)` | 함수 이름으로 행렬곱임을 명시 |
| `q * k` | 대응하는 원소끼리 곱셈 |

`matmul()`이 마지막 두 차원으로 행렬곱을 수행한다는 성질이 Multi-Head Attention의 차원 배치를 이해하는 기준이 된다.

## 2. Multi-Head Attention에서 Head 나누기 — 3-5강

### 전체 차원과 Head 차원

Multi-Head Attention은 여러 Head가 서로 다른 표현 공간에서 Attention을 계산하도록 구성한다. 일반적인 구현에서는 입력을 Q·K·V로 각각 선형 변환한 뒤 Head 단위로 나눈다.

이 정리에서는 각 Projection의 출력 차원을 D_model로 두고, H개의 Head에 같은 크기로 나누는 구성을 사용한다.

$$
D_{\text{head}}=\frac{D_{\text{model}}}{H}
$$

| 기호 | 의미 | 예시 값 |
| --- | --- | --- |
| B | Batch Size | 2 |
| L | 토큰 수 | 5 |
| D_model | 전체 Hidden Dimension | 12 |
| H | Head 개수 | 3 |
| D_head | 각 Head의 특징 차원 | 4 |

이 수치는 차원 계산을 설명하기 위한 가정이다. `12 / 3 = 4`이므로 Head 분리 직후 Shape은 다음과 같다.

```text
[B, L, D_model] → [B, L, H, D_head]
[2, 5, 12]     → [2, 5, 3, 4]
```

### 왜 토큰과 Head의 축을 교환하는가?

각 Head에서 토큰 사이의 관계를 계산하려면 마지막 두 차원이 `[L, D_head]`가 되도록 배치해야 한다.

```python
q = q.transpose(1, 2)
```

여기서 `1`, `2`는 0부터 세므로 두 번째와 세 번째 차원을 뜻한다. Head를 분리한 직후의 Tensor에 적용하면 다음과 같다.

```text
[B, L, H, D_head] → [B, H, L, D_head]
[2, 5, 3, 4]     → [2, 3, 5, 4]
```

변경된 구조는 다음처럼 읽을 수 있다.

```text
Batch 1
 ├─ Head 1 → [5, 4]
 ├─ Head 2 → [5, 4]
 └─ Head 3 → [5, 4]

Batch 2
 ├─ Head 1 → [5, 4]
 ├─ Head 2 → [5, 4]
 └─ Head 3 → [5, 4]
```

각 `[5, 4]`는 해당 배치와 Head의 토큰 5개를 담는다. 이렇게 배치하면 B와 H를 구분한 채 각 Head의 토큰 간 Attention을 계산할 수 있다.

## 3. 마지막 두 차원과 Head별 행렬곱

### 올바른 차원 배치

Q와 K를 `[B, H, L, D_head]`로 배치한 뒤 K의 마지막 두 축을 바꾼다.

```text
Q:    [B, H, L, D_head]
Kᵀ:   [B, H, D_head, L]

QKᵀ:  [B, H, L, L]
```

예시 수치를 대입하면 다음과 같다.

$$
[2,3,5,4]\times[2,3,4,5]=[2,3,5,5]
$$

앞의 `[2, 3]`은 Batch와 Head를 구분하는 차원이다. 마지막 `[5, 5]`는 각 Head에서 계산한 Query 토큰 5개와 Key 토큰 5개 사이의 점수다.

Multi-Head Attention에서는 각 Head의 Q·K 특징 차원이 D_head이므로 점수를 `sqrt(D_head)`로 나눈다. Softmax도 각 Query가 참고할 Key 방향인 마지막 차원에 적용한다.

### 축을 바꾸지 않고 바로 곱하면 어떻게 되는가?

Head 분리 직후의 `[B, L, H, D_head]`에서 바로 마지막 두 축을 전치하고 행렬곱하면 다음과 같다.

$$
[2,5,3,4]\times[2,5,4,3]=[2,5,3,3]
$$

이 배치에서는 `[B, L]`을 앞의 배치 차원처럼 취급한다. 마지막 두 축의 곱은 각 토큰 위치에서 Head 3개 사이의 점수를 계산하는 형태가 된다.

행렬곱 자체는 가능하지만, 원하는 Head별 토큰 관계 `[5, 5]`와는 다른 계산이다. 따라서 먼저 `[B, H, L, D_head]`로 순서를 바꿔야 한다.

| 차원 배치 | Score Shape | 계산하는 관계 |
| --- | --- | --- |
| `[B, H, L, D_head]` | `[B, H, L, L]` | Head별 토큰 사이의 관계 |
| `[B, L, H, D_head]` | `[B, L, H, H]` | 토큰별 Head 사이의 점수 |

## 4. Head별 Context 병합과 Output Projection

Weight와 V를 곱하면 각 Head의 Context가 만들어진다.

```text
Attention Weight: [B, H, L, L]
Value:            [B, H, L, D_head]
    ↓ 행렬곱
Context:          [B, H, L, D_head]
```

Head들을 다시 합칠 때는 먼저 토큰 축을 원래 위치로 되돌린다.

```text
[B, H, L, D_head]
    ↓ transpose(1, 2)
[B, L, H, D_head]
    ↓ reshape
[B, L, D_model]
    ↓ Output Projection
[B, L, D_model]
```

아래는 자료의 단계를 연결한 설명용 코드다. x는 `[B, L, D_model]` Tensor이며, `q_proj`, `k_proj`, `v_proj`, `out_proj`는 미리 생성한 `D_model → D_model` 선형 변환이라고 가정한다. Head 개수는 위 예시처럼 3으로 둔다.

```python
B, L, D_model = x.shape
H = 3
assert D_model % H == 0
D_head = D_model // H

q = q_proj(x).reshape(B, L, H, D_head).transpose(1, 2)
k = k_proj(x).reshape(B, L, H, D_head).transpose(1, 2)
v = v_proj(x).reshape(B, L, H, D_head).transpose(1, 2)

scores = torch.matmul(q, k.transpose(-2, -1))
scores = scores / (D_head ** 0.5)
weights = torch.softmax(scores, dim=-1)
context = torch.matmul(weights, v)

merged = context.transpose(1, 2).reshape(B, L, D_model)
output = out_proj(merged)
```

Head를 합칠 때 `transpose(1, 2)` 없이 바로 `[B, L, D_model]`로 바꾸면 Shape은 맞더라도 토큰과 Head의 성분 배치가 달라질 수 있다. 병합 전에 축의 의미를 맞추는 과정이 필요하다.

Output Projection은 합쳐진 Head들의 정보를 다시 선형 변환한다. 위 구성에서는 출력 차원도 D_model로 두므로 최종 Shape이 유지된다. 코드는 Mask·Dropout 등을 생략하고 차원 흐름에 집중한 예시다.

## 5. 전체 Shape 흐름과 디버깅 메모

```text
입력 및 Q·K·V Projection
[B, L, D_model]
    ↓ Head 분리
[B, L, H, D_head]
    ↓ Head와 토큰 축 교환
[B, H, L, D_head]
    ↓ Head별 Q × Kᵀ
[B, H, L, L]
    ↓ Scaling + Key 방향 Softmax
[B, H, L, L]
    ↓ Attention Weight × V
[B, H, L, D_head]
    ↓ 토큰 축을 앞으로 되돌리기
[B, L, H, D_head]
    ↓ Head 병합
[B, L, D_model]
    ↓ Output Projection
[B, L, D_model]
```

| 확인 항목 | 기준 |
| --- | --- |
| Head 분리 조건 | `D_model % H == 0`인지 확인 |
| Q·K·V 축 순서 | `[B, H, L, D_head]`인지 확인 |
| K 전치 | 마지막 두 축만 바뀌는지 확인 |
| Score Shape | `[B, H, L, L]`인지 확인 |
| Scaling 기준 | 각 Head의 Q·K 특징 차원 D_head 사용 |
| Softmax 방향 | Key 방향인 마지막 차원, `dim=-1` 사용 |
| 정규화 결과 | 각 Query의 Key 방향 Weight 합이 1인지 확인 |
| Context Shape | `[B, H, L, D_head]`인지 확인 |
| Head 병합 순서 | `[B, L, H, D_head]`로 되돌린 뒤 병합 |

특히 `[B, L, L]`에서 Query 축은 `dim=1`이지만, `[B, H, L, L]`에서는 `dim=2`다. Head 차원이 추가되면 양수 인덱스의 의미도 달라진다. 축 번호를 외우기보다 각 축이 무엇을 나타내는지 확인해야 한다.

## 현재 이해와 남은 과제

Head를 나누는 과정은 이해했다. Head와 토큰 축을 교환하는 이유, `matmul()`이 마지막 두 차원을 기준으로 계산하는 원리는 대략적으로 이해한 상태다.

Head별 Attention 계산을 위한 Tensor 배치는 아직 완전히 익숙하지 않다. 우선 위의 전체 흐름을 기억하고, 이후 실제 코드를 다룰 때 단계별 Shape을 확인하며 이해를 보완하기로 했다.
