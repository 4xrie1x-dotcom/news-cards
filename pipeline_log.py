"""main.py 실행 과정을 logs/{날짜}.log 파일에 자동으로 기록하는 기능

collect.py, filters.py, article_picker.py, photo_pipeline.py, card_deck.py 등
파이프라인 각 단계가 이미 무슨 일이 있었는지 한글로 print하고 있으므로, 그
출력을 화면에 그대로 보여주면서 동시에 파일에도 남긴다(tee 방식). 실행
시작·종료 시각과 총 소요 시간은 이 모듈이 앞뒤로 덧붙인다.

파일 이름을 logging.py로 짓지 않은 이유: 프로젝트 루트에 logging.py를 두면
파이썬 표준 라이브러리 logging 모듈을 가려버려서, 내부적으로 그 모듈을 쓰는
requests(→urllib3)가 임포트 단계에서 깨진다(실제로 재현해서 확인함)."""

import sys
import os
from datetime import datetime, timezone, timedelta

LOG_DIR = "logs"
# Actions 러너 시스템 시간대는 UTC라 명시적으로 KST로 변환한다(main.py의 날짜와
# 어긋나지 않게 하기 위해 — output/{날짜}/와 logs/{날짜}.log가 같은 기준을 써야 함)
KST = timezone(timedelta(hours=9))


class Tee:
    """write()를 여러 스트림에 동시에 흘려보내는 도우미. print()가 화면과
    로그 파일에 동시에 찍히게 하는 데 쓴다."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()  # 강제 종료·예외가 나도 그때까지의 로그는 디스크에 남아야 한다

    def flush(self):
        for stream in self.streams:
            stream.flush()


def start_logging():
    """오늘 날짜 로그 파일을 열고(이미 있으면 이어쓰기) 표준출력을 화면+파일
    동시 기록으로 바꾼다. 로그 파일 핸들과 시작 시각을 돌려준다."""
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now(KST).date().isoformat()
    log_path = f"{LOG_DIR}/{today}.log"
    log_file = open(log_path, "a", encoding="utf-8")
    start_time = datetime.now(KST)

    sys.stdout = Tee(sys.__stdout__, log_file)
    print(f"\n{'=' * 60}")
    print(f"실행 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
    return log_file, start_time


def stop_logging(log_file, start_time):
    """종료 시각과 총 소요 시간을 기록하고 표준출력을 원래대로 되돌린다."""
    end_time = datetime.now(KST)
    duration = end_time - start_time
    print(f"실행 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')} (소요 시간: {duration})")
    print(f"{'=' * 60}\n")
    sys.stdout = sys.__stdout__
    log_file.close()
