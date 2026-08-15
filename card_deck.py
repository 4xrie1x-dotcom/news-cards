"""summarize.py가 만든 JSON으로 hook→본문→워터마크까지 카드셋을 만드는 기능"""

import re
from body_card import draw_body_card
from hook_card import draw_hook_card
from watermark_card import draw_watermark_card

MAX_SENTENCES_PER_CARD = 2  # 한 카드당 문장 1개가 기본, 짧으면 2개까지 허용
WHAT_MAX_SECTION_CARDS = 3  # what 상한. "무슨 일인가"에 치우치지 않게 낮춰뒀다
WHY_MIN_SECTION_CARDS = 2  # why 최소 보장. "왜 이게 뉴스인가"가 밀려나지 않게 한다
WHY_MAX_SECTION_CARDS = 3  # why 상한. 지면이 남으면 여기까지 늘어난다
# 전체 카드 상한 7장(hook 1 + 본문 + 워터마크 1) 기준 본문 상한
MAX_BODY_CARDS_TOTAL = 5

# 본문 76px ExtraBold, 안전폭 900px에서 실측한 평균 글자폭(약 56px)으로
# 줄당 16자, 최대 4줄(body_card.py의 BODY_MAX_LINES) 기준 편안한 상한을 잡았다
BODY_CHAR_LIMIT = 64


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


def group_into_cards(sentences, max_per_card, char_limit):
    """문장 목록을 카드 단위로 묶는다. 문장 수가 max_per_card를 넘거나,
    합친 글자 수가 char_limit을 넘으면 새 카드로 나눈다."""
    cards = []
    current = []
    for sentence in sentences:
        candidate = current + [sentence]
        if current and (len(candidate) > max_per_card or len(" ".join(candidate)) > char_limit):
            cards.append(" ".join(current))
            current = [sentence]
        else:
            current = candidate
    if current:
        cards.append(" ".join(current))
    return cards


def build_section_cards(sentences, max_section_cards):
    """한 섹션(what 또는 why)의 문장을 카드로 묶고, 최대 장수를 넘으면
    뒤쪽(덜 중요한) 문장부터 잘라낸다."""
    cards = group_into_cards(sentences, MAX_SENTENCES_PER_CARD, BODY_CHAR_LIMIT)
    return cards[:max_section_cards]


def build_body_cards(summary_json):
    """what을 채우되 why 최소 보장분(WHY_MIN_SECTION_CARDS)을 먼저 뗴어두고,
    남는 지면만큼만 what에 준다. why는 what이 쓰고 남은 지면 안에서
    최소~최대 장수로 담긴다. terms는 카드로 만들지 않는다."""
    what_sentences = split_sentences(summary_json["what"])
    why_sentences = split_sentences(summary_json["why"])

    why_cards_max = build_section_cards(why_sentences, WHY_MAX_SECTION_CARDS)
    why_reserved = min(WHY_MIN_SECTION_CARDS, len(why_cards_max))

    what_budget = min(WHAT_MAX_SECTION_CARDS, MAX_BODY_CARDS_TOTAL - why_reserved)
    what_cards = build_section_cards(what_sentences, what_budget)

    why_budget = MAX_BODY_CARDS_TOTAL - len(what_cards)
    why_cards = why_cards_max[:why_budget]

    body_texts = what_cards + why_cards
    print(f"what {len(what_cards)}장, why {len(why_cards)}장 사용 (본문 합계 {len(body_texts)}장)")
    return body_texts


def render_all_cards(summary_json, source, date):
    """hook 카드 → 본문 카드 → 워터마크 카드까지 이미지 리스트로 만든다.
    question은 워터마크 카드의 CTA와 역할이 겹쳐서, terms와 마찬가지로
    카드로 만들지 않고 그대로 반환한다(둘 다 나중에 caption.py에서 쓴다).
    {"images", "terms", "question"} 딕셔너리를 반환하며, 아직 파일로 저장하지는 않는다."""
    body_texts = build_body_cards(summary_json)

    total_content_cards = 1 + len(body_texts)  # hook 포함, 워터마크는 카운트에서 뺀다
    print(f"본문 {len(body_texts)}장, 전체 {total_content_cards + 1}장 (전체 목표 최대 7장)")

    images = [draw_hook_card(summary_json["hook"], date_text=date)]
    for i, text in enumerate(body_texts, start=2):
        images.append(draw_body_card(text, card_number=i, total_cards=total_content_cards))
    images.append(draw_watermark_card(outlet=source))

    return {
        "images": images,
        "terms": summary_json.get("terms", []),
        "question": ensure_period(summary_json["question"]),
    }
