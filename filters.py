"""수집한 기사 중 의견·지역 홍보·사진 게시물을 걸러내는 필터 모음"""

# 제목에 이 표시가 있으면 의견 기사로 보고 제외한다
OPINION_TAGS = [
    "[사설]", "[칼럼]", "[기자의 눈]", "[기고]",
    "[논설실 Pick]", "[논설]", "[시론]", "[데스크]", "[오피니언]", "[전문가 칼럼]",
]

# 지역 동정·홍보성 기사로 보고 제외할 표시와 문구
LOCAL_TAGS = ["[동정]", "[게시판]", "[인사]", "[부고]", "[포토]", "[사진]"]
LOCAL_PHRASES = ["국비 확보", "간담회", "협력망 구축"]

# 본문 없는 사진·멀티미디어 게시물로 보고 제외할 단어
PHOTO_KEYWORDS = ["사진", "멀티미디어", "포토"]


def is_opinion(title):
    """제목에 의견 기사 표시가 있으면 True를 반환한다."""
    return any(tag in title for tag in OPINION_TAGS)


def is_local_promo(title):
    """제목에 지역 동정·홍보성 표시나 문구가 있으면 True를 반환한다."""
    if any(tag in title for tag in LOCAL_TAGS):
        return True
    return any(phrase in title for phrase in LOCAL_PHRASES)


def is_photo_multimedia(title, link):
    """제목이나 링크에 사진·멀티미디어 관련 단어가 있으면 True를 반환한다."""
    text = title + link
    return any(word in text for word in PHOTO_KEYWORDS)


def filter_entries(entries):
    """기사를 종류별로 걸러내고, 걸러낸 목록과 종류별 제외 건수를 함께 반환한다.
    한 기사는 먼저 걸리는 필터 하나에만 속해서, 건수가 서로 겹치지 않게 한다."""
    counts = {"의견": 0, "지역 홍보": 0, "사진/멀티미디어": 0}
    kept = []
    for entry in entries:
        if is_opinion(entry.title):
            counts["의견"] += 1
        elif is_local_promo(entry.title):
            counts["지역 홍보"] += 1
        elif is_photo_multimedia(entry.title, entry.link):
            counts["사진/멀티미디어"] += 1
        else:
            kept.append(entry)
    return kept, counts
