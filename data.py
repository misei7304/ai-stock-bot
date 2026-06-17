import yfinance as yf


def get_stock_data(ticker, period="6mo"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data


def calculate_rsi(data, period=14):
    delta = data["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    average_gain = gain.rolling(period).mean()
    average_loss = loss.rolling(period).mean()

    rs = average_gain / average_loss

    data["RSI"] = 100 - (100 / (1 + rs))

    return data


def calculate_indicators(data):
    data["MA5"] = data["Close"].rolling(5).mean()
    data["MA20"] = data["Close"].rolling(20).mean()

    data["Volume_MA5"] = data["Volume"].rolling(5).mean()
    data["Volume_MA20"] = data["Volume"].rolling(20).mean()

    data = calculate_rsi(data)

    return data