"""추출된 본문에서 사이트 요소를 잘라내고, 잘못 뽑힌 경우를 가려내는 기능"""

from dedupe import extract_keywords

# 이 문구로 시작하는 줄은 본문 앞쪽 사이트 요소로 보고 버린다
FRONT_LINE_PREFIXES = ["기사 본문 영역", "AD", "입력 2026.", "등록 2026.", "수정 2026."]

# 이 문구가 나오면 그 지점부터 뒤는 저작권 안내로 보고 버린다
BACK_MARKERS = ["저작권자", "무단전재", "재배포 금지"]

# 메뉴만 뽑힌 경우로 판단할 사이트 내비게이션 단어들
MENU_MARKERS = ["LIVE", "검색", "English", "日本語"]
MIN_MENU_HITS = 2


def clean_body(text, title):
    """본문 앞뒤의 사이트 요소를 잘라내고, 정리 전후 글자 수도 함께 반환한다."""
    original_length = len(text)
    lines = text.split("\n")
    cleaned_lines = []
    started = False

    for line in lines:
        stripped = line.strip()
        if not started:
            if not stripped:
                continue
            if stripped in title or title in stripped:
                continue
            if any(stripped.startswith(prefix) for prefix in FRONT_LINE_PREFIXES):
                continue
            started = True
        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()
    for marker in BACK_MARKERS:
        index = cleaned.find(marker)
        if index != -1:
            cleaned = cleaned[:index].strip()

    return cleaned, original_length, len(cleaned)


def has_keyword_match(title, body):
    """제목의 핵심 단어가 본문에 하나라도 있으면 True. 없으면 엉뚱한 기사가 뽑힌 것으로 본다.
    제목 끝의 '- 언론사' 부분은 먼저 떼어낸다. 안 그러면 언론사 이름이 바이라인에
    항상 등장해서 어떤 본문과 비교해도 일치한다고 잘못 판단하게 된다."""
    headline = title.rsplit(" - ", 1)[0] if " - " in title else title
    keywords = extract_keywords(headline)
    if not keywords:
        return True
    return any(keyword in body for keyword in keywords)


def is_menu_only(text):
    """글자 수 대신 메뉴 단어 개수로 내비게이션만 뽑힌 경우를 가려낸다."""
    hits = sum(1 for marker in MENU_MARKERS if marker in text)
    return hits >= MIN_MENU_HITS
