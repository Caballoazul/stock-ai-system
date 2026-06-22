from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from analysis import (
    make_analysis,
    build_quant_dataframe,
    build_per_scenarios,
    calc_per_gap
)

from telegram_sender import send_telegram


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
    samsung = df[df["name"] == "Samsung"].iloc[0]
    sk = df[df["name"] == "SK Hynix"].iloc[0]

    micron_per = float(micron["pe"])

    report = ""

    # =================================================
    # Micron
    # =================================================

    report += (
        "=====================\n"
        "Micron\n"
        "=====================\n"
        f"현재주가 : ${micron['price']:,.1f}\n"
        f"현재PER  : {micron['pe']:.2f}\n"
        f"현재EPS  : {micron['eps']:,.1f}\n\n"
    )

    # =================================================
    # Samsung
    # =================================================

    samsung_gap = calc_per_gap(
        samsung["pe"],
        micron_per
    )

    report += (
        "=====================\n"
        "Samsung\n"
        "=====================\n"
        f"현재주가 : {samsung['price']:,.0f}\n"
        f"현재PER  : {samsung['pe']:.2f}\n"
        f"현재EPS  : {samsung['eps']:,.1f}\n"
        f"MicronPER: {micron_per:.2f}\n"
        f"PER Gap  : {samsung_gap:.1f}%\n\n"
    )

    samsung_scenarios = build_per_scenarios(
        samsung,
        micron_per
    )

    report += (
        "[PER 0.5 단위 시나리오]\n"
        "------------------------------------------------------------\n"
    )

    for row in samsung_scenarios[:-1]:

        report += (
            f"PER {row['per']:>4.1f} | "
            f"목표가 {row['target_price']:>10,.0f} | "
            f"상승 {row['upside']:>7.1f}%\n"
        )

    report += (
        "\n[Micron 100% 기준]\n"
        f"목표가 : {samsung_scenarios[-1]['micron_target']:,.0f}\n"
        f"상승여력 : {samsung_scenarios[-1]['micron_upside']:.1f}%\n\n"
    )

    # =================================================
    # SK Hynix
    # =================================================

    sk_gap = calc_per_gap(
        sk["pe"],
        micron_per
    )

    report += (
        "\n============================================================\n"
        "SKHynix\n"
        "============================================================\n"
        f"현재주가 : {sk['price']:,.0f}\n"
        f"현재PER  : {sk['pe']:.2f}\n"
        f"현재EPS  : {sk['eps']:,.1f}\n"
        f"MicronPER: {micron_per:.2f}\n"
        f"PER Gap  : {sk_gap:.1f}%\n\n"
    )

    sk_scenarios = build_per_scenarios(
        sk,
        micron_per
    )

    report += (
        "[PER 0.5 단위 시나리오]\n"
        "------------------------------------------------------------\n"
    )

    for row in sk_scenarios[:-1]:

        report += (
            f"PER {row['per']:>4.1f} | "
            f"목표가 {row['target_price']:>10,.0f} | "
            f"상승 {row['upside']:>7.1f}%\n"
        )

    report += (
        "\n[Micron 100% 기준]\n"
        f"목표가 : {sk_scenarios[-1]['micron_target']:,.0f}\n"
        f"상승여력 : {sk_scenarios[-1]['micron_upside']:.1f}%\n\n"
    )

    # =================================================
    # 투자 해석
    # =================================================

    report += (
        "\n🧠 최종 투자 해석\n"
        "============================================================\n"
    )

    if samsung_gap > sk_gap:

        report += (
            f"현재 Micron 대비 가장 할인율이 큰 종목은 "
            f"Samsung ({samsung_gap:.1f}%) 입니다.\n"
        )

    else:

        report += (
            f"현재 Micron 대비 가장 할인율이 큰 종목은 "
            f"SK Hynix ({sk_gap:.1f}%) 입니다.\n"
        )

    return report


if __name__ == "__main__":

    try:

        report = build_report()

        print(report)

        send_telegram(report)

        print("[SUCCESS] Telegram sent")

    except Exception as e:

        print(f"[ERROR] {e}")
