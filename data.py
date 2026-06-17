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


def calculate_macd(data):
    data["EMA12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA26"] = data["Close"].ewm(span=26, adjust=False).mean()

    data["MACD"] = data["EMA12"] - data["EMA26"]
    data["MACD_SIGNAL"] = data["MACD"].ewm(span=9, adjust=False).mean()
    data["MACD_HISTOGRAM"] = data["MACD"] - data["MACD_SIGNAL"]

    return data


def calculate_indicators(data):
    data["MA5"] = data["Close"].rolling(5).mean()
    data["MA20"] = data["Close"].rolling(20).mean()

    data["Volume_MA5"] = data["Volume"].rolling(5).mean()
    data["Volume_MA20"] = data["Volume"].rolling(20).mean()

    data = calculate_rsi(data)
    data = calculate_macd(data)

    return data