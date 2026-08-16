"""카드 렌더링에서 여러 파일이 공통으로 쓰는 캔버스·색상·폰트 상수 (CLAUDE.md 디자인 규격)"""

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350
MARGIN_SIDE = 90
MARGIN_TOP = 150
MARGIN_BOTTOM = 160

BACKGROUND_COLOR = "#FFFFFF"
BODY_COLOR = "#16181C"
MUTED_COLOR = "#8B9099"
DIVIDER_COLOR = "#E5E5E5"
TITLE_COLOR = "#FFFFFF"
EMPHASIS_COLOR = "#E03A2F"  # 문장 내 핵심 구절 강조색 (최대 1곳)
FALLBACK_BG_COLOR = "#16181C"  # 사진이 없을 때 hook 카드에 쓰는 배경

LABEL_FONT_SIZE = 26
FONT_EXTRABOLD_PATH = "fonts/Pretendard-ExtraBold.otf"
FONT_REGULAR_PATH = "fonts/Pretendard-Regular.otf"

# hook 카드 사진/검정 영역 동적 분할 (제목이 짧으면 사진을 크게, 길면 검정을 크게)
# 검정 영역 = 제목 줄 수·폰트 크기로 정해지는 실제 필요 높이(제목+날짜+여백).
# 인스타 탐색 탭 썸네일은 정중앙 1080x1080으로 크롭돼 캔버스 하단 135px가 잘리므로
# (CLAUDE.md), 그 여백은 항상 그대로 지킨다.
HOOK_LINE_SPACING = 1.2
HOOK_MAX_LINES = 3  # 제목은 최대 3줄 (CLAUDE.md 디자인 규격)
HOOK_FONT_SIZE_STEPS = [108, 96, 84]  # 안전영역을 넘으면 이 순서로 축소
HOOK_BLACK_MARGIN_TOP = 40  # 사진/검정 경계에서 제목 시작까지 여백
HOOK_DATE_GAP = 16  # 제목과 날짜 사이 여백
HOOK_SAFE_MARGIN_BOTTOM = 135  # 탐색 탭 크롭 높이와 동일한 하단 여백


def hook_black_area_height(font_size, num_lines):
    """제목 폰트 크기·줄 수로 실제 필요한 검정 영역 높이(제목+날짜+여백)를 계산한다."""
    line_height = int(font_size * HOOK_LINE_SPACING)
    title_height = line_height * num_lines
    date_height = int(LABEL_FONT_SIZE * 1.2)
    return HOOK_BLACK_MARGIN_TOP + title_height + HOOK_DATE_GAP + date_height + HOOK_SAFE_MARGIN_BOTTOM


# 1줄 제목(가장 큰 108px) 기준 최소값, 3줄·108px(자동 축소가 걸리지 않는 최댓값) 기준 최댓값
HOOK_MIN_BLACK_AREA_HEIGHT = hook_black_area_height(HOOK_FONT_SIZE_STEPS[0], 1)
HOOK_MAX_BLACK_AREA_HEIGHT = hook_black_area_height(HOOK_FONT_SIZE_STEPS[0], HOOK_MAX_LINES)
# 사진 영역이 가장 작아지는 경우(검정 영역 최대) 기준. photo_quality.py가 이 값으로
# 화질을 검사해야 어떤 제목 길이가 와도 안전하다
HOOK_MIN_PHOTO_AREA_HEIGHT = CANVAS_HEIGHT - HOOK_MAX_BLACK_AREA_HEIGHT

# 워터마크 카드 CTA 크기·색 (확정)
WATERMARK_MAIN_FONT_SIZE = 68
WATERMARK_SECONDARY_FONT_SIZE = 40
WATERMARK_SECONDARY_COLOR = "#C7CBD1"  # MUTED_COLOR보다 밝게 해서 잘 보이게 함
WATERMARK_ACCOUNT_FONT_SIZE = 34  # 계정명. 출처보다 살짝 크게
WATERMARK_SOURCE_FONT_SIZE = 30  # 출처·AI 요약. 보조 요소라 이전 크기 유지

ACCOUNT_NAME = "데일리정치"  # 표시 이름. 캡션 해시태그 등 이름 형태로 쓰는 자리
ACCOUNT_HANDLE = "@dailypolitics_kr"  # 핸들. 카드 이미지 위 계정 표시(팔로우 유도) 자리
