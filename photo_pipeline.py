"""6-2-d단계: 인물명 추출 → 위키백과 인포박스 → 위키미디어 커먼즈 → Pexels →
텍스트 fallback까지 hook 카드 배경 사진 조달 순서를 하나로 묶는 기능
"""

import re
import random
from wikipedia_infobox import fetch_wikipedia_infobox_photo
from photo_source import fetch_wikimedia_photos, get_wikimedia_credit
from pexels_source import fetch_pexels_photo

# assembly_source.py(국회 열린국회정보 프로필 사진)는 저작권 확인 전까지 비활성화.
# 국회 사이트 저작권 정책상 자유이용은 "공공누리 마크가 개별 부착된 저작물"에만
# 적용되는데, 의원 프로필 사진에는 그 마크가 없어 사전 협의 없이는 자유이용
# 대상이 아님을 확인했다(2026-08-16). CLAUDE.md의 "저작권 프리 소스에서만
# 조달" 원칙에 어긋나므로 확인될 때까지 위키미디어를 1순위로 되돌린다.

# 이름 뒤에 이 직함이 붙어 있으면 "요약에 언급된 주요 인물"로 본다.
# 정당명은 이름 앞이나 뒤 어디든 끼어들 수 있어서(예: "이진숙 국민의힘 의원",
# "국민의힘 이진숙 의원") 이름으로 착각하지 않도록 미리 지운 뒤 찾는다.
# 직함 바로 앞 글자만 이름으로 보는 단순한 규칙이라, 중간에 다른 단어가
# 끼면 못 잡을 수 있다
PERSON_TITLE_MARKERS = ["의원", "대표", "장관", "대통령", "총리", "위원장", "시장", "지사", "원내대표"]
TITLE_GROUP = "(?:" + "|".join(PERSON_TITLE_MARKERS) + ")"
NAME_PATTERN = re.compile(rf"([가-힣]{{2,4}})\s*{TITLE_GROUP}")

KNOWN_ORG_NAMES = [
    "더불어민주당", "국민의힘", "정의당", "개혁신당", "조국혁신당", "진보당",
    "국민의당", "새역사국민운동",
]

# 기사 맥락 단어 → Pexels 검색어. 사물·정물 위주로만 두고 인물·군중 키워드는 아예 넣지 않는다
CONTEXT_KEYWORD_MAP = [
    # "Korea national assembly"는 경복궁·광화문 사진과 오매칭됐다(2026-08-17
    # 확인, [07][09] 실행에서 재현). 여의도·실제 건물명을 넣어 궁궐과 구분한다.
    (("국회",), "Yeouido national assembly building"),
    (("청문회", "질의", "회의"), "microphone"),
    (("표결", "판결", "결정", "재검표"), "gavel"),
    (("서류", "자료", "문서", "보고서", "조사"), "documents"),
]
DEFAULT_KEYWORDS = ["documents", "microphone", "podium"]


def extract_person_name(summary_json):
    """hook/what/why에서 직함이 붙은 인물명을 하나 찾는다. 없으면 None을 반환한다.
    정당명 등 알려진 조직명은 사람 이름으로 착각하지 않도록 미리 지운다."""
    text = f"{summary_json.get('hook', '')} {summary_json.get('what', '')} {summary_json.get('why', '')}"
    text = text.replace("{", "").replace("}", "")
    for org in KNOWN_ORG_NAMES:
        text = text.replace(org, " ")
    for match in NAME_PATTERN.finditer(text):
        name = match.group(1)
        if name not in KNOWN_ORG_NAMES:
            return name
    return None


def extract_pexels_keywords(summary_json):
    """기사 맥락 단어를 보고 Pexels 검색어를 최대 3개 뽑는다. 못 찾으면 기본값을 쓴다."""
    text = f"{summary_json.get('hook', '')} {summary_json.get('what', '')} {summary_json.get('why', '')}"
    keywords = []
    for triggers, keyword in CONTEXT_KEYWORD_MAP:
        if any(trigger in text for trigger in triggers) and keyword not in keywords:
            keywords.append(keyword)
    return keywords[:3] if keywords else DEFAULT_KEYWORDS


def get_hook_background(summary_json):
    """hook 카드 배경 사진을 조달한다. 인물명이 있으면 위키백과 인포박스를
    먼저 시도하고, 실패하면 위키미디어 커먼즈 검색을, 그래도 실패하면
    Pexels로 상황 사진을 찾는다. 모두 실패하면 (None, None)을 반환해서
    hook_card.py가 텍스트 전용 fallback을 쓰게 한다.
    (사진 경로, 캡션에 넣을 출처 표시) 튜플을 반환한다 — 텍스트 fallback이면
    출처가 없으니 두 번째 값도 None이다."""
    person_name = extract_person_name(summary_json)
    if person_name:
        print(f"인물명 추출: {person_name}")

        infobox_path = fetch_wikipedia_infobox_photo(person_name)
        if infobox_path:
            print(f"배경 사진 조달 성공(위키백과 인포박스): {infobox_path}")
            return infobox_path, get_wikimedia_credit(infobox_path)
        print(f"위키백과 인포박스에서 '{person_name}' 사진을 못 찾아 위키미디어 커먼즈 검색으로 넘어갑니다.")

        photo_paths = fetch_wikimedia_photos(person_name)
        if photo_paths:
            photo_path = random.choice(photo_paths)
            print(f"배경 사진 조달 성공(위키미디어 커먼즈, {len(photo_paths)}장 중 무작위 선택): {photo_path}")
            return photo_path, get_wikimedia_credit(photo_path)
        print(f"위키미디어 커먼즈에서 '{person_name}' 사진을 못 찾아 Pexels로 넘어갑니다.")
    else:
        print("본문에서 직함이 붙은 인물명을 찾지 못해 Pexels로 넘어갑니다.")

    keywords = extract_pexels_keywords(summary_json)
    print(f"Pexels 검색 키워드: {keywords}")
    photo_path, photographer = fetch_pexels_photo(keywords)
    if photo_path:
        print(f"배경 사진 조달 성공(Pexels): {photo_path}")
        return photo_path, f"Pexels ({photographer})"

    print("배경 사진 조달 실패. hook 카드는 텍스트 전용 fallback을 씁니다.")
    return None, None
