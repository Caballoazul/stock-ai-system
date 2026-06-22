
# =====================================================
# main.py
# Semiconductor PER Dashboard v5
# =====================================================

from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from analysis import (
    make_analysis,
    build_quant_dataframe,
    build_per_scenarios
)

from telegram_sender import send_telegram


# =====================================================
# Report Builder
# =====================================================

def build_report():

    raw_data = [
        get_micron_data(),
        get_samsung_data(),
        get_skhynix_data()
    ]

    results = [
        make_analysis(d)
        for d in raw_data
    ]

    df = build_quant_dataframe(results)

    micron = df[df["name"] == "Micron"].iloc[0]

    micron_price = micron["price"]
    micron_per = micron["pe"]
    micron_eps = micron["eps"]

    report = ""

    # =================================================
    # Micron
    # =================================================

    report += (
        "=====================\n"
        "Micron\n"
        "=====================\n"
        f"현재주가 : ${micron_price:,.1f}\n"
        f"현재PER  : {micron_per:.2f}\n"
        f"현재EPS  : {micron_eps:.1f}\n\n"
    )

    # =================================================
    # Samsung
    # =================================================

    samsung = df[df["name"] == "Samsung"].iloc[0]

    gap = (micron_per / samsung["pe"] - 1) * 100

    report += (
        "=====================\n"
        "Samsung\n"
        "=====================\n"
        f"현재주가 : {samsung['price']:,.0f}\n"
        f"현재PER  : {samsung['pe']:.2f}\n"
        f"현재EPS  : {samsung['eps']:,.1f}\n"
        f"MicronPER: {micron_per:.2f}\n"
        f"PER Gap  : {gap:.1f}%\n\n"
    )

    # =================================================
    # Samsung Scenario
    # =================================================

    samsung_scenario = build_per_scenarios(
        samsung,
        micron_per
    )

    report += (
        "[PER 0.5 단위 시나리오]\n"
        "------------------------------------------------------------\n"
    )

    for row in samsung_scenario:

        report += (
            f"PER {row['per']:>4.1f} | "
            f"목표가 {row['target_price']:>10,.0f} | "
            f"상승 {row['upside']:>7.1f}%\n"
        )

    report += (
        f"\n[Micron 100% 기준]\n"
        f"목표가 : {samsung_scenario[-1]['micron_target']:,.0f}\n"
        f"상승여력 : {samsung_scenario[-1]['micron_upside']:.1f}%\n\n"
    )

    # =================================================
    # SK Hynix
    # =================================================

    sk = df[df["name"] == "SK Hynix"].iloc[0]

    gap = (micron_per / sk["pe"] - 1) * 100

    report += (
        "\n============================================================\n"
        "SKHynix\n"
        "============================================================\n"
        f"현재주가 : {sk['price']:,.0f}\n"
        f"현재PER  : {sk['pe']:.2f}\n"
        f"현재EPS  : {sk['eps']:,.1f}\n"
        f"MicronPER: {micron_per:.2f}\n"
        f"PER Gap  : {gap:.1f}%\n\n"
    )

    sk_scenario = build_per_scenarios(
        sk,
        micron_per
    )

    report += (
        "[PER 0.5 단위 시나리오]\n"
        "------------------------------------------------------------\n"
    )

    for row in sk_scenario:

        report += (
            f"PER {row['per']:>4.1f} | "
            f"목표가 {row['target_price']:>10,.0f} | "
            f"상승 {row['upside']:>7.1f}%\n"
        )

    report += (
        f"\n[Micron 100% 기준]\n"
        f"목표가 : {sk_scenario[-1]['micron_target']:,.0f}\n"
        f"상승여력 : {sk_scenario[-1]['micron_upside']:.1f}%\n\n"
    )

    # =================================================
    # Final Comment
    # =================================================

    report += (
        "\n🧠 최종 투자 해석\n"
        "============================================================\n"
    )

    if samsung["pe"] < sk["pe"]:

        report += (
            "삼성전자가 SK하이닉스 대비 더 낮은 PER에서 거래되고 있습니다.\n"
            "Micron 대비 할인율이 가장 큰 종목은 삼성전자입니다.\n"
        )

    else:

        report += (
            "SK하이닉스가 Micron 대비 상대가치 매력이 높습니다.\n"
        )

    return report


# =====================================================
# Execute
# =====================================================

if __name__ == "__main__":

    try:

        report = build_report()

        print(report)

        send_telegram(report)

        print("[SUCCESS] Telegram sent")

    except Exception as e:

        print(f"[ERROR] {e}")


