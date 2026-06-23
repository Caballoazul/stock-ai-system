from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from telegram_sender import send_telegram


# =====================================
# 리포트 생성
# =====================================
def build_report():

    micron = get_micron_data()
    samsung = get_samsung_data()
    sk = get_skhynix_data()

    report = f"""
📊 Semiconductor Dashboard
=====================

Micron
------
Price : {micron['price']}
PER   : {micron['pe']}
EPS   : {micron['eps']}

Samsung
------
Price : {samsung['price']}
PER   : {samsung['pe']}
EPS   : {samsung['eps']}

SK Hynix
------
Price : {sk['price']}
PER   : {sk['pe']}
EPS   : {sk['eps']}
"""

    return report


# =====================================
# 실행 엔트리 포인트
# =====================================
if __name__ == "__main__":

    try:
        report = build_report()

        print(report)

        send_telegram(report)

        print("Telegram Sent")

    except Exception as e:
        print("Error occurred:", str(e))
