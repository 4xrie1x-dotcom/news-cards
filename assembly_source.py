"""[비활성화 - photo_pipeline.py에서 사용하지 않음] 대한민국 국회
열린국회정보(open.assembly.go.kr)에서 의원 프로필 사진을 검색·다운로드하는 기능

국회 홈페이지 저작권 정책 확인 결과(2026-08-16), 자유이용은 "공공누리 마크가
개별 저작물에 부착된 경우"에만 적용되고 의원 프로필 사진에는 그 마크가 없어
사전 협의 없이는 자유이용 대상이 아니다. CLAUDE.md의 "저작권 프리 소스에서만
조달" 원칙에 어긋나므로, 저작권 관계를 국회사무처에 확인하기 전까지는 이 모듈을
photo_pipeline.py에 연결하지 않는다.

위키미디어보다 사진 해상도가 대체로 높아 1순위로 쓸 계획이었다. 열린국회정보의
검색 API가 돌려주는 deptImgUrl은 축소판(/thumb/)이라, 경로에서 그 부분을
제거하면 원본 해상도 사진 주소를 얻을 수 있다는 것까지는 확인했다."""

import os
import json
import requests
from PIL import Image
from io import BytesIO
from photo_quality import check_resolution

SEARCH_API = "https://open.assembly.go.kr/portal/assm/search/searchAssmMemberSch.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}
PEOPLE_DIR = "assets/people/assembly"


def search_assembly_member(name):
    """이름으로 제22대 국회의원을 검색해서 첫 번째 결과를 돌려준다. 없으면 None."""
    data = {
        "statusCd": "", "unitCd": "100022", "gubunId": "MA", "excelNm": "",
        "schHgNm": name, "schPoly": "", "schCmit": "", "schUpOrig": "", "schOrig": "",
        "schSexGbn": "", "schAge": "", "schReeleGbn": "", "schElectGbn": "",
        "rows": "10", "page": "1",
    }
    response = requests.post(SEARCH_API, headers=HEADERS, data=data, timeout=10)
    response.raise_for_status()
    results = response.json().get("data", [])
    return results[0] if results else None


def fetch_assembly_photo(person_name):
    """이름으로 국회 프로필 사진을 찾아 다운로드한다. 이미 저장된 사진이 있으면
    API를 부르지 않고 그 경로를 바로 돌려준다. 실패하면 이유를 한글로 출력하고
    None을 반환한다."""
    image_path = f"{PEOPLE_DIR}/{person_name}.png"
    json_path = f"{PEOPLE_DIR}/{person_name}.json"
    if os.path.exists(image_path):
        print(f"캐시 사용: {image_path}")
        if not check_resolution(Image.open(image_path), f"'{person_name}' 캐시 사진(국회)"):
            return None
        return image_path

    try:
        member = search_assembly_member(person_name)
        if not member or not member.get("deptImgUrl"):
            print(f"국회 열린국회정보에서 '{person_name}' 사진을 찾지 못했습니다.")
            return None

        full_url = member["deptImgUrl"].replace("/thumb/", "/")
        image_response = requests.get(full_url, headers={**HEADERS, "Referer": member["linkUrl"]}, timeout=10)
        image_response.raise_for_status()
        image = Image.open(BytesIO(image_response.content)).convert("RGB")
        if not check_resolution(image, f"'{person_name}' 국회 프로필 사진"):
            return None

        os.makedirs(PEOPLE_DIR, exist_ok=True)
        image.save(image_path, "PNG")
        meta = {
            "person": person_name, "party": member.get("polyNm"), "district": member.get("origNm"),
            "source_url": member["linkUrl"], "photo_url": full_url,
            "credit": "대한민국 국회 열린국회정보(open.assembly.go.kr)",
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"다운로드 완료: {image_path}")
        return image_path
    except Exception as error:
        print(f"'{person_name}' 국회 프로필 사진을 가져오는 중 오류: {error}")
        return None


if __name__ == "__main__":
    fetch_assembly_photo("이진숙")
