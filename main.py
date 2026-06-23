from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from analysis import make_summary_report

from telegram_sender import send_telegram


# =====================================================
# 데이터 수집 레이어
# =====================================================
def get_all_data():

    micron = get_micron_data()
    samsung = get_samsung_data()
    sk = get_skhynix_data()

    return micron, samsung, sk


# =====================================================
# 리포트 생성
# =====================================================
def build_report():

    micron, samsung, sk = get_all_data()

    report = make_summary_report(
        micron,
        samsung,
        samsung,   # common
        sk
    )

    return report


# =====================================================
# 실행 엔트리 포인트
# =====================================================
if __name__ == "__main__":

    try:

        report = build_report()

        print(report)

        send_telegram(report)

        print("\n[OK] Telegram Sent Successfully")

    except Exception as e:

        print("\n[ERROR]", str(e))
