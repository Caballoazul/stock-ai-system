import pandas as pd

def make_analysis(data):


return {
    "name": data["name"],
    "price": data["price"],
    "pe": data["pe"],
    "eps": data["eps"],
    "change_pct": data["change_pct"],
    "eps_growth": data["eps_growth"],
    "revenue_growth": data["revenue_growth"],
    "roe": data["roe"]
}


def normalize(series):


return (
    series - series.min()
) / (
    series.max() - series.min() + 1e-9
)


def build_quant_dataframe(results):


df = pd.DataFrame(results)

micron = df[df["name"] == "Micron"].iloc[0]
micron_per = float(micron["pe"])

df["per_score"] = (
    1 - (df["pe"] / micron_per)
)

df["eps_score"] = normalize(
    df["eps_growth"].fillna(0)
)

df["revenue_score"] = normalize(
    df["revenue_growth"].fillna(0)
)

df["roe_score"] = normalize(
    df["roe"].fillna(0)
)

df["final_score"] = (
    df["per_score"] * 0.40
    + df["eps_score"] * 0.25
    + df["revenue_score"] * 0.20
    + df["roe_score"] * 0.15
)

return df


def calc_per_gap(current_per, micron_per):


return (
    micron_per / current_per - 1
) * 100


def build_per_scenarios(company, micron_per):


eps = float(company["eps"])

scenario_pers = [
    6.5, 7.0, 7.5, 8.0,
    8.5, 9.0, 9.5, 10.0
]

scenarios = []

for per in scenario_pers:

    scenarios.append({
        "per": per,
        "target_price": eps * per
    })

scenarios.append({
    "micron_per": micron_per,
    "micron_target": eps * micron_per
})

return scenarios


if name == "main":


print("Semiconductor Quant Engine Ready")


