# 이미지 구조와 Convolution·Padding·Stride

> 학습일: 2026-08-28

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

### 이미지와 Channel

MLP는 보통 이미지의 `C × H × W`를 Flatten해 하나의 Feature 벡터로 만든다. CNN은 이미지의 공간적인 배치를 유지하며 작은 영역의 특징을 찾는다. 공간 구조를 사용한다는 것이 H, W 크기를 항상 유지한다는 뜻은 아니다.

PyTorch CNN의 이미지 Batch는 `(N, C, H, W)`로 읽는다.

```text
N → 한 번에 처리하는 이미지 수
C → Channel 수: 흑백 1, RGB 3
H → 이미지 높이
W → 이미지 너비
```

이미지 하나가 `(H, W, C)`로 준비되어 있다면 `permute(2, 0, 1)`로 `(C, H, W)` 순서로 바꾼다. 이후 여러 이미지를 Batch로 묶으면 `(N, C, H, W)`가 된다.

### Filter와 Kernel 구분

Filter와 Kernel은 자료에 따라 같은 뜻으로 사용되기도 한다. 여기서는 **일반적인 `groups=1` Conv2d의 가중치 구조**를 이해하기 위해 다음처럼 구분한다.

| 용어 | 이 문서에서 가리키는 것 | Shape |
| --- | --- | --- |
| 채널별 2D Kernel | 한 입력 채널과 한 출력 채널 사이의 작은 가중치 배열 | `(K_H, K_W)` |
| Filter 하나 | 입력 채널별 Kernel들을 묶어 출력 Feature Map 하나를 만드는 가중치 묶음 | `(in_channels, K_H, K_W)` |
| 전체 Conv2d Weight | `out_channels`개 Filter를 모은 Tensor | `(out_channels, in_channels, K_H, K_W)` |

즉 **Filter는 가중치이고, Feature Map은 계산 결과**다. Filter 하나가 입력의 모든 채널에서 지역적인 곱셈·합산을 수행하고, 그 결과를 채널 간에도 더해 출력 채널 하나를 만든다. Bias를 사용하는 경우에는 Bias도 더한다. ([CS231n Convolutional Layer](https://cs231n.github.io/convolutional-networks/#conv))

RGB 이미지에 `3×3` 크기의 Filter 8개를 적용한다면 다음과 같다.

```python
conv = nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3)

conv.weight.shape
# torch.Size([8, 3, 3, 3])
```

```text
Filter 하나
→ RGB 각각에 대응하는 3×3 Kernel 3개를 묶음
→ 세 채널의 계산 결과를 합쳐 Feature Map 1개 생성

Filter 8개
→ 이미지 하나당 Feature Map 8개
→ out_channels = 8
```

`kernel_size=3`은 Kernel의 공간 크기가 `3×3`이라는 뜻이지 Kernel이나 Filter가 3개라는 뜻은 아니다. 입력이 흑백이면 채널별 Kernel이 하나뿐이어서 Filter 하나와 2D Kernel 하나의 구분이 눈에 잘 드러나지 않는다.

### Padding과 Stride

- **Padding**: 가장자리에 값을 덧붙여 가장자리도 계산에 포함될 기회를 늘리고, 출력 크기의 감소를 조절한다. 기본 Zero Padding은 0을 덧붙인다.
- **Stride**: Filter를 한 번 계산한 뒤 몇 칸 이동할지 정한다. 커지면 방문하는 위치가 줄어 출력 H, W가 작아지고 연산량도 줄어들 수 있지만 공간 정보는 더 잃을 수 있다.

Filter를 여러 위치로 이동시켜 계산한 반응값들을 모은 것이 Feature Map이다. 출력 Batch의 Shape는 `(N, out_channels, H_out, W_out)`이다.

### 출력 크기 공식

이번 강의처럼 **`dilation=1`이고, 각 축의 양쪽에 같은 크기로 Padding을 넣는 Conv2d**에서는 다음과 같이 계산한다. ([PyTorch Conv2d](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Conv2d.html))

$$
H_{out} = \left\lfloor \frac{H_{in} + 2P_H - K_H}{S_H} \right\rfloor + 1
$$

$$
W_{out} = \left\lfloor \frac{W_{in} + 2P_W - K_W}{S_W} \right\rfloor + 1
$$

- `H_in`, `W_in`: 입력 높이와 너비
- `K_H`, `K_W`: Kernel의 높이와 너비
- `P_H`, `P_W`: 위·아래 각각에 붙이는 Padding, 왼쪽·오른쪽 각각에 붙이는 Padding
- `S_H`, `S_W`: 높이·너비 방향 Stride
- 바닥 함수 `⌊ ⌋`: 소수 부분을 버리고 아래쪽 정수로 내림

가장자리에 양쪽으로 Padding을 붙이므로 `2P`가 더해진다. Kernel을 놓을 수 있는 이동 범위를 Stride로 나눈 뒤, 처음 놓는 위치 하나를 포함하기 위해 `+1`한다.

계산 결과가 소수여도 반올림하지 않는다. 예를 들어 한 축이 길이 6이고 `K=3`, `P=0`, `S=2`라면 다음과 같다.

```text
floor((6 + 2×0 - 3) / 2) + 1
= floor(1.5) + 1
= 2
```

Kernel이 입력 범위를 벗어나지 않고 놓일 수 있는 위치만 센다. `kernel_size`, `padding`, `stride`를 정수 하나로 지정하면 높이와 너비 양쪽에 같은 값을 사용한다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: `permute(2, 0, 1)`은 왜 `2, 0, 1`인가?

`permute`의 숫자는 새 차원의 크기가 아니라 **기존 차원을 어떤 순서로 가져올지** 나타낸다.

```text
원본 Shape: (H, W, C)
기존 Dim:    0  1  2

원하는 순서: (C, H, W)
가져올 Dim:  2  0  1
```

```python
chw_image = hwc_image.permute(2, 0, 1)
```

픽셀 값을 새로 계산하거나 바꾸는 것이 아니라 축의 순서를 재배치한다.

---

### 이해 수정: Filter와 Kernel

처음에는 Filter가 Kernel로 나누어진 이미지 영역이거나, Feature Map의 개수 자체라고 생각했다.

Filter는 이미지를 자른 영역도, 개수를 나타내는 숫자도 아니다. **특징을 찾는 학습 가능한 가중치 묶음**이며, Kernel이 적용되는 이미지의 작은 영역과 구분해야 한다.

Filter 하나가 위치별 반응을 모아 Feature Map 하나를 만들기 때문에 `Filter 개수 = 이미지 하나당 Feature Map 개수 = out_channels`가 된다.

---

### 이해 수정: Convolution 결과는 정확도인가?

처음에는 곱셈·합산 결과가 모델이 찾는 이미지를 얼마나 정확하게 맞혔는지 비교하는 값이라고 생각했다.

Convolution 결과는 정답과 비교한 정확도가 아니다. **해당 Filter가 그 위치의 입력에 얼마나 반응했는지 나타내는 값**이다.

```text
이미지의 작은 영역과 가중치
→ 같은 위치끼리 곱하기
→ 공간·입력 채널 방향으로 합산
→ Bias가 있으면 더하기
→ 그 위치의 반응값 하나
```

이 계산을 여러 위치에서 반복한 결과가 Feature Map이다.

---

### 질문: `5×5` 이미지에 `3×3` Kernel을 적용하면 크기도 줄어드는가?

Padding 없이 Stride 1, Dilation 1로 계산하면 높이와 너비가 각각 3이 된다.

```text
(5 + 2×0 - 3) / 1 + 1 = 3

5×5 입력 → 3×3 Feature Map
```

Filter 하나를 놓을 수 있는 위치가 가로 3개, 세로 3개이므로 **Filter 하나당 출력값 9개**를 만든다. Filter가 여러 개라면 이런 Feature Map도 여러 개 생긴다.

---

### 질문: Stride를 크게 하면 더 빠르게 학습하고, Padding은 많이 넣어도 괜찮은가?

처음에는 Stride가 커질수록 학습도 더 빨라진다고 생각했다.

```text
Stride 증가
→ 계산 위치와 출력 H, W 감소
→ 연산량 감소 가능
→ 공간 정보 손실 증가 가능
```

계산은 가벼워질 수 있지만, 모델이 더 잘 학습되거나 더 빨리 수렴한다는 뜻은 아니다.

Padding도 많이 넣는 것이 무조건 좋지는 않다. 필요한 출력 크기와 가장자리 계산을 고려해 적절하게 정한다.

---

### 이해 수정: CNN에서는 H, W가 항상 유지되는가?

처음에는 CNN이 이미지 구조를 유지하므로 높이와 너비도 항상 그대로라고 생각했다.

공간 구조를 이용한다는 것과 공간 크기가 같다는 것은 다르다. 출력 크기는 Kernel Size, Padding, Stride에 따라 달라진다.

이번 기본 설정인 `dilation=1`에서 자주 사용하는 조합은 다음과 같다.

```text
kernel_size = 3
padding = 1
stride = 1

H_out = (H_in + 2×1 - 3) / 1 + 1 = H_in
W_out = (W_in + 2×1 - 3) / 1 + 1 = W_in
```

이 조합에서는 H, W가 유지되지만 Channel 수는 `out_channels` 설정에 따라 바뀔 수 있다.
