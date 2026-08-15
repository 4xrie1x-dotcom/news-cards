"""6단계: collect→extract→summarize→render→caption 파이프라인을 기사 1개로 실행하는 스크립트

사진 자동 조달(위키미디어/Pexels)은 아직 없다. hook 카드는 텍스트 전용 fallback으로 만든다.
기사 1개만 끝까지 처리한다.
"""

import sys, os, json, datetime
from collect import KEYWORDS, build_search_url, fetch_feed
from filters import filter_entries
from dedupe import get_outlet
from extract import resolve_real_url, get_article_text
from summarize import summarize
from card_deck import render_all_cards
from caption import build_caption

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

ARTICLE_NUMBER = "01"  # 기사 1개만 처리하므로 고정값

def find_first_article():
    """키워드 순서대로 기사를 모아 필터를 통과한 첫 기사를 돌려준다."""
    for keyword in KEYWORDS:
        feed = fetch_feed(build_search_url(keyword))
        if not feed or not feed.entries:
            continue
        filtered_entries, _, _ = filter_entries(feed.entries)
        if filtered_entries:
            return filtered_entries[0]
    return None


def main():
    """기사 1개를 끝까지 처리해서 카드와 캡션을 만들고 저장한다."""
    today = datetime.date.today()
    output_dir = f"output/{today.isoformat()}/{ARTICLE_NUMBER}"
    print("1단계: 기사 수집 중...")
    entry = find_first_article()
    if not entry:
        print("실패(1단계 수집): 필터를 통과한 기사를 찾지 못했습니다.")
        return
    outlet = get_outlet(entry)
    print(f"1단계 완료: [{outlet}] {entry.title}")
    print("2단계: 본문 추출 중...")
    try:
        real_url = resolve_real_url(entry.link)
        if not real_url:
            print("실패(2단계 추출): 실제 기사 주소를 얻지 못했습니다.")
            return
        body = get_article_text(real_url, entry.title)
        if not body:
            print("실패(2단계 추출): 본문을 추출하지 못했습니다.")
            return
        print(f"2단계 완료: 본문 {len(body)}자")
    except Exception as error:
        print(f"실패(2단계 추출): {error}")
        return
    print("3단계: Gemini 요약 중...")
    try:
        summary_json = summarize(entry.title, body)
        if not summary_json:
            print("실패(3단계 요약): 요약 결과를 받지 못했습니다.")
            return
        print(f"3단계 완료: {summary_json['hook']}")
    except Exception as error:
        print(f"실패(3단계 요약): {error}")
        return
    print("4단계: 카드 생성 중...")
    try:
        deck = render_all_cards(summary_json, source=outlet, date=today.strftime("%Y.%m.%d"))
        print(f"4단계 완료: 카드 {len(deck['images'])}장")
    except Exception as error:
        print(f"실패(4단계 카드 생성): {error}")
        return
    print("5단계: 캡션 생성 중...")
    try:
        caption_result = build_caption(summary_json, deck["terms"], deck["question"], source=outlet)
        print(f"5단계 완료: 캡션 {len(caption_result['caption'])}자")
    except Exception as error:
        print(f"실패(5단계 캡션 생성): {error}")
        return
    print("6단계: 저장 중...")
    try:
        os.makedirs(output_dir, exist_ok=True)
        for i, image in enumerate(deck["images"], start=1):
            image.save(f"{output_dir}/card_{i}.png")
        with open(f"{output_dir}/caption.txt", "w", encoding="utf-8") as f:
            f.write(caption_result["caption"])
        data = {**summary_json, "source": outlet, "url": real_url, "date": today.isoformat()}
        with open(f"{output_dir}/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"6단계 완료: {output_dir}에 카드 {len(deck['images'])}장, caption.txt, data.json 저장")
    except Exception as error:
        print(f"실패(6단계 저장): {error}")
        return
    print("전체 파이프라인 성공")


if __name__ == "__main__":
    main()
