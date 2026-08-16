"""summarize.py가 만든 JSON으로 hook 카드 1장을 만드는 기능

카드 구조가 hook 1장으로 단순화되면서 본문·워터마크 카드 조립 로직은
없앴다. what/why/terms/question과 원래 워터마크 카드 몫이던 내용은 전부
caption.py가 캡션으로 옮겨 담는다. body_card.py, watermark_card.py 자체는
당장 안 쓰지만 나중을 위해 지우지 않고 남겨둔다."""

from hook_card import draw_hook_card


def ensure_period(text):
    """문장 끝에 마침표·물음표·느낌표가 없으면 마침표를 붙인다."""
    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."
    return text


def render_all_cards(summary_json, date, hook_background_path=None):
    """hook 카드 1장만 이미지로 만들어 {"images": [hook_image]}로 반환한다.
    hook_background_path가 있으면 배경 사진으로 쓰고, 없으면 hook_card.py의
    텍스트 전용 fallback이 대신 쓰인다."""
    image = draw_hook_card(summary_json["hook"], date_text=date, background_path=hook_background_path)
    return {"images": [image]}
