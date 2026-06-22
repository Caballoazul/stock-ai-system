import yfinance as yf

def get_skhynix_data():
    ticker = "000660.KS"
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": "SK Hynix",
        "price": info.get("currentPrice"),
        "eps": info.get("epsCurrentYear"),
        "pe": info.get("trailingPE")
    }