# Python 문자열

> 학습일: 2026-08-06

Python에서는 문자열을 작은따옴표(`'`) 또는 큰따옴표(`"`)로 표현할 수 있다.

```python
text1 = 'Hello'
text2 = "Python"
```

두 방식의 동작은 같기 때문에 문자열 안에 포함된 따옴표에 맞춰 선택하면 된다.

```python
message1 = "I'm studying Python."
message2 = '그는 "안녕하세요"라고 말했다.'
```

여러 줄로 이루어진 문자열은 작은따옴표나 큰따옴표를 세 개 연속해서 작성한다.

```python
message = """첫 번째 줄
두 번째 줄
세 번째 줄"""

print(message)
```

여러 줄 문자열은 긴 텍스트를 저장하거나 함수와 클래스의 설명을 작성하는 문서화 문자열에 주로 사용한다.

---

## 1. 문자열 인덱싱

문자열의 각 문자는 인덱스를 이용해 가져올 수 있다.

인덱스는 `0`부터 시작하며, 음수 인덱스는 문자열의 뒤에서부터 접근한다.

```python
text = "Python"

print(text[0])   # P
print(text[1])   # y
print(text[-1])  # n
print(text[-2])  # o
```

---

## 2. 문자열 슬라이싱

문자열의 일부분을 가져올 때는 슬라이싱을 사용한다.

```text
문자열[start:end:step]
```

- `start`: 시작 인덱스
- `end`: 종료 인덱스이며, 해당 인덱스는 포함하지 않는다.
- `step`: 문자를 가져올 간격

각 항목은 필요에 따라 생략할 수 있다.

### 예제 1: 문자열 슬라이싱

```python
text = "hello, World!"

print(text[0:5])    # hello
print(text[7:])     # World!
print(text[:5])     # hello
print(text[-6:-1])  # World
print(text[::])     # hello, World!
print(text[::2])    # hlo ol!
```

`end`에 작성한 인덱스는 결과에 포함되지 않는다.

```python
text = "Python"

print(text[0:3])  # Pyt
```

`step`에 `-1`을 넣으면 문자열을 뒤집을 수 있다.

```python
text = "Python"

reversed_text = text[::-1]

print(reversed_text)
```

출력:

```text
nohtyP
```

---

## 3. 문자열 반복과 길이

문자열에 정수를 곱하면 문자열이 지정한 횟수만큼 반복된다.

```python
text = "Hi! "

print(text * 3)
```

출력:

```text
Hi! Hi! Hi!
```

`len()` 함수는 문자열의 길이를 반환한다.

```python
text = "Python"

print(len(text))
```

출력:

```text
6
```

공백과 특수문자도 문자열의 길이에 포함된다.

---

## 4. 대소문자 변환

`upper()`는 모든 영문을 대문자로 변환하고, `lower()`는 소문자로 변환한다.

```python
text = "Hello Python"

print(text.upper())
print(text.lower())
```

출력:

```text
HELLO PYTHON
hello python
```

사용자 입력이나 데이터의 형식을 통일할 때 활용하기 좋다.

```python
answer = input("yes 또는 no를 입력하세요: ").strip().lower()

if answer == "yes":
    print("동의했습니다.")
```

---

## 5. 문자열 검색

문자열에서 특정 문자의 위치를 찾을 때 `find()` 또는 `index()`를 사용할 수 있다.

```python
text = "Hello Python"

print(text.find("Python"))
print(text.index("Python"))
```

두 메서드 모두 찾은 문자열의 시작 인덱스를 반환한다.

문자열을 찾지 못했을 때의 동작은 다르다.

```python
text = "Hello Python"

print(text.find("Java"))   # -1
print(text.index("Java"))  # ValueError 발생
```

- `find()`: 찾지 못하면 `-1`을 반환한다.
- `index()`: 찾지 못하면 `ValueError`를 발생시킨다.

문자열이 몇 번 등장하는지 확인할 때는 `count()`를 사용할 수 있다.

```python
text = "Python is easy. Python is powerful."

print(text.count("Python"))
```

---

## 6. 공백 제거

`strip()`은 문자열 양쪽 끝의 공백을 제거한다.

```python
text = "   Hello Python   "

clean_text = text.strip()

print(clean_text)
```

왼쪽 또는 오른쪽 공백만 제거할 수도 있다.

```python
text = "   Hello Python   "

print(text.lstrip())
print(text.rstrip())
```

- `lstrip()`: 왼쪽 공백 제거
- `rstrip()`: 오른쪽 공백 제거

---

## 7. 문자열 분리와 결합

### `split()`

`split()`은 문자열을 구분자를 기준으로 나누고 리스트로 반환한다.

```python
fruits = "apple,banana,cherry"

fruit_list = fruits.split(",")

print(fruit_list)
```

출력:

```text
['apple', 'banana', 'cherry']
```

구분자를 생략하면 연속된 공백을 기준으로 문자열을 나눈다.

```python
text = "Python   is   easy"

words = text.split()

print(words)
```

출력:

```text
['Python', 'is', 'easy']
```

### `join()`

`join()`은 여러 문자열을 하나의 문자열로 결합한다.

```python
words = ["Python", "is", "easy"]

sentence = " ".join(words)

print(sentence)
```

출력:

```text
Python is easy
```

다른 구분자를 사용할 수도 있다.

```python
fruits = ["apple", "banana", "cherry"]

result = " | ".join(fruits)

print(result)
```

출력:

```text
apple | banana | cherry
```

---

## 8. 문자열은 불변 객체

Python의 문자열은 생성된 뒤 내부 문자를 직접 변경할 수 없는 불변 객체이다.

다음 코드는 오류가 발생한다.

```python
text = "Hello"

# TypeError 발생
# text[0] = "Y"
```

문자열을 변경하려면 필요한 부분을 조합해 새로운 문자열을 만들어야 한다.

### 예제 2: 새로운 문자열 만들기

```python
text = "Hello"

new_text = "Y" + text[1:]

print(new_text)
```

출력:

```text
Yello
```

`replace()`와 같은 문자열 메서드도 기존 문자열을 직접 변경하는 것이 아니라 새로운 문자열을 반환한다.

```python
text = "Hello Python"

new_text = text.replace("Python", "Java")

print(text)
print(new_text)
```

---

## 실습

문자열의 인덱싱과 슬라이싱으로 필요한 문자를 추출하고, `strip()`, `lower()`, `count()`, `replace()` 등의 문자열 메서드를 활용해 문자열을 가공했다. 또한 `split()`으로 문자열을 리스트로 분리하고, `join()`으로 다시 하나의 문자열로 결합하는 방법을 실습했다.

- [문자열 실습 코드](./3-String-Practice.py)

---

## 정리

- 문자열은 작은따옴표와 큰따옴표로 표현할 수 있다.
- 여러 줄 문자열은 따옴표 세 개를 사용한다.
- 슬라이싱은 `[start:end:step]` 형식이며 `end` 인덱스는 포함하지 않는다.
- `[::-1]`을 사용하면 문자열을 뒤집을 수 있다.
- 문자열에 정수를 곱하면 반복되고, `len()`은 문자열의 길이를 반환한다.
- `upper()`와 `lower()`는 영문 대소문자를 변환한다.
- `find()`는 검색 실패 시 `-1`, `index()`는 오류를 발생시킨다.
- `strip()`은 양쪽 공백을 제거한다.
- `split()`은 문자열을 리스트로 나누고, `join()`은 문자열을 하나로 합친다.
- 문자열은 불변 객체이므로 수정 결과를 새로운 변수에 저장해야 한다.
