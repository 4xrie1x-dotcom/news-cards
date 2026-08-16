"""4단계: hook 카드 1장을 만드는지 확인하는 스크립트

카드 구조가 hook 1장으로 단순화되어 card_deck.py의 render_all_cards()는
hook_card.py 하나만 그린다. TEST_SUMMARY는 caption.py의 자체 테스트에서도
그대로 재사용한다.
"""

import sys
import os
from card_deck import render_all_cards

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = "output/test"

# 어제 만든 재검표 기사 요약 JSON을 그대로 하드코딩해서 테스트한다
TEST_SUMMARY = {
    "hook": '"아, 고르세요! 날짜 받아갈게요"…재검표 일정 두고 여야 폭발한 이유',
    "what": (
        "국회 지방선거 투표용지 부족 사태 국정조사특별위원회 3차 청문회에서 여야가 "
        "잠실 올림픽공원 투표지 재검표 일정과 방식을 두고 정면으로 충돌했다. "
        "더불어민주당은 18일 재검표를 서둘러 진행하자고 주장했으나, 국민의힘은 출범할 "
        "선관위 특검과 연계해야 한다고 맞섰다. 결국 합의가 무산되면서 야당은 청문회 "
        "일정을 단독으로 진행했고, 국민의힘은 투표율 오입력 문제를 집중 질타했다."
    ),
    "why": (
        "6·3 지방선거 당시 발생한 투표용지 부족 사태와 투표자 수 통계 오류의 진상을 "
        "규명하기 위해 국회에 국정조사권이 부여되었다. 그러나 조사 연장 기간 내에 "
        "투표지 재검표를 즉각 실시하려는 야당과, 곧 꾸려질 특검 수사와 연계해 신중하게 "
        "검증해야 한다는 여당의 입장이 부딪히면서 현재 국회 의사일정 전체가 파행을 빚고 있다."
    ),
    "terms": [
        {"term": "현안 질의", "definition": "국회가 소관 상임위원회나 특별위원회에서 주요 현안에 대해 관계자를 출석시켜 질의하고 보고를 받는 활동"},
        {"term": "오입력", "definition": "데이터를 입력할 때 실수나 잘못된 지침으로 실제 값과 다른 정보가 입력되는 일"},
    ],
    "question": "재검표를 서둘러야 한다는 입장과, 특검과 연계해야 한다는 입장 중 어떤 주장이 더 타당하다고 보십니까?",
}


def main():
    """hook 카드 1장을 만들어 output/test/에 저장한다."""
    try:
        result = render_all_cards(TEST_SUMMARY, date="2026.08.13")
        images = result["images"]
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        for i, image in enumerate(images, start=1):
            path = f"{OUTPUT_DIR}/card_{i}.png"
            image.save(path)
            print(f"저장: {path}")
        print(f"카드 총 {len(images)}장 생성 완료")
    except Exception as error:
        print(f"카드셋 생성 실패: {error}")


if __name__ == "__main__":
    main()
