"""다운로드한 사진의 해상도를 확인하는 기능

hook 배경은 캔버스(1080x1350)를 꽉 채우도록 크롭되므로, 가로형 사진은
가로 폭이, 세로형 인물 사진은 세로 길이가 부족하면 업스케일로 흐려진다.
그래서 사진의 가로/세로 비율에 따라 기준을 다르게 적용한다."""

MIN_WIDTH = 1080  # 가로형 사진(Pexels 상황 사진 등) 최소 가로 폭
MIN_PORTRAIT_HEIGHT = 1350  # 세로형 인물 사진(국회 프로필 등) 최소 세로 길이, 캔버스 세로와 동일


def check_resolution(image, label):
    """이미지 해상도를 화면에 출력하고, 가로/세로형에 맞는 최소 기준을 만족하는지 확인한다."""
    width, height = image.size
    print(f"{label} 해상도: {width}x{height}")
    if width >= height:
        if width < MIN_WIDTH:
            print(f"{label} 저화질로 판단(가로형, 가로 {width}px < 최소 {MIN_WIDTH}px). 사용하지 않습니다.")
            return False
    else:
        if height < MIN_PORTRAIT_HEIGHT:
            print(f"{label} 저화질로 판단(세로형, 세로 {height}px < 최소 {MIN_PORTRAIT_HEIGHT}px). 사용하지 않습니다.")
            return False
    return True
