# Python 입력과 출력

> 학습일: 2026-08-04

Python에서는 `print()`를 사용해 값을 출력하고, `input()`을 사용해 사용자에게 값을 입력받는다.

---

## 1. 출력: `print()`

### 1.1 f-string으로 문자열 포매팅하기

문자열 안에 변수나 계산 결과를 넣고 싶을 때는 f-string을 사용할 수 있다.

문자열 앞에 `f`를 붙이고, 중괄호 `{}` 안에 변수나 표현식을 작성한다.

```python
name = "leejungsu"
age = 25

print(f"name: {name}, age: {age}")
```

출력:

```text
name: leejungsu, age: 25
```

f-string은 문자열과 변수를 함께 출력할 때 자주 사용한다.

---

### 1.2 `end`로 출력 끝 문자 바꾸기

`print()`는 기본적으로 출력이 끝난 뒤 줄바꿈을 한다.

`end` 값을 지정하면 줄바꿈 대신 다른 문자열을 출력할 수 있다.

```python
print("hello!", end=" ")
print("my name is leejungsu")
```

출력:

```text
hello! my name is leejungsu
```

줄바꿈을 완전히 없애려면 다음처럼 작성한다.

```python
print("hello!", end="")
print("my name is leejungsu")
```

출력:

```text
hello!my name is leejungsu
```

---

### 1.3 `sep`으로 출력 구분자 바꾸기

`print()`에 여러 값을 전달하면 기본적으로 공백으로 구분된다.

`sep`을 사용하면 값 사이에 들어갈 구분자를 직접 지정할 수 있다.

```python
year = 2026
month = 8
day = 6

print(year, month, day, sep="-")
```

출력:

```text
2026-8-6
```

다른 구분자를 사용할 수도 있다.

```python
print("Python", "Unity", "Git", sep=" | ")
```

출력:

```text
Python | Unity | Git
```

---

### 1.4 f-string으로 계산 결과 출력하기

f-string의 중괄호 안에는 변수뿐 아니라 계산식도 작성할 수 있다.

```python
num1 = 11
num2 = 5

print(f"{num1} + {num2} = {num1 + num2}")
print(f"{num1} - {num2} = {num1 - num2}")
print(f"{num1} * {num2} = {num1 * num2}")
print(f"{num1} / {num2} = {num1 / num2}")
print(f"{num1} // {num2} = {num1 // num2}")
print(f"{num1} % {num2} = {num1 % num2}")
```

출력:

```text
11 + 5 = 16
11 - 5 = 6
11 * 5 = 55
11 / 5 = 2.2
11 // 5 = 2
11 % 5 = 1
```

연산자의 의미:

- `/`: 나눗셈
- `//`: 몫
- `%`: 나머지

---

## 2. 입력: `input()`

Python에서는 `input()`을 사용해 사용자에게 값을 입력받는다.

괄호 안에 문자열을 작성하면 입력 안내 문구로 사용할 수 있다.

```python
name = input("안녕하세요. 이름을 입력하세요: ")
```

`input()`으로 입력받은 값은 항상 문자열(`str`)이다.

---

### 2.1 문자열 입력받기

```python
name = input("input name: ")

print(f"hello {name}, sir")
```

---

### 2.2 정수 입력받기

숫자를 계산에 사용하려면 `int()`로 변환해야 한다.

```python
age = int(input("input your age: "))

print(f"your age is {age + 1} next year")
```

---

### 2.3 실수 입력받기

실수 값을 입력받으려면 `float()`로 변환한다.

```python
height = float(input("input your height: "))

print(f"your height is {height} cm")
```

---

### 2.4 여러 값 입력받기

공백으로 구분된 여러 값을 입력받을 때는 `split()`과 `map()`을 함께 사용할 수 있다.

```python
num1, num2 = map(int, input("숫자 두 개를 입력하세요: ").split())

print(num1, num2)
```

동작 과정:

1. `input()`으로 문자열을 입력받는다.
2. `split()`으로 문자열을 공백 기준으로 나눈다.
3. `map(int, ...)`으로 각 문자열을 정수로 변환한다.
4. 변환된 값을 `num1`, `num2`에 저장한다.

입력:

```text
10 20
```

출력:

```text
10 20
```

---

### 2.5 여러 값을 리스트로 입력받기

입력 개수가 정해져 있지 않다면 리스트로 저장할 수 있다.

```python
num_list = list(map(int, input("숫자를 입력하세요: ").split()))

print(num_list)
```

입력:

```text
1 2 3 4 5
```

출력:

```text
[1, 2, 3, 4, 5]
```

---

### 2.6 다른 구분자로 입력받기

`split()` 안에 구분자를 지정하면 공백이 아닌 다른 문자를 기준으로 나눌 수 있다.

```python
number1, number2 = map(int, input("두 숫자를 #으로 구분해 입력하세요: ").split("#"))

print(number1, number2)
```

입력:

```text
10#20
```

출력:

```text
10 20
```

여러 값을 리스트로 저장할 수도 있다.

```python
number_list = list(
    map(
        int,
        input("숫자를 #으로 구분해 입력하세요: ").split("#")
    )
)

print(number_list)
```

입력:

```text
1#2#3#4
```

출력:

```text
[1, 2, 3, 4]
```

---

## 3. 입력값을 이용한 계산기 예제

여러 숫자와 연산자를 입력받아 계산하는 간단한 예제이다.

```python
while True:
    operator = input("input operator (+, -, *, /, q): ").lower()

    if operator == "q":
        print("프로그램을 종료합니다.")
        break

    if operator not in ["+", "-", "*", "/"]:
        print("잘못된 연산자입니다.")
        continue

    num_list = list(
        map(
            float,
            input("input numbers: ").split()
        )
    )

    if len(num_list) == 0:
        print("숫자를 한 개 이상 입력해주세요.")
        continue

    result = num_list[0]

    try:
        for num in num_list[1:]:
            if operator == "+":
                result += num
            elif operator == "-":
                result -= num
            elif operator == "*":
                result *= num
            elif operator == "/":
                result /= num

        print(f"result: {result}")

    except ZeroDivisionError:
        print("0으로 나눌 수 없습니다.")
```

실행 예시:

```text
input operator (+, -, *, /, q): +
input numbers: 10 20 30
result: 60.0
```

---

## 정리

- `print()`는 값을 출력할 때 사용한다.
- f-string을 사용하면 문자열 안에 변수와 계산식을 쉽게 넣을 수 있다.
- `end`는 출력이 끝난 뒤 들어갈 문자열을 지정한다.
- `sep`은 여러 출력값 사이의 구분자를 지정한다.
- `input()`의 결과는 항상 문자열이다.
- 숫자로 사용하려면 `int()` 또는 `float()`로 변환해야 한다.
- 여러 값을 입력받을 때는 `split()`과 `map()`을 함께 사용할 수 있다.
