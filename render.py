"""4단계: Pillow로 본문 카드 1장을 실제로 그릴 수 있는지 확인하는 스크립트

CLAUDE.md의 v4 디자인 규격(2장부터 본문 카드) 중 텍스트 부분만 그린다.
사진, 위키미디어, Pexels 연동은 이번 단계에서 다루지 않는다.
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
from text_fit import fit_body_text

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

# 캔버스와 안전 여백 (CLAUDE.md 디자인 규격)
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350
MARGIN_SIDE = 90
MARGIN_TOP = 150
MARGIN_BOTTOM = 160
# 색상 (CLAUDE.md 디자인 규격)
BACKGROUND_COLOR = "#FFFFFF"
BODY_COLOR = "#16181C"
MUTED_COLOR = "#8B9099"
DIVIDER_COLOR = "#E5E5E5"
# 폰트 크기·행간, 폰트 파일 경로
FONT_SIZE_STEPS = [76, 68, 60]  # 안전영역을 넘으면 이 순서로 축소
LABEL_FONT_SIZE = 26
LINE_SPACING = 1.35
# 본문 카드는 1~2문장이 목적이라 잡은 값. CLAUDE.md에 정해진 수치는 없음
MAX_LINES = 4
FONT_EXTRABOLD_PATH = "fonts/Pretendard-ExtraBold.otf"
FONT_REGULAR_PATH = "fonts/Pretendard-Regular.otf"
ACCOUNT_NAME = "@placeholder"  # 계정명 미정. 정해지면 이 값만 바꾸면 된다
OUTPUT_PATH = "output/test/card_1.png"


def draw_body_card(text, card_number, total_cards):
    """본문 카드 1장을 그려서 이미지 객체로 반환한다."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    label_font = ImageFont.truetype(FONT_REGULAR_PATH, LABEL_FONT_SIZE)

    safe_width = CANVAS_WIDTH - MARGIN_SIDE * 2
    body_font, lines, used_size, step = fit_body_text(
        text, draw, safe_width, MAX_LINES, FONT_SIZE_STEPS, FONT_EXTRABOLD_PATH
    )
    if step == 0:
        print(f"폰트 축소 없음: {used_size}px 그대로 사용")
    else:
        print(f"폰트 축소 {step}단계: {FONT_SIZE_STEPS[0]}px → {used_size}px ({len(lines)}줄)")

    # 본문을 안전영역 안에서 세로 중앙 정렬
    line_height = int(used_size * LINE_SPACING)
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
    draw.text((MARGIN_SIDE, divider_y + 15), ACCOUNT_NAME, font=label_font, fill=MUTED_COLOR)

    return image


def main():
    """일부러 아주 긴 문장으로 카드 1장을 만들어, 폰트 축소가 실제로 일어나는지 확인한다."""
    test_sentence = (
        "국회 지방선거 투표용지 부족 사태 국정조사특별위원회 3차 청문회에서 "
        "여야가 재검표 일정과 방식을 두고 정면으로 충돌했으며 결국 합의에 "
        "이르지 못한 채 야당 단독으로 현안 질의가 진행됐다"
    )
    try:
        image = draw_body_card(test_sentence, card_number=1, total_cards=6)
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        image.save(OUTPUT_PATH)
        print(f"카드 저장 완료: {OUTPUT_PATH}")
    except Exception as error:
        print(f"카드 생성 실패: {error}")


if __name__ == "__main__":
    main()
