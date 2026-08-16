"""5단계: terms·question과 요약 JSON을 조합해 CLAUDE.md 캡션 규격대로
캡션을 만들 수 있는지 확인하는 스크립트"""

import sys
from card_deck import ensure_period
from card_config import ACCOUNT_NAME
from render import TEST_SUMMARY

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

HASHTAGS = "#뉴스요약 #시사상식 #고등학생 #카드뉴스"


def has_batchim(word):
    """마지막 글자에 받침이 있는지 확인한다. 한글 음절이 아니면 받침 없다고 본다."""
    code = ord(word[-1]) - 0xAC00
    if 0 <= code <= 11171:
        return code % 28 != 0
    return False


def build_caption(summary_json, terms, question, source, photo_credit=None):
    """CLAUDE.md 캡션 규격대로 캡션 텍스트를 만든다.
    question은 워터마크 카드 CTA와 겹쳐서 카드와 마찬가지로 캡션에도 넣지 않되,
    반환값에는 그대로 남겨서 나중에 다른 용도로 쓸 수 있게 한다.
    photo_credit은 hook 배경으로 실제 사진(위키미디어 인물 사진 또는 Pexels
    상황 사진)을 썼을 때만 넘어온다 — 텍스트 전용 fallback이면 None."""
    hook = summary_json["hook"]
    # what+why를 문장 연결어 정도만 다듬어 그대로 이어붙인다 (새로 창작하지 않음)
    paragraph = f"{ensure_period(summary_json['what'])} {ensure_period(summary_json['why'])}"

    lines = [hook, "", paragraph, "", "—"]

    if terms:
        term, definition = terms[0]["term"], ensure_period(terms[0]["definition"])
        particle = "은" if has_batchim(term) else "는"
        lines.append(f"알아두기  {term}{particle} {definition}")

    lines.append(f"출처  {source}")
    lines.append("AI 요약")
    if photo_credit:
        lines.append(f"사진  {photo_credit}")
    lines.append("")
    account_tag = ACCOUNT_NAME.lstrip("@")
    lines.append(f"{HASHTAGS} #{account_tag}")

    caption = "\n".join(lines)
    return {"caption": caption, "question": question, "paragraph_length": len(paragraph)}


def main():
    """어제 그 재검표 기사로 캡션을 만들어보고, 글자 수와 함께 화면에 출력한다."""
    try:
        result = build_caption(
            TEST_SUMMARY,
            terms=TEST_SUMMARY["terms"],
            question=TEST_SUMMARY["question"],
            source="한국경제",
        )
        print(result["caption"])
        print("-" * 40)
        print(f"줄글 길이: {result['paragraph_length']}자 (목표 300~500자)")
        print(f"캡션 전체 길이: {len(result['caption'])}자")
        print(f"캡션에서 뺀 question(반환값에는 남음): {result['question']}")
    except Exception as error:
        print(f"캡션 생성 실패: {error}")


if __name__ == "__main__":
    main()
