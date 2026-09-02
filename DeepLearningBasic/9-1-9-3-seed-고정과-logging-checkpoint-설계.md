# Seed 고정과 Logging·Checkpoint 설계

> 학습일: 2026-08-27

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

딥러닝 실험은 모델의 초기 weight, 난수, DataLoader의 shuffle처럼 랜덤하게 결정되는 요소가 많다. 같은 코드를 다시 실행해도 결과가 달라질 수 있으므로, 실험을 비교하려면 먼저 이런 랜덤 요소를 최대한 같은 조건으로 맞춰야 한다.

재현성은 모든 결과를 무조건 완전히 똑같게 만드는 것이라기보다, 랜덤 요소를 통제해 같은 조건에서 비슷한 결과를 다시 얻을 수 있게 하는 것이다. Python, NumPy, PyTorch의 seed는 다음처럼 한 함수에서 함께 고정할 수 있다.

```python
import random
import numpy as np
import torch


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
```

모델의 weight와 bias는 모델을 생성하는 순간 초기화되므로 seed는 모델 생성 전에 고정해야 한다.

```text
Seed 고정
→ 모델 생성
→ Weight와 Bias 초기화
→ 학습
```

학습 DataLoader의 shuffle 순서도 재현하려면 별도의 Generator에 seed를 지정할 수 있다.

```python
from torch.utils.data import DataLoader

SEED = 40
set_seed(SEED)

model = MLP()

shuffle_generator = torch.Generator().manual_seed(SEED)

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True,
    generator=shuffle_generator,
)

valid_loader = DataLoader(
    valid_dataset,
    batch_size=32,
    shuffle=False,
)
```

Validation은 보통 `shuffle=False`이므로 shuffle 순서를 위한 Generator가 필요하지 않다. 또한 같은 seed를 사용해도 PyTorch·CUDA 버전이나 CPU/GPU 연산 방식이 다르면 결과가 완전히 같지 않을 수 있다.

Seed를 고정했다면 실험이 끝난 뒤에도 **어떤 조건에서 어떤 결과가 나왔는지** 확인할 수 있어야 한다. 기존의 `history` dictionary는 실행 중인 메모리에 metric을 보관하므로 프로그램이나 런타임이 종료되면 사라질 수 있다. 이를 파일에 남기는 것이 logging이다.

```text
config.json
→ 어떤 조건으로 실험했는가

metrics.csv
→ 그 조건에서 어떤 결과가 나왔는가
```

`config.json`에는 seed, learning rate, batch size, optimizer, 모델 구조처럼 실험 전에 정한 설정을 저장한다. 설정은 항목별·계층적으로 표현할 수 있으므로 JSON이 잘 맞는다.

```json
{
  "seed": 40,
  "learning_rate": 0.001,
  "batch_size": 32,
  "optimizer": "Adam",
  "model": {
    "name": "MLP",
    "hidden_dim": 128
  }
}
```

`metrics.csv`에는 각 epoch이 끝날 때 측정한 train/validation loss와 accuracy 등을 같은 column 구조로 한 행씩 기록한다.

```csv
epoch,train_loss,train_acc,valid_loss,valid_acc
1,0.68,0.61,0.65,0.64
2,0.54,0.73,0.57,0.70
```

Print Log는 학습 중 현재 상태를 바로 확인하기 위한 것이고, File Log는 학습이 끝난 뒤에도 결과를 보존하고 비교하기 위한 것이다. `config.json`과 `metrics.csv`를 함께 보면 실험 조건과 결과를 연결할 수 있다.

Logging이 실험을 사람이 확인하기 위한 기록이라면, checkpoint는 중단된 학습을 다시 이어가기 위한 **학습의 save point**에 가깝다.

`state_dict`는 객체의 현재 상태값을 담은 Python dictionary이다.

```text
model.state_dict()
→ Weight, Bias 등 모델의 학습된 상태

optimizer.state_dict()
→ Learning Rate, Step 수, Adam 내부 누적 상태 등
```

`model.state_dict()`에는 모델 클래스나 `forward()` 코드가 들어 있지 않다. 따라서 저장된 상태를 불러오려면 먼저 같은 모델 구조를 생성해야 한다.

학습 재개에 필요한 상태는 checkpoint dictionary 하나로 묶어 `.pth` 파일로 저장할 수 있다.

```python
checkpoint = {
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "completed_epochs": 5,
    "history": history,
    "config": config,
}

torch.save(checkpoint, "checkpoint.pth")
```

`completed_epochs`는 완전히 끝난 epoch의 개수다. 값이 `5`라면 5 epoch까지 끝났다는 뜻이므로 다음 학습은 6 epoch부터 이어간다. 더 정확한 재현이 필요하다면 RNG나 DataLoader Generator의 상태도 checkpoint에 추가할 수 있다.

각 파일의 역할은 다음처럼 구분했다.

```text
config.json
→ 실험 조건을 사람이 확인

metrics.csv
→ Epoch별 결과를 분석하고 비교

checkpoint.pth
→ 모델·Optimizer·학습 진행 상태를 복원
```

Checkpoint 안의 `config`와 `history`는 `.json`, `.csv` 파일이 들어가는 것이 아니라 Python dictionary나 list 상태로 함께 저장된다. 같은 내용이 별도 파일과 checkpoint 양쪽에 존재할 수 있지만, 하나는 분석·비교용이고 다른 하나는 학습 복원용이라는 목적의 차이가 있다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: Seed를 고정하는 시점

처음에는 학습을 시작하기 전에만 seed를 고정하면 된다고 생각했다.

하지만 weight와 bias는 모델을 생성하는 순간 초기화된다. 이미 모델을 만든 뒤 seed를 고정해도 기존 초기값은 바뀌지 않으므로, 정확한 기준은 **학습 전이 아니라 모델 생성 전**이다.

---

### 이해한 내용: 전역 Seed와 DataLoader Generator

재현성이 필요한 이유는 실행할 때마다 결과가 달라지면 모델 성능을 공정하게 비교하기 어렵기 때문이다.

```text
Seed
→ 모델 초기값 등 전체적인 랜덤성 통제

DataLoader Generator
→ shuffle 순서 통제
```

같은 seed 값을 사용하더라도 각 Generator는 별개의 난수 생성기이며, 자신이 담당하는 랜덤 작업의 시작점을 재현한다.

---

### 질문: Seed 숫자를 한 곳에서 일괄 관리할 수 있는가?

가능하다. seed 값을 하나의 변수에 저장하고 필요한 곳에서 함께 사용하면 된다.

```python
SEED = 40

set_seed(SEED)

generator = torch.Generator()
generator.manual_seed(SEED)
```

`40` 자체에 특별한 의미가 있는 것은 아니며, 다른 고정 정수를 사용해도 된다.

---

### 질문: 100 Epoch를 학습하면 기록도 100개 남는가?

각 epoch가 끝날 때 metric을 한 번 기록한다면 100 epoch 학습 시 `metrics.csv`에 데이터 행 100개가 남는다. 이와 별도로 column 이름을 나타내는 header가 한 줄 있다.

```text
1 Epoch 완료   → Metric 1행 기록
2 Epoch 완료   → Metric 1행 기록
...
100 Epoch 완료 → Metric 1행 기록
```

`config.json`은 매 epoch의 결과가 아니라 해당 실험의 설정을 기록하므로 일반적으로 실험 하나에 하나를 둔다.

---

### 이해 수정: `history`의 역할

처음에는 `history`로 모델을 학습한다고 표현했다.

실제로 학습을 수행하는 것은 모델, loss, optimizer이며, `history`는 학습 중 계산된 loss와 accuracy 등의 metric을 메모리에 기록하는 역할이다. 실행이 끝난 뒤에도 기록을 보존하려면 파일로 저장해야 한다.

---

### 이해 수정: Config에 저장하는 정보

처음에는 Config에 모델 정보만 저장한다고 생각했다.

Config에는 모델 구조뿐 아니라 seed, learning rate, batch size, optimizer 등 **실험을 어떤 조건으로 실행했는지 설명하는 설정 전체**를 기록한다.

---

### 이해 수정: Config와 Metric으로 실험 비교하기

처음에는 Config와 Metric 중 하나라도 없으면 실험 비교 자체가 불가능하다고 생각했다.

하나가 없다고 단순 비교까지 불가능한 것은 아니지만, 의미 있는 비교는 어려워진다.

- Metric만 있으면 어느 실험의 성능이 높은지는 볼 수 있지만, 어떤 설정 차이가 결과에 영향을 주었는지 알기 어렵다.
- Config만 있으면 어떤 조건으로 실행했는지는 알 수 있지만, 실제 성능 결과는 확인할 수 없다.
- 둘을 함께 남기면 **실험 조건과 결과를 연결해서 비교**할 수 있다.

---

### 질문: `state_dict`에는 가중치 값만 저장되는가?

주로 weight와 bias 같은 학습 parameter가 저장되지만, BatchNorm의 running mean과 running variance처럼 계속 관리되어야 하는 상태도 포함될 수 있다.

반면 모델 클래스, `forward()` 코드, layer 구성 방식에 대한 Python 코드는 저장되지 않는다.

```text
같은 모델 구조 생성
→ state_dict 불러오기
```

순서가 필요한 이유다.

---

### 질문: 모델 코드는 어디에 저장하는가?

모델 구조와 학습 코드는 GitHub 같은 코드 저장소에서 관리하고, 학습된 상태는 `.pt`나 `.pth` 파일로 별도 저장할 수 있다.

```text
코드 저장소
→ 모델 구조와 학습 방법

state_dict / checkpoint
→ 학습된 현재 상태
```

---

### 질문: Config·Metric·Checkpoint는 어떻게 저장하는가?

각 파일을 별도로 저장하는 것과 여러 상태를 checkpoint에 묶는 것을 구분해야 한다.

```text
config.json
→ Config를 JSON 형식으로 별도 저장

metrics.csv
→ Epoch별 Metric을 CSV 형식으로 별도 저장

checkpoint.pth
└─ Dictionary
   ├─ model_state_dict
   ├─ optimizer_state_dict
   ├─ completed_epochs
   ├─ history
   └─ config
```

Config나 metric도 기술적으로 `.pth` 안에 넣을 수 있다. 다만 JSON은 설정을 사람이 읽기 좋고, CSV는 결과를 표로 분석하기 좋으며, PTH는 PyTorch와 Python의 상태를 저장하고 복원하기 좋기 때문에 용도에 따라 형식을 나눈다.

Checkpoint 안의 `config`와 `history`는 다시 `.json`, `.csv` 파일 형태로 들어가는 것이 아니라 checkpoint dictionary의 값으로 저장된다.

---

### 질문: Metric을 Checkpoint에도 넣는 이유는 무엇인가?

`metrics.csv`는 분석과 실험 비교를 위한 기록이고, checkpoint의 `history`는 학습을 재개할 때 현재까지의 기록도 함께 복원하기 위한 데이터다.

```text
metrics.csv
→ 분석 / 비교

checkpoint.pth의 history
→ 학습 상태 복원
```

Checkpoint의 `history`를 나중에 CSV로 만들 수도 있지만, 실험 비교가 목적이라면 처음부터 CSV도 함께 기록하는 편이 자연스럽다.

---

### 질문: Checkpoint도 Epoch마다 저장되는가?

Epoch마다 저장하도록 설계할 수 있지만, 매번 별도의 파일을 만들어야 하는 것은 아니다. 같은 파일명을 사용하면 이전 파일을 덮어쓰면서 최신 save point 하나만 유지할 수 있다.

```text
Epoch 1 완료 → checkpoint.pth 저장
Epoch 2 완료 → 같은 파일에 최신 상태 저장
Epoch 3 완료 → 같은 파일에 최신 상태 저장
```

CSV가 epoch별 결과를 계속 누적하는 기록이라면, checkpoint는 돌아갈 수 있는 현재 학습 상태를 보존하는 save point에 가깝다.

---

### 이해 수정: Optimizer 상태를 저장하는 이유

처음에는 optimizer 상태를 재현성을 위해 저장한다고 생각했다.

가장 직접적인 목적은 **학습을 제대로 이어서 재개하기 위해서**다. Adam 같은 optimizer는 이전 step 수와 gradient의 누적 상태를 가지고 있다.

```text
모델 상태만 복원
+ Optimizer 새로 생성
→ Weight는 이어지지만 Optimizer의 진행 상태는 초기화됨
```

정확한 재현까지 필요하다면 optimizer 상태 외에도 RNG와 DataLoader Generator 상태 등을 함께 보존해야 한다.

---

### 이해한 내용: 실험 기록과 학습 재개 흐름

전체 흐름을 다음처럼 이해했다.

```text
학습 시작
→ config.json으로 실험 조건 기록

각 Epoch 완료
→ metrics.csv에 결과 기록

학습 중간
→ checkpoint.pth에 현재 학습 상태 저장

중단 발생
→ checkpoint를 이용해 이어서 학습

학습 완료
→ config.json과 metrics.csv로 다른 실험과 비교
```
