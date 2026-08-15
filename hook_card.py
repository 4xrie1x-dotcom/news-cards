"""사진 배경 위에 제목이 올라가는 hook(1장) 카드를 그리는 기능

캔버스를 사진 영역(위 880px, 약 65%)과 고정 검정 영역(아래 470px, 약 35%)으로
나눈다. 제목 3줄+최소 폰트(84px) 조합이 검정 영역 안전공간을 넘지 않도록
역산해서 정한 비율이다. 사진은 위 영역에만 비율 유지하며 맞춰 배치하고(1.5배 넘게 확대해야
하면 photo_quality.py가 이미 걸러낸 뒤라 여기선 항상 기준 이내), 제목은
아래 고정 검정 영역에 놓는다. 경계에는 짧은 그라데이션을 넣어 사진과 검정
영역이 자연스럽게 이어지게 한다."""

from PIL import Image, ImageDraw, ImageFont, ImageOps
from text_fit import fit_body_text
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE, HOOK_PHOTO_AREA_HEIGHT,
    MUTED_COLOR, TITLE_COLOR, FALLBACK_BG_COLOR, LABEL_FONT_SIZE,
    FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH,
)

BOUNDARY_GRADIENT_HEIGHT = 150  # 사진/검정 경계에 넣는 그라데이션 높이
BLACK_AREA_MARGIN_TOP = 40  # 경계에서 제목 시작까지 여백
BLACK_AREA_MARGIN_BOTTOM = 48  # 날짜 아래 여백
HOOK_LINE_SPACING = 1.2
HOOK_MAX_LINES = 3  # 제목은 최대 3줄 (CLAUDE.md 디자인 규격)
HOOK_FONT_SIZE_STEPS = [108, 96, 84]  # 안전영역을 넘으면 이 순서로 축소


def apply_boundary_gradient(image):
    """사진 영역 하단 150px 구간에 검정(투명) → 검정(불투명) 그라데이션을 얹어
    아래 고정 검정 영역과 자연스럽게 이어지게 한다."""
    width, _ = image.size
    gradient_top = HOOK_PHOTO_AREA_HEIGHT - BOUNDARY_GRADIENT_HEIGHT
    alpha_mask = Image.new("L", (1, BOUNDARY_GRADIENT_HEIGHT))
    for y in range(BOUNDARY_GRADIENT_HEIGHT):
        alpha_mask.putpixel((0, y), int(255 * y / (BOUNDARY_GRADIENT_HEIGHT - 1)))
    alpha_mask = alpha_mask.resize((width, BOUNDARY_GRADIENT_HEIGHT))
    black_layer = Image.new("RGB", (width, BOUNDARY_GRADIENT_HEIGHT), FALLBACK_BG_COLOR)
    image.paste(black_layer, (0, gradient_top), alpha_mask)
    return image


def draw_hook_card(title, date_text, background_path=None):
    """hook 카드(1장)를 그려서 이미지 객체로 반환한다.
    배경 사진이 없으면 CLAUDE.md의 텍스트 전용 fallback(#16181C)을 전체에 쓴다."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), FALLBACK_BG_COLOR)
    if background_path:
        source_image = Image.open(background_path).convert("RGB")
        # 비율 유지한 채 사진 영역(1080x1080)을 꽉 채우도록 맞추고 중앙 기준으로 크롭한다
        photo = ImageOps.fit(source_image, (CANVAS_WIDTH, HOOK_PHOTO_AREA_HEIGHT),
                              method=Image.LANCZOS, centering=(0.5, 0.5))
        image.paste(photo, (0, 0))
        image = apply_boundary_gradient(image)

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

    # 고정 검정 영역(1080~1350px) 안에 제목 여러 줄 + 날짜를 위에서부터 배치한다
    line_height = int(used_size * HOOK_LINE_SPACING)
    title_height = line_height * len(lines)
    date_gap = 16
    date_height = int(LABEL_FONT_SIZE * 1.2)
    start_y = HOOK_PHOTO_AREA_HEIGHT + BLACK_AREA_MARGIN_TOP
    block_height = title_height + date_gap + date_height
    available_height = CANVAS_HEIGHT - BLACK_AREA_MARGIN_BOTTOM - start_y
    if block_height > available_height:
        print(f"경고: 제목+날짜 블록({block_height}px)이 검정 영역 안전공간({available_height}px)을 넘습니다.")

    for i, line in enumerate(lines):
        draw.text((MARGIN_SIDE, start_y + i * line_height), line, font=title_font, fill=TITLE_COLOR)

    date_y = start_y + title_height + date_gap
    draw.text((MARGIN_SIDE, date_y), date_text, font=label_font, fill=MUTED_COLOR)

    return image
