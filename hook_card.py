"""사진 배경 위에 제목이 올라가는 hook(1장) 카드를 그리는 기능

캔버스를 사진 영역(위 720px, 약 53%)과 고정 검정 영역(아래 630px, 약 47%)으로
나눈다. CLAUDE.md 규칙상 인스타 탐색 탭 썸네일은 정중앙 1080x1080으로 크롭되어
위아래 각 135px가 잘리므로, 실제 안전영역은 캔버스 세로 [135, 1215] 구간이다.
자동 축소 로직(text_fit.fit_body_text)은 "줄바꿈이 3줄 이내면 큰 폰트(108px)를
그대로 쓴다" 방식이라, 108px로 3줄이 나오는 조합(더 작은 폰트로는 축소되지 않음)이
세로로 가장 많은 공간을 차지하는 실제 최댓값이다. 이 조합 기준으로 역산해 비율을
정했다. 사진은 위 영역에만 비율 유지하며 맞춰 배치하고(1.5배 넘게 확대해야
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
EXPLORE_TAB_CROP = 135  # 인스타 탐색 탭 썸네일이 위아래로 잘라내는 높이 (CLAUDE.md)
SAFE_AREA_TOP = EXPLORE_TAB_CROP  # 135px, 이보다 위는 탐색 탭에서 잘림
SAFE_AREA_BOTTOM = CANVAS_HEIGHT - EXPLORE_TAB_CROP  # 1215px, 이보다 아래는 탐색 탭에서 잘림
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
        # 비율 유지한 채 사진 영역을 꽉 채우도록 맞추고 중앙 기준으로 크롭한다
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

    # 고정 검정 영역 안에 제목 여러 줄 + 날짜를 위에서부터 배치한다
    line_height = int(used_size * HOOK_LINE_SPACING)
    title_height = line_height * len(lines)
    date_gap = 16
    date_height = int(LABEL_FONT_SIZE * 1.2)
    start_y = HOOK_PHOTO_AREA_HEIGHT + BLACK_AREA_MARGIN_TOP
    date_y = start_y + title_height + date_gap
    block_bottom = date_y + date_height
    if block_bottom > SAFE_AREA_BOTTOM:
        print(f"경고: 날짜 하단({block_bottom}px)이 탐색 탭 안전영역 하단({SAFE_AREA_BOTTOM}px)을 넘어 잘릴 수 있습니다.")
    if start_y < SAFE_AREA_TOP:
        print(f"경고: 제목 상단({start_y}px)이 탐색 탭 안전영역 상단({SAFE_AREA_TOP}px)보다 위라 잘릴 수 있습니다.")

    for i, line in enumerate(lines):
        draw.text((MARGIN_SIDE, start_y + i * line_height), line, font=title_font, fill=TITLE_COLOR)

    draw.text((MARGIN_SIDE, date_y), date_text, font=label_font, fill=MUTED_COLOR)

    return image
