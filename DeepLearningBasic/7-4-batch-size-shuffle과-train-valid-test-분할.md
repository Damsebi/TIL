# Batch Size, Shuffle과 Train·Valid·Test 분할

> 학습일: 2026-08-26

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

전체 Dataset을 나누는 이유는 **학습에 쓰는 데이터와 모델을 고르는 데이터, 최종 성적을 확인하는 데이터를 분리하기 위해서**다.

| Split | 역할 |
| --- | --- |
| Train | Parameter 학습 |
| Validation | 모델 구조와 Hyperparameter 등 설정 선택 |
| Test | 모든 선택이 끝난 모델의 최종 성능 평가 |

Test 결과를 본 뒤 다시 모델이나 설정을 고르면 Test가 사실상 Validation처럼 사용된다. 따라서 Test는 최종 선택이 끝난 뒤 확인한다.

`batch_size`는 한 번의 Forward·Backward에서 처리할 Sample 수다. Dataset 크기가 Batch Size로 정확히 나누어지지 않으면 마지막 Batch가 더 작을 수 있으며 정상이다. 특히 Validation과 Test는 모든 Sample을 평가할 수 있도록 보통 `drop_last=False`로 둔다.

Train Loader는 Sample 순서의 영향을 줄이기 위해 보통 `shuffle=True`, Validation·Test Loader는 같은 순서로 평가하기 위해 `shuffle=False`를 사용한다. 랜덤 Augmentation도 일반적으로 Train에만 적용한다.

```python
import torch
from torch.utils.data import DataLoader, random_split

train_size = int(len(dataset) * 0.8)
valid_size = int(len(dataset) * 0.1)
test_size = len(dataset) - train_size - valid_size

generator = torch.Generator().manual_seed(42)

train_set, valid_set, test_set = random_split(
    dataset,
    [train_size, valid_size, test_size],
    generator=generator,
)

train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
valid_loader = DataLoader(valid_set, batch_size=32, shuffle=False)
test_loader = DataLoader(test_set, batch_size=32, shuffle=False)
```

`random_split()`에 전달하는 세 크기의 합은 `len(dataset)`과 같아야 한다. 같은 Split을 다시 만들고 싶다면 고정 Seed를 가진 Generator를 전달한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `manual_seed(42)`도 실행 시간이나 컴퓨터에 따라 달라지는가?

아니다. `42`는 시간에서 자동으로 가져온 값이 아니라 사용자가 직접 정한 고정 Seed다.

Seed는 의사난수 생성기의 시작점을 정한다. 같은 환경에서 같은 Seed와 같은 코드를 사용하면 `random_split()`이 같은 Index를 선택하도록 재현할 수 있다.

`42`라는 숫자 자체에 특별한 기능은 없으며, 다른 고정 정수를 사용해도 된다. 시스템의 Random Source나 시간을 사용해 Seed를 자동 생성하는 경우와 `manual_seed(42)`는 구분해야 한다.

---

### 질문: 같은 Seed면 어느 컴퓨터에서나 결과가 완전히 같은가?

모든 연산 결과가 항상 완전히 같다고 보장할 수는 없다. PyTorch·CUDA 버전, CPU와 GPU, 사용한 연산 등 실행 환경의 차이로 결과가 달라지거나 작은 수치 차이가 생길 수 있다.

Seed 고정은 우선 **같은 실험 환경에서 Split과 난수 동작을 다시 재현하기 위한 설정**으로 이해했다. 결과 전체를 최대한 동일하게 재현하려면 Seed뿐 아니라 라이브러리 버전과 하드웨어 등의 환경도 함께 관리해야 한다.

---

### 이해 수정: 학습·검증·테스트를 실행하는 기기

#### 처음 이해

Seed와 실행 환경에 따라 결과가 달라질 수 있으므로, 학습한 기기에서 Validation과 Test까지 모두 끝내야 한다고 생각했다.

#### 수정된 이해

반드시 같은 기기에서 평가할 필요는 없다. 학습한 Model Weight를 저장한 뒤 다른 기기에서 불러와 Validation이나 Test를 실행할 수 있다.

일반적인 성능 평가에서는 다음 조건을 같게 유지하는 것이 중요하다.

- 같은 Model Weight
- 같은 Dataset과 Split
- 같은 전처리
- `model.eval()`을 적용한 평가 모드
- 같은 Metric 계산 방식

반면 수치까지 최대한 똑같이 재현하는 실험이 목적이라면 PyTorch·CUDA 버전과 하드웨어 등 실행 환경도 최대한 맞추는 편이 좋다.
