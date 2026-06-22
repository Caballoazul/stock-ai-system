from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_sk_hynix_data
from analysis import make_analysis
from telegram_sender import send_telegram


def run():
    try:
        raw_data = [
            get_micron_data(),
            get_samsung_data(),
            get_sk_hynix_data()
        ]

        results = [make_analysis(d) for d in raw_data]

        report = "=== Semiconductor Analysis ===\n\n"

        for r in results:
            report += f"""
{r['name']}
Price: {r['price']}
EPS: {r['eps']}
PER: {r['pe']}
Fair Value: {r['fair_value']}
Gap: {r['gap']}
--------------------
"""

        return report

    except Exception as e:
        print(f"[ERROR] run() failed: {e}")
        return None


if __name__ == "__main__":

    report = run()

    if report:
        try:
            send_telegram(report)
            print("[SUCCESS] Telegram sent")
        except Exception as e:
            print(f"[ERROR] Telegram failed: {e}")
    else:
        print("[SKIP] No report generated")
