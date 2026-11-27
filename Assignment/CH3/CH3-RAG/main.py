"""KANT NEXT DevDesk RAG. 이 파일의 빈칸만 작성하세요."""

from qdrant_client import models

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 문서를 저장하고 현행 자료만 검색하기
def prepare_chunks(documents):
    chunks = []
    for document in documents:
        seen = set()
        number = 0
        for paragraph in document["paragraphs"]:
            text = " ".join(paragraph.split())
            if not text or text == "KANT NEXT | 내부 문서" or text in seen:
                continue
            seen.add(text)
            # chunk = todo("문서 정보 5개와 chunk_id, text를 담은 사전을 만드세요.")
            chunk = {
                "title": document["title"],
                "status": document["status"],
                "category": document["category"],
                "source": document["source"],
                "document_id": document["document_id"],
                "chunk_id": document["document_id"] + ":" + str(number),
                "text": text
            }
            chunks.append(chunk)
            number += 1
    # 이유: 문단을 유지하는 이유와 보존해야 할 메타데이터를 한두 줄로 적으세요.
    # 데이터가 처음부터 문단으로 나누어져 있고, 문단하나가 상한보다 짧기 때문에 굳이 더 복잡한 청킹 기법을 사용할 필요가 없기 때문이다. 글자로 자르는것 보다 내용을 보존할 수 있다.
    # 보존해야할 메타데이터는 검색 정확도를 높이는 title, 근거중에서 현재상태인지 확인하는 status와 맞는 근거인지 확인하기 위한 category, 근거를 확인하기 위한 source, 답변에서 표시하기 위한 chunk_id와 평가에 사용하기 위한 document_id
    return chunks


def build_index(chunks, embedder):
    texts = ["passage: " + row["title"] + "\n" + row["text"] for row in chunks]
    #vectors = todo("texts를 정규화된 문서 벡터로 바꾸세요.")
    #vector = embedder.encode(["query: " + question], normalize_embeddings=True)[0]
    vectors = embedder.encode(texts, normalize_embeddings=True)
    client = support.empty_store(len(vectors[0]))
    points = []
    for i, (row, vector) in enumerate(zip(chunks, vectors, strict=True)):
        #point = todo("i, vector, row를 Qdrant PointStruct에 연결하세요.")
        point = models.PointStruct(id=i, vector=vector, payload=row)
        points.append(point)
    client.upsert(collection_name="devdesk", points=points, wait=True)
    return client


def search(client, embedder, question, category, top_k=2):
    if type(top_k) is not int or not 1 <= top_k <= 5:
        raise ValueError("top_k는 1~5의 정수여야 합니다.")
    vector = embedder.encode(["query: " + question], normalize_embeddings=True)[0]
    #scope = todo("현행 문서이면서 지정한 category인 Qdrant 필터를 만드세요.")
    scope = models.Filter(
        must=[
            models.FieldCondition(key="status", match=models.MatchValue(value="current")),
            models.FieldCondition(key="category", match=models.MatchValue(value=category))                        
        ]
    )
    hits = client.query_points(
        collection_name="devdesk",
        query=list(vector),
        query_filter=scope,
        limit=top_k,
        with_payload=True,
    ).points
    return [{**hit.payload, "score": hit.score} for hit in hits]


# 필수 2. 별칭 검색을 개선하고 답변을 비교하기
def rewrite_query(question, aliases):
    rewritten = question
    for alias, formal_name in aliases.items():
        #rewritten = todo("현재 문자열에서 alias를 formal_name으로 바꾸세요.")
        rewritten = rewritten.replace(alias, formal_name)
    return rewritten


def answer_question(question, rows, generate):
    if not rows:
        return {
            "answer": "확인할 문서가 없습니다.",
            "citations": [],
            "needs_human": True,
        }
    #context = todo("각 검색 결과를 [chunk_id] 본문으로 묶고 빈 줄로 연결하세요.")
    context = []
    for row in rows:
        temp = "[" + row["chunk_id"] + "] " + row["text"]
        context.append(temp)
    context = "\n\n".join(context)
    reply = support.validate_shape(generate(question, context))
    allowed = {row["chunk_id"] for row in rows}
    #if todo("검색 결과에 없는 출처가 하나라도 있는지 검사하세요."):
    for temp in reply["citations"]:
        if temp not in allowed:
            raise ValueError("검색하지 않은 출처가 있습니다.")
    if reply["needs_human"] == bool(reply["citations"]):
        raise ValueError("답변에는 출처가 필요하며 담당자 확인에는 출처를 비웁니다.")
    return reply


def make_golden():
    #return todo("답이 있는 사례와 자료가 없는 사례를 하나씩 작성하세요.")
    return [
        {
            "question_id": "vpn-test-01",
            "question": "초록문을 하려면 어떻게 해야 하나요?",
            "category": "access",
            "reference_answer": "VPN 원격 접속을 사용하려면 보안팀에 승인을 요청해야 합니다. 승인 후 회사 계정으로 로그인하고 다중 인증을 완료합니다.",
            "relevant_document_ids": ["vpn"],
            "required_terms": ["보안팀", "승인", "요청"]
        },
        {
            "question_id": "vpn-test-02",
            "question": "빨간문에 푸른열쇠를 하고 싶어요",
            "category": "overseas",
            "reference_answer": "확인할 문서가 없습니다.",
            "relevant_document_ids": [],
            "required_terms": []
        },
    ]


def measure(case, rows, reply):
    expected = set(case["relevant_document_ids"])
    found = {row["document_id"] for row in rows}
    #recall = todo("필요한 문서 중 찾은 비율을 계산하세요. 필요한 문서가 없으면 None입니다.")
    if expected:
        recall = len(expected - (expected - found)) / len(expected)
    else:
        recall = None
    answer_ok = (
        (
            all(term in reply["answer"] for term in case["required_terms"])
            and not reply["needs_human"]
        )
        if expected
        else reply["needs_human"]
    )
    failure = "없음"
    if expected and recall < 1:
        failure = "검색 누락"
    elif not answer_ok:
        failure = "답변 확인 필요" if expected else "보류 실패"
    # 관측: 실제 evaluate 결과에서 개선, 악화 질문과 답변 본문을 확인해 기록합니다.
    return {
        "document_recall": recall,
        "answer_check": bool(answer_ok),
        "failure": failure,
    }


# 선택 심화 1. 두 검색 순위를 합쳐 근거를 모으기
def fuse_rankings(rankings, top_k=2):
    # 선택 심화: 문제의 RRF 규칙에 맞춰 직접 작성하세요.
    # type(...) is not int로 검사해야 bool(True/False)도 걸러집니다.
    if type(top_k) is not int or not 1 <= top_k <= 5:
        raise ValueError("top_k는 1~5의 정수여야 합니다.")
    scores = {}  # chunk_id -> 합친 RRF 점수
    first = {}   # chunk_id -> 처음 등장한 청크 사전
    for ranking in rankings:
        seen = []  # 이 목록 안에서 중복을 뺀 chunk_id 순서
        for row in ranking:
            if row["chunk_id"] not in seen:
                seen.append(row["chunk_id"])
                if row["chunk_id"] not in first:
                    first[row["chunk_id"]] = row
        for rank, key in enumerate(seen, start=1):
            scores[key] = scores.get(key, 0) + 1 / (60 + rank)
    # 점수 내림차순, 동점이면 chunk_id 오름차순
    order = sorted(scores, key=lambda key: (-scores[key], key))
    # 새 사전을 만들어 score만 바꾸므로 입력 사전은 바뀌지 않습니다.
    return [{**first[key], "score": scores[key]} for key in order[:top_k]]


if __name__ == "__main__":
    support.cli(globals())
