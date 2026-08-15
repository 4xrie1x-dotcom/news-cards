"""summarize.py가 만든 JSON으로 hook→본문 여러 장→워터마크까지 카드셋 전체를 만드는 기능"""

import re
from body_card import draw_body_card
from hook_card import draw_hook_card
from watermark_card import draw_watermark_card

MAX_SENTENCES_PER_CARD = 2
MIN_BODY_CARDS = 3
MAX_BODY_CARDS = 6  # CLAUDE.md 카드 규칙(2장~7장 본문)의 상한과 같다


def split_sentences(text):
    """마침표·물음표·느낌표 뒤 공백을 기준으로 문장을 나눈다."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s]


def ensure_period(text):
    """문장 끝에 마침표·물음표·느낌표가 없으면 마침표를 붙인다."""
    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."
    return text


def group_into_cards(sentences, max_per_card):
    """문장 목록을 최대 문장 수 기준으로 카드 단위(문자열 하나씩)로 묶는다."""
    return [" ".join(sentences[i:i + max_per_card]) for i in range(0, len(sentences), max_per_card)]


def build_body_cards(summary_json, max_per_card):
    """what/why는 묶어서 여러 문장 카드로 만들고, terms 각각과 question은
    다른 카드 종류라 서로 이어붙이지 않고 항상 독립된 카드로 둔다."""
    narrative = split_sentences(summary_json["what"]) + split_sentences(summary_json["why"])
    narrative_cards = group_into_cards(narrative, max_per_card)

    term_cards = [
        f"{term['term']}: {ensure_period(term['definition'])}"
        for term in summary_json.get("terms", [])
    ]

    question_card = [ensure_period(summary_json["question"])]

    return narrative_cards + term_cards + question_card


def render_all_cards(summary_json, source, date):
    """hook 카드 → 본문 카드 여러 장 → 워터마크 카드까지 이미지 리스트로 만들어 반환한다.
    아직 파일로 저장하지는 않는다."""
    body_texts = build_body_cards(summary_json, MAX_SENTENCES_PER_CARD)
    if len(body_texts) > MAX_BODY_CARDS:
        body_texts = build_body_cards(summary_json, MAX_SENTENCES_PER_CARD + 1)
    print(f"본문 {len(body_texts)}장 (범위: 최소 {MIN_BODY_CARDS}장 ~ 최대 {MAX_BODY_CARDS}장)")

    # 카드번호는 hook을 1번으로 치고, 워터마크는 카운트에서 뺀다
    total_content_cards = 1 + len(body_texts)

    images = [draw_hook_card(summary_json["hook"], date_text=date)]
    for i, text in enumerate(body_texts, start=2):
        images.append(draw_body_card(text, card_number=i, total_cards=total_content_cards))
    images.append(draw_watermark_card(outlet=source))

    return images
