# 실습 문제 1: 문자열 인덱싱과 슬라이싱
#
# 사용자로부터 문자열을 하나 입력받아 다음 내용을 출력한다.
# 1. 첫 번째 문자와 마지막 문자
# 2. 문자열의 앞 3글자와 뒤 3글자
# 3. 문자열을 거꾸로 뒤집은 결과

text = input("문자열을 입력하세요: ")

if text:
    print(
        f"첫 번째 문자: {text[0]}, "
        f"마지막 문자: {text[-1]}"
    )
    print(
        f"앞 3글자: {text[:3]}, "
        f"뒤 3글자: {text[-3:]}"
    )
    print(f"뒤집은 문자열: {text[::-1]}")
else:
    print("빈 문자열이 입력되었습니다.")


print("-" * 50)


# 실습 문제 2: 문자열 메서드 활용
#
# 다음 문자열을 이용해 아래 작업을 수행한다.
# 1. 양쪽 공백을 제거한다.
# 2. 소문자로 변환한다.
# 3. "python"이 등장하는 횟수를 구한다.
# 4. "python"을 "java"로 치환한다.
# 5. 공백을 기준으로 문자열을 나누어 리스트로 만든다.

sentence = "   I love Python. Python is powerful!   "

clean_sentence = sentence.strip().lower()
python_count = clean_sentence.count("python")
replaced_sentence = clean_sentence.replace(
    "python",
    "java"
)
word_list = clean_sentence.split()

print(f"정리된 문자열: {clean_sentence}")
print(f"python 등장 횟수: {python_count}")
print(f"치환 결과: {replaced_sentence}")
print(f"단어 리스트: {word_list}")


print("-" * 50)


# 실습 문제 3: 문자열 합치기와 분리
#
# 1. "Hello"와 "Python"을 연결해 "Hello Python!"을 만든다.
# 2. "apple,banana,cherry"를 리스트로 나눈다.
# 3. 리스트를 " | " 구분자로 다시 합친다.

greeting = "Hello"
language = "Python"

message = greeting + " " + language + "!"
print(message)

fruit_text = "apple,banana,cherry"
fruit_list = fruit_text.split(",")
print(fruit_list)

joined_fruits = " | ".join(fruit_list)
print(joined_fruits)
