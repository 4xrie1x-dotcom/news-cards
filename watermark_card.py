"""매 발행마다 마지막에 붙는 고정 워터마크 카드를 그리는 기능"""

from PIL import Image, ImageDraw, ImageFont
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE, MARGIN_TOP, MARGIN_BOTTOM,
    TITLE_COLOR, MUTED_COLOR, FALLBACK_BG_COLOR, LABEL_FONT_SIZE,
    FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH, ACCOUNT_NAME,
)

ACCOUNT_FONT_SIZE = 84
# CLAUDE.md는 핸들을 Light 32px로 정했지만, 보유한 폰트가 ExtraBold·Regular뿐이라
# 일단 Regular로 대체한다
HANDLE_FONT_SIZE = 32
HANDLE_PLACEHOLDER = "@placeholder"  # 핸들도 계정명처럼 미정이라 임시값
CTA_FONT_SIZE = 36  # 크기가 CLAUDE.md에 없어서 임시로 잡은 값
CTA_LINES = ["이 사안, 어떻게 보세요?", "저장해두세요", "도움됐다면 팔로우"]


def draw_centered_line(draw, text, font, y, fill):
    """가로 중앙 정렬로 한 줄을 그린다."""
    width = draw.textlength(text, font=font)
    draw.text(((CANVAS_WIDTH - width) / 2, y), text, font=font, fill=fill)


def draw_watermark_card(outlet):
    """워터마크 카드(마지막 고정 카드)를 그려서 이미지 객체로 반환한다."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), FALLBACK_BG_COLOR)
    draw = ImageDraw.Draw(image)

    account_font = ImageFont.truetype(FONT_EXTRABOLD_PATH, ACCOUNT_FONT_SIZE)
    handle_font = ImageFont.truetype(FONT_REGULAR_PATH, HANDLE_FONT_SIZE)
    cta_font = ImageFont.truetype(FONT_REGULAR_PATH, CTA_FONT_SIZE)
    label_font = ImageFont.truetype(FONT_REGULAR_PATH, LABEL_FONT_SIZE)

    # (텍스트, 폰트, 색, 다음 줄까지 간격) 순서로 늘어놓는다. "divider"는 구분선.
    items = [
        (ACCOUNT_NAME, account_font, TITLE_COLOR, 20),
        (HANDLE_PLACEHOLDER, handle_font, MUTED_COLOR, 60),
        ("divider", None, MUTED_COLOR, 60),
        (CTA_LINES[0], cta_font, TITLE_COLOR, 30),
        (CTA_LINES[1], cta_font, TITLE_COLOR, 30),
        (CTA_LINES[2], cta_font, TITLE_COLOR, 60),
        ("divider", None, MUTED_COLOR, 50),
        (f"출처  {outlet}", label_font, MUTED_COLOR, 20),
        ("AI 요약", label_font, MUTED_COLOR, 0),
    ]

    # 안전영역 안에서 전체 블록을 세로 중앙 정렬하기 위해 총 높이를 먼저 잰다
    total_height = sum((2 if text == "divider" else font.size) + gap for text, font, _, gap in items)
    safe_top = MARGIN_TOP
    safe_bottom = CANVAS_HEIGHT - MARGIN_BOTTOM
    y = safe_top + (safe_bottom - safe_top - total_height) // 2

    for text, font, color, gap in items:
        if text == "divider":
            draw.line((MARGIN_SIDE, y, CANVAS_WIDTH - MARGIN_SIDE, y), fill=color, width=2)
            y += 2 + gap
        else:
            draw_centered_line(draw, text, font, y, color)
            y += font.size + gap

    return image
