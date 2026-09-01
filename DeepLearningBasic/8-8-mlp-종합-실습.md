# MLP 종합 실습

> 학습일: 2026-08-26

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

8장에서 배운 요소들을 다음과 같은 하나의 학습 파이프라인으로 연결했다.

```text
TensorDataset
→ DataLoader
→ MLP
→ Loss·Optimizer
→ Train Loop
→ Epoch별 Loss를 History에 저장
→ Report 작성
```

입력 `x.shape`이 `(40, 4)`라면 `40`은 Batch에 들어 있는 Sample 수이고 `4`가 Sample 하나의 Feature 수다. 따라서 첫 Linear는 `in_features=4`를 사용한다.

이번 예제의 정답은 Class `0`, `1`이므로 Cross Entropy 방식의 Model은 Sample마다 두 개의 Logit을 출력한다. 단순히 Layer를 순서대로 통과하는 구조는 `nn.Sequential`로 묶었다.

```python
from torch import nn

model = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)
```

DataLoader의 각 Batch에서 Prediction과 Loss를 계산하고 `zero_grad → backward → step`으로 Parameter를 수정한다. Epoch Loss를 `history`에 계속 저장하면 학습 중 가장 작은 Loss와 마지막 Loss를 구분해 Report로 만들 수 있다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: 입력과 정답을 DataLoader에 함께 전달하기

#### 처음 시도

입력 `x`만 DataLoader에 넣었다.

```python
loader = DataLoader(x, batch_size=40, shuffle=True)
```

이 구조에서는 반복문에서 입력과 정답을 `bx, by`로 함께 받을 수 없다.

#### 수정된 이해

먼저 `TensorDataset`으로 같은 Index의 입력과 정답을 묶은 뒤 DataLoader에 전달한다.

```python
dataset = TensorDataset(x, y)
loader = DataLoader(dataset, batch_size=40, shuffle=True)
```

이제 각 Batch에서 `bx`, `by`를 함께 받을 수 있다.

---

### 이해 수정: `nn.Linear`의 입력 크기

#### 처음 시도

`x.shape == (40, 4)`의 `40`을 첫 Linear의 입력 크기로 사용하려고 했다.

```python
nn.Linear(40, 40)
```

#### 수정된 이해

`nn.Linear`의 `in_features`는 Batch Size가 아니라 **Sample 하나에 들어 있는 Feature 수**다.

```text
x.shape = (40, 4)
           ↑   ↑
         Batch Feature
```

따라서 이번 Model은 `4개 입력 Feature → Hidden Layer → 2개 Class Logit`으로 연결한다.

---

### 이해 수정: MLP Layer 연결

#### 처음 시도

같은 속성인 `self.net`에 두 Linear를 차례로 대입했다.

```python
self.net = nn.Linear(4, 2)
self.net = nn.Linear(2, 2)
```

두 번째 대입이 첫 번째 Layer를 덮어쓰므로 두 Layer가 연결되는 코드가 아니다. 또한 정확한 클래스 이름은 `nn.Relu()`가 아니라 `nn.ReLU()`다.

#### 수정된 이해

여러 Layer를 일렬로 실행하는 이번 구조에서는 `nn.Sequential`을 사용하면 선언한 순서대로 Forward가 실행된다.

```python
self.net = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)

def forward(self, x):
    return self.net(x)
```

Layer를 속성으로 선언만 하는 것이 아니라 Forward에서 입력을 실제로 통과시켜야 한다.

---

### 이해한 내용: Optimizer Update 순서

다음 세 호출의 역할을 구분했다.

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

- `zero_grad()`: 이전 Gradient 초기화
- `backward()`: 현재 Loss에 대한 Gradient 계산
- `step()`: Gradient를 이용해 Parameter 수정

Prediction과 Loss를 먼저 계산한 뒤, 새로운 `backward()` 전에 이전 Gradient를 비우고 Parameter를 업데이트한다.

---

### 이해한 내용: `history`로 Report 만들기

```python
history = [0.9, 0.7, 0.62, 0.58]

report = {
    "best_loss": min(history),
    "final_loss": history[-1],
    "config": config,
}
```

- `best_loss`: 해당 History에서 가장 작은 Loss
- `final_loss`: 마지막 Epoch에 기록한 Loss

History가 Train Loss를 저장한 목록이라면 `best_loss`도 가장 작은 **Train Loss**다. Best Validation Model을 고르려면 Validation History와 해당 시점의 Model 상태를 기준으로 봐야 한다.
