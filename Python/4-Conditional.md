# Python 조건문

> 학습일: 2026-08-06

Python에서는 조건에 따라 실행할 코드를 나누기 위해 `if`, `elif`, `else`를 사용한다.

다른 언어의 `else if`와 달리 Python에서는 `elif`라고 작성한다.

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("C")
```

Python에서는 중괄호 대신 들여쓰기로 코드 블록을 구분한다.

---

## 1. 기본 조건문

조건식이 `True`이면 `if` 아래의 코드가 실행되고, 그렇지 않으면 `else` 아래의 코드가 실행된다.

### 예제 1: 홀수와 짝수 판별

```python
number = int(input("숫자를 입력하세요: "))

if number % 2 == 0:
    print("짝수입니다.")
else:
    print("홀수입니다.")
```

`number % 2`는 숫자를 2로 나눈 나머지를 의미한다.

- 나머지가 `0`이면 짝수
- 나머지가 `1`이면 홀수

---

## 2. 여러 조건 처리하기

조건이 여러 개일 때는 `elif`를 사용할 수 있다.

```python
temperature = int(input("온도를 입력하세요: "))

if temperature >= 30:
    print("덥습니다.")
elif temperature >= 20:
    print("따뜻합니다.")
elif temperature >= 10:
    print("선선합니다.")
else:
    print("춥습니다.")
```

조건문은 위에서부터 순서대로 검사하며, 처음으로 `True`가 된 블록 하나만 실행한다.

---

## 3. 복합 조건문

여러 조건을 함께 검사할 때는 `and`, `or`, `not`을 사용한다.

### `and`

모든 조건이 `True`일 때만 전체 결과가 `True`가 된다.

```python
age = 20
has_ticket = True

if age >= 19 and has_ticket:
    print("입장할 수 있습니다.")
```

### `or`

조건 중 하나 이상이 `True`이면 전체 결과가 `True`가 된다.

```python
is_weekend = False
is_holiday = True

if is_weekend or is_holiday:
    print("쉬는 날입니다.")
```

### `not`

조건의 결과를 반대로 바꾼다.

```python
is_logged_in = False

if not is_logged_in:
    print("로그인이 필요합니다.")
```

---

## 4. 로그인 조건문 예제

아이디가 일치하지만 비밀번호가 다르면 비밀번호 오류를 출력하고, 아이디가 다르면 존재하지 않는 계정으로 처리한다.

```python
admin_id = "lee"
admin_password = "1234"

input_id, input_password = input(
    "아이디와 비밀번호를 입력하세요: "
).split()

if (
    admin_id == input_id
    and admin_password == input_password
):
    print("login success")
elif (
    admin_id == input_id
    and admin_password != input_password
):
    print("wrong password")
else:
    print("no exist account")
```

두 번째 조건은 아이디가 같고 비밀번호가 다른지를 확인해야 한다.

---

## 5. 조건 표현식

간단한 `if`와 `else`는 한 줄의 조건 표현식으로 작성할 수 있다.

```text
참일 때 값 if 조건식 else 거짓일 때 값
```

예시:

```python
number = int(input("숫자를 입력하세요: "))

result = "짝수" if number % 2 == 0 else "홀수"

print(result)
```

조건 표현식은 짧고 단순한 조건에 사용하는 것이 좋다. 조건이 복잡하면 일반적인 `if` 문으로 작성하는 편이 읽기 쉽다.

---

## 6. `pass`

`pass`는 아무 작업도 하지 않고 넘어가는 문장이다.

조건문, 함수, 클래스의 구조를 먼저 작성했지만 내부 구현은 나중에 추가하려고 할 때 사용할 수 있다.

```python
score = 85

if score >= 90:
    pass
else:
    print("90점 미만입니다.")
```

Python에서는 코드 블록을 비워둘 수 없기 때문에, 임시로 비어 있는 블록을 만들 때 `pass`를 작성한다.

`pass`는 조건을 종료하거나 프로그램을 멈추는 기능이 아니다.

---

## 7. `in`과 `not in`

`in`은 특정 값이 문자열, 리스트, 튜플 등의 자료에 포함되어 있는지 확인한다.

```python
fruits = ["apple", "banana", "cherry"]

if "apple" in fruits:
    print("사과가 있습니다.")
```

`not in`은 특정 값이 포함되어 있지 않은지 확인한다.

```python
fruits = ["apple", "banana", "cherry"]

if "orange" not in fruits:
    print("오렌지가 없습니다.")
```

문자열에서도 사용할 수 있다.

```python
message = "Hello Python"

if "Python" in message:
    print("Python이 포함되어 있습니다.")
```

---

## 실습

영화관 티켓 요금, BMI 상태, 삼각형 종류를 조건문으로 판별하는 문제를 실습했다.

- [조건문 실습 코드](./4-Conditional-Practice.py)

---

## 정리

- Python에서는 `if`, `elif`, `else`로 조건문을 작성한다.
- 여러 조건을 결합할 때는 `and`, `or`, `not`을 사용한다.
- 간단한 조건은 `참일 때 값 if 조건식 else 거짓일 때 값` 형태로 작성할 수 있다.
- `pass`는 아직 구현하지 않은 코드 블록을 임시로 비워둘 때 사용한다.
- `in`과 `not in`은 값이 자료 안에 포함되어 있는지 확인한다.
- 조건문은 위에서부터 순서대로 검사하며 처음으로 참이 된 블록 하나를 실행한다.
