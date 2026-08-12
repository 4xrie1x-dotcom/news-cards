"""수집한 기사 중 의견·지역 홍보·사진 게시물을 걸러내는 필터 모음"""

# 제목에 이 표시가 있으면 의견 기사로 보고 제외한다
OPINION_TAGS = [
    "[사설]", "[칼럼]", "[기자의 눈]", "[기고]",
    "[논설실 Pick]", "[논설]", "[시론]", "[데스크]", "[오피니언]", "[전문가 칼럼]",
]

# 지역 동정·홍보성 기사로 보고 제외할 표시와 문구
# [포토]는 사진이 메인이라는 표시일 뿐 본문이 없다는 뜻은 아니라서 제외 대상에서 뺐다
LOCAL_TAGS = ["[동정]", "[게시판]", "[인사]", "[부고]", "[사진]"]
LOCAL_PHRASES = ["국비 확보", "간담회", "협력망 구축"]


def is_opinion(title):
    """제목에 의견 기사 표시가 있으면 True를 반환한다."""
    return any(tag in title for tag in OPINION_TAGS)


def is_local_promo(title):
    """제목에 지역 동정·홍보성 표시나 문구가 있으면 True를 반환한다."""
    if any(tag in title for tag in LOCAL_TAGS):
        return True
    return any(phrase in title for phrase in LOCAL_PHRASES)


def is_photo_multimedia(title, link):
    """제목에 '사진'과 '멀티미디어'가 함께 있으면 본문 없는 사진 게시물로 보고 True를 반환한다.
    둘 다 있어야 확실한 표시로 보고, 단어 하나만으로는 걸러내지 않는다."""
    return "사진" in title and "멀티미디어" in title


def filter_entries(entries):
    """기사를 종류별로 걸러내고, 남긴 목록·종류별 제외 건수·제외된 (기사, 사유) 목록을 반환한다.
    한 기사는 먼저 걸리는 필터 하나에만 속해서, 건수가 서로 겹치지 않게 한다."""
    counts = {"의견": 0, "지역 홍보": 0, "사진/멀티미디어": 0}
    kept = []
    excluded = []
    for entry in entries:
        if is_opinion(entry.title):
            counts["의견"] += 1
            excluded.append((entry, "의견"))
        elif is_local_promo(entry.title):
            counts["지역 홍보"] += 1
            excluded.append((entry, "지역 홍보"))
        elif is_photo_multimedia(entry.title, entry.link):
            counts["사진/멀티미디어"] += 1
            excluded.append((entry, "사진/멀티미디어"))
        else:
            kept.append(entry)
    return kept, counts, excluded
