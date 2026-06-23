from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from analysis import (
    build_per_scenarios,
    make_summary_report
)

from telegram_sender import send_telegram


# =====================================
# 데이터 수집
# =====================================
def get_data():

    micron = get_micron_data()
    samsung = get_samsung_data()
    sk = get_skhynix_data()

    return micron, samsung, sk


# =====================================
# 메인 리포트 생성
# =====================================
def build_report():

    micron, samsung, sk = get_data()

    report = make_summary_report(
        micron,
        samsung,
        sk
    )

    return report


# =====================================
# 실행
# =====================================
if __name__ == "__main__":

    try:

        report = build_report()

        print(report)

        send_telegram(report)

        print("Telegram Sent")

    except Exception as e:
        print("Error:", str(e))
