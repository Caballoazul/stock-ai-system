def run():
    try:
        raw_data = [
            get_micron_data(),
            get_samsung_data(),
            get_sk_hynix_data()
        ]

        results = [make_analysis(d) for d in raw_data]

        print("\n=== Semiconductor Analysis ===\n")

        report = "=== Semiconductor Analysis ===\n\n"

        for r in results:
            print(f"{r['name']}")
            print(f"Price: {r['price']}")
            print(f"EPS: {r['eps']}")
            print(f"PER: {r['pe']}")
            print(f"Fair Value: {r['fair_value']}")
            print(f"Gap: {r['gap']}")
            print("--------------------")

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

    from telegram_sender import send_telegram

    report = run()

    if report:
        try:
            send_telegram(report)
            print("[SUCCESS] Telegram sent")
        except Exception as e:
            print(f"[ERROR] Telegram failed: {e}")
    else:
        print("[SKIP] No report generated")
