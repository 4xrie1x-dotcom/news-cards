"""6단계: collect→extract→summarize→render→caption 파이프라인을 하루 여러
사건(기본 DAILY_ARTICLE_COUNT건)에 대해 실행하는 스크립트

기사 선정(사건 그룹화·다중 소재 건너뛰기)은 article_picker.py가 맡고,
사건 1건을 끝까지 처리하는 건 article_pipeline.py가 맡는다. 이 파일은
사건 그룹 상위 N개를 순회하며 하나씩 넘기기만 한다 — 같은 그룹에서
여러 건을 뽑지 않고 서로 다른 사건을 고른다. 하나가 실패해도 나머지는
계속 진행한다.
"""

import sys
from datetime import datetime, timezone, timedelta
from article_picker import find_candidate_event_groups
from article_pipeline import process_article
from output_writer import next_article_number
from pipeline_log import start_logging, stop_logging

# 윈도우 콘솔 기본 인코딩이 UTF-8이 아니라 한글이 깨져 보이는 문제를 방지
sys.stdout.reconfigure(encoding="utf-8")

# Actions 러너 시스템 시간대는 UTC라 명시적으로 KST로 변환한다(안 그러면 자정 근처 실행 시 날짜가 밀림)
KST = timezone(timedelta(hours=9))
DAILY_ARTICLE_COUNT = 3  # 하루에 처리할 서로 다른 사건 수


def main():
    """오늘의 사건 그룹 상위 DAILY_ARTICLE_COUNT개를 각각 끝까지 처리해서
    카드와 캡션을 만들고 저장한다."""
    today = datetime.now(KST).date()
    date_dir = f"output/{today.isoformat()}"

    print("1단계: 기사 후보 수집 중...")
    groups = find_candidate_event_groups()
    if not groups:
        print("실패(1단계 수집): 필터를 통과한 기사를 찾지 못했습니다.")
        return
    print(f"1단계 완료: 사건 그룹 {len(groups)}개 확보")

    target_groups = groups[:DAILY_ARTICLE_COUNT]
    success_count = 0
    for group in target_groups:
        article_number = next_article_number(date_dir)
        print(f"=== [{article_number}] 처리 시작 ({len(group['entries'])}곳이 다룬 사건) ===")
        try:
            success = process_article(group, article_number, today, date_dir)
        except Exception as error:
            print(f"[{article_number}] 실패(예상 못 한 예외): {error}")
            success = False
        print(f"=== [{article_number}] {'완료' if success else '건너뜀'} ===")
        if success:
            success_count += 1

    print(f"전체 파이프라인 종료: {success_count}/{len(target_groups)}건 성공")


if __name__ == "__main__":
    log_file, start_time = start_logging()
    try:
        main()
    finally:
        stop_logging(log_file, start_time)
