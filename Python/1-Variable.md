# Python 변수

> 학습일: 2026-08-04

Python에서는 변수를 선언할 때 자료형을 직접 지정하지 않아도 된다.  
변수에 저장한 값에 따라 자료형이 결정된다.

```python
age = 25
name = "leejungsu"
is_active = True
height = 175.5
```

각 변수의 자료형은 다음과 같다.

- `age`: 정수형 `int`
- `name`: 문자열형 `str`
- `is_active`: 불리언형 `bool`
- `height`: 실수형 `float`

변수의 자료형은 `type()`으로 확인할 수 있다.

```python
age = 25

print(type(age))
```

출력:

```text
<class 'int'>
```

---

## 1. 변수 이름 작성하기

변수 이름은 저장된 값의 역할을 알 수 있도록 명확하게 작성하는 것이 좋다.

Python에서는 여러 단어를 밑줄(`_`)로 연결하는 `snake_case` 방식을 주로 사용한다.

```python
player_name = "leejungsu"
player_age = 25
vector_a = [1, 2, 3]
```

불리언 값을 저장하는 변수에는 `is`, `has`, `can` 등을 사용하면 의미를 쉽게 파악할 수 있다.

```python
is_active = True
has_item = False
can_move = True
```

다음과 같이 의미를 알기 어려운 이름은 피하는 것이 좋다.

```python
a = 25
b = True
data = "leejungsu"
```

---

## 2. 문자열 변수 연산

문자열에는 덧셈과 곱셈 연산을 사용할 수 있다.

### 문자열 덧셈

문자열끼리 더하면 두 문자열이 하나로 연결된다.

```python
first_name = "lee"
last_name = "jungsu"

full_name = first_name + last_name

print(full_name)
```

출력:

```text
leejungsu
```

문자열 사이에 공백을 넣고 싶다면 공백 문자열을 함께 더한다.

```python
first_name = "lee"
last_name = "jungsu"

full_name = first_name + " " + last_name

print(full_name)
```

출력:

```text
lee jungsu
```

### 문자열 곱셈

문자열에 정수를 곱하면 문자열이 지정한 횟수만큼 반복된다.

```python
first_name = "lee"

repeat_name = first_name * 3

print(repeat_name)
```

출력:

```text
leeleelee
```

문자열에는 뺄셈과 나눗셈을 사용할 수 없다.

```python
first_name = "lee"

# 오류가 발생한다.
# result = first_name - "l"
# result = first_name / 3
```

---

## 3. 입력값과 변수

`input()`으로 입력받은 값은 항상 문자열형 `str`이다.

```python
name = input("이름을 입력해주세요: ")

print(name)
print(type(name))
```

숫자를 입력받아 계산하려면 `int()` 또는 `float()`로 자료형을 변환해야 한다.

```python
age = int(input("나이를 입력해주세요: "))
height = float(input("키를 입력해주세요: "))

print(age)
print(height)
```

여러 정수를 한 번에 입력받으려면 `split()`과 `map()`을 사용할 수 있다.

```python
num1, num2 = map(
    int,
    input("숫자 두 개를 입력해주세요: ").split()
)

print(num1, num2)
```

---

## 4. 불리언 입력 처리

`bool()`은 문자열의 내용이 `"True"`인지 `"False"`인지 확인하지 않는다.

빈 문자열은 `False`가 되고, 비어 있지 않은 문자열은 모두 `True`가 된다.

```python
print(bool(""))       # False
print(bool("True"))   # True
print(bool("False"))  # True
```

따라서 문자열로 입력받은 `"True"`와 `"False"`를 불리언 값으로 바꾸려면 직접 비교해야 한다.

```python
boolean_text = input(
    "True 또는 False를 입력해주세요: "
).strip().lower()

if boolean_text not in ("true", "false"):
    raise ValueError(
        "True 또는 False만 입력할 수 있습니다."
    )

boolean = boolean_text == "true"

print(boolean)
print(type(boolean))
```

`strip()`은 문자열 앞뒤의 공백을 제거하고, `lower()`는 영문을 소문자로 변환한다.

---

## 5. 종합 예제

변수, 입력, 자료형 변환, 불리언 값, 조건문을 함께 사용한 예제이다.

```python
age = int(
    input("나이를 입력해주세요: ")
)

name = input(
    "이름을 입력해주세요: "
)

num1, num2 = map(
    int,
    input("숫자 두 개를 입력해주세요: ").split()
)

boolean_text = input(
    "True 또는 False를 입력해주세요: "
).strip().lower()

if boolean_text not in ("true", "false"):
    raise ValueError(
        "True 또는 False만 입력할 수 있습니다."
    )

boolean = boolean_text == "true"

print(f"입력된 불리언 값: {boolean}")
print(f"자료형: {type(boolean)}")

if boolean:
    age += 1
    result = num1 + num2

    print(
        f"{age} / {name} / "
        f"{num1} + {num2} = {result}"
    )
else:
    age -= 1
    result = num1 * num2

    print(
        f"{age} / {name} / "
        f"{num1} * {num2} = {result}"
    )
```

---

## 정리

- Python에서는 변수를 선언할 때 자료형을 직접 지정하지 않아도 된다.
- 변수에 저장한 값에 따라 자료형이 결정된다.
- 변수 이름은 값의 역할을 알 수 있도록 작성한다.
- 문자열은 덧셈으로 연결하고 곱셈으로 반복할 수 있다.
- `input()`의 결과는 항상 문자열이므로 필요한 자료형으로 변환해야 한다.
- 문자열 `"False"`를 `bool()`로 변환하면 `True`가 되므로 직접 비교해야 한다.
