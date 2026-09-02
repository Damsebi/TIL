# Seed 고정과 Logging 설계

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
