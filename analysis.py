# =====================================================

# analysis.py

# Semiconductor Quant Engine v6

# =====================================================

import pandas as pd

# =====================================================

# 개별 종목 분석

# =====================================================

def make_analysis(data):

```
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
```

# =====================================================

# 정규화

# =====================================================

def normalize(series):

```
return (

    series - series.min()

) / (

    series.max() - series.min() + 1e-9

)
```

# =====================================================

# 퀀트 점수 계산

# =====================================================

def build_quant_dataframe(results):

```
df = pd.DataFrame(results)

micron = (
    df[df["name"] == "Micron"]
    .iloc[0]
)

micron_per = float(micron["pe"])

# -------------------------------------------------
# PER 점수
# -------------------------------------------------

df["per_score"] = (

    1 -
    (df["pe"] / micron_per)

)

# -------------------------------------------------
# 성장성 점수
# -------------------------------------------------

df["eps_score"] = normalize(
    df["eps_growth"].fillna(0)
)

df["revenue_score"] = normalize(
    df["revenue_growth"].fillna(0)
)

# -------------------------------------------------
# ROE 점수
# -------------------------------------------------

df["roe_score"] = normalize(
    df["roe"].fillna(0)
)

# -------------------------------------------------
# 최종 점수
# -------------------------------------------------

df["final_score"] = (

    df["per_score"] * 0.40 +

    df["eps_score"] * 0.25 +

    df["revenue_score"] * 0.20 +

    df["roe_score"] * 0.15

)

return df
```

# =====================================================

# 투자 순위

# =====================================================

def get_ranking(df):

```
ranked = (

    df.sort_values(
        "final_score",
        ascending=False
    )

)

result = []

for _, row in ranked.iterrows():

    result.append({

        "name":
            row["name"],

        "score":
            round(
                row["final_score"],
                3
            )

    })

return result
```

# =====================================================

# Micron 대비 PER Gap

# =====================================================

def calc_per_gap(

```
current_per,
micron_per
```

):

```
return (

    micron_per
    / current_per
    - 1

) * 100
```

# =====================================================

# PER 시나리오

# =====================================================

def build_per_scenarios(

```
company,
micron_per
```

):

```
eps = float(company["eps"])

scenarios = []

scenario_pers = [

    6.5,
    7.0,
    7.5,
    8.0,
    8.5,
    9.0,
    9.5,
    10.0

]

for per in scenario_pers:

    target_price = eps * per

    scenarios.append({

        "per":
            per,

        "target_price":
            target_price

    })

scenarios.append({

    "micron_per":
        micron_per,

    "micron_target":
        eps * micron_per

})

return scenarios
```

# =====================================================

# 단독 테스트

# =====================================================

if **name** == "**main**":

```
print(
    "Semiconductor Quant Engine v6 Ready"
)
```


