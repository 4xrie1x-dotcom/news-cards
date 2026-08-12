"""1단계: 구글뉴스 RSS가 실제로 응답하는지 확인하는 스크립트"""

import sys
from urllib.parse import quote
import feedparser
from filters import filter_entries

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

# 검색할 키워드 목록. 정치 사건 중심으로 고정. 나중에 여기만 고치면 된다
KEYWORDS = ["국회", "여야", "대통령실", "국무회의", "법안"]

# 키워드당 화면에 출력할 최대 기사 수
MAX_ARTICLES = 5


def build_search_url(keyword):
    """키워드로 구글뉴스 검색 RSS 주소를 만든다."""
    encoded_keyword = quote(keyword)
    return f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"


def fetch_feed(url):
    """RSS 주소에서 피드 데이터를 가져온다. 실패하면 None을 반환한다."""
    try:
        feed = feedparser.parse(url)
        # feedparser는 네트워크 오류가 나도 예외를 안 던질 때가 있어서
        # bozo 플래그로 파싱 실패 여부를 따로 확인한다
        if feed.bozo:
            raise feed.bozo_exception
        return feed
    except Exception as error:
        print(f"RSS를 가져오는 데 실패했습니다: {error}")
        return None


def print_titles_and_links(keyword, feed):
    """필터를 적용한 뒤, 키워드 이름과 함께 상위 기사의 제목과 링크를 출력한다."""
    if not feed or not feed.entries:
        print(f"[{keyword}] 가져온 기사가 없습니다.")
        return

    filtered_entries, counts = filter_entries(feed.entries)
    print(
        f"[{keyword}] 의견 {counts['의견']}건, 지역 홍보 {counts['지역 홍보']}건, "
        f"사진/멀티미디어 {counts['사진/멀티미디어']}건 제외"
    )

    for entry in filtered_entries[:MAX_ARTICLES]:
        print(f"[{keyword}] {entry.title}")
        print(entry.link)
        print("-" * 40)


def main():
    """키워드마다 검색 RSS를 호출해서 결과를 출력한다."""
    for keyword in KEYWORDS:
        url = build_search_url(keyword)
        feed = fetch_feed(url)
        print_titles_and_links(keyword, feed)


if __name__ == "__main__":
    main()
