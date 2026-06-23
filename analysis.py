import pandas as pd


# =====================================
# PER Gap 계산
# =====================================
def calc_gap(current_pe, micron_pe):

    return (micron_pe / current_pe - 1) * 100


# =====================================
# 개별 종목 분석
# =====================================
def analyze_company(company, micron):

    price = float(company["price"])
    pe = float(company["pe"])
    eps = float(company["eps"])

    micron_pe = float(micron["pe"])

    target_price = eps * micron_pe

    gap = calc_gap(pe, micron_pe)

    return {
        "name": company["name"],
        "price": price,
        "pe": pe,
        "eps": eps,
        "gap": gap,
        "target_price": target_price
    }


# =====================================
# PER 시나리오 (0.5 step)
# =====================================
def build_per_scenarios(company, micron_per):

    price = float(company["price"])
    pe = float(company["pe"])

    eps = price / pe

    scenarios = []

    start = round(pe * 2) / 2

    per = start

    while per <= micron_per:

        scenarios.append({
            "PER": round(per, 1),
            "Target Price": int(eps * per)
        })

        per += 0.5

    return scenarios


# =====================================
# 전체 리포트 생성
# =====================================
def make_summary_report(micron, samsung, sk):

    m = analyze_company(micron, micron)
    s = analyze_company(samsung, micron)
    k = analyze_company(sk, micron)

    report = []

    report.append("📊 Semiconductor Investment Report")
    report.append("=" * 50)

    report.append(f"Micron PER: {m['pe']:.2f}")
    report.append("=" * 50)

    # ================================
    # 삼성전자 / SK하이닉스
    # ================================
    for item in [s, k]:

        report.append(f"\n{item['name']}")
        report.append("-" * 40)

        report.append(f"Price : {item['price']:,.0f}")
        report.append(f"PER   : {item['pe']:.2f}")
        report.append(f"EPS   : {item['eps']:.2f}")

        report.append(f"Micron 대비 Gap : {item['gap']:.1f}%")

        report.append(
            f"Target Price (Micron PER): {item['target_price']:,.0f}"
        )

        # ============================
        # PER 시나리오
        # ============================
        report.append("\nPER Scenario (0.5 step)")

        scenarios = build_per_scenarios(item, m["pe"])

        for s in scenarios:

            report.append(
                f"PER {s['PER']:.1f} → {s['Target Price']:,.0f}"
            )

        report.append("\n" + "=" * 50)

    return "\n".join(report)
