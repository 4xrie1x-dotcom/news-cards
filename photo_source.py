"""6-2-a단계: 인물명으로 위키미디어 커먼즈에서 사진을 검색·다운로드하는 기능

CLAUDE.md 절대 규칙: 보도사진은 쓰지 않는다. 저작권 프리 소스(위키미디어)에서만
사진을 조달하고, 라이선스·저작자 정보를 같이 저장한다.

같은 인물이 여러 기사에 반복 등장할 때 매번 똑같은 사진이 나오지 않도록,
검색 상위 후보 중 화질 기준을 통과하는 사진을 모두 캐시해 둔다. 실제로 어느
사진을 쓸지 고르는 것은 photo_pipeline.py가 담당한다."""

import os
import json
import glob
import requests
from PIL import Image
from io import BytesIO
from photo_quality import check_resolution
from wikimedia_api import HEADERS, search_wikimedia_files, get_file_info

PEOPLE_DIR = "assets/people"
CANDIDATE_LIMIT = 5  # 검색 상위 몇 개까지 화질 검사를 시도할지


def fetch_wikimedia_photos(person_name):
    """인물명으로 위키미디어에서 화질 기준을 통과하는 사진을 모두 찾아
    assets/people/{인물명}/01.png, 02.png... 형식으로 캐시한다.
    이미 캐시된 사진이 있으면 API를 부르지 않고 그 경로 목록을 바로 돌려준다.
    실패하면(후보가 없거나 전부 저화질이면) 빈 리스트를 반환한다."""
    person_dir = f"{PEOPLE_DIR}/{person_name}"
    if os.path.isdir(person_dir):
        cached = sorted(glob.glob(f"{person_dir}/*.png"))
        if cached:
            print(f"캐시 사용: {person_dir} ({len(cached)}장)")
            return cached

    try:
        file_titles = search_wikimedia_files(f"{person_name} 국회의원", CANDIDATE_LIMIT)
    except Exception as error:
        print(f"'{person_name}' 검색 중 오류: {error}")
        return []
    if not file_titles:
        print(f"위키미디어에서 '{person_name}' 사진을 찾지 못했습니다.")
        return []

    saved_paths = []
    for file_title in file_titles:
        try:
            info = get_file_info(file_title)
            if not info or not info.get("url"):
                continue
            image_response = requests.get(info["url"], headers=HEADERS, timeout=10)
            image_response.raise_for_status()
            image = Image.open(BytesIO(image_response.content)).convert("RGB")
        except Exception as error:
            print(f"'{file_title}' 후보를 가져오는 중 오류: {error}")
            continue
        if not check_resolution(image, f"'{person_name}' 후보 {len(saved_paths) + 1}"):
            continue

        os.makedirs(person_dir, exist_ok=True)
        index = len(saved_paths) + 1
        image_path = f"{person_dir}/{index:02d}.png"
        image.save(image_path, "PNG")
        meta = {
            "person": person_name, "file_title": file_title, "source_url": info["url"],
            "license": info["license"], "artist": info["artist"], "credit": info["credit"],
        }
        with open(f"{person_dir}/{index:02d}.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"다운로드 완료: {image_path} (라이선스: {info['license']})")
        saved_paths.append(image_path)

    if not saved_paths:
        print(f"'{person_name}' 후보 {len(file_titles)}개 중 화질 기준을 통과한 사진이 없습니다.")
    return saved_paths


if __name__ == "__main__":
    fetch_wikimedia_photos("한동훈")
