import pandas as pd


# =====================================================
# PER 괴리율 계산 (Micron 대비)
# =====================================================
def calc_gap(pe, micron_pe):

    return (micron_pe / pe - 1) * 100


# =====================================================
# 삼성 우선주 할인율 (괴리율)
# =====================================================
def calc_samsung_spread(common_price, preferred_price):

    return (common_price - preferred_price) / common_price


# =====================================================
# PER 시나리오 (0.5 step)
# =====================================================
def build_per_scenarios(price, pe, micron_pe):

    eps = price / pe

    scenarios = []

    per = round(pe * 2) / 2

    while per <= micron_pe:

        scenarios.append({
            "PER": round(per, 2),
            "Price": int(eps * per)
        })

        per += 0.5

    return scenarios


# =====================================================
# 개별 종목 분석 (공통)
# =====================================================
def analyze_basic(company, micron):

    price = float(company["price"])
    pe = float(company["pe"])
    eps = float(company["eps"])

    micron_pe = float(micron["pe"])

    gap = calc_gap(pe, micron_pe)

    target_price = eps * micron_pe

    return {
        "name": company["name"],
        "price": price,
        "pe": pe,
        "eps": eps,
        "gap": gap,
        "target_price": target_price
    }


# =====================================================
# 삼성 (보통주 + 우선주 통합 분석)
# =====================================================
def analyze_samsung(common, preferred, micron):

    common_price = float(common["price"])
    preferred_price = float(preferred["price"])

    pe = float(common["pe"])
    eps = common_price / pe

    micron_pe = float(micron["pe"])

    # 1. 괴리율
    spread = calc_samsung_spread(common_price, preferred_price)

    # 2. 보정 PER
    adjusted_per = pe * (1 + spread)

    # 3. 적정가
    target_micron = eps * micron_pe
    target_adjusted = eps * adjusted_per

    # 4. PER 시나리오
    scenarios = build_per_scenarios(
        common_price,
        pe,
        micron_pe
    )

    return {
        "name": "Samsung",
        "common_price": common_price,
        "preferred_price": preferred_price,
        "pe": pe,
        "eps": eps,
        "spread": spread,
        "adjusted_per": adjusted_per,
        "gap": calc_gap(pe, micron_pe),
        "target_micron": target_micron,
        "target_adjusted": target_adjusted,
        "scenarios": scenarios
    }


# =====================================================
# SK하이닉스 (기존 구조 유지)
# =====================================================
def analyze_sk(sk, micron):

    return analyze_basic(sk, micron)


# =====================================================
# 전체 리포트 생성
# =====================================================
def make_summary_report(micron, samsung_common, samsung_preferred, sk):

    m_pe = float(micron["pe"])

    s = analyze_samsung(samsung_common, samsung_preferred, micron)
    k = analyze_sk(sk, micron)

    report = []

    report.append("📊 Semiconductor Valuation Report (v2)")
    report.append("=" * 60)

    report.append(f"Micron PER: {m_pe:.2f}")
    report.append("=" * 60)

    # =========================
    # 삼성전자
    # =========================
    report.append("\n🔷 Samsung Common")
    report.append(f"Price: {s['common_price']:,.0f}")
    report.append(f"PER  : {s['pe']:.2f}")
    report.append(f"EPS  : {s['eps']:.2f}")
    report.append(f"Gap  : {s['gap']:.1f}%")

    report.append(f"Target (Micron): {s['target_micron']:,.0f}")
    report.append(f"Target (Adj PER): {s['target_adjusted']:,.0f}")

    report.append("\nPER Scenario")
    for x in s["scenarios"]:
        report.append(f"{x['PER']:.2f} → {x['Price']:,.0f}")

    # =========================
    # 삼성 우선주
    # =========================
    report.append("\n🔷 Samsung Preferred")
    report.append(f"Price: {s['preferred_price']:,.0f}")
    report.append(f"Spread: {s['spread']:.2%}")

    # =========================
    # SK하이닉스
    # =========================
    report.append("\n🔷 SK Hynix")
    report.append(f"Price: {k['price']:,.0f}")
    report.append(f"PER  : {k['pe']:.2f}")
    report.append(f"EPS  : {k['eps']:.2f}")
    report.append(f"Gap  : {k['gap']:.1f}%")
    report.append(f"Target: {k['target_price']:,.0f}")

    k_scen = build_per_scenarios(k["price"], k["pe"], m_pe)

    report.append("\nPER Scenario")
    for x in k_scen:
        report.append(f"{x['PER']:.2f} → {x['Price']:,.0f}")

    report.append("\n" + "=" * 60)

    # =========================
    # 요약
    # =========================
    report.append("\n📌 Summary")

    report.append(
        f"Samsung Spread: {s['spread']:.2%}"
    )

    report.append(
        f"Samsung Adjusted PER: {s['adjusted_per']:.2f}"
    )

    return "\n".join(report)
