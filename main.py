from micron_per import get_micron_data
from samsung_per import (
    get_samsung_common_data,
    get_samsung_preferred_data
)
from skhynix_per import get_skhynix_data

from analysis import make_summary_report

from telegram_sender import send_telegram


# =====================================================
# 데이터 수집 레이어
# =====================================================
def get_all_data():

    micron = get_micron_data()

    samsung_common = get_samsung_common_data()
    samsung_preferred = get_samsung_preferred_data()

    sk = get_skhynix_data()

    return micron, samsung_common, samsung_preferred, sk


# =====================================================
# 리포트 생성
# =====================================================
def build_report():

    micron, samsung_common, samsung_preferred, sk = get_all_data()

    report = make_summary_report(
        micron,
        samsung_common,
        samsung_preferred,
        sk
    )

    return report


# =====================================================
# 실행 엔트리 포인트
# =====================================================
if __name__ == "__main__":

    try:

        report = build_report()

        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)

        send_telegram(report)

        print("\n[OK] Telegram Sent Successfully")

    except Exception as e:

        print("\n[ERROR]", str(e))
