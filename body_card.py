"""본문 카드(2장부터)를 그리는 기능"""

import re
from PIL import Image, ImageDraw, ImageFont
from text_fit import fit_body_text
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE, MARGIN_TOP, MARGIN_BOTTOM,
    BACKGROUND_COLOR, BODY_COLOR, MUTED_COLOR, DIVIDER_COLOR, EMPHASIS_COLOR,
    LABEL_FONT_SIZE, FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH, ACCOUNT_NAME,
)

BODY_FONT_SIZE_STEPS = [76, 68, 60]  # 안전영역을 넘으면 이 순서로 축소
BODY_LINE_SPACING = 1.35
# 본문 카드는 1~2문장이 목적이라 잡은 값. CLAUDE.md에 정해진 수치는 없음
BODY_MAX_LINES = 4


def parse_emphasis(text):
    """{}로 감싼 구절을 찾아 뜻대로 떼어내고, 중괄호를 뺀 순수 텍스트와
    강조할 구절 목록을 함께 반환한다."""
    phrases = re.findall(r"\{([^{}]*)\}", text)
    plain_text = re.sub(r"[{}]", "", text)
    return plain_text, phrases


def draw_line_with_emphasis(draw, line, x, y, font, phrases):
    """한 줄을 그리되, 줄 안에 강조 구절이 있으면 그 부분만 강조색으로 그린다.
    왼쪽 정렬은 그대로 유지한다."""
    for phrase in phrases:
        if phrase and phrase in line:
            before, after = line.split(phrase, 1)
            cursor_x = x
            draw.text((cursor_x, y), before, font=font, fill=BODY_COLOR)
            cursor_x += draw.textlength(before, font=font)
            draw.text((cursor_x, y), phrase, font=font, fill=EMPHASIS_COLOR)
            cursor_x += draw.textlength(phrase, font=font)
            draw.text((cursor_x, y), after, font=font, fill=BODY_COLOR)
            return
    draw.text((x, y), line, font=font, fill=BODY_COLOR)


def draw_body_card(text, card_number, total_cards):
    """본문 카드 1장을 그려서 이미지 객체로 반환한다. 텍스트의 {}로 감싼 구절은
    강조색으로 렌더링되고, 중괄호 자체는 화면에 나오지 않는다."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.truetype(FONT_REGULAR_PATH, LABEL_FONT_SIZE)

    plain_text, phrases = parse_emphasis(text)
    safe_width = CANVAS_WIDTH - MARGIN_SIDE * 2
    body_font, lines, used_size, step = fit_body_text(
        plain_text, draw, safe_width, BODY_MAX_LINES, BODY_FONT_SIZE_STEPS, FONT_EXTRABOLD_PATH
    )
    if step == 0:
        print(f"폰트 축소 없음: {used_size}px 그대로 사용")
    else:
        print(f"폰트 축소 {step}단계: {BODY_FONT_SIZE_STEPS[0]}px → {used_size}px ({len(lines)}줄)")

    # 본문을 안전영역 안에서 세로 중앙 정렬
    line_height = int(used_size * BODY_LINE_SPACING)
    block_height = line_height * len(lines)
    safe_top = MARGIN_TOP
    safe_bottom = CANVAS_HEIGHT - MARGIN_BOTTOM
    start_y = safe_top + (safe_bottom - safe_top - block_height) // 2

    for i, line in enumerate(lines):
        draw_line_with_emphasis(draw, line, MARGIN_SIDE, start_y + i * line_height, body_font, phrases)

    # 카드번호: 우상단
    card_label = f"{card_number}/{total_cards}"
    label_width = draw.textlength(card_label, font=label_font)
    draw.text((CANVAS_WIDTH - MARGIN_SIDE - label_width, 60), card_label, font=label_font, fill=MUTED_COLOR)

    # 구분선과 핸들: 하단
    divider_y = CANVAS_HEIGHT - 70
    draw.line((MARGIN_SIDE, divider_y, CANVAS_WIDTH - MARGIN_SIDE, divider_y), fill=DIVIDER_COLOR, width=2)
    draw.text((MARGIN_SIDE, divider_y + 15), ACCOUNT_NAME, font=label_font, fill=MUTED_COLOR)

    return image
