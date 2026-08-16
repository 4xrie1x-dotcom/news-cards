"""7단계: 완성된 카드·캡션·메타데이터를 output/{날짜}/{번호}/ 에 저장하는 기능"""

import os
import json


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
