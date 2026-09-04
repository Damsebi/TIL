# Pooling과 Feature Map Shape·Classifier 연결

> 학습일: 2026-08-28

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### Pooling과 Flatten은 다르다

Pooling은 Feature Map의 공간 크기를 줄이는 연산이다. 이번에 사용한 Max Pooling은 **각 Channel의 작은 영역에서 가장 큰 반응값 하나를 선택**한다. 공간 정보를 일부 버리는 대신 뒤에서 처리할 데이터와 연산량을 줄일 수 있다.

`nn.MaxPool2d(2)`는 기본적으로 `2×2` 영역을 Stride 2로 이동하며 계산한다. N과 C는 유지되고, 이번처럼 H·W가 짝수이면 각각 절반으로 줄어든다. 다른 설정을 생략한 기본 동작에서는 홀수 크기를 내림하므로, 예를 들어 길이 5는 2가 된다. ([PyTorch MaxPool2d](https://docs.pytorch.org/docs/2.14/generated/torch.nn.MaxPool2d.html))

반면 Flatten은 **값이나 원소 수를 줄이지 않고 Shape만 펼친다.** Pooling으로 공간 크기를 줄이는 것과, 남은 Feature Map을 한 줄로 펼치는 것은 다른 역할이다.

```text
Pooling
→ 작은 영역의 대표값 선택
→ 공간 크기와 원소 수 감소

Flatten
→ 남아 있는 C, H, W를 한 차원으로 펼침
→ 원소 수 유지
```

### Feature Extractor에서 Classifier까지 연결하기

이번 CNN은 앞부분에서 특징을 추출하고, 뒷부분에서 그 특징을 클래스별 점수로 바꾸는 구조다.

```text
Conv2d → ReLU → MaxPool2d
→ Feature Extractor

Flatten
→ Feature Map을 벡터로 연결

Linear
→ Classifier
→ 클래스별 Logits
```

각 층을 통과할 때 무엇이 바뀌는지 확인한다.

| Layer | Shape에서 확인할 내용 |
| --- | --- |
| Conv2d | N은 유지, C는 `out_channels`가 됨. H·W는 Kernel·Padding·Stride 등에 따라 결정 |
| ReLU | 값에 비선형성을 넣지만 Shape는 유지 |
| MaxPool2d(2) | N·C는 유지, 기본 설정에서는 H·W를 각각 절반으로 내림 |
| Flatten(`start_dim=1`) | `(N, C, H, W) → (N, C×H×W)` |
| Linear | 입력 Feature 수를 받아 `(N, num_classes)` Logits로 변환 |

마지막 Feature Map에서 `flatten_dim = C × H × W`를 계산하고, 이를 `Linear`의 `in_features`와 맞춘다. Conv나 Pooling 구조가 바뀌면 마지막 Shape도 달라질 수 있으므로, 예전 `flatten_dim`을 그대로 쓰지 않고 다시 확인해야 한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `Conv2d`는 무엇이며, 인자들은 무엇을 의미하는가?

이미지나 Feature Map의 작은 영역을 보며 특징을 추출하는 2차원 Convolution Layer다.

```python
nn.Conv2d(3, 16, kernel_size=3, padding=1)
```

이 코드는 입력 Channel 3개를 받아 Filter 16개로 출력 Feature Map 16개를 만든다.

```text
첫 번째 3  → in_channels
16         → out_channels
kernel_size=3 → 3×3 공간 크기
padding=1     → 각 가장자리에 Padding 1
```

앞의 `3`, `16`은 Batch Size가 아니라 Channel 수다.

---

### 질문: 왜 `Conv2d → ReLU → MaxPool2d` 순서인가? 처음부터 줄이면 안 되는가?

이번 구조는 먼저 Conv로 특징을 추출하고, ReLU로 비선형성을 넣은 뒤 Pooling으로 공간 크기를 줄인다.

Pooling부터 하면 특징을 충분히 추출하기 전에 원본의 공간 정보를 버릴 수 있다. 따라서 **특징을 먼저 찾고, 그 반응을 줄여서 전달하는 흐름**으로 이해했다. 모든 CNN이 반드시 이 순서여야 한다는 뜻은 아니다.

---

### 질문: Pooling을 반복하는 것과 중간에 Conv2d를 다시 넣는 것은 무엇이 다른가?

`Conv → ReLU → Pool → ReLU → Pool`처럼 Pooling만 반복하면 이미 추출한 특징을 계속 줄이는 흐름에 가깝다. ReLU와 Max Pooling에는 새 특징을 학습하는 가중치가 없다.

반면 중간에 Conv를 다시 넣으면 이전 Feature Map을 입력으로 받아 새로운 특징을 학습할 수 있다.

```text
Conv → ReLU → Pool
→ Conv → ReLU → Pool
```

즉 공간 크기를 줄이는 것과 학습 가능한 Filter로 특징을 다시 추출하는 것을 구분했다.

---

### 질문: 왜 CNN에서 Flatten을 하는가?

이번 Classifier는 이미지 하나의 Feature Map 전체를 하나의 벡터로 받아 클래스별 Logits를 계산한다. 그래서 Conv 부분과 Linear 부분 사이에 Flatten을 둔다.

```text
(N, C, H, W)
→ Flatten
→ (N, C×H×W)
→ Linear
→ (N, num_classes)
```

Flatten 자체가 값을 골라 버리거나 가중합하는 것은 아니다. Feature Map을 Classifier가 사용할 입력 형태로 펼치는 연결 단계라고 이해했다.

---

### 질문: 코드에서는 어떻게 연결되는가?

미리 준비한 Layer들을 Forward에서 순서대로 호출한다.

```python
x = conv(x)
x = relu(x)
x = pool(x)

x = torch.flatten(x, start_dim=1)
x = linear(x)
```

`start_dim=1`이므로 0번 차원인 N은 유지하고 C·H·W만 펼친다. 이때 `linear`는 실제 Flatten 결과의 마지막 차원과 같은 입력 크기로 준비되어 있어야 한다.

---

### 질문: `nn.Linear(32 * 8 * 8, num_classes)`는 왜 `32 * 8 * 8`인가?

마지막 Feature Map이 이미지 하나당 `(32, 8, 8)`이기 때문이다.

```text
32 × 8 × 8 = 2048

(N, 32, 8, 8)
→ (N, 2048)
→ (N, num_classes)
```

따라서 다음처럼 입력 크기를 맞춘다.

```python
linear = nn.Linear(32 * 8 * 8, num_classes)
```

`2048`은 항상 사용하는 고정값이 아니라 **현재 구조에서 마지막으로 나온 C·H·W의 곱**이다. Pooling을 더 하거나 Channel 수를 바꾸면 이 값도 다시 계산해야 한다.

---

### 질문: Conv2d를 지나도 앞의 Batch Size는 왜 안 바뀌는가?

일반적인 Conv2d·ReLU·MaxPool2d는 Batch 안의 이미지들을 합치거나 개수를 줄이지 않고, 각 이미지에 같은 연산을 적용한다.

```text
N   → 이미지 개수이므로 유지
C   → Conv2d의 out_channels에 따라 변경
H,W → Kernel·Padding·Stride·Pooling에 따라 변경
```

Pooling에서 줄어드는 것도 이미지 개수 N이 아니라 각 이미지의 공간 크기 H·W다.

---

### 질문: Classifier가 무엇인가?

Feature Extractor가 추출한 특징을 사용해 **클래스별 Logits를 계산하는 부분**이다.

현재 구조에서는 Conv2d·ReLU·MaxPool2d가 Feature Extractor, Flatten이 연결 단계, 마지막 Linear가 Classifier 역할을 한다. 클래스가 `num_classes`개이면 샘플마다 점수가 그 개수만큼 나오므로 최종 Shape는 `(N, num_classes)`다.
