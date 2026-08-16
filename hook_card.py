"""사진 배경 위에 제목이 올라가는 hook(1장) 카드를 그리는 기능

캔버스를 사진 영역(위)과 고정 검정 영역(아래, 제목·날짜)으로 나누되, 그
경계는 고정값이 아니라 실제 제목의 줄 수·폰트 크기로 매번 다시 계산한다.
제목이 짧으면 검정 영역이 작아지고 사진이 그만큼 크게 보인다. CLAUDE.md
규칙상 인스타 탐색 탭 썸네일은 정중앙 1080x1080으로 크롭되어 캔버스 하단
135px가 잘리므로, 검정 영역은 항상 이 여백을 포함해서 계산한다
(card_config.hook_black_area_height 참고). 사진은 사진 영역에만 비율
유지하며 맞춰 배치하고(1.5배 넘게 확대해야 하면 photo_quality.py가 이미
걸러낸 뒤라 여기선 항상 기준 이내), 경계에는 짧은 그라데이션을 넣어 사진과
검정 영역이 자연스럽게 이어지게 한다."""

from PIL import Image, ImageDraw, ImageFont, ImageOps
from text_fit import fit_body_text
from card_config import (
    CANVAS_WIDTH, CANVAS_HEIGHT, MARGIN_SIDE,
    HOOK_LINE_SPACING, HOOK_MAX_LINES, HOOK_FONT_SIZE_STEPS,
    HOOK_BLACK_MARGIN_TOP, HOOK_DATE_GAP, HOOK_SAFE_MARGIN_BOTTOM,
    HOOK_MIN_BLACK_AREA_HEIGHT, HOOK_MAX_BLACK_AREA_HEIGHT, hook_black_area_height,
    MUTED_COLOR, TITLE_COLOR, FALLBACK_BG_COLOR, LABEL_FONT_SIZE,
    FONT_EXTRABOLD_PATH, FONT_REGULAR_PATH,
)

BOUNDARY_GRADIENT_HEIGHT = 150  # 사진/검정 경계에 넣는 그라데이션 높이
LOGO_PATH = "assets/logo_card_white.png"  # 사진 배경 위라 어두운 톤이 많아 흰색 버전 사용
LOGO_HEIGHT = 48  # 좌상단 로고 세로 크기 (40~60px 범위)


def apply_boundary_gradient(image, photo_area_height):
    """사진 영역 하단 150px 구간에 검정(투명) → 검정(불투명) 그라데이션을 얹어
    아래 검정 영역과 자연스럽게 이어지게 한다."""
    width, _ = image.size
    gradient_top = photo_area_height - BOUNDARY_GRADIENT_HEIGHT
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
    draw = ImageDraw.Draw(image)
    safe_width = CANVAS_WIDTH - MARGIN_SIDE * 2

    # 사진을 배치하기 전에 제목이 몇 줄·몇 px로 나올지 먼저 계산해야 검정 영역
    # 크기(=사진 영역 크기)를 정할 수 있다
    title_font, lines, used_size, step = fit_body_text(
        title, draw, safe_width, HOOK_MAX_LINES, HOOK_FONT_SIZE_STEPS, FONT_EXTRABOLD_PATH
    )
    if step == 0:
        print(f"제목 폰트 축소 없음: {used_size}px 그대로 사용")
    else:
        print(f"제목 폰트 축소 {step}단계: {HOOK_FONT_SIZE_STEPS[0]}px → {used_size}px ({len(lines)}줄)")

    black_area_height = hook_black_area_height(used_size, len(lines))
    black_area_height = max(HOOK_MIN_BLACK_AREA_HEIGHT, min(HOOK_MAX_BLACK_AREA_HEIGHT, black_area_height))
    photo_area_height = CANVAS_HEIGHT - black_area_height
    print(f"검정 영역 {black_area_height}px / 사진 영역 {photo_area_height}px (제목 {len(lines)}줄 기준 동적 계산)")

    if background_path:
        source_image = Image.open(background_path).convert("RGB")
        # 비율 유지한 채 사진 영역을 꽉 채우도록 맞추고 중앙 기준으로 크롭한다
        photo = ImageOps.fit(source_image, (CANVAS_WIDTH, photo_area_height),
                              method=Image.LANCZOS, centering=(0.5, 0.5))
        image.paste(photo, (0, 0))
        image = apply_boundary_gradient(image, photo_area_height)

    # 좌상단 로고 (흰 텍스트 + 투명 배경 PNG를 세로 48px로 맞춰 얹는다)
    label_font = ImageFont.truetype(FONT_REGULAR_PATH, LABEL_FONT_SIZE)
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_width = int(logo.width * LOGO_HEIGHT / logo.height)
    logo = logo.resize((logo_width, LOGO_HEIGHT), Image.LANCZOS)
    image.paste(logo, (MARGIN_SIDE, 60), logo)

    # 검정 영역 안에 제목 여러 줄 + 날짜를 위에서부터 배치한다
    line_height = int(used_size * HOOK_LINE_SPACING)
    title_height = line_height * len(lines)
    date_height = int(LABEL_FONT_SIZE * 1.2)
    start_y = photo_area_height + HOOK_BLACK_MARGIN_TOP
    date_y = start_y + title_height + HOOK_DATE_GAP
    block_bottom = date_y + date_height
    safe_area_bottom = CANVAS_HEIGHT - HOOK_SAFE_MARGIN_BOTTOM
    if block_bottom > safe_area_bottom:
        print(f"경고: 날짜 하단({block_bottom}px)이 탐색 탭 안전영역 하단({safe_area_bottom}px)을 넘어 잘릴 수 있습니다.")

    for i, line in enumerate(lines):
        draw.text((MARGIN_SIDE, start_y + i * line_height), line, font=title_font, fill=TITLE_COLOR)

    draw.text((MARGIN_SIDE, date_y), date_text, font=label_font, fill=MUTED_COLOR)

    return image
