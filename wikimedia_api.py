"""위키미디어 커먼즈 API와 직접 통신하는 기능 (검색, 파일 정보 조회)

photo_source.py가 이 모듈을 이용해 후보 파일 목록과 각 파일의 실제 이미지
주소·라이선스 정보를 가져온다."""

import re
import requests

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "NewsCardsBot/0.1 (student CAS project)"}


def strip_html(text):
    """위키미디어가 돌려주는 저작자·라이선스 문구에 섞인 HTML 태그를 제거한다."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def search_wikimedia_files(query, limit):
    """위키미디어 커먼즈 파일(namespace=6)을 검색해서 상위 결과의 제목 목록을 돌려준다."""
    params = {"action": "query", "list": "search", "srsearch": query, "srnamespace": 6,
              "srlimit": limit, "format": "json"}
    response = requests.get(WIKIMEDIA_API, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    results = response.json().get("query", {}).get("search", [])
    return [r["title"] for r in results]


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
