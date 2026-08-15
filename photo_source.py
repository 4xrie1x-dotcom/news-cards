"""6-2-a단계: 인물명으로 위키미디어 커먼즈에서 사진을 검색·다운로드하는 기능

CLAUDE.md 절대 규칙: 보도사진은 쓰지 않는다. 저작권 프리 소스(위키미디어)에서만
사진을 조달하고, 라이선스·저작자 정보를 같이 저장한다."""

import os
import re
import json
import requests
from PIL import Image
from io import BytesIO
from photo_quality import check_resolution

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "NewsCardsBot/0.1 (student CAS project)"}
PEOPLE_DIR = "assets/people"


def strip_html(text):
    """위키미디어가 돌려주는 저작자·라이선스 문구에 섞인 HTML 태그를 제거한다."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def search_wikimedia_file(query):
    """위키미디어 커먼즈 파일(namespace=6)을 검색해서 첫 번째 결과의 제목을 돌려준다."""
    params = {"action": "query", "list": "search", "srsearch": query, "srnamespace": 6, "format": "json"}
    response = requests.get(WIKIMEDIA_API, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    results = response.json().get("query", {}).get("search", [])
    return results[0]["title"] if results else None


def get_file_info(file_title):
    """파일의 실제 이미지 주소와 라이선스·저작자 정보를 가져온다."""
    params = {
        "action": "query", "titles": file_title, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "format": "json",
    }
    response = requests.get(WIKIMEDIA_API, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        imageinfo = page.get("imageinfo")
        if not imageinfo:
            continue
        info = imageinfo[0]
        meta = info.get("extmetadata", {})
        return {
            "url": info.get("url"),
            "license": meta.get("LicenseShortName", {}).get("value", "정보 없음"),
            "artist": strip_html(meta.get("Artist", {}).get("value", "")),
            "credit": strip_html(meta.get("Credit", {}).get("value", "")),
        }
    return None


def fetch_wikimedia_photo(person_name):
    """인물명으로 위키미디어 커먼즈에서 사진을 찾아 다운로드한다.
    이미 저장된 사진이 있으면 API를 부르지 않고 그 경로를 바로 돌려준다.
    실패하면 이유를 한글로 출력하고 None을 반환한다."""
    image_path = f"{PEOPLE_DIR}/{person_name}.png"
    json_path = f"{PEOPLE_DIR}/{person_name}.json"
    if os.path.exists(image_path):
        print(f"캐시 사용: {image_path}")
        if not check_resolution(Image.open(image_path), f"'{person_name}' 캐시 사진"):
            return None
        return image_path

    try:
        file_title = search_wikimedia_file(f"{person_name} 국회의원")
        if not file_title:
            print(f"위키미디어에서 '{person_name}' 사진을 찾지 못했습니다.")
            return None
        info = get_file_info(file_title)
        if not info or not info.get("url"):
            print(f"'{person_name}' 파일 정보를 가져오지 못했습니다.")
            return None
        image_response = requests.get(info["url"], headers=HEADERS, timeout=10)
        image_response.raise_for_status()
        image = Image.open(BytesIO(image_response.content)).convert("RGB")
        if not check_resolution(image, f"'{person_name}' 위키미디어 사진"):
            return None

        os.makedirs(PEOPLE_DIR, exist_ok=True)
        image.save(image_path, "PNG")
        meta = {
            "person": person_name, "file_title": file_title, "source_url": info["url"],
            "license": info["license"], "artist": info["artist"], "credit": info["credit"],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"다운로드 완료: {image_path} (라이선스: {info['license']})")
        return image_path
    except Exception as error:
        print(f"'{person_name}' 사진을 가져오는 중 오류: {error}")
        return None


if __name__ == "__main__":
    fetch_wikimedia_photo("이진숙")
