"""다운로드한 사진의 해상도를 확인하는 기능

hook 배경은 ImageOps.fit()으로 캔버스(1080x1350)를 꽉 채우도록 크롭되는데,
이때 원본을 얼마나 확대해야 하는지(확대 배율)가 실제 화질을 좌우한다.
절대 해상도 기준(가로/세로 몇 px 이상)은 원본 크기와 무관하게 캔버스보다
살짝만 작아도 거부해버려서 지나치게 엄격하다. 인스타그램 업로드 자체가
사진을 압축하므로, 확대 배율이 낮으면(1.5배 이내) 육안으로 티가 잘 안 난다."""

from card_config import CANVAS_WIDTH, CANVAS_HEIGHT

MAX_MAGNIFICATION = 1.5  # 이 배율을 넘게 확대해야 캔버스를 채울 수 있으면 저화질로 본다


def check_resolution(image, label):
    """이미지 해상도와 캔버스를 채우는 데 필요한 확대 배율을 출력하고, 배율이
    기준 이내인지 확인한다."""
    width, height = image.size
    magnification = max(CANVAS_WIDTH / width, CANVAS_HEIGHT / height)
    print(f"{label} 해상도: {width}x{height} (캔버스 확대 배율 {magnification:.2f}배)")
    if magnification > MAX_MAGNIFICATION:
        print(f"{label} 저화질로 판단(확대 배율 {magnification:.2f}배 > 최대 {MAX_MAGNIFICATION}배). 사용하지 않습니다.")
        return False
    return True
