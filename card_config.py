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

# 워터마크 카드 CTA 크기·색 (확정)
WATERMARK_MAIN_FONT_SIZE = 68
WATERMARK_SECONDARY_FONT_SIZE = 40
WATERMARK_SECONDARY_COLOR = "#C7CBD1"  # MUTED_COLOR보다 밝게 해서 잘 보이게 함
WATERMARK_ACCOUNT_FONT_SIZE = 34  # 계정명. 출처보다 살짝 크게
WATERMARK_SOURCE_FONT_SIZE = 30  # 출처·AI 요약. 보조 요소라 이전 크기 유지

ACCOUNT_NAME = "@placeholder"  # 계정명 미정. 정해지면 이 값만 바꾸면 된다
