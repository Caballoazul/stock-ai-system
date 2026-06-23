import pandas as pd


# =====================================
# PER 시나리오 생성
# =====================================
def build_per_scenarios(price, current_per, target_per):

    eps = price / current_per

    scenarios = []

    per_list = [6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, target_per]

    for per in per_list:

        target_price = eps * per

        scenarios.append({
            "PER": round(per, 2),
            "Target Price": int(target_price)
        })

    return pd.DataFrame(scenarios)


# =====================================
# 정규화 함수
# =====================================
def normalize(series):

    return (series - series.min()) / (series.max() - series.min() + 1e-9)


# =====================================
# 퀀트 점수 생성
# =====================================
def build_quant_dataframe(df):

    df = df.copy()

    micron_per = df[df["name"] == "Micron"]["pe"].iloc[0]

    df["per_score"] = 1 - (df["pe"] / micron_per)

    df["eps_score"] = normalize(df["eps_growth"].fillna(0))
    df["revenue_score"] = normalize(df["revenue_growth"].fillna(0))
    df["roe_score"] = normalize(df["roe"].fillna(0))

    df["final_score"] = (
        df["per_score"] * 0.40 +
        df["eps_score"] * 0.25 +
        df["revenue_score"] * 0.20 +
        df["roe_score"] * 0.15
    )

    return df


# =====================================
# PER Gap 계산
# =====================================
def calc_per_gap(current_per, micron_per):

    return (micron_per / current_per - 1) * 100


# =====================================
# 분석 텍스트 생성
# =====================================
def make_analysis(df):

    micron = df[df["name"] == "Micron"].iloc[0]

    result = []
    result.append(f"Micron PER 기준: {micron['pe']:.2f}")
    result.append("-" * 40)

    for _, row in df.iterrows():

        if row["name"] == "Micron":
            continue

        gap = calc_per_gap(row["pe"], micron["pe"])

        result.append(
            f"{row['name']} | PER: {row['pe']:.2f} | Gap: {gap:.1f}%"
        )
