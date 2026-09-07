# GPU Memory와 CNN 구조 실험

> 학습일: 2026-08-31

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### GPU Memory에는 모델만 올라가는 것이 아니다

GPU Memory는 모델 parameter만 사용하는 공간이 아니다. 학습할 때는 입력 batch와 label, 중간 activation과 feature map, gradient, optimizer가 관리하는 상태까지 함께 올라간다.

```text
입력 batch와 label
+ 모델 parameter
+ 중간 activation / feature map
+ gradient
+ optimizer state
→ 전체 GPU Memory 사용량
```

이 합계가 GPU에서 사용할 수 있는 용량을 넘으면 CUDA OOM이 발생한다. MLP는 큰 Linear layer 때문에 parameter가 많아질 수 있고, CNN은 중간 feature map 때문에 메모리를 많이 사용할 수 있으므로 모델 종류만 보고 어느 쪽이 더 가볍다고 단정할 수 없다.

OOM이 발생하면 우선 다음 순서로 점검한다.

```text
1. batch size가 너무 크지 않은지 확인
2. validation / inference에서 torch.no_grad()를 사용했는지 확인
3. loss나 logits Tensor를 계속 저장하고 있지 않은지 확인
```

기록에 숫자만 필요하다면 `loss` Tensor 자체 대신 `loss.item()`을 저장한다. `torch.cuda.empty_cache()`는 현재 사용 중인 Tensor를 없애지 못하므로 근본적인 해결책으로 보지 않는다.

### CNN 구조는 Baseline에서 하나씩 바꾼다

CNN 구조를 비교할 때는 먼저 기준이 되는 baseline을 정하고, filter 수나 kernel size처럼 확인하려는 조건만 하나씩 변경한다.

```text
baseline
→ filter 수만 변경해 비교
→ 다시 같은 조건에서 kernel size만 변경해 비교
```

한 번에 여러 조건을 바꾸면 어떤 변경 때문에 결과가 달라졌는지 판단하기 어렵다. 따라서 seed, train·validation split, epoch, batch size, optimizer, learning rate 등 나머지 조건은 같게 유지한다.

```text
filter 수
→ 몇 종류의 특징을 표현할지 결정
→ 출력 channel 수와 연결

kernel size
→ 한 번에 살펴보는 지역 범위의 크기

stride
→ kernel이 한 번 계산한 뒤 이동하는 간격
```

홀수 kernel을 사용하고 `stride=1`인 현재 실습에서는 다음과 같이 padding을 정하면 입력과 출력의 H, W를 유지할 수 있다.

```python
padding = kernel_size // 2
```

### 구조 확인과 성능 비교는 다르다

모델을 만든 뒤에는 먼저 logits Shape와 parameter 수를 확인해 구조가 의도대로 연결됐는지 검사한다. 그다음 같은 학습 조건에서 실제로 학습시켜 validation loss와 accuracy를 비교한다.

```text
logits Shape + parameter 수
→ 모델 구조와 크기 확인

validation loss + accuracy
→ 실제 학습 성능 확인
```

Shape가 정상이라고 해서 성능도 좋은 것은 아니다. 실험 조건은 config에 기록하고, 결과에는 parameter 수와 validation 성능을 함께 남겨 **모델이 커진 만큼 성능 향상이 있었는지** 확인한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: MLP 대신 CNN을 사용하는 이유는 더 복잡한 계산을 하기 위해서인가?

단순히 계산을 더 복잡하게 만들기 위해서가 아니다. CNN은 이미지의 가까운 픽셀 사이에 있는 지역적·공간적 관계를 유지하면서 특징을 찾기 위해 사용한다.

```text
MLP
→ 이미지를 Flatten해서 입력

CNN
→ 이미지의 지역 영역을 살펴보며 특징 추출
```

---

### 질문: MLP는 CNN보다 GPU Memory를 적게 사용하는가?

항상 그렇지는 않다. MLP는 큰 Linear layer의 parameter가 메모리를 많이 사용할 수 있고, CNN은 여러 중간 feature map과 activation이 큰 비중을 차지할 수 있다.

따라서 실제 입력 크기와 모델 구조를 기준으로 비교해야 한다.

---

### 질문: Batch Size를 줄이면 학습이 제대로 되지 않을 수 있는가?

작은 batch로도 학습할 수 있지만 gradient의 특성이 달라질 수 있다.

```text
큰 batch
→ gradient가 비교적 안정적
→ 메모리 사용량이 큼

작은 batch
→ gradient 변동이 커질 수 있음
→ 메모리 사용량이 작음
```

OOM이 발생하면 먼저 batch size를 줄여 실행 가능한 상태로 만든 뒤, train·validation 결과를 다시 확인한다.

---

### 이해 수정: CUDA 사용 확인

#### 처음 이해

`torch.cuda.is_available()`을 호출하면 GPU 사용을 선언하는 것이라고 생각했다.

#### 수정된 이해

`torch.cuda.is_available()`은 현재 환경에서 CUDA를 사용할 수 있는지 확인할 뿐이다. 확인 결과로 device를 정한 뒤 모델, 입력, label을 같은 device로 옮겨야 한다.

```text
CUDA 사용 가능 여부 확인
→ device 선택
→ model / images / labels 이동
```

---

### 이해 수정: OOM이 발생하는 이유와 대응

#### 처음 이해

GPU Memory가 원래 크지 않기 때문에 OOM이 발생한다고 생각했다.

#### 수정된 이해

GPU Memory의 절대적인 크기보다, 현재 학습에 필요한 모든 데이터의 합이 사용 가능한 용량을 넘었는지가 기준이다.

우선 batch size를 줄이고, 평가 구간에서 `torch.no_grad()`가 적용됐는지 확인한다. Tensor를 list 등에 계속 보관하면 계산 그래프까지 참조할 수 있으므로 값만 필요할 때는 `.item()`으로 기록한다.

`model.eval()`은 layer를 평가 모드로 바꾸고, `torch.no_grad()`는 Autograd 추적을 끄는 기능이므로 역할이 다르다.

---

### 질문: Kernel이 크면 이미지를 더 빨리 스캔하는가?

아니다. Kernel size는 한 번에 보는 영역의 크기이고, 이동 간격은 stride가 결정한다.

```text
kernel size
→ 보는 범위

stride
→ 이동 간격
```

Kernel이 커지면 한 위치에서 계산할 값이 많아지므로 오히려 parameter와 연산량이 증가할 수 있다.

---

### 질문: Kernel의 보는 범위를 크게 만드는 이유는 무엇인가?

더 넓은 영역의 패턴과 주변 관계를 한 번에 확인하기 위해서다.

```text
작은 kernel
→ 좁은 지역 패턴 확인

큰 kernel
→ 더 넓은 지역 관계 확인
```

범위를 넓히는 대신 parameter와 연산량도 늘어날 수 있으므로 실험 결과를 보고 선택한다.

---

### 이해 수정: Padding 계산

#### 처음 이해

`kernel_size // 2`에서 나온 나머지를 padding으로 사용한다고 생각했다.

#### 수정된 이해

`//`는 나머지가 아니라 **나눗셈의 몫**을 구하는 연산이다.

```text
3 // 2 = 1
5 // 2 = 2
7 // 2 = 3
```

따라서 홀수 kernel과 `stride=1`을 사용하는 이번 설정에서는 `padding = kernel_size // 2`로 H와 W를 유지할 수 있다.

---

### 질문: OOM만 발생하지 않는다면 Parameter 수는 중요하지 않은가?

Parameter 수는 OOM 여부 외에도 모델의 크기, 계산량, 학습·추론 시간, 저장 공간과 관련된다. 모델이 복잡해지면 과적합 가능성에도 영향을 줄 수 있다.

따라서 accuracy만 보는 것이 아니라 그 성능을 얻기 위해 사용한 parameter 수도 함께 비교한다.

---

### 질문: Parameter 수의 크고 작음을 판단하는 표준이 있는가?

모든 모델에 적용되는 절대적인 기준은 없다. 모델 종류, 데이터 규모, 목적, hardware에 따라 적절한 크기가 달라진다.

같은 실험 안에서 다음 두 가지를 함께 비교한다.

```text
parameter가 얼마나 증가했는가?
↔ 그만큼 validation 성능도 좋아졌는가?
```
