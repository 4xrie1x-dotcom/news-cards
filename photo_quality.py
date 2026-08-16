"""다운로드한 사진의 해상도를 확인하는 기능

hook 배경 사진은 캔버스(1080x1350) 전체가 아니라 위쪽 사진 영역에만
ImageOps.fit()으로 맞춰 배치되는데, 이 영역의 실제 높이는 제목 줄 수에 따라
동적으로 정해진다(card_config.hook_black_area_height 참고). 사진을 사는
시점에는 어떤 기사에 쓰일지, 제목이 몇 줄일지 미리 알 수 없으므로, 사진
영역이 가장 작아지는 최악의 경우(HOOK_MIN_PHOTO_AREA_HEIGHT, 제목 3줄
기준)를 기준으로 미리 검사해 둔다. 이때 통과하면 어떤 제목 길이가 와도
사진 영역이 이보다 커질 일만 있으니 안전하다.

이때 원본을 얼마나 확대해야 하는지(확대 배율)가 실제 화질을 좌우한다.
절대 해상도 기준(가로/세로 몇 px 이상)은 원본 크기와 무관하게 사진 영역보다
살짝만 작아도 거부해버려서 지나치게 엄격하다. 인스타그램 업로드 자체가
사진을 압축하므로, 확대 배율이 낮으면 육안으로 티가 잘 안 난다.

1.5배→1.6배로 완화(2026-08-16): 오세훈 위키백과 인포박스 사진(716x993,
1.51배)을 실제로 hook 카드에 렌더링해서 이전에 통과 기준이었던 한동훈
사진(944x1259, 1.14배, 원본이 영상 캡처본이라 배율과 무관하게 소스
자체가 흐릿함)과 육안으로 비교한 결과, 1.51배 쪽이 오히려 더 또렷했다.
배율 숫자만으로 체감 화질을 예단하기 어렵다는 뜻이라, 이 정도까지는
완화해도 안전하다고 판단."""

from card_config import CANVAS_WIDTH, HOOK_MIN_PHOTO_AREA_HEIGHT

MAX_MAGNIFICATION = 1.6  # 이 배율을 넘게 확대해야 사진 영역을 채울 수 있으면 저화질로 본다


def check_resolution(image, label):
    """이미지 해상도와 사진 영역을 채우는 데 필요한 확대 배율을 출력하고, 배율이
    기준 이내인지 확인한다."""
    width, height = image.size
    magnification = max(CANVAS_WIDTH / width, HOOK_MIN_PHOTO_AREA_HEIGHT / height)
    print(f"{label} 해상도: {width}x{height} (사진 영역 확대 배율 {magnification:.2f}배)")
    if magnification > MAX_MAGNIFICATION:
        print(f"{label} 저화질로 판단(확대 배율 {magnification:.2f}배 > 최대 {MAX_MAGNIFICATION}배). 사용하지 않습니다.")
        return False
    return True
