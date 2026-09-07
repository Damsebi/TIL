# 장기 의존성과 LSTM·Transformer 등장 배경

> 학습일: 2026-08-31

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 오래된 정보와 Gradient가 시간축을 지나가는 문제

기본 RNN은 현재 입력과 이전 Hidden State로 새로운 Hidden State를 계속 만든다. Sequence가 길어지면 맨 앞에서 본 중요한 정보가 여러 갱신을 거치면서 뒤쪽 결과에 충분한 영향을 주기 어려워질 수 있다. 이것이 **Long-Term Dependency** 문제다.

```text
앞쪽의 중요한 정보
→ 여러 Time Step을 거쳐 Hidden State 갱신
→ 뒤쪽까지 의미와 영향이 충분히 유지되지 않을 수 있음
```

장기 의존성은 순전파 중 앞쪽 값의 숫자가 단순히 작아지는 현상을 뜻하지 않는다. 핵심은 **오래전 정보가 뒤쪽 판단에 필요한데도 그 영향이 제대로 유지되지 않는 것**이다.

학습할 때는 시간축을 거슬러 역전파한다. 이 과정에서 작은 미분값이 반복해서 곱해지면 앞쪽으로 갈수록 Gradient가 매우 작아질 수 있다. 이를 **Gradient Vanishing**이라고 한다.

```text
Gradient Vanishing
→ 앞쪽 시점의 parameter까지 학습 신호가 충분히 전달되지 않음

Gradient Exploding
→ 큰 값이 반복해서 곱해져 Gradient가 지나치게 커짐
```

두 현상은 RNN에만 생기는 것은 아니다. 깊은 MLP나 CNN에서도 발생할 수 있지만, RNN은 긴 Sequence를 시간축으로 펼치면 매우 깊은 계산처럼 이어지므로 특히 중요하다.

### LSTM은 기억을 유지하는 별도의 길을 만든다

LSTM은 기본 RNN의 Hidden State에 **Cell State**를 추가하고, Gate를 이용해 이전 기억과 새로운 정보를 얼마나 반영할지 조절한다.

```text
Forget Gate
→ 기존 Cell State에서 얼마나 유지할지 결정

Candidate Memory
→ 새로 기억할 후보를 만듦

Input Gate
→ 후보 기억을 Cell State에 얼마나 반영할지 결정

Output Gate
→ Cell State의 정보를 현재 Hidden State로 얼마나 드러낼지 결정
```

Forget Gate와 Input Gate는 같은 정보를 두 번 거르는 과정이 아니다.

```text
기존 기억 × Forget Gate
+ 후보 기억 × Input Gate
→ 새로운 Cell State c_t

새로운 Cell State c_t
→ Output Gate로 현재 드러낼 정보 조절
→ 현재 Hidden State h_t
```

Cell State도 모든 Time Step을 지나며 계속 갱신된다. 다만 매번 완전히 새로운 표현으로 바꾸기보다, 기존 정보를 얼마나 유지하고 새 정보를 얼마나 더할지 Gate가 선택할 수 있어 오래된 정보를 보존하기에 기본 RNN보다 유리하다.

1-layer, 단방향 LSTM에서 마지막 상태의 Shape는 다음과 같다.

```text
h_n = (1, B, H)
c_n = (1, B, H)
```

두 상태는 역할은 다르지만 같은 LSTM의 `hidden_size=H`를 사용하므로 마지막 차원의 크기는 같다.

### LSTM의 한계가 Transformer로 연결된다

LSTM은 장기 기억 문제를 완화하지만 완전히 없애지는 못한다. Sequence가 매우 길어지면 오래전 정보를 유지하는 데 여전히 한계가 있다.

또한 RNN과 LSTM은 이전 Time Step의 결과가 있어야 다음 Time Step을 처리할 수 있다.

```text
첫 번째 시점 계산
→ 두 번째 시점 계산
→ 세 번째 시점 계산
→ ...
```

이 순차 처리 구조는 여러 토큰을 동시에 계산하기 어렵게 만들어 병렬화에 불리하다. 오래된 문맥을 유지하기 어렵다는 점과 시간축을 순서대로 처리해야 한다는 점이 이후 Transformer가 등장하게 된 배경으로 연결된다.

### 오답 노트

| 처음 이해 | 수정된 이해 |
| --- | --- |
| 장기 의존성은 순전파하면서 앞의 값 자체가 작아지는 현상이다. | 값의 크기보다 오래전 정보의 의미와 영향이 뒤쪽까지 유지되기 어렵다는 문제다. |
| Candidate Memory는 저장이 확정된 새로운 기억이다. | 새로 저장할 후보이며, Input Gate가 실제 반영량을 결정한다. |
| Forget Gate를 통과한 정보를 Input Gate가 다시 선별한다. | Forget Gate는 기존 기억을, Input Gate는 새로운 후보 기억을 각각 조절한다. |
| Output Gate가 Cell State 자체를 그대로 내보낸다. | Cell State의 정보 중 현재 Hidden State `h_t`로 얼마나 드러낼지 조절한다. |

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 역전파하면 Gradient가 점점 작아지는가?

항상 작아지는 것은 아니다. 시간축을 따라 역전파할 때 작은 미분값이 반복해서 곱해지는 조건에서는 Sequence가 길수록 Gradient가 0에 가까워질 수 있다.

반대로 반복해서 곱해지는 값이 크면 Gradient가 지나치게 커질 수도 있다. 중요한 점은 역전파 자체가 언제나 Gradient를 작게 만드는 것이 아니라, **연결된 미분값들의 반복적인 곱이 크기에 영향을 준다**는 것이다.

---

### 질문: 다른 신경망에서도 Gradient Vanishing이 발생하는가?

발생할 수 있다. 깊은 MLP나 CNN도 많은 연산을 거슬러 Gradient를 전달하므로 같은 문제가 생길 수 있다.

RNN은 같은 구조를 여러 Time Step에 반복 적용하며, 긴 Sequence를 펼쳐 보면 깊은 신경망처럼 계산이 길게 이어지기 때문에 Gradient Vanishing이 특히 중요한 문제다.

---

### 질문: 미분값이 커질 수도 있는가?

미분값이 반드시 1보다 작은 것은 아니다. 큰 값이 시간축을 따라 반복해서 곱해지면 Gradient가 급격히 커질 수 있으며, 이를 Gradient Exploding이라고 한다.

```text
작은 값이 반복해서 곱해짐
→ Gradient Vanishing

큰 값이 반복해서 곱해짐
→ Gradient Exploding
```

---

### 질문: Candidate Memory가 새로 기억할 정보라면 이미 확정된 것 아닌가?

아니다. Candidate Memory는 이름 그대로 새롭게 저장할 **후보 정보**다. Input Gate가 후보의 각 정보를 Cell State에 얼마나 반영할지 결정해야 실제 기억 갱신에 사용된다.

```text
Candidate Memory
→ 무엇을 새로 기억할지 제안

Input Gate
→ 그 후보를 얼마나 반영할지 조절
```

---

### 질문: Hidden State와 Cell State는 같은 Time Step 수를 지나는데 왜 Cell State가 더 오래 기억할 수 있는가?

두 상태가 지나가는 Time Step 수는 같다. 차이는 Cell State가 Gate를 통해 기존 정보를 선택적으로 유지하고 새로운 정보를 더하는 경로로 설계됐다는 점이다.

따라서 지나가는 거리가 짧아서가 아니라, **정보를 갱신하고 전달하는 방식이 다르기 때문에** 기본 RNN의 Hidden State보다 장기 정보를 보존하기 유리하다.

---

### 질문: Cell State도 결국 변형되는가?

그렇다. Cell State도 Forget Gate와 Input Gate에 의해 매 Time Step 갱신되므로 완전히 같은 값으로 보존되지는 않는다.

다만 학습을 통해 기존 정보 중 무엇을 남기고 후보 정보 중 무엇을 추가할지 조절할 수 있다는 것이 핵심이다.

---

### 질문: `h_n`과 `c_n`의 H 크기는 같은가?

같다. 같은 LSTM에 설정한 `hidden_size=H`를 사용하므로 1-layer, 단방향 기준 두 Tensor의 Shape는 모두 `(1, B, H)`다.

```text
h_n
→ 마지막 Hidden State

c_n
→ 마지막 Cell State
```

역할은 다르지만 마지막 차원의 크기는 같다.
