"""본문 텍스트를 안전영역에 맞게 줄바꿈하고, 안 맞으면 폰트 크기를 단계적으로 줄이는 기능"""

from PIL import ImageFont


def wrap_text(text, font, draw, max_width):
    """긴 문장을 안전영역 너비에 맞게 여러 줄로 나눈다."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_body_text(text, draw, max_width, max_lines, font_sizes, font_path):
    """폰트 크기를 큰 것부터 순서대로 시도해서, 줄바꿈 결과가 최대 줄 수 안에
    들어가는 첫 조합을 찾는다. 끝까지 안 맞으면 가장 작은 크기로 진행한다.
    (폰트, 줄 목록, 실제로 쓴 크기, 몇 단계 줄었는지)를 반환한다."""
    font = None
    lines = []
    for step, font_size in enumerate(font_sizes):
        font = ImageFont.truetype(font_path, font_size)
        lines = wrap_text(text, font, draw, max_width)
        if len(lines) <= max_lines:
            return font, lines, font_size, step
    return font, lines, font_sizes[-1], len(font_sizes) - 1
