import yfinance as yf


def analyze_market():

    kospi = yf.Ticker("^KS11")
    data = kospi.history(period="6mo")

    data = data.dropna(subset=["Close"])

    data["MA20"] = data["Close"].rolling(20).mean()
    data = data.dropna(subset=["MA20"])

    if data.empty:
        return {
            "market_name": "KOSPI",
            "current_price": 0,
            "ma20": 0,
            "is_market_bull": False,
        }

    current_price = data["Close"].iloc[-1]
    ma20 = data["MA20"].iloc[-1]

    is_market_bull = current_price > ma20

    return {
        "market_name": "KOSPI",
        "current_price": current_price,
        "ma20": ma20,
        "is_market_bull": is_market_bull,
    }