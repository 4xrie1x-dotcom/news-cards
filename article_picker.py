"""main.py가 처리할 사건 그룹 후보를 모으고, 그룹 안에서 조건을 만족하는
첫 기사를 고르는 기능"""

from functools import cmp_to_key
from collect import KEYWORDS, build_search_url, fetch_feed
from filters import filter_entries, is_multi_topic_broadcast
from dedupe import get_outlet, get_headline, group_entries_by_event
from extract import resolve_real_url, get_article_text

LOG_TOP_GROUPS = 10  # 사건 그룹을 로그에 몇 개까지 남길지
RERANK_TOP_GROUPS = 10  # 언론사 수 상위 몇 개 그룹 안에서 갈등 신호로 재정렬할지
CONFLICT_OVERRIDE_RATIO = 2.5  # 이 배율 미만 차이면 갈등 신호가 언론사 수 열세를 뒤집는다
CONFLICT_KEYWORDS = [
    "공방", "충돌", "대립", "맞서", "비판", "반발", "저지", "몸싸움", "파행", "정면", "vs",
]
# 따옴표 인용은 처음엔 갈등 신호로 넣었으나 뺐다 — 한국 정치 기사는 일방적 발표도
# 관행적으로 따옴표로 인용하는 경우가 대부분이라(예: "4년 중임제가 수용성 높아"),
# 실제로 넣어 테스트해보니 상위 그룹 전부가 갈등 신호로 잘못 표시됐다(2026-08-17 확인)


def has_conflict_signal(group):
    """그룹 안 기사 제목 중 하나라도 갈등 신호 키워드(공방·충돌 등)를
    담고 있으면 True를 반환한다."""
    for entry in group["entries"]:
        outlet = get_outlet(entry)
        headline = get_headline(entry, outlet)
        if any(keyword in headline for keyword in CONFLICT_KEYWORDS):
            return True
    return False


def rerank_top_groups(groups, top_n):
    """언론사 수 상위 top_n개 그룹만 갈등 신호 기준으로 재정렬한다. 언론사
    수 차이가 CONFLICT_OVERRIDE_RATIO배 이상이면 언론사 수를 그대로
    우선하고, 그 정도로 차이나지 않으면 갈등 신호가 있는 그룹을 우선한다.
    top_n 밖의 그룹은 그대로 둔다."""
    def compare(a, b):
        count_a, count_b = len(a["entries"]), len(b["entries"])
        bigger, smaller = max(count_a, count_b), min(count_a, count_b)
        if smaller == 0 or bigger >= smaller * CONFLICT_OVERRIDE_RATIO:
            return count_b - count_a
        if has_conflict_signal(a) != has_conflict_signal(b):
            return -1 if has_conflict_signal(a) else 1
        return count_b - count_a

    head = sorted(groups[:top_n], key=cmp_to_key(compare))
    return head + groups[top_n:]


def find_candidate_event_groups():
    """키워드 순서대로 기사를 모아 필터(제목 기준)를 통과한 후보를 모은다.
    같은 사건을 여러 언론사가 다뤘는지로 사건 그룹을 나누고, 언론사 수가
    많은 그룹부터 앞에 오도록 정렬한 뒤 상위 그룹끼리는 갈등 신호로 한 번
    더 조정한다(rerank_top_groups). 그룹 목록을 그대로 반환해서, 하루
    여러 건을 처리할 때 main.py가 그룹 단위로(사건이 안 섞이게) 순회할
    수 있게 한다. 필터 제외 건수·사건 그룹 상위 목록을 로그에 남긴다."""
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
    groups = rerank_top_groups(groups, RERANK_TOP_GROUPS)
    print(f"사건 그룹 {len(groups)}개로 정리, 언론사 수 순 상위 {min(LOG_TOP_GROUPS, len(groups))}개 "
          f"(상위 {RERANK_TOP_GROUPS}개는 갈등 신호로 재정렬):")
    for i, group in enumerate(groups[:LOG_TOP_GROUPS], start=1):
        first_outlet = get_outlet(group["entries"][0])
        headline = get_headline(group["entries"][0], first_outlet)
        tag = " [갈등 신호]" if has_conflict_signal(group) else ""
        print(f"  {i}. ({len(group['entries'])}곳{tag}) {headline} - {first_outlet}")

    return groups


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
