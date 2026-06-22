import yfinance as yf

def get_micron_data():
    ticker = "MU"
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": "Micron",
        "price": info.get("currentPrice"),
        "eps": info.get("epsCurrentYear"),
        "pe": info.get("trailingPE")
    }