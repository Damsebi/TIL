# 1장 1강 실습: 벡터의 수학적 정의와 기하학적 해석
#
# 실행 전 필요한 패키지:
# pip install numpy pandas ucimlrepo

import numpy as np
import pandas as pd
from ucimlrepo import fetch_ucirepo


# 데이터 준비

wine_quality = fetch_ucirepo(id=186)

X = wine_quality.data.features.copy()
X = X.select_dtypes(include="number")
X = X.fillna(X.median(numeric_only=True))

print(f"데이터 shape: {X.shape}")


# 문제 1-1: 스칼라·벡터·행렬 구분하기
#
# 1. X에서 첫 번째 샘플의 측정값을 v1으로 추출한다.
# 2. X 전체 표, v1, v1의 첫 번째 원소와 shape을 출력한다.
# 3. 각 대상이 행렬, 벡터, 스칼라 중 무엇인지 확인한다.

v1 = X.iloc[0].to_numpy()

print("\n[문제 1-1]")
print(X)
print(f"X shape: {X.shape}")
print(f"v1: {v1}")
print(f"v1 shape: {v1.shape}")
print(f"v1의 첫 번째 원소: {v1[0]}")

print("X는 행렬입니다.")
print("v1은 벡터입니다.")
print("v1의 첫 번째 원소는 스칼라입니다.")


# 문제 1-2: 벡터의 덧셈과 스칼라 곱 계산하기
#
# 1. 두 번째 샘플의 측정값을 v2로 추출한다.
# 2. 두 샘플의 평균 벡터를 (v1 + v2) * 0.5로 계산한다.
# 3. v1의 각 성분을 2배로 키운 2 * v1을 계산한다.

v2 = X.iloc[1].to_numpy()

mean_vector = (v1 + v2) * 0.5
doubled_vector = 2 * v1

print("\n[문제 1-2]")
print(f"v2: {v2}")
print(f"두 샘플의 평균 벡터: {mean_vector}")
print(f"2 * v1: {doubled_vector}")


# 문제 2-1: L1·L2·L∞ 노름 계산하기
#
# 1. v1의 L1, L2, L∞ 노름을 계산한다.
# 2. L2 노름을 직접 계산한 결과와 np.linalg.norm() 결과를 비교한다.

l1_norm = np.sum(np.abs(v1))
l2_norm_direct = np.sqrt(np.sum(v1 ** 2))
l2_norm = np.linalg.norm(v1, ord=2)
l_inf_norm = np.max(np.abs(v1))

print("\n[문제 2-1]")
print(f"L1 노름: {l1_norm}")
print(f"직접 계산한 L2 노름: {l2_norm_direct}")
print(f"np.linalg.norm()으로 계산한 L2 노름: {l2_norm}")
print(f"L2 계산 결과 일치 여부: {np.isclose(l2_norm_direct, l2_norm)}")
print(f"L∞ 노름: {l_inf_norm}")


# 문제 2-2: 정규화로 단위벡터 만들기
#
# 1. v1을 자신의 L2 노름으로 나누어 단위벡터 u1을 만든다.
# 2. u1의 L2 노름이 1인지 확인한다.
# 3. 앞 5개 샘플의 정규화 전후 노름을 비교한다.

u1 = v1 / l2_norm
u1_norm = np.linalg.norm(u1, ord=2)

sample = X.iloc[:5].copy()
norm_before = np.linalg.norm(sample.to_numpy(), axis=1)

normalized_sample = sample.div(norm_before, axis=0)
norm_after = np.linalg.norm(
    normalized_sample.to_numpy(),
    axis=1
)

comparison = pd.DataFrame(
    {
        "정규화 전 노름": norm_before,
        "정규화 후 노름": norm_after,
    },
    index=sample.index,
)

print("\n[문제 2-2]")
print(f"단위벡터 u1: {u1}")
print(f"u1의 L2 노름: {u1_norm}")
print(comparison)
