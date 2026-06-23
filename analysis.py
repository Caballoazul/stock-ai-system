import pandas as pd


# =====================================================
# 포맷 함수 (한글화 + 통화)
# =====================================================
def format_krw(value):
    return f"{value:,.0f}원"


def format_usd(value):
    return f"${value:,.2f}"


# =====================================================
# PER 괴리율 (Micron 기준)
# =====================================================
def calc_gap(pe, micron_pe):

    return (micron_pe / pe - 1) * 100


# =====================================================
# 삼성 우선주 괴리율
# =====================================================
def calc_spread(common_price, preferred_price):

    return (common_price - preferred_price) / common_price


# =====================================================
# PER 시나리오 (0.5 step)
# =====================================================
def build_per_scenarios(price, pe, micron_pe):

    eps = price / pe if pe != 0 else 0

    scenarios = []

    per = max(0.5, round(pe * 2) / 2)

    while per <= micron_pe:

        scenarios.append({
            "per": per,
            "price": eps * per
        })

        per += 0.5

    return scenarios


# =====================================================
# 기본 종목 분석 (SK 포함)
# =====================================================
def analyze_basic(company, micron):

    price = float(company["price"])
    pe = float(company["pe"])
    eps = float(company["eps"])

    micron_pe = float(micron["pe"])

    return {
        "name": company["name"],
        "price": price,
        "pe": pe,
        "eps": eps,
        "gap": calc_gap(pe, micron_pe),
        "target_price": eps * micron_pe,
        "scenarios": build_per_scenarios(price, pe, micron_pe)
    }


# =====================================================
# 삼성 분석 (보통주 + 우선주)
# =====================================================
def analyze_samsung(common, preferred, micron):

    c_price = float(common["price"])
    p_price = float(preferred["price"])

    pe = float(common["pe"])
    eps = float(common["eps"])

    micron_pe = float(micron["pe"])

    # spread
    spread = calc_spread(c_price, p_price)

    # adjusted PER
    adj_per = pe * (1 + spread)

    return {
        "name": "삼성전자",

        # 보통주
        "common_price": c_price,
        "common_pe": pe,

        # 우선주
        "preferred_price": p_price,
        "preferred_pe": p_price / eps if eps else 0,

        # EPS
        "eps": eps,

        # 핵심 지표
        "spread": spread,
        "adjusted_pe": adj_per,

        # Micron 비교
        "gap_common": calc_gap(pe, micron_pe),
        "gap_preferred": calc_gap(p_price / eps if eps else 0, micron_pe),

        # 적정가
        "target_common": eps * micron_pe,
        "target_adjusted": eps * adj_per,

        # 시나리오 (보통주 기준)
        "scenarios_common": build_per_scenarios(c_price, pe, micron_pe),

        # 시나리오 (우선주 기준)
        "scenarios_preferred": build_per_scenarios(p_price, p_price / eps if eps else 0, micron_pe)
    }


# =====================================================
# SK하이닉스
# =====================================================
def analyze_sk(sk, micron):

    return analyze_basic(sk, micron)


# =====================================================
# 전체 리포트 생성 (한글 + 통화 + 콤마)
# =====================================================
def make_summary_report(micron, samsung_common, samsung_preferred, sk):

    m_pe = float(micron["pe"])

    s = analyze_samsung(samsung_common, samsung_preferred, micron)
    k = analyze_sk(sk, micron)

    report = []

    # =========================
    # 헤더
    # =========================
    report.append("📊 반도체 투자 밸류에이션 리포트")
    report.append("=" * 60)
    report.append(f"마이크론 PER: {m_pe:.2f}배 (USD 기준)")
    report.append("=" * 60)

    # =========================
    # 삼성전자 보통주
    # =========================
    report.append("\n🔷 삼성전자 (보통주)")

    report.append(f"현재가 : {format_krw(s['common_price'])}")
    report.append(f"PER    : {s['common_pe']:.2f}배")
    report.append(f"EPS    : {format_krw(s['eps'])}")
    report.append(f"괴리율 : {s['gap_common']:.1f}%")

    report.append(f"적정가 (Micron 기준): {format_krw(s['target_common'])}")
    report.append(f"적정가 (보정 PER)   : {format_krw(s['target_adjusted'])}")

    report.append("\n📌 PER 시나리오")
    for x in s["scenarios_common"]:
        report.append(
            f"{x['per']:.2f}배 → {format_krw(x['price'])}"
        )

    # =========================
    # 삼성 우선주
    # =========================
    report.append("\n🔷 삼성전자 (우선주)")

    report.append(f"현재가 : {format_krw(s['preferred_price'])}")
    report.append(f"PER    : {s['preferred_pe']:.2f}배")
    report.append(f"괴리율 : {s['spread']*100:.2f}%")

    report.append(f"적정가 (Micron 기준): {format_krw(s['target_common'])}")

    report.append("\n📌 PER 시나리오")
    for x in s["scenarios_preferred"]:
        report.append(
            f"{x['per']:.2f}배 → {format_krw(x['price'])}"
        )

    # =========================
    # SK하이닉스
    # =========================
    report.append("\n🔷 SK하이닉스")

    report.append(f"현재가 : {format_krw(k['price'])}")
    report.append(f"PER    : {k['pe']:.2f}배")
    report.append(f"EPS    : {format_krw(k['eps'])}")
    report.append(f"괴리율 : {k['gap']:.1f}%")
    report.append(f"적정가 : {format_krw(k['target_price'])}")

    report.append("\n📌 PER 시나리오")
    for x in k["scenarios"]:
        report.append(
            f"{x['per']:.2f}배 → {format_krw(x['price'])}"
        )

    # =========================
    # 요약
    # =========================
    report.append("\n" + "=" * 60)
    report.append("📌 투자 요약")

    report.append(f"삼성 Spread(우선주 할인): {s['spread']*100:.2f}%")
    report.append(f"삼성 보정 PER: {s['adjusted_pe']:.2f}배")
    report.append(f"마이크론 기준 PER: {m_pe:.2f}배")

    return "\n".join(report)
