# 1장 2강 실습: 내적과 코사인 유사도
#
# 실행 전 필요한 패키지:
# pip install numpy pandas scikit-learn ucimlrepo

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from ucimlrepo import fetch_ucirepo


# 데이터 준비

retail = fetch_ucirepo(id=352).data.original.copy()

retail = retail.dropna(
    subset=["CustomerID", "StockCode"]
)

M_df = retail.pivot_table(
    index="CustomerID",
    columns="StockCode",
    values="Quantity",
    aggfunc="sum",
    fill_value=0,
)

top_customers = M_df.sum(axis=1).sort_values(
    ascending=False
).head(60).index

M_df = M_df.loc[top_customers]

top_products = M_df.sum(axis=0).sort_values(
    ascending=False
).head(150).index

M_df = M_df[top_products].astype(float)
M = M_df.to_numpy()

print(f"고객-상품 행렬 shape: {M.shape}")


# 문제 1-1: 고객 벡터의 내적 직접 계산하기
#
# 1. M_df에서 0번, 1번 고객의 구매량 벡터 a, b를 추출한다.
# 2. 두 벡터의 shape을 확인한다.
# 3. np.sum(a * b), np.dot(a, b), a @ b의 결과를 비교한다.
# 4. 내적 결과가 스칼라인지 확인한다.

a = M[0]
b = M[1]

dot_manual = np.sum(a * b)
dot_numpy = np.dot(a, b)
dot_operator = a @ b

print("\n[문제 1-1]")
print(f"a shape: {a.shape}")
print(f"b shape: {b.shape}")
print(f"직접 계산한 내적: {dot_manual}")
print(f"np.dot(a, b): {dot_numpy}")
print(f"a @ b: {dot_operator}")
print(
    "세 결과 일치 여부:",
    np.isclose(
        dot_manual,
        dot_numpy,
    )
    and np.isclose(
        dot_numpy,
        dot_operator,
    ),
)
print(f"내적 결과 차원: {np.ndim(dot_numpy)}")
print(f"내적 결과 자료형: {type(dot_numpy)}")


# 문제 1-2: 내적 값이 구매 규모의 영향을 받는지 확인하기
#
# 1. 0번 고객과 모든 고객의 내적을 M @ a로 계산한다.
# 2. 내적을 내림차순으로 정렬한다.
# 3. 자기 자신을 제외한 상위 5명의 고객과 총 구매량을 출력한다.
# 4. 전체 고객의 평균 총 구매량과 비교한다.

dots = M @ a
total_quantity = M.sum(axis=1)

dot_order = np.argsort(dots)[::-1]
top_dot_indices = dot_order[1:6]

top_dot_customers = pd.DataFrame(
    {
        "customer": M_df.index[top_dot_indices],
        "dot": dots[top_dot_indices],
        "total_quantity": total_quantity[
            top_dot_indices
        ],
    }
)

print("\n[문제 1-2]")
print(
    "내적 1위 고객:",
    M_df.index[dot_order[0]],
)
print(
    "기준 고객:",
    M_df.index[0],
)
print(
    "자기 자신과의 내적:",
    dots[0],
)
print(
    "|a|²:",
    np.sum(a ** 2),
)
print("\n자기 자신을 제외한 내적 상위 5명")
print(top_dot_customers)
print(
    "\n전체 고객 평균 총 구매량:",
    total_quantity.mean(),
)


# 문제 2-1: 코사인 유사도를 공식으로 직접 구현하기
#
# 1. 내적을 두 벡터 노름의 곱으로 나누는 cosine() 함수를 만든다.
# 2. 0번 고객과 1번 고객의 코사인 유사도를 계산한다.
# 3. 자기 자신, 스칼라배 벡터, 겹치는 성분이 없는 벡터를 비교한다.

def cosine(vector_a, vector_b):
    return np.dot(
        vector_a,
        vector_b,
    ) / (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )


p = np.array([1.0, 0.0, 2.0])
q = np.array([0.0, 5.0, 0.0])

print("\n[문제 2-1]")
print(
    "고객 0과 고객 1:",
    cosine(a, b),
)
print(
    "고객 0과 자기 자신:",
    cosine(a, a),
)
print(
    "고객 0과 3 * 고객 0:",
    cosine(a, 3 * a),
)
print(
    "겹치는 성분이 없는 벡터:",
    cosine(p, q),
)


# 문제 2-2: 유사 고객 상위 5명 찾기
#
# 1. cosine_similarity(M)으로 전체 고객 간 유사도를 계산한다.
# 2. 고객 ID를 인덱스로 가지는 DataFrame을 만든다.
# 3. 0번 고객 자신을 제외한 코사인 유사도 상위 5명을 출력한다.
# 4. 내적 상위 5명과 코사인 유사도 상위 5명을 비교한다.

similarity_matrix = cosine_similarity(M)

similarity_df = pd.DataFrame(
    similarity_matrix,
    index=M_df.index,
    columns=M_df.index,
)

target_customer = M_df.index[0]

top_cosine = (
    similarity_df.loc[target_customer]
    .drop(index=target_customer)
    .sort_values(ascending=False)
    .head(5)
)

dot_customer_ids = list(
    M_df.index[top_dot_indices]
)
cosine_customer_ids = list(
    top_cosine.index
)

overlap_count = len(
    set(dot_customer_ids)
    & set(cosine_customer_ids)
)

print("\n[문제 2-2]")
print(
    f"유사도 행렬 shape: "
    f"{similarity_matrix.shape}"
)
print("\n코사인 유사도 상위 5명")
print(top_cosine)
print(
    "\n내적 기준 상위 5명:",
    dot_customer_ids,
)
print(
    "코사인 기준 상위 5명:",
    cosine_customer_ids,
)
print(
    "두 목록에 함께 포함된 고객 수:",
    overlap_count,
)
