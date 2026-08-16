"""7단계: 완성된 카드·캡션·메타데이터를 output/{날짜}/{번호}/ 에 저장하는 기능"""

import os
import re
import json


def next_article_number(date_dir):
    """date_dir(output/{날짜}) 안에 이미 있는 두 자리 번호 폴더를 확인해서
    다음 번호를 두 자리 문자열로 돌려준다. 폴더가 없거나 번호 폴더가 없으면
    01부터 시작한다."""
    if not os.path.isdir(date_dir):
        return "01"
    existing = [int(name) for name in os.listdir(date_dir) if re.fullmatch(r"\d{2}", name)]
    return f"{max(existing, default=0) + 1:02d}"


def save_output(output_dir, deck, caption_result, summary_json, outlet, real_url, date_iso):
    """카드 이미지·캡션·데이터 JSON을 output_dir에 저장한다.
    본문 텍스트는 CLAUDE.md 절대 규칙상 저장하지 않는다."""
    os.makedirs(output_dir, exist_ok=True)
    for i, image in enumerate(deck["images"], start=1):
        image.save(f"{output_dir}/card_{i}.png")
    with open(f"{output_dir}/caption.txt", "w", encoding="utf-8") as f:
        f.write(caption_result["caption"])
    data = {**summary_json, "source": outlet, "url": real_url, "date": date_iso}
    with open(f"{output_dir}/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
