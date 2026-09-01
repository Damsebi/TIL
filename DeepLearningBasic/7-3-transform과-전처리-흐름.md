# Transform과 전처리 흐름

> 학습일: 2026-08-26

## 1. 오늘 학습한 내용을 나만의 언어로 정리하기

Transform은 **원본 데이터를 모델에 넣기 좋은 모습으로 바꿔서 반환하는 전처리 과정**이다. 원본 이미지 파일을 수정하는 것이 아니라 Dataset이 Sample을 꺼낼 때 메모리에서 변환한다.

일반적인 이미지 전처리 순서는 다음과 같다.

```text
Resize·Augmentation
→ ToTensor
→ Normalize
→ DataLoader가 Batch로 묶음
```

일반적인 이미지의 `(H, W, C)` 순서는 `ToTensor`를 거치며 `(C, H, W)`가 되고, DataLoader가 여러 Sample을 묶으면 `(N, C, H, W)`가 된다.

`Resize`는 크기를 통일하고, Augmentation은 학습 이미지의 모습을 바꾸며, Normalize는 Tensor 값의 분포와 Scale을 조정한다. Transform마다 받을 수 있는 자료형이 다를 수 있으므로 이번에는 이미지 변형 뒤에 `ToTensor → Normalize`를 적용했다.

Train에는 랜덤 Augmentation을 넣어 같은 이미지를 여러 모습으로 학습할 수 있지만, Validation에는 보통 결과가 매번 달라지는 랜덤 변형을 넣지 않는다. Train과 Validation이 같은 원본 Dataset을 공유한다면 Transform 속성을 번갈아 덮어쓰지 않고, 각각의 Transform을 보관하는 Wrapper를 따로 둔다.

## 2. 학습하며 겪었던 문제점과 해결 과정

### 질문: 여기서 `transform`은 AI의 Transformer와 다른 것인가?

서로 다른 개념이다.

- `transform`: 이미지 크기·방향·값의 범위 등을 바꾸는 데이터 전처리
- Transformer: Attention을 중심으로 만든 모델 구조

이번 강의의 Transform은 Transformer 모델과 직접 관련이 없다.

---

### 질문: Normalize가 학습하기 편하게 만들면 자원도 덜 사용하는가?

Normalize는 Tensor의 Shape를 줄이지 않으므로 GPU 메모리를 직접 크게 줄이는 기능은 아니다.

입력 Scale을 조정하면 최적화가 더 안정적으로 진행될 수 있어 원하는 성능까지 걸리는 시간이 줄어드는 등 간접적인 이점은 생길 수 있다. 하지만 Normalize를 했다는 이유만으로 메모리 사용량이나 학습 시간이 반드시 감소하는 것은 아니다.

---

### 질문: 이미지가 적으면 Augmentation으로 늘릴 수 있는가? 오히려 모델이 망가질 수도 있는가?

Augmentation을 사용하면 학습할 때 같은 원본을 좌우 반전·회전·Crop·밝기 변화 등 여러 모습으로 보여줄 수 있어 과적합을 줄이는 데 도움이 될 수 있다.

다만 온라인 Augmentation은 Dataset의 원본 개수나 새로운 정보 자체를 늘리는 것이 아니라 **기존 Sample의 다양한 변형을 보여주는 방식**이다. 변형이 너무 강하거나 실제 데이터에서 일어나기 어려운 모습이면 중요한 특징을 훼손해 성능이 떨어질 수도 있다.

따라서 단순히 크기만 여러 번 바꾸는 Resize보다는 문제에서 의미가 유지되는 변형을 골라야 하며, 데이터가 극단적으로 적은 문제를 Augmentation만으로 완전히 해결할 수는 없다.

---

### 이해 수정: `transform()`과 `Compose`의 역할

#### 처음 이해

PyTorch에 기본 `transform()` 함수가 있고, 호출하면 Resize·`ToTensor`·Normalize가 자동으로 실행된다고 생각했다. `Compose` 자체가 Transform을 바로 실행하는 함수라고도 이해했다.

#### 수정된 이해

`transform`은 내장함수 이름이 아니라 사용자가 정한 변수명이다. 먼저 `Compose`로 실행할 작업과 순서를 묶어 하나의 Callable 객체를 만든다.

```python
from torchvision import transforms

train_transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.5, 0.5, 0.5),
        std=(0.5, 0.5, 0.5),
    ),
])
```

그다음 실제 이미지를 넣어 호출해야 등록한 Transform들이 순서대로 실행된다.

```python
transformed_image = train_transform(image)
```

Custom Transform 하나만 사용한다면 `Compose` 없이 바로 호출할 수 있고, 여러 Transform을 연결할 때 `Compose`로 묶을 수 있다.

---

### 이해 수정: Flip·Normalize·Shape 변화

- `RandomHorizontalFlip`은 랜덤 회전이 아니라 좌우 반전이다. 회전은 `RandomRotation`을 사용한다.
- Normalize는 Shape를 바꾸지 않고 각 Channel의 값을 `(x - mean) / std`로 바꾼다.
- Normalize 결과가 항상 `[-1, 1]`이 되는 것은 아니다.
- 일반적인 이미지의 `HWC → CHW` 변화는 Transform 전체가 아니라 `ToTensor` 단계에서 일어난다.

`ToTensor` 후 값이 `[0, 1]`이고 `mean=0.5`, `std=0.5`일 때는 Normalize 결과가 대략 `[-1, 1]`이 된다.

---

### 이해 수정: Train과 Validation에 서로 다른 Transform 적용하기

#### 처음 이해

`random_split()`으로 나눈 두 Subset은 독립된 Dataset이므로 각각 원본의 `transform`을 바꿔도 된다고 생각했다.

#### 수정된 이해

`Subset`은 데이터를 복사하지 않고 **같은 원본 Dataset과 서로 다른 Index 목록을 공유**한다.

따라서 다음 두 코드는 서로 다른 객체를 바꾸는 것이 아니라 같은 원본 Dataset의 속성을 두 번 바꾼다.

```python
train_subset.dataset.transform = train_transform
valid_subset.dataset.transform = valid_transform
```

마지막에 넣은 `valid_transform`이 원본 Dataset의 Transform으로 남으므로 두 Subset 모두 그 설정을 사용하게 된다.

이를 피하려면 원본과 Index는 공유하되 Train·Validation Transform을 각각 보관하는 Wrapper를 둔다. 사진첩으로 생각하면 Subset은 사용할 페이지 번호 목록이고, Wrapper는 같은 사진첩을 볼 때 적용하는 별도의 필터다.

---

### 질문: Transform을 적용하면 원본 데이터도 바뀌는가?

원본 이미지 파일 자체가 수정되거나 다시 저장되는 것은 아니다.

Dataset이 원본을 읽고 메모리에서 Transform을 실행한 뒤 변환된 Sample을 반환한다. 다음에 같은 Sample을 꺼낼 때는 원본을 다시 읽고 Transform을 새로 적용하므로, 랜덤 Augmentation이 포함되어 있다면 같은 이미지도 호출할 때마다 다른 모습으로 나올 수 있다.

---

### 질문: `transform=None`은 왜 사용하는가?

Transform을 차단하는 특별한 명령이 아니라 **전처리가 전달되지 않은 상태를 나타내는 기본값**이다.

```python
def __init__(self, transform=None):
    self.transform = transform

def __getitem__(self, idx):
    image, label = self.load_sample(idx)

    if self.transform is not None:
        image = self.transform(image)

    return image, label
```

이렇게 작성하면 같은 Dataset 클래스를 Transform이 있는 경우와 없는 경우에 모두 사용할 수 있다.

---

### 질문: Custom Transform 객체는 왜 함수처럼 호출할 수 있는가?

일반 객체는 바로 `obj()` 형태로 호출할 수 없지만, 클래스에 `__call__()`을 구현하면 Callable 객체가 된다.

```python
class SimpleNormalize:
    def __call__(self, x):
        return (x - x.mean()) / (x.std() + 1e-6)


transform = SimpleNormalize()
transformed_x = transform(x)
```

마지막 줄은 객체 내부의 `__call__(x)`를 실행한다. 따라서 직접 만든 Transform도 torchvision Transform처럼 파이프라인에서 함수 형태로 사용할 수 있다.

---

### 이해한 내용: 학습 전에 전처리 결과 확인하기

전처리 코드를 작성한 뒤 바로 모델을 학습시키지 않고 Dataset에서 Sample 하나를 먼저 꺼내 확인한다.

```python
image, label = dataset[0]

print(image.shape)
print(image.dtype)
print(image.min())
print(image.max())
print(image.mean())
```

Shape와 Dtype이 모델 입력에 맞는지, 값의 최소·최대 범위가 이상하지 않은지, Normalize 후 평균이 예상 범위인지 확인한 다음 학습으로 넘어간다.
