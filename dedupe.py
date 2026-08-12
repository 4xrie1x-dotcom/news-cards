"""필터링된 기사 중 같은 사건을 보도한 것끼리 묶는 기능"""

# 핵심 단어로 치지 않을 흔한 단어들
STOPWORDS = {"관련", "위한", "대한", "오늘", "이번", "한다", "했다", "됐다", "등", "및", "그리고"}

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
