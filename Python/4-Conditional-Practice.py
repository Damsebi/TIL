"""Python 조건문 실습.

1. 영화관 티켓 요금 계산
2. BMI 지수로 건강 상태 판정
3. 삼각형 종류 판별
"""


def calculate_ticket_price() -> None:
    """나이에 따라 영화관 티켓 요금을 출력한다."""
    audience_age = int(
        input("관람객의 나이를 입력하세요: ")
    )

    if audience_age < 0 or audience_age > 150:
        print("잘못된 나이입니다.")
        return

    if audience_age <= 6:
        category = "유아"
        price = 0
    elif audience_age <= 18:
        category = "청소년"
        price = 8_000
    elif audience_age <= 64:
        category = "성인"
        price = 12_000
    else:
        category = "시니어"
        price = 6_000

    print(f"{category} 요금은 {price}원입니다.")


def check_bmi() -> None:
    """키와 몸무게를 입력받아 BMI 상태를 출력한다."""
    height_cm, weight_kg = map(
        float,
        input(
            "키(cm)와 몸무게(kg)를 입력하세요: "
        ).split()
    )

    if height_cm <= 0 or weight_kg <= 0:
        print("잘못된 입력입니다.")
        return

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        status = "저체중"
    elif bmi < 23:
        status = "정상"
    elif bmi < 25:
        status = "과체중"
    else:
        status = "비만"

    print(f"BMI: {bmi:.2f}")
    print(f"판정: {status}")


def classify_triangle() -> None:
    """세 변의 길이로 삼각형의 종류를 판별한다."""
    side_a, side_b, side_c = map(
        int,
        input(
            "세 변의 길이를 입력하세요: "
        ).split()
    )

    has_invalid_side = (
        side_a <= 0
        or side_b <= 0
        or side_c <= 0
    )

    violates_triangle_inequality = (
        side_a + side_b <= side_c
        or side_a + side_c <= side_b
        or side_b + side_c <= side_a
    )

    if (
        has_invalid_side
        or violates_triangle_inequality
    ):
        print("삼각형이 아닙니다.")
        return

    if side_a == side_b == side_c:
        triangle_type = "정삼각형"
    elif (
        side_a == side_b
        or side_b == side_c
        or side_a == side_c
    ):
        triangle_type = "이등변 삼각형"
    elif (
        side_a ** 2 + side_b ** 2 == side_c ** 2
        or side_b ** 2 + side_c ** 2 == side_a ** 2
        or side_a ** 2 + side_c ** 2 == side_b ** 2
    ):
        triangle_type = "직각 삼각형"
    else:
        triangle_type = "일반 삼각형"

    print(triangle_type)


def main() -> None:
    """세 가지 실습을 순서대로 실행한다."""
    print("[실습 1] 영화관 티켓 요금 계산")
    calculate_ticket_price()

    print("\n[실습 2] BMI 상태 판정")
    check_bmi()

    print("\n[실습 3] 삼각형 종류 판별")
    classify_triangle()


if __name__ == "__main__":
    main()
