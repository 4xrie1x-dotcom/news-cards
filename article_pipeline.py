"""사건 그룹 하나를 골라 본문 추출부터 카드·캡션 저장까지 전체 과정을
처리하는 기능

main.py가 하루 여러 사건(기본 3건)을 처리할 때 사건마다 한 번씩 이
함수를 부른다. 그룹 안 후보 중 하나라도 추출에 성공하면 끝까지
저장하고 True를, 그룹 전체가 실패하거나 중간 단계에서 실패하면
False를 반환해서 main.py가 다음 사건으로 건너뛸 수 있게 한다."""

from article_picker import extract_first_valid_article
from dedupe import get_outlet
from summarize import summarize
from photo_pipeline import get_hook_background
from card_deck import render_all_cards
from caption import build_caption
from output_writer import save_output


def process_article(group, article_number, today, date_dir):
    """사건 그룹 하나를 처리해서 {date_dir}/{article_number}/에 저장한다.
    성공하면 True, 실패하면 False를 반환하고 이유를 화면에 출력한다."""
    output_dir = f"{date_dir}/{article_number}"
    tag = f"[{article_number}]"

    print(f"{tag} 2단계: 본문 추출·다중 소재 검사 중...")
    entry, real_url, body = extract_first_valid_article(group["entries"])
    if not entry:
        print(f"{tag} 실패(2단계 추출): 조건을 만족하는 기사를 찾지 못했습니다.")
        return False
    outlet = get_outlet(entry)
    print(f"{tag} 2단계 완료: [{outlet}] {entry.title}, 본문 {len(body)}자, 주소: {real_url}")

    print(f"{tag} 3단계: Gemini 요약 중...")
    try:
        summary_json = summarize(entry.title, body)
        if not summary_json:
            print(f"{tag} 실패(3단계 요약): 요약 결과를 받지 못했습니다.")
            return False
        print(f"{tag} 3단계 완료: {summary_json['hook']}")
    except Exception as error:
        print(f"{tag} 실패(3단계 요약): {error}")
        return False

    print(f"{tag} 4단계: hook 배경 사진 조달 중...")
    try:
        background_path, photo_credit = get_hook_background(summary_json)
        print(f"{tag} 4단계 완료: {background_path or '텍스트 전용 fallback 사용'}")
    except Exception as error:
        print(f"{tag} 실패(4단계 배경 사진 조달): {error}")
        background_path, photo_credit = None, None

    print(f"{tag} 5단계: 카드 생성 중...")
    try:
        deck = render_all_cards(
            summary_json, date=today.strftime("%Y.%m.%d"), hook_background_path=background_path,
        )
        print(f"{tag} 5단계 완료: 카드 {len(deck['images'])}장")
    except Exception as error:
        print(f"{tag} 실패(5단계 카드 생성): {error}")
        return False

    print(f"{tag} 6단계: 캡션 생성 중...")
    try:
        caption_result = build_caption(summary_json, source=outlet, photo_credit=photo_credit)
        print(f"{tag} 6단계 완료: 캡션 {len(caption_result['caption'])}자")
    except Exception as error:
        print(f"{tag} 실패(6단계 캡션 생성): {error}")
        return False

    print(f"{tag} 7단계: 저장 중...")
    try:
        save_output(output_dir, deck, caption_result, summary_json, outlet, real_url, today.isoformat())
        print(f"{tag} 7단계 완료: {output_dir}에 카드 {len(deck['images'])}장, caption.txt, data.json 저장")
    except Exception as error:
        print(f"{tag} 실패(7단계 저장): {error}")
        return False

    return True
