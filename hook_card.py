"""사진 배경 위에 제목이 올라가는 hook(1장) 카드를 그리는 기능"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
from text_fit import fit_body_text
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE, MARGIN_BOTTOM,
    MUTED_COLOR, TITLE_COLOR, FALLBACK_BG_COLOR, LABEL_FONT_SIZE,
    FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH,
)

GRADIENT_HEIGHT_RATIO = 0.55  # 하단 55% 구간에 그라데이션
HOOK_LINE_SPACING = 1.2
HOOK_MAX_LINES = 3  # 제목은 최대 3줄 (CLAUDE.md 디자인 규격)
HOOK_FONT_SIZE_STEPS = [108, 96, 84]  # 안전영역을 넘으면 이 순서로 축소


def apply_bottom_gradient(image):
    """이미지 하단 55% 구간에 검정(불투명) → 투명 세로 그라데이션을 얹는다."""
    width, height = image.size
    gradient_height = int(height * GRADIENT_HEIGHT_RATIO)
    alpha_mask = Image.new("L", (1, gradient_height))
    for y in range(gradient_height):
        alpha_mask.putpixel((0, y), int(255 * y / (gradient_height - 1)))
    alpha_mask = alpha_mask.resize((width, gradient_height))
    black_layer = Image.new("RGB", (width, gradient_height), "#000000")
    image.paste(black_layer, (0, height - gradient_height), alpha_mask)
    return image


def draw_hook_card(title, date_text, background_path=None):
    """hook 카드(1장)를 그려서 이미지 객체로 반환한다.
    배경 이미지가 없으면 CLAUDE.md의 텍스트 전용 fallback(#16181C)을 쓴다."""
    if background_path:
        # 비율을 유지한 채 캔버스를 꽉 채우도록 확대 후 중앙 기준으로 크롭한다 (늘리기 금지)
        source_image = Image.open(background_path).convert("RGB")
        image = ImageOps.fit(source_image, (CANVAS_WIDTH, CANVAS_HEIGHT), method=Image.LANCZOS, centering=(0.5, 0.5))
        image = apply_bottom_gradient(image)
    else:
        image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), FALLBACK_BG_COLOR)

    draw = ImageDraw.Draw(image)
    safe_width = CANVAS_WIDTH - MARGIN_SIDE * 2

    title_font, lines, used_size, step = fit_body_text(
        title, draw, safe_width, HOOK_MAX_LINES, HOOK_FONT_SIZE_STEPS, FONT_EXTRABOLD_PATH
    )
    if step == 0:
        print(f"제목 폰트 축소 없음: {used_size}px 그대로 사용")
    else:
        print(f"제목 폰트 축소 {step}단계: {HOOK_FONT_SIZE_STEPS[0]}px → {used_size}px ({len(lines)}줄)")

    # 좌상단 로고 텍스트마크 자리 (디자인 미확정, 임시 텍스트)
    label_font = ImageFont.truetype(FONT_REGULAR_PATH, LABEL_FONT_SIZE)
    draw.text((MARGIN_SIDE, 60), "LOGO", font=label_font, fill=TITLE_COLOR)

    # 하단부: 제목 여러 줄 + 날짜
    line_height = int(used_size * HOOK_LINE_SPACING)
    title_height = line_height * len(lines)
    date_gap = 20
    date_height = int(LABEL_FONT_SIZE * 1.2)
    start_y = (CANVAS_HEIGHT - MARGIN_BOTTOM) - date_height - date_gap - title_height

    for i, line in enumerate(lines):
        draw.text((MARGIN_SIDE, start_y + i * line_height), line, font=title_font, fill=TITLE_COLOR)

    date_y = start_y + title_height + date_gap
    draw.text((MARGIN_SIDE, date_y), date_text, font=label_font, fill=MUTED_COLOR)

    return image
