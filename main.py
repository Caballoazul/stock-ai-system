# =====================================================
# main.py
# Semiconductor Quant Dashboard v4.0
# =====================================================

from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from analysis import (
    make_analysis,
    build_quant_dataframe,
    get_ranking,
    build_scenario
)

from telegram_sender import send_telegram


# =====================================================
# 리포트 생성
# =====================================================

def build_report():

    raw_data = [

        get_micron_data(),
        get_samsung_data(),
        get_skhynix_data()

    ]

    # 개별 분석
    results = [
        make_analysis(d)
        for d in raw_data
    ]

    # 퀀트 엔진
    df = build_quant_dataframe(results)

    ranking = get_ranking(df)

    scenarios = build_scenario(df)

    report = ""

    # =================================================
    # 1. 퀀트 스코어
    # =================================================

    report += "📊 반도체 퀀트 스코어\n"
    report += "=" * 30 + "\n\n"

    for _, row in df.iterrows():

        report += (
            f"{row['name']}\n"
            f"Score : {row['final_score']:.3f}\n"
            f"PER   : {row['pe']:.2f}\n"
            f"ROE   : {row['roe']:.2f}\n\n"
        )

    # =================================================
    # 2. 순위
    # =================================================

    report += "\n🏆 투자 순위\n"
    report += "=" * 30 + "\n"

    for idx, r in enumerate(ranking, start=1):

        report += (
            f"{idx}위 "
            f"{r['name']} "
            f"(Score {r['score']})\n"
        )

    # =================================================
    # 3. Micron 시나리오
    # =================================================

    report += "\n\n📈 Micron PER 기준 시나리오\n"
    report += "=" * 30 + "\n"

    for s in scenarios:

        report += (
            f"\n{s['name']}\n"
            f"현재 PER : {s['current_per']}\n"
            f"Micron PER : {s['micron_per']}\n"
            f"목표가 : {s['target_price']:,.0f}\n"
            f"상승여력 : {s['upside']}%\n"
        )

    # =================================================
    # 4. 최종 해석
    # =================================================

    top = ranking[0]

    report += "\n\n🧠 최종 투자 해석\n"
    report += "=" * 30 + "\n"

    report += (
        f"현재 퀀트 모델 기준 "
        f"최우수 종목은 "
        f"{top['name']} 입니다.\n\n"
    )

    report += (
        "본 모델은 PER + 성장성 + "
        "ROE를 결합한 "
        "상대가치 기반 모델입니다.\n"
    )

    report += (
        "Micron을 글로벌 메모리 "
        "벤치마크로 활용하여 "
        "상대가치를 평가합니다.\n"
    )

    return report


# =====================================================
# 실행
# =====================================================

if __name__ == "__main__":

    try:

        report = build_report()

        print(report)

        send_telegram(report)

        print(
            "\n[SUCCESS] Telegram sent"
        )

    except Exception as e:

        print(
            f"\n[ERROR] {e}"
        )
