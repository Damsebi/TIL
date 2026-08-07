# 1장 3강 실습: 행렬 연산과 딥러닝 레이어
#
# 실행 전 필요한 패키지:
# pip install numpy pandas scikit-learn ucimlrepo

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


# 데이터 준비

try:
    from ucimlrepo import fetch_ucirepo

    dataset = fetch_ucirepo(id=222)
    X_raw = dataset.data.features.copy()
except Exception as error:
    print(f"UCI 데이터 로드 실패: {error}")
    print("대체 데이터를 사용합니다.")

    from sklearn.datasets import make_classification

    fallback_data, _ = make_classification(
        n_samples=3000,
        n_features=12,
        n_informative=6,
        random_state=RANDOM_STATE,
    )

    columns = [
        f"feature_{index}"
        for index in range(fallback_data.shape[1])
    ]

    X_raw = pd.DataFrame(
        fallback_data,
        columns=columns,
    )

X_numeric = X_raw.select_dtypes(
    include="number"
).copy()

X_numeric = X_numeric.replace(
    [np.inf, -np.inf],
    np.nan,
)

X_numeric = X_numeric.fillna(
    X_numeric.median(numeric_only=True)
)

feature_columns = [
    "age",
    "balance",
    "duration",
    "pdays",
    "previous",
]

feature_columns = [
    column
    for column in feature_columns
    if column in X_numeric.columns
]

if not feature_columns:
    feature_columns = list(
        X_numeric.columns[:5]
    )

X_sample = X_numeric[
    feature_columns
].sample(
    n=8,
    random_state=RANDOM_STATE,
)

X = StandardScaler().fit_transform(
    X_sample
)

print(f"데이터 행렬 X shape: {X.shape}")


# 문제 1-1: 데이터 행렬 X와 완전연결층 Shape 확인하기
#
# 1. X의 Shape와 각 축의 의미를 확인한다.
# 2. 출력 점수 3개를 만들기 위한 W와 b를 생성한다.
# 3. Y = X @ W + b를 계산한다.
# 4. X, W, b, Y의 Shape를 확인한다.

sample_count, feature_count = X.shape
output_count = 3

W = np.random.randn(
    feature_count,
    output_count,
)

b = np.random.randn(
    output_count
)

Y = X @ W + b

print("\n[문제 1-1]")
print(
    f"X: {X.shape} "
    "-> (샘플 수, 특성 수)"
)
print(
    f"W: {W.shape} "
    "-> (입력 차원, 출력 차원)"
)
print(
    f"b: {b.shape} "
    "-> (출력 차원,)"
)
print(
    f"Y: {Y.shape} "
    "-> (샘플 수, 출력 차원)"
)


# 문제 1-2: 반복문 계산과 행렬곱 결과 비교하기
#
# 1. 고객 한 명씩 X[i] @ W + b를 계산한다.
# 2. 반복문 결과와 Y의 Shape를 비교한다.
# 3. np.allclose()로 두 결과가 같은지 확인한다.

rows = []

for index in range(X.shape[0]):
    rows.append(
        X[index] @ W + b
    )

Y_loop = np.array(rows)

print("\n[문제 1-2]")
print(
    f"반복문 결과 Shape: "
    f"{Y_loop.shape}"
)
print(
    f"행렬곱 결과 Shape: "
    f"{Y.shape}"
)
print(
    "두 결과 일치 여부:",
    np.allclose(
        Y_loop,
        Y,
    ),
)


# 문제 2-1: Shape 오류를 재현하고 수정하기
#
# 1. X의 열 수와 맞지 않는 W_wrong을 만든다.
# 2. X @ W_wrong을 실행해 오류를 확인한다.
# 3. 올바른 Shape의 W_fixed로 다시 계산한다.

W_wrong = np.random.randn(
    4,
    3,
)

print("\n[문제 2-1]")
print(f"X Shape: {X.shape}")
print(
    f"W_wrong Shape: "
    f"{W_wrong.shape}"
)

try:
    X @ W_wrong
except ValueError as error:
    print(f"오류 발생: {error}")

W_fixed = np.random.randn(
    X.shape[1],
    3,
)

fixed_result = X @ W_fixed

print(
    f"W_fixed Shape: "
    f"{W_fixed.shape}"
)
print(
    f"수정 후 결과 Shape: "
    f"{fixed_result.shape}"
)


# 문제 2-2: 전치 Shape와 전치 성질 검증하기
#
# 1. X.T의 Shape를 확인한다.
# 2. (X @ W).T와 W.T @ X.T를 비교한다.
# 3. X.T @ W.T가 가능한지 확인한다.

left = (X @ W).T
right = W.T @ X.T

print("\n[문제 2-2]")
print(f"X Shape: {X.shape}")
print(f"X.T Shape: {X.T.shape}")
print(f"W Shape: {W.shape}")
print(f"W.T Shape: {W.T.shape}")
print(
    f"(X @ W).T Shape: "
    f"{left.shape}"
)
print(
    f"W.T @ X.T Shape: "
    f"{right.shape}"
)
print(
    "두 결과 일치 여부:",
    np.allclose(
        left,
        right,
    ),
)

try:
    X.T @ W.T
except ValueError as error:
    print(
        f"X.T @ W.T 오류: "
        f"{error}"
    )

print(
    "행렬곱을 전치하면 "
    "각 행렬의 전치와 함께 "
    "곱셈 순서도 반대로 바뀝니다."
)
