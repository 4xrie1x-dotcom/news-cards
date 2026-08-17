"""6-2-b단계: Pexels로 상황 사진(사물·정물 위주)을 검색·다운로드하는 기능

위키미디어에서 인물 사진을 못 찾았을 때 hook 카드 배경 후보로 쓴다.
CLAUDE.md 규칙: 건물·랜드마크는 지역명을 포함해 검색하고, 인물·군중보다
사물·정물 키워드를 우선한다(국가 오매칭 완화 목적). 같은 상황 사진을
여러 기사에 재사용하는 게 부자연스러워서 위키미디어와 달리 캐시하지 않고
매번 새로 검색한다.

Pexels 저작권 정책: 웹사이트에서 직접 받으면 출처 표시가 필수는 아니지만,
API로 프로그램에서 받아오면 "Pexels로 눈에 띄게 연결되는 표시"가 필수다
(공식 문서 확인). 캡션의 사진 출처 줄로 이 요구를 충족한다.
"""

import os
import random
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from photo_quality import check_resolution

load_dotenv()

PEXELS_API = "https://api.pexels.com/v1/search"
TEMP_DIR = "tmp/pexels"
SEARCH_POOL_SIZE = 10  # 상위 몇 개 결과 중에서 무작위로 고를지

# 검색어를 아무리 구체적으로 써도 Pexels가 궁궐·전통 건축 사진을 섞어서
# 돌려주는 경우가 있어서(예: "Korea national assembly"가 경복궁 사진과
# 오매칭됨, 2026-08-17 확인) alt 텍스트로 한 번 더 걸러낸다.
LANDMARK_MISMATCH_WORDS = ["palace", "gyeongbokgung", "gwanghwamun", "temple", "traditional"]


def is_landmark_mismatch(photo):
    """사진의 alt 텍스트에 궁궐·전통 건축 관련 단어가 있으면 오매칭으로 본다."""
    alt = photo.get("alt") or ""
    alt = alt.lower()
    return any(word in alt for word in LANDMARK_MISMATCH_WORDS)


def search_pexels_photo(keyword, api_key):
    """키워드 하나로 Pexels를 검색해서, 궁궐·전통 건축 오매칭을 alt 텍스트로
    걸러낸 뒤 남은 결과 중 무작위로 하나를 돌려준다. 매번 1위만 쓰면 같은
    키워드가 항상 같은 사진으로 고정되는 문제(2026-08-17 확인)를 막기
    위해 상위 SEARCH_POOL_SIZE개 중에서 고른다."""
    headers = {"Authorization": api_key}
    params = {"query": keyword, "per_page": SEARCH_POOL_SIZE}
    response = requests.get(PEXELS_API, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    photos = response.json().get("photos", [])
    valid_photos = [p for p in photos if not is_landmark_mismatch(p)]
    if not valid_photos:
        return None
    return random.choice(valid_photos)


def fetch_pexels_photo(keywords):
    """keywords를 순서대로 시도해서 Pexels 상황 사진을 찾아 임시 경로에 저장한다.
    캐시하지 않고 매번 새로 검색한다. 성공하면 (저장 경로, 촬영자명)을,
    실패하면 이유를 한글로 출력하고 (None, None)을 반환한다."""
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("PEXELS_API_KEY가 .env에 없습니다.")
        return None, None

    for keyword in keywords:
        try:
            photo = search_pexels_photo(keyword, api_key)
            if not photo:
                print(f"'{keyword}'로 검색했지만 사진을 찾지 못했습니다.")
                continue

            # large(가로 940px)는 카드 캔버스(1080px)보다 작아서 original로 요청한다
            image_response = requests.get(photo["src"]["original"], timeout=10)
            image_response.raise_for_status()

            image = Image.open(BytesIO(image_response.content)).convert("RGB")
            if not check_resolution(image, f"'{keyword}' Pexels 사진"):
                continue

            os.makedirs(TEMP_DIR, exist_ok=True)
            image_path = f"{TEMP_DIR}/pexels_{photo['id']}.png"
            image.save(image_path, "PNG")

            photographer = photo.get("photographer", "정보 없음")
            print(f"'{keyword}'로 사진을 찾았습니다: {image_path} (촬영자: {photographer})")
            return image_path, photographer
        except Exception as error:
            print(f"'{keyword}' 검색 중 오류: {error}")
            continue

    print("모든 키워드로 검색했지만 사진을 찾지 못했습니다.")
    return None, None


if __name__ == "__main__":
    fetch_pexels_photo(["Yeouido national assembly building", "gavel", "documents"])
