"""본문 카드(2장부터)를 그리는 기능"""

from PIL import Image, ImageDraw, ImageFont
from text_fit import fit_body_text
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE, MARGIN_TOP, MARGIN_BOTTOM,
    BACKGROUND_COLOR, BODY_COLOR, MUTED_COLOR, DIVIDER_COLOR,
    LABEL_FONT_SIZE, FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH, ACCOUNT_HANDLE,
)

BODY_FONT_SIZE_STEPS = [76, 68, 60]  # 안전영역을 넘으면 이 순서로 축소
BODY_LINE_SPACING = 1.35
# 본문 카드는 1~2문장이 목적이라 잡은 값. CLAUDE.md에 정해진 수치는 없음
BODY_MAX_LINES = 4


def draw_body_card(text, card_number, total_cards):
    """본문 카드 1장을 그려서 이미지 객체로 반환한다. 강조 마크업은 쓰지 않고
    본문 전체를 같은 색(#16181C)으로 그린다. 혹시 텍스트에 {}가 섞여 있으면
    화면에 그대로 노출되지 않도록 제거만 한다."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.truetype(FONT_REGULAR_PATH, LABEL_FONT_SIZE)

    plain_text = text.replace("{", "").replace("}", "")
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
        draw.text((MARGIN_SIDE, start_y + i * line_height), line, font=body_font, fill=BODY_COLOR)

    # 카드번호: 우상단
    card_label = f"{card_number}/{total_cards}"
    label_width = draw.textlength(card_label, font=label_font)
    draw.text((CANVAS_WIDTH - MARGIN_SIDE - label_width, 60), card_label, font=label_font, fill=MUTED_COLOR)

    # 구분선과 핸들: 하단
    divider_y = CANVAS_HEIGHT - 70
    draw.line((MARGIN_SIDE, divider_y, CANVAS_WIDTH - MARGIN_SIDE, divider_y), fill=DIVIDER_COLOR, width=2)
    draw.text((MARGIN_SIDE, divider_y + 15), ACCOUNT_HANDLE, font=label_font, fill=MUTED_COLOR)

    return image
