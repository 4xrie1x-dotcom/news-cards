"""2단계: 기사 링크에서 trafilatura로 본문을 뽑을 수 있는지 확인하는 스크립트

구글뉴스 RSS 링크는 news.google.com/rss/articles/... 형태의 리다이렉트 주소라
trafilatura가 실제 기사 페이지 대신 구글뉴스 페이지만 받아온다.
그래서 googlenewsdecoder로 진짜 기사 주소를 먼저 알아낸 뒤 추출한다.
"""

import sys
import trafilatura
from googlenewsdecoder import gnewsdecoder
from collect import KEYWORDS, build_search_url, fetch_feed

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

# 테스트할 기사 개수. 전체를 다 돌리지 않고 소수만 확인한다
TEST_COUNT = 3

# 화면에 보여줄 본문 앞부분 길이. 확인용이라 본문 전체는 다루지 않는다
PREVIEW_LENGTH = 200


def resolve_real_url(google_news_link):
    """구글뉴스 리다이렉트 링크를 실제 기사 주소로 바꾼다. 실패하면 None을 반환한다."""
    try:
        result = gnewsdecoder(google_news_link)
        if result.get("status"):
            return result["decoded_url"]
        print(f"주소 변환 실패: {result}")
        return None
    except Exception as error:
        print(f"주소 변환 중 오류: {error}")
        return None


def extract_preview(real_url):
    """실제 기사 주소에서 본문을 뽑아 앞부분만 반환한다. 본문 전체는 메모리에서만 쓰고 버린다."""
    try:
        downloaded = trafilatura.fetch_url(real_url)
        if not downloaded:
            print("페이지 다운로드 실패")
            return None
        text = trafilatura.extract(downloaded)
        if not text:
            print("본문 추출 실패")
            return None
        return text[:PREVIEW_LENGTH]
    except Exception as error:
        print(f"본문 추출 중 오류: {error}")
        return None


def main():
    """첫 키워드로 기사 몇 개만 가져와 본문 추출이 되는지 확인한다."""
    feed = fetch_feed(build_search_url(KEYWORDS[0]))
    if not feed or not feed.entries:
        print("기사를 가져오지 못했습니다.")
        return

    for entry in feed.entries[:TEST_COUNT]:
        print(f"제목: {entry.title}")
        real_url = resolve_real_url(entry.link)
        if not real_url:
            print("-" * 40)
            continue
        print(f"실제 주소: {real_url}")
        preview = extract_preview(real_url)
        if preview:
            print(f"본문 앞부분: {preview}")
        print("-" * 40)


if __name__ == "__main__":
    main()
