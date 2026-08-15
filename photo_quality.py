"""다운로드한 사진의 해상도를 확인하는 기능"""

# 카드 캔버스 가로 크기(1080px)보다 작으면 저화질로 본다
MIN_WIDTH = 1080


def check_resolution(image, label):
    """이미지 해상도를 화면에 출력하고, 최소 가로 폭 기준을 만족하는지 확인한다."""
    width, height = image.size
    print(f"{label} 해상도: {width}x{height}")
    if width < MIN_WIDTH:
        print(f"{label} 저화질로 판단(가로 {width}px < 최소 {MIN_WIDTH}px). 사용하지 않습니다.")
        return False
    return True
