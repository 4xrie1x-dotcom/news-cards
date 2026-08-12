"""1단계: 구글뉴스 RSS가 실제로 응답하는지 확인하는 스크립트"""

import sys
import feedparser

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

# 구글뉴스 한국어 인기 뉴스 RSS 주소
RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"


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


def print_titles_and_links(feed):
    """피드에 담긴 기사들의 제목과 링크만 출력한다."""
    if not feed or not feed.entries:
        print("가져온 기사가 없습니다.")
        return

    for entry in feed.entries:
        print(entry.title)
        print(entry.link)
        print("-" * 40)


def main():
    """전체 흐름을 실행한다: 가져오고, 출력한다."""
    feed = fetch_feed(RSS_URL)
    print_titles_and_links(feed)


if __name__ == "__main__":
    main()
