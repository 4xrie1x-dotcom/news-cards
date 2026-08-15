"""매 발행마다 마지막에 붙는 고정 워터마크 카드를 그리는 기능"""

from PIL import Image, ImageDraw, ImageFont
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE, MARGIN_TOP, MARGIN_BOTTOM,
    TITLE_COLOR, MUTED_COLOR, FALLBACK_BG_COLOR,
    FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH, ACCOUNT_NAME,
    WATERMARK_MAIN_FONT_SIZE, WATERMARK_SECONDARY_FONT_SIZE, WATERMARK_SECONDARY_COLOR,
    WATERMARK_ACCOUNT_FONT_SIZE, WATERMARK_SOURCE_FONT_SIZE,
)

MAIN_CTA_TEXT = "이 사안, 어떻게 보세요?"
SECONDARY_LINE = "저장하고 팔로우까지"
FOOTER_GAP = 60  # CTA 블록과 하단 계정명·출처 사이 최소 간격


def draw_centered_line(draw, text, font, y, fill):
    """가로 중앙 정렬로 한 줄을 그린다."""
    width = draw.textlength(text, font=font)
    draw.text(((CANVAS_WIDTH - width) / 2, y), text, font=font, fill=fill)


def stacked_height(items):
    """(텍스트, 폰트, 색, 간격) 목록을 위에서부터 쌓았을 때 총 높이를 구한다."""
    return sum((2 if text == "divider" else font.size) + gap for text, font, _, gap in items)


def draw_stacked_lines(draw, items, start_y):
    """items를 start_y부터 위에서 아래로 그린다. "divider"는 구분선으로 그린다."""
    y = start_y
    for text, font, color, gap in items:
        if text == "divider":
            draw.line((MARGIN_SIDE, y, CANVAS_WIDTH - MARGIN_SIDE, y), fill=color, width=2)
            y += 2 + gap
        else:
            draw_centered_line(draw, text, font, y, color)
            y += font.size + gap


def draw_watermark_card(outlet):
    """워터마크 카드(마지막 고정 카드)를 그려서 이미지 객체로 반환한다.
    메인 CTA를 화면 가운데쯤에 크게 두고, 계정명·출처는 하단에 작게 배치한다."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), FALLBACK_BG_COLOR)
    draw = ImageDraw.Draw(image)

    main_font = ImageFont.truetype(FONT_EXTRABOLD_PATH, WATERMARK_MAIN_FONT_SIZE)
    secondary_font = ImageFont.truetype(FONT_REGULAR_PATH, WATERMARK_SECONDARY_FONT_SIZE)
    account_font = ImageFont.truetype(FONT_REGULAR_PATH, WATERMARK_ACCOUNT_FONT_SIZE)
    source_font = ImageFont.truetype(FONT_REGULAR_PATH, WATERMARK_SOURCE_FONT_SIZE)

    cta_items = [
        (MAIN_CTA_TEXT, main_font, TITLE_COLOR, 30),
        (SECONDARY_LINE, secondary_font, WATERMARK_SECONDARY_COLOR, 0),
    ]
    footer_items = [
        (ACCOUNT_NAME, account_font, MUTED_COLOR, 12),
        (f"출처 {outlet} · AI 요약", source_font, MUTED_COLOR, 0),
    ]

    safe_top = MARGIN_TOP
    safe_bottom = CANVAS_HEIGHT - MARGIN_BOTTOM

    # 계정명·출처는 안전영역 맨 아래에 붙이고, CTA는 그 위 남는 공간에서 가운데 정렬한다
    footer_y = safe_bottom - stacked_height(footer_items)
    cta_bottom_limit = footer_y - FOOTER_GAP
    cta_y = safe_top + (cta_bottom_limit - safe_top - stacked_height(cta_items)) // 2

    draw_stacked_lines(draw, cta_items, cta_y)
    draw_stacked_lines(draw, footer_items, footer_y)

    return image
