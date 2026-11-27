"""main.py의 todo(...) 부분을 작성하세요. support.py와 checks.py는 그대로 사용합니다."""

import copy
import hashlib
import json
import sys

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 필요한 자료와 사용자 기억 관리하기
def select_context(items, user_id, now):
    kept = []
    for item in items:
        # allowed = todo("접근 범위, 신뢰, 현행 여부와 만료 조건")
        is_trusted = item["trusted"]
        is_active = item["active"]
        is_accessible = item["user_id"] in ("public", user_id)
        is_unexpired = item["expires_at"] is None or item["expires_at"] > now

        allowed = is_trusted and is_active and is_accessible and is_unexpired

        if allowed:
            kept.append(copy.deepcopy(item))
    # 이유: 높은 우선순위의 자료를 먼저 고르면 어떤 문제가 생기는지 적으세요.
    # 필터링을 먼저 하지 않으면 모델 입력에 들어가면 안되는 정보들이 우선순위가 높게 나왔을 경우 먼저 출력 될 수 있기 때문에 항상 필터링을 해야 한다.
    return sorted(kept, key=lambda item: (-item["priority"], item["id"]))


def memory_action(records, user_id, action, name, value=None):
    support.validate_memory_input(user_id, action, name, value)
    key = f"{user_id}:{name}"
    if action == "read":
        # return todo("현재 사용자의 기억 조회")
        return copy.deepcopy(records.get(key))
    if action == "create":
        if key in records:
            raise ValueError("이미 있는 기억입니다. update를 사용하세요.")
        # records[key] = todo("새 기억 저장")
        records[key] = copy.deepcopy(value)
    elif action == "update":
        if key not in records:
            raise KeyError("수정할 기억이 없습니다.")
        # records[key] = todo("기존 기억 수정")
        records[key] = copy.deepcopy(value)
    elif action == "delete":
        # return todo("현재 사용자의 기억 삭제")
        return records.pop(key, None)
    return copy.deepcopy(records[key])


def build_messages(prefix, question, context, turns, summary):
    data = json.dumps(
        {"reference_data": context, "summary": summary}, ensure_ascii=False
    )
    history = [message for turn in turns for message in turn["messages"]]
    # 이유: 장기 기억과 세션 상태의 차이, 자료와 지시를 나누는 이유를 적으세요.
    # 장기 기억(style)은 json파일로 저장되서 다음에 다시 열어도 저장되어 있고, 세션(task)은 메모리 안에 저장되어서 세션이 끝나면 휘발된다.
    # 자료와 지시를 나누는 이유는 자료 속 문장을 명령으로 따르면 안되기 때문이다.
    
    # return todo("고정 지시, 참고 자료, 대화, 현재 질문 순서의 메시지")
    return [
        {"role": "developer", "content": prefix},
        {"role": "user", "content": data},
        *history,
        {"role": "user", "content": question},
    ]


# 필수 2. 긴 대화를 줄이고 반복 입력 재사용하기
def summarize(turns):
    summary = {}
    for turn in turns:
        for name, value in support.fact_lines(turn["messages"][0]["content"]):
            #summary[name] = todo("최신 값과 출처 턴")
            summary[name] = {"value" : value, "source_turn_id" : turn["id"]}
    return summary


def select_window(turns, limit, reserve, margin, make_messages, count):
    support.validate_budget(limit, reserve, margin)
    #budget = todo("입력에 쓸 수 있는 예산")
    budget = limit - (reserve + margin)
    if budget <= 0 or count(make_messages([])) > budget:
        raise ValueError("고정 입력만으로 예산을 넘었습니다.")
    kept = []
    for turn in reversed(turns):
        candidate = [turn, *kept]
        #if todo("전체 후보 입력이 예산을 넘는지"):
        if count(make_messages(candidate)) > budget:
            break
        kept = candidate
    # 관측: 압축 비교 후 토큰 수, 빠진 사실, 선택한 한도를 기록합니다.
    # run compare --live 결과
    # | 조건             | 한도 | 남은 턴 | 추정 입력 | 실제 입력 | 출력 | 사실 일치 | 추정 비용(USD) | 지연(ms) |
    # |------------------|------|---------|-----------|-----------|------|-----------|----------------|----------|
    # | 전체 대화        | 5000 | T01~T07 | 1999      | 1938      | 45   | 3/3       | 0.0004416      | 3317     |
    # | 최근 대화        | 2300 | T05~T07 | 1744      | 1699      | 57   | 0/3       | 0.0004082      | 1768     |
    # | 요약과 최근 대화 | 2300 | T06~T07 | 1744      | 1695      | 45   | 3/3       | 0.0003930      | 1218     |
    # 요약과 최근 대화를 고른다. 전체 대화보다 토큰이 적고,
    # 최근 대화는 T01~T04가 잘려 사실 일치가 0/3이었지만 요약 덕분에 3/3을 유지했다.
    
    return kept


def cache_key(prefix, user_id):
    #return todo("사용자와 고정 지시로 만드는 캐시 키")
    return hashlib.sha256((user_id + "\n" + prefix).encode("utf-8")).hexdigest()
    # 관측: 실제 캐시 읽기/쓰기와 비용을 확인하고 미관측이면 그대로 적습니다.
    # run cache --live 결과
    # | 호출          | 캐시 쓰기 | 캐시 읽기 | 입력 토큰 | 실제 입력 비용(USD) | 캐시 없을 때(USD) | 지연(ms) |
    # |---------------|-----------|-----------|-----------|---------------------|-------------------|----------|
    # | ① 캐시 비사용 | 0         | 0         | 1533      | 0.0003066           | 0.0003066         | 1419     |
    # | ② 첫 사용     | 1228      | 0         | 1533      | 0.0003680           | 0.0003066         | 969      |
    # | ③ 재사용      | 0         | 1228      | 1533      | 0.0000856           | 0.0003066         | 874      |

    # 첫 사용에서 캐시를 쓰는데 1228개의 토큰을 사용했고, 읽기에서는 재사용에서 1228개의 토큰을 사용했다.
    # 캐시를 사용하지 않았을 때 보다는 첫사용의 비용이 더 늘긴 했지만  재사용에서 비용이 첫 사용에 비해 약 4.3배가량이 줄었다. 비사용에 비해선 3.6 배 가까이 줄었다
    # tainted-document와 unverified-tool이 최종 입력에 없다
    
# 선택 심화 1. 새 대화만 반영하고 변경 이력 남기기
def merge_summary(previous, turns):
    # previous를 직접 바꾸지 않도록 사본 위에서 작업한다.
    result = copy.deepcopy(previous)
    current, changes, processed = result["current"], result["changes"], result["processed_ids"]
    for turn in turns:
        if turn["id"] in processed:  # 이미 읽은 턴은 건너뛰어 재처리해도 결과가 같다.
            continue
        # 한 턴만 summarize에 넣으면 그 턴의 사실이 {"value", "source_turn_id"} 모양으로 나온다.
        for name, fact in summarize([turn]).items():
            before = current.get(name)
            # 값이 실제로 바뀔 때만 이력을 남긴다. 새 항목이나 같은 값 재확인은 출처만 갱신한다.
            if before is not None and before["value"] != fact["value"]:
                changes.append({"name": name, "before": before, "after": fact})
            current[name] = fact
        processed.append(turn["id"])  # 사실이 없는 턴도 처리한 것으로 기록한다.
    return result


if __name__ == "__main__":
    raise SystemExit(support.cli(sys.modules[__name__]))
