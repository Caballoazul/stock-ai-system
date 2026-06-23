import pandas as pd


# =====================================================
# PER 괴리율 (Micron 대비)
# =====================================================
def calc_gap(pe, micron_pe):

    return (micron_pe / pe - 1) * 100


# =====================================================
# 삼성 우선주 할인율 (Spread)
# =====================================================
def calc_spread(common_price, preferred_price):

    return (common_price - preferred_price) / common_price


# =====================================================
# PER 시나리오 (0.5 step)
# =====================================================
def build_per_scenarios(price, pe, micron_pe):

    eps = price / pe if pe != 0 else 0

    scenarios = []

    start = max(0.5, round(pe * 2) / 2)

    per = start

    while per <= micron_pe:

        scenarios.append({
            "per": round(per, 2),
            "price": int(eps * per)
        })

        per += 0.5

    return scenarios


# =====================================================
# 기본 종목 분석 (SK 포함 공통)
# =====================================================
def analyze_basic(company, micron):

    price = float(company["price"])
    pe = float(company["pe"])
    eps = float(company["eps"])

    micron_pe = float(micron["pe"])

    gap = calc_gap(pe, micron_pe)

    target_price = eps * micron_pe if eps else 0

    scenarios = build_per_scenarios(price, pe, micron_pe)

    return {
        "name": company["name"],
        "price": price,
        "pe": pe,
        "eps": eps,
        "gap": gap,
        "target_price": target_price,
        "scenarios": scenarios
    }


# =====================================================
# 삼성 (보통주 + 우선주 통합 분석)
# =====================================================
def analyze_samsung(common, preferred, micron):

    common_price = float(common["price"])
    preferred_price = float(preferred["price"])

    pe = float(common["pe"])
    eps = float(common["eps"])

    micron_pe = float(micron["pe"])

    # 1️⃣ spread (우선주 할인율)
    spread = calc_spread(common_price, preferred_price)

    # 2️⃣ 보정 PER
    adjusted_pe = pe * (1 + spread)

    # 3️⃣ 적정가
    target_micron = eps * micron_pe if eps else 0
    target_adjusted = eps * adjusted_pe if eps else 0

    # 4️⃣ PER 시나리오
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
        "adjusted_pe": adjusted_pe,

        "gap": calc_gap(pe, micron_pe),

        "target_micron": target_micron,
        "target_adjusted": target_adjusted,

        "scenarios": scenarios
    }


# =====================================================
# SK 하이닉스 (기존 구조 유지)
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

    # ================================
    # Header
    # ================================
    report.append("📊 Semiconductor Valuation Report (v2)")
    report.append("=" * 60)
    report.append(f"Micron PER: {m_pe:.2f}")
    report.append("=" * 60)

    # ================================
    # 삼성전자
    # ================================
    report.append("\n🔷 Samsung Common")
    report.append(f"Price : {s['common_price']:,.0f}")
    report.append(f"PER   : {s['pe']:.2f}")
    report.append(f"EPS   : {s['eps']:.2f}")
    report.append(f"Gap   : {s['gap']:.1f}%")

    report.append(f"Target (Micron): {s['target_micron']:,.0f}")
    report.append(f"Target (Adj PER): {s['target_adjusted']:,.0f}")

    report.append("\nPER Scenario")
    for x in s["scenarios"]:
        report.append(f"{x['per']:.2f} → {x['price']:,.0f}")

    # ================================
    # 삼성 우선주
    # ================================
    report.append("\n🔷 Samsung Preferred")
    report.append(f"Price : {s['preferred_price']:,.0f}")
    report.append(f"Spread: {s['spread']:.2%}")
    report.append(f"Adj PER: {s['adjusted_pe']:.2f}")

    # ================================
    # SK 하이닉스
    # ================================
    report.append("\n🔷 SK Hynix")
    report.append(f"Price : {k['price']:,.0f}")
    report.append(f"PER   : {k['pe']:.2f}")
    report.append(f"EPS   : {k['eps']:.2f}")
    report.append(f"Gap   : {k['gap']:.1f}%")
    report.append(f"Target: {k['target_price']:,.0f}")

    report.append("\nPER Scenario")
    for x in k["scenarios"]:
        report.append(f"{x['per']:.2f} → {x['price']:,.0f}")

    # ================================
    # Summary
    # ================================
    report.append("\n" + "=" * 60)
    report.append("📌 Summary")

    report.append(
        f"Samsung Spread (Pref Discount): {s['spread']:.2%}"
    )

    report.append(
        f"Samsung Adjusted PER: {s['adjusted_pe']:.2f}"
    )

    report.append(
        f"Micron Benchmark PER: {m_pe:.2f}"
    )

    return "\n".join(report)
