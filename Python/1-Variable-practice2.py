age = int(input("나이를 입력해주세요: "))
name = input("이름을 입력해주세요: ")
num1, num2 = map(int, input("숫자 두 개를 입력해주세요: ").split())

boolean_text = input("True 또는 False를 입력해주세요: ").strip().lower()

if boolean_text not in ("true", "false"):
    raise ValueError("True 또는 False만 입력할 수 있습니다.")

boolean = boolean_text == "true"

print(f"입력된 불리언 값: {boolean}")
print(f"자료형: {type(boolean)}")

if boolean:
    age += 1
    result = num1 + num2
    print(f"{age} / {name} / num1 + num2 = {result}")
else:
    age -= 1
    result = num1 * num2
    print(f"{age} / {name} / num1 * num2 = {result}")
