"""위키백과 인포박스 대표 이미지로 인물 사진을 조달하는 기능

문서가 있고 대표 이미지(인포박스 사진)가 있으면, 위키미디어 커먼즈
자유 검색보다 화질이 좋을 때가 많다(커먼즈 검색은 아무 사진이나
걸리는 반면 인포박스 사진은 그 인물의 "대표" 사진으로 관리팀·본인이
직접 고른 경우가 많음). 문서가 없거나 대표 이미지가 없으면 None을
반환해서 photo_pipeline.py가 기존 커먼즈 검색
(photo_source.fetch_wikimedia_photos)으로 넘어가게 한다."""

import os
import json
import requests
from PIL import Image
from io import BytesIO
from photo_quality import check_resolution
from wikimedia_api import HEADERS, get_file_info

WIKIPEDIA_KO_API = "https://ko.wikipedia.org/w/api.php"
PEOPLE_DIR = "assets/people"


def search_wikipedia_page(name):
    """한국어 위키백과에서 인물명으로 문서를 검색해 제목을 돌려준다. 없으면 None."""
    params = {"action": "query", "list": "search", "srsearch": name, "srlimit": 1, "format": "json"}
    response = requests.get(WIKIPEDIA_KO_API, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    results = response.json().get("query", {}).get("search", [])
    return results[0]["title"] if results else None


def get_page_image_filename(title):
    """문서의 대표 이미지(인포박스 사진) 파일명을 돌려준다. 없으면 None."""
    params = {"action": "query", "titles": title, "prop": "pageimages", "piprop": "name", "format": "json"}
    response = requests.get(WIKIPEDIA_KO_API, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        filename = page.get("pageimage")
        if filename:
            return filename
    return None


def fetch_wikipedia_infobox_photo(person_name):
    """위키백과에서 인물명으로 문서를 찾고, 그 문서의 인포박스 대표
    이미지를 원본 해상도로 다운로드한다. 이미 캐시된 파일이 있으면
    API를 부르지 않고 그 경로를 바로 돌려준다. 문서가 없거나 대표
    이미지가 없거나 화질 기준을 못 넘으면 None을 반환한다."""
    person_dir = f"{PEOPLE_DIR}/{person_name}"
    image_path = f"{person_dir}/infobox.png"
    json_path = f"{person_dir}/infobox.json"
    if os.path.exists(image_path):
        print(f"캐시 사용: {image_path}")
        if not check_resolution(Image.open(image_path), f"'{person_name}' 위키백과 인포박스 캐시 사진"):
            return None
        return image_path

    try:
        title = search_wikipedia_page(person_name)
        if not title:
            print(f"위키백과에서 '{person_name}' 문서를 찾지 못했습니다.")
            return None
        filename = get_page_image_filename(title)
        if not filename:
            print(f"'{title}' 문서에 대표 이미지가 없습니다.")
            return None
        info = get_file_info(f"File:{filename}")
        if not info or not info.get("url"):
            print(f"'{filename}' 파일 정보를 가져오지 못했습니다.")
            return None
        image_response = requests.get(info["url"], headers=HEADERS, timeout=10)
        image_response.raise_for_status()
        image = Image.open(BytesIO(image_response.content)).convert("RGB")
        if not check_resolution(image, f"'{person_name}' 위키백과 인포박스 사진"):
            return None

        os.makedirs(person_dir, exist_ok=True)
        image.save(image_path, "PNG")
        meta = {
            "person": person_name, "wikipedia_title": title, "file_title": filename,
            "source_url": info["url"], "license": info["license"], "artist": info["artist"],
            "credit": info["credit"],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"다운로드 완료: {image_path} (라이선스: {info['license']})")
        return image_path
    except Exception as error:
        print(f"'{person_name}' 위키백과 인포박스 사진을 가져오는 중 오류: {error}")
        return None


if __name__ == "__main__":
    fetch_wikipedia_infobox_photo("한동훈")
