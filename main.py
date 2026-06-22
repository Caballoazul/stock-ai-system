from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from telegram_sender import send_telegram

def build_report():

    micron = get_micron_data()

    samsung = get_samsung_data()

    sk = get_skhynix_data()

report = f"""


📊 Semiconductor Dashboard

=====================
Micron
======

Price : {micron['price']}
PER   : {micron['pe']}
EPS   : {micron['eps']}

=====================
Samsung
=======

Price : {samsung['price']}
PER   : {samsung['pe']}
EPS   : {samsung['eps']}

=====================
SK Hynix
========

Price : {sk['price']}
PER   : {sk['pe']}
EPS   : {sk['eps']}
"""


return report


if name == "main":


report = build_report()

print(report)

send_telegram(report)

print("Telegram Sent")

