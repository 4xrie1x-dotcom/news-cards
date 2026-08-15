"""main.py가 처리할 기사 후보를 모으고, 조건을 만족하는 첫 기사를 고르는 기능"""

from collect import KEYWORDS, build_search_url, fetch_feed
from filters import filter_entries, is_multi_topic_broadcast
from dedupe import get_outlet
from extract import resolve_real_url, get_article_text


def find_candidate_articles():
    """키워드 순서대로 기사를 모아 필터(제목 기준)를 통과한 후보 목록을 돌려준다."""
    candidates = []
    for keyword in KEYWORDS:
        feed = fetch_feed(build_search_url(keyword))
        if not feed or not feed.entries:
            continue
        filtered_entries, _, _ = filter_entries(feed.entries)
        candidates.extend(filtered_entries)
    return candidates


def extract_first_valid_article(candidates):
    """후보를 순서대로 시도해서, 추출 성공 + 다중 소재 아님을 만족하는
    첫 기사의 (entry, 실제 주소, 본문)을 돌려준다. 없으면 (None, None, None)이다.
    조건에 안 맞는 후보는 건너뛰고 이유를 화면에 출력한다."""
    for candidate in candidates:
        outlet = get_outlet(candidate)
        url = resolve_real_url(candidate.link)
        if not url:
            print(f"건너뜀: [{outlet}] 실제 주소를 얻지 못함 - {candidate.title}")
            continue
        text = get_article_text(url, candidate.title)
        if not text:
            print(f"건너뜀: [{outlet}] 본문 추출 실패 - {candidate.title}")
            continue
        if is_multi_topic_broadcast(text):
            print(f"건너뜀: [{outlet}] 다중 소재 방송 리포트로 판단 - {candidate.title}")
            continue
        return candidate, url, text
    return None, None, None
