"""main.py가 처리할 기사 후보를 모으고, 조건을 만족하는 첫 기사를 고르는 기능"""

from collect import KEYWORDS, build_search_url, fetch_feed
from filters import filter_entries, is_multi_topic_broadcast
from dedupe import get_outlet, get_headline, group_entries_by_event
from extract import resolve_real_url, get_article_text

LOG_TOP_GROUPS = 10  # 사건 그룹을 로그에 몇 개까지 남길지


def find_candidate_articles():
    """키워드 순서대로 기사를 모아 필터(제목 기준)를 통과한 후보를 모은다.
    같은 사건을 여러 언론사가 다뤘는지(제목 핵심 단어 겹침)로 사건 그룹을
    나누고, 언론사 수가 많은 그룹부터 앞에 오도록 정렬해서 돌려준다 —
    여러 곳이 다룬 사건일수록 먼저 시도된다. 필터별 제외 건수와 사건
    그룹 상위 목록을 로그에 남겨서 "왜 이게 뽑혔는지" 나중에 추적할 수
    있게 한다."""
    candidates = []
    total_counts = {"의견": 0, "지역 홍보": 0, "사진/멀티미디어": 0}
    for keyword in KEYWORDS:
        feed = fetch_feed(build_search_url(keyword))
        if not feed or not feed.entries:
            continue
        filtered_entries, counts, _ = filter_entries(feed.entries)
        candidates.extend(filtered_entries)
        for key, value in counts.items():
            total_counts[key] += value
    print(f"필터 제외 건수: {total_counts}")

    groups = group_entries_by_event(candidates)
    print(f"사건 그룹 {len(groups)}개로 정리, 언론사 수 순 상위 {min(LOG_TOP_GROUPS, len(groups))}개:")
    for i, group in enumerate(groups[:LOG_TOP_GROUPS], start=1):
        first_outlet = get_outlet(group["entries"][0])
        headline = get_headline(group["entries"][0], first_outlet)
        print(f"  {i}. ({len(group['entries'])}곳) {headline} - {first_outlet}")

    return [entry for group in groups for entry in group["entries"]]


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
