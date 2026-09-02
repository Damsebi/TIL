# Checkpoint 저장과 학습 재개

> 학습일: 2026-08-27

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

`state_dict`는 객체의 **현재 상태값을 담은 Python dictionary**다.

```text
model.state_dict()
→ Weight, Bias 등 모델의 학습된 상태

optimizer.state_dict()
→ Learning Rate, Step 수, Adam 내부 누적 상태 등
```

`model.state_dict()`에는 모델 클래스나 `forward()` 코드가 들어 있지 않다. 저장된 상태를 다시 사용하려면 코드에 있는 같은 모델 구조를 먼저 생성한 뒤 상태값을 불러와야 한다.

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

`completed_epochs`는 완전히 끝난 epoch의 개수다. 값이 `5`라면 5 epoch까지 완료했다는 뜻이므로 다음 학습은 6 epoch부터 이어간다. 더 정확한 재현이 필요하면 RNG와 DataLoader Generator의 상태도 checkpoint에 추가할 수 있다.

Checkpoint를 불러올 때 `torch.load()`는 파일에 저장된 checkpoint dictionary를 복원한다. 하지만 모델과 optimizer 객체를 대신 만들어주지는 않으므로 저장할 때와 같은 구조의 객체를 먼저 생성해야 한다.

```python
checkpoint = torch.load(
    "checkpoint.pth",
    map_location=device,
)

model = MLP()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

completed_epochs = checkpoint["completed_epochs"]
history = checkpoint["history"]
start_epoch = completed_epochs + 1
```

`map_location`은 checkpoint 안의 Tensor를 현재 사용하는 CPU/GPU 환경에 맞춰 불러오기 위한 설정이다.

복원 범위는 목적에 따라 달라진다.

```text
추론
→ model_state_dict

일반적인 학습 재개
→ model_state_dict
→ optimizer_state_dict
→ completed_epochs

정확한 Epoch 경계 재개
→ 위 상태들
→ history
→ RNG state
→ DataLoader Generator state 등
```

재개 후에는 기존 `history`에 새 기록을 이어 붙이고, 이어서 학습한 최신 상태로 checkpoint도 다시 저장한다.

각 파일의 목적은 다음처럼 구분했다.

```text
config.json
→ 실험 조건을 사람이 확인

metrics.csv
→ Epoch별 결과를 분석하고 비교

checkpoint.pth
→ 모델·Optimizer·학습 진행 상태를 복원
```

Checkpoint 안의 `config`와 `history`는 `.json`, `.csv` 파일이 들어가는 것이 아니라 Python dictionary나 list 상태로 함께 저장된다. 같은 내용이 양쪽에 존재할 수 있지만, 별도 파일은 분석·비교용이고 checkpoint 내부 데이터는 학습 복원용이라는 목적의 차이가 있다.

## 2. 학습하며 겪었던 문제점과 해결 과정

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

### 질문: 학습 재개 시 Checkpoint 상태를 대부분 복원하는가?

대체로 맞다. 추론이라면 모델 상태만 필요하지만, 학습을 제대로 이어가려면 optimizer와 진행 epoch도 함께 복원해야 한다. 정확한 epoch 경계부터 이어가려면 checkpoint에 저장해둔 `history`, RNG, DataLoader Generator 상태까지 최대한 복원한다.

---

### 이해 수정: 학습을 재개할 Epoch

처음에는 `completed_epochs`부터 다시 시작한다고 생각했다.

`completed_epochs`는 이미 완전히 끝난 epoch의 수이므로 다음 epoch부터 시작해야 한다.

```text
completed_epochs = 5
→ 5 Epoch까지 완료
→ 6 Epoch부터 재개
```

따라서 시작 epoch는 `completed_epochs + 1`이다.

---

### 이해한 내용: Checkpoint를 불러오는 흐름

Checkpoint에는 모델 객체 자체가 아니라 상태값이 들어 있으므로, 같은 구조의 객체를 만든 다음 그 상태를 주입한다.

```text
저장된 checkpoint
→ torch.load(..., map_location=device)로 현재 Device에 맞춰 Dictionary 불러오기
→ 같은 구조의 Model 생성
→ Optimizer 생성
→ model.load_state_dict()로 모델 상태 복원
→ optimizer.load_state_dict()로 Optimizer 상태 복원
→ completed_epochs + 1부터 학습 재개
```

재개 후에는 기존 `history`에 새 metric을 이어서 기록하고, 최신 학습 상태로 checkpoint를 다시 갱신한다.
