"""3단계: Gemini API가 응답하는지, 중립성·고등학생 눈높이 요약이 나오는지 확인하는 스크립트"""

import sys
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from collect import build_search_url, fetch_feed
from extract import resolve_real_url, get_article_text
from prompts import SUMMARY_PROMPT

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

# .env에서 GEMINI_API_KEY 등 환경변수를 읽어온다
load_dotenv()

# 테스트에 쓸 검색어와 무료 모델 이름
TEST_KEYWORD = "여야"
MODEL_NAME = "gemini-flash-lite-latest"


def find_test_entry():
    """'여야 재검표 공방' 관련 기사 하나를 찾는다. 없으면 첫 기사를 대신 쓴다."""
    feed = fetch_feed(build_search_url(TEST_KEYWORD))
    if not feed or not feed.entries:
        return None
    for entry in feed.entries:
        if "재검표" in entry.title:
            return entry
    return feed.entries[0]


def summarize(title, body):
    """Gemini에게 요약을 요청하고 JSON으로 파싱해서 반환한다. 실패하면 None을 반환한다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY가 .env에 없습니다.")
        return None

    prompt = SUMMARY_PROMPT.format(title=title, body=body)
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
    except Exception as error:
        print(f"Gemini API 요청 실패: {error}")
        return None

    try:
        return json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as error:
        print(f"Gemini 응답을 JSON으로 읽지 못했습니다: {error}")
        return None


def main():
    """기사 1개만 가져와 Gemini 요약 결과를 확인한다."""
    entry = find_test_entry()
    if not entry:
        print("테스트할 기사를 찾지 못했습니다.")
        return

    print(f"제목: {entry.title}")
    real_url = resolve_real_url(entry.link)
    if not real_url:
        return

    body = get_article_text(real_url, entry.title)
    if not body:
        return

    result = summarize(entry.title, body)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
