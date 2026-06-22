import yfinance as yf

def get_samsung_data():
    ticker = "005930.KS"
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": "Samsung",
        "price": info.get("currentPrice"),
        "eps": info.get("epsCurrentYear"),
        "pe": info.get("trailingPE")
    }