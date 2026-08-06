# Python 변수

> 학습일: 2026-08-04

Python에서는 변수를 선언할 때 자료형을 직접 지정하지 않아도 된다.  
변수에 저장된 값에 따라 자료형이 결정된다.

```python
age = 20
name = "Jungsu"
is_active = True
```

- `age`는 `int`
- `name`은 `str`
- `is_active`는 `bool`

## 변수 이름 작성 규칙

변수 이름은 값의 역할을 알 수 있도록 명확하게 작성한다.

Python에서는 일반적으로 여러 단어를 밑줄(`_`)로 연결하는 `snake_case` 방식을 사용한다.

```python
is_action = True
vector_a = [1, 2, 3]
player_name = "Lee"
```

불리언 값을 저장하는 변수에는 `is`, `has`, `can`과 같은 표현을 사용하면 의미를 파악하기 쉽다.

```python
is_active = True
has_item = False
can_move = True
```

## 예제 1: 문자열 연산

[예제 코드 보기](./1-Variable-practice1.py)

문자열에는 덧셈과 곱셈 연산을 사용할 수 있다.

```python
first_name = "lee"
last_name = "jungsu"

full_name = first_name + " " + last_name
repeat_name = first_name * 3
```

- 문자열끼리 더하면 하나의 문자열로 연결된다.
- 문자열에 정수를 곱하면 해당 문자열이 지정한 횟수만큼 반복된다.
- 문자열에는 뺄셈과 나눗셈을 사용할 수 없다.

## 예제 2: 입력과 자료형 변환

[예제 코드 보기](./1-Variable-practice2.py)

`input()`으로 입력받은 값은 기본적으로 문자열이다.  
숫자로 계산하려면 `int()` 또는 `float()`를 사용해 자료형을 변환해야 한다.

```python
age = int(input("나이를 입력해주세요: "))
num1, num2 = map(int, input("숫자 두 개를 입력해주세요: ").split())
```

문자열을 `bool()`에 바로 전달하면 빈 문자열이 아닌 모든 문자열이 `True`가 된다.

```python
bool("False")  # True
```

따라서 사용자가 입력한 `"True"`와 `"False"`를 직접 비교하여 불리언 값으로 변환하는 것이 안전하다.

```python
boolean_text = input("True 또는 False를 입력해주세요: ").strip().lower()
boolean = boolean_text == "true"
```

## 정리

- Python 변수는 값을 저장할 때 자료형을 직접 선언하지 않아도 된다.
- 변수 이름은 역할을 쉽게 알 수 있도록 작성한다.
- 문자열은 덧셈으로 연결하고 곱셈으로 반복할 수 있다.
- `input()`의 결과는 문자열이므로 필요한 자료형으로 변환해야 한다.
