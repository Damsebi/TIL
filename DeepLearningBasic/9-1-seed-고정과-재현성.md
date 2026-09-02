# Seed 고정과 재현성

> 학습일: 2026-08-27

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

같은 코드를 다시 실행해도 Model 초기값과 DataLoader의 Shuffle 순서 같은 랜덤 요소 때문에 결과가 달라질 수 있다. 재현성은 이 랜덤 요소를 통제해 **같은 조건의 실험을 다시 비교할 수 있게 만드는 것**이다.

Python·NumPy·PyTorch의 Seed는 하나의 함수에서 함께 설정할 수 있다.

```python
import random

import numpy as np
import torch


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
```

중요한 것은 함수 자체를 외우는 것보다 Seed를 **랜덤한 작업보다 먼저 설정하는 것**이다. 특히 Model의 Weight와 Bias는 Model을 생성하는 순간 초기화되므로 Seed도 Model 생성 전에 고정한다.

```text
Seed 고정
→ Model 생성
→ Weight·Bias 초기화
→ 학습
```

학습 DataLoader의 Shuffle 순서는 별도의 `torch.Generator`로 관리할 수 있다.

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

Validation은 보통 `shuffle=False`이므로 Shuffle 순서를 위한 Generator가 필요하지 않다. Seed를 고정하더라도 GPU·CUDA의 병렬 연산과 실행 환경 차이 등으로 모든 결과가 항상 100% 같아지는 것은 아니며, 랜덤성을 최대한 통제하는 것으로 이해했다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 이해 수정: Seed를 고정하는 시점

#### 처음 이해

Model을 학습하기 전에만 Seed를 고정하면 된다고 생각했다.

#### 수정된 이해

정확한 기준은 **학습 전이 아니라 Model 생성 전**이다. Model을 만드는 순간 Weight와 Bias의 초기값이 이미 정해질 수 있다.

Model 생성 후에 Seed를 설정해도 이미 만들어진 Parameter의 값은 바뀌지 않는다. 같은 초기값부터 실험하려면 Seed를 다시 설정한 뒤 Model을 생성해야 한다.

---

### 이해한 내용: 전역 Seed와 DataLoader Generator

역할을 다음처럼 나누어 이해했다.

```text
Python·NumPy·PyTorch Seed
→ Model 초기값 등 각 라이브러리의 랜덤성 통제

DataLoader Generator
→ shuffle=True일 때 Sample 순서 통제
```

Generator는 전역 PyTorch 난수 상태와 별도로 자기 상태를 가진다. 같은 `SEED` 숫자를 사용해도 모든 곳이 하나의 Generator를 공유하는 것은 아니다.

---

### 질문: Seed 숫자를 한 곳에서 일괄 관리할 수 있는가?

가능하다. Seed를 상수 하나로 정하고 필요한 설정에 같은 값을 전달하면 실험 설정을 바꾸거나 확인하기 쉽다.

```python
SEED = 40

set_seed(SEED)

generator = torch.Generator()
generator.manual_seed(SEED)
```

`SEED` 값은 하나로 관리하더라도 각 Generator는 별개의 난수 생성기다. 같은 시작값을 받아 각자 맡은 랜덤 작업의 순서를 재현한다.
