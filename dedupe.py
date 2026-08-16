"""필터링된 기사 중 같은 사건을 보도한 것끼리 묶는 기능"""

# 핵심 단어로 치지 않을 흔한 단어들. 어느 정치 기사에나 나올 법한 범용
# 단어(국무회의, 국회 등)까지 포함해서, 이런 단어만으로 서로 다른 사건이
# 잘못 하나로 묶이는 걸 막는다
STOPWORDS = {
    "관련", "위한", "대한", "오늘", "이번", "한다", "했다", "됐다", "등", "및", "그리고",
    "국무회의", "국회", "발표", "개최", "의결", "주재", "진행", "예정",
}

# 단어를 나눌 때 무시할 문장부호
PUNCTUATION = '…"\'“”‘’·『』「」[]()-,.?!:'

# 핵심 단어가 이 개수 이상 겹치면 같은 사건으로 본다
MIN_SHARED_KEYWORDS = 2


def get_outlet(entry):
    """기사 항목에서 언론사 이름을 뽑는다. 정보가 없으면 빈 문자열을 돌려준다."""
    source = entry.get("source")
    return source.get("title", "") if source else ""


def get_headline(entry, outlet):
    """제목 끝에 붙은 '- 언론사' 부분을 떼어내고 순수 헤드라인만 남긴다."""
    suffix = f" - {outlet}"
    if outlet and entry.title.endswith(suffix):
        return entry.title[: -len(suffix)]
    return entry.title


def extract_keywords(headline):
    """헤드라인에서 핵심 단어(명사 후보)만 뽑는다. 완벽한 형태소 분석은 아니다."""
    cleaned = headline
    for ch in PUNCTUATION:
        cleaned = cleaned.replace(ch, " ")
    words = cleaned.split()
    return {word for word in words if len(word) >= 2 and word not in STOPWORDS}


def group_duplicates(entries):
    """제목 핵심 단어가 일정 개수 이상 겹치는 기사끼리 묶어서,
    언론사 수가 많은 그룹부터 정렬해 돌려준다."""
    groups = []
    for entry in entries:
        outlet = get_outlet(entry)
        headline = get_headline(entry, outlet)
        keywords = extract_keywords(headline)

        target = None
        for group in groups:
            if len(keywords & group["keywords"]) >= MIN_SHARED_KEYWORDS:
                target = group
                break

        if target:
            target["items"].append((headline, outlet))
        else:
            groups.append({"keywords": keywords, "items": [(headline, outlet)]})

    groups.sort(key=lambda group: len(group["items"]), reverse=True)
    return groups


def group_entries_by_event(entries):
    """entry 객체를 유지한 채로 제목 핵심 단어가 겹치는 기사끼리 묶는다.
    group_duplicates()와 같은 매칭 기준(MIN_SHARED_KEYWORDS)을 쓰지만,
    화면 출력용 (headline, outlet) 대신 실제 entry를 보존해서 이후 단계
    (본문 추출 등)에 바로 쓸 수 있게 한다. 언론사 수가 많은 그룹부터
    정렬해서 반환한다 — article_picker.py가 "여러 언론사가 다룬 사건
    우선" 순서를 만드는 데 쓴다.

    그룹 대표 키워드는 첫 기사 것으로 고정하지 않고, 기사가 합류할 때마다
    "그 기사의 키워드와의 교집합"으로 갱신한다. 헤드라인 표현이 매체마다
    조금씩 달라도(조사·어순 차이) 그룹 전체가 공유하는 핵심 단어만 남아서,
    그룹이 커질수록 대표 키워드가 무한정 넓어지는 대신 사건을 실제로
    구분 짓는 단어로 점점 좁혀진다."""
    groups = []
    for entry in entries:
        outlet = get_outlet(entry)
        headline = get_headline(entry, outlet)
        keywords = extract_keywords(headline)

        target = None
        for group in groups:
            if len(keywords & group["keywords"]) >= MIN_SHARED_KEYWORDS:
                target = group
                break

        if target:
            target["entries"].append(entry)
            target["keywords"] &= keywords  # 교집합 유지 — 공통 핵심어로 점점 좁혀짐
        else:
            groups.append({"keywords": keywords, "entries": [entry]})

    groups.sort(key=lambda group: len(group["entries"]), reverse=True)
    return groups
