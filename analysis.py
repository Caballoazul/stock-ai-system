def calculate_fair_value(eps, target_pe=10):
    if not eps:
        return None
    return eps * target_pe


def calculate_gap(price, fair_value):
    if not price or not fair_value:
        return None
    return (fair_value - price) / price * 100


def make_analysis(data):
    eps = data.get("eps")
    price = data.get("price")

    fair_value = calculate_fair_value(eps)
    gap = calculate_gap(price, fair_value)

    return {
        "name": data["name"],
        "price": price,
        "eps": eps,
        "pe": data.get("pe"),
        "fair_value": fair_value,
        "gap": gap
    }