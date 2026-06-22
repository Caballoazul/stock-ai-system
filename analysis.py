# =====================================================
# analysis.py
# Semiconductor Quant Engine v5
# =====================================================

import pandas as pd


# =====================================================
# 개별 종목 분석
# =====================================================

def make_analysis(data):

    return {
        "name": data["name"],
        "price": data["price"],
        "pe": data["pe"],
        "eps": data["eps"],
        "eps_growth": data["eps_growth"],
        "revenue_growth": data["revenue_growth"],
        "roe": data["roe"]
    }


# =====================================================
# 정규화
# =====================================================

def normalize(series):

    return (
        series - series.min()
    ) / (
        series.max() - series.min() + 1e-9
    )


# =====================================================
# 퀀트 데이터프레임 생성
# =====================================================

def build_quant_dataframe(results):

    df = pd.DataFrame(results)

    micron = (
        df[df["name"] == "Micron"]
        .iloc[0]
    )

    micron_per = micron["pe"]

    # -------------------------------------------
    # PER 점수
    # -------------------------------------------

    df["per_score"] = (
        1 - (df["pe"] / micron_per)
    )

    # -------------------------------------------
    # 성장성 점수
    # -------------------------------------------

    df["eps_score"] = normalize(
        df["eps_growth"].fillna(0)
    )

    df["revenue_score"] = normalize(
        df["revenue_growth"].fillna(0)
    )

    # -------------------------------------------
    # ROE 점수
    # -------------------------------------------

    df["roe_score"] = normalize(
        df["roe"].fillna(0)
    )

    # -------------------------------------------
    # 최종 점수
    # -------------------------------------------

    df["final_score"] = (

        df["per_score"] * 0.40 +

        df["eps_score"] * 0.25 +

        df["revenue_score"] * 0.20 +

        df["roe_score"] * 0.15
    )

    return df


# =====================================================
# 투자 순위
# =====================================================

def get_ranking(df):

    ranked = (
        df.sort_values(
            "final_score",
            ascending=False
        )
    )

    result = []

    for _, row in ranked.iterrows():

        result.append({

            "name": row["name"],

            "score": round(
                row["final_score"],
                3
            )

        })

    return result


# =====================================================
# PER 시나리오 생성
# =====================================================

def build_per_scenarios(
    company,
    micron_per
):

    current_per = float(company["pe"])

    current_price = float(
        company["price"]
    )

    eps = float(
        company["eps"]
    )

    scenarios = []

    p = round(current_per, 1)

    while p <= micron_per + 0.01:

        target_price = eps * p

        upside = (
            target_price /
            current_price - 1
        ) * 100

        scenarios.append({

            "per": round(p, 1),

            "target_price":
                target_price,

            "upside":
                upside

        })

        p += 0.5

    micron_target = (
        eps * micron_per
    )

    micron_upside = (

        micron_target
        / current_price
        - 1

    ) * 100

    scenarios.append({

        "micron_target":
            micron_target,

        "micron_upside":
            micron_upside

    })

    return scenarios


# =====================================================
# 단독 테스트
# =====================================================

if __name__ == "__main__":

    print(
        "Semiconductor Quant Engine Ready"
    )

