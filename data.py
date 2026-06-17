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


def calculate_bollinger_bands(data, period=20):
    data["BOLLINGER_MIDDLE"] = data["Close"].rolling(period).mean()
    data["BOLLINGER_STD"] = data["Close"].rolling(period).std()

    data["BOLLINGER_UPPER"] = (
        data["BOLLINGER_MIDDLE"] + data["BOLLINGER_STD"] * 2
    )

    data["BOLLINGER_LOWER"] = (
        data["BOLLINGER_MIDDLE"] - data["BOLLINGER_STD"] * 2
    )

    return data


def calculate_atr(data, period=14):
    high_low = data["High"] - data["Low"]

    high_close = (
        data["High"] - data["Close"].shift()
    ).abs()

    low_close = (
        data["Low"] - data["Close"].shift()
    ).abs()

    data["TR"] = high_low

    data["TR"] = data[["TR"]].join(
        high_close.rename("HIGH_CLOSE")
    ).join(
        low_close.rename("LOW_CLOSE")
    ).max(axis=1)

    data["ATR"] = data["TR"].rolling(period).mean()

    data["ATR_PERCENT"] = (
        data["ATR"] / data["Close"]
    ) * 100

    return data


def calculate_indicators(data):
    data["MA5"] = data["Close"].rolling(5).mean()
    data["MA20"] = data["Close"].rolling(20).mean()

    data["Volume_MA5"] = data["Volume"].rolling(5).mean()
    data["Volume_MA20"] = data["Volume"].rolling(20).mean()

    data = calculate_rsi(data)
    data = calculate_macd(data)
    data = calculate_bollinger_bands(data)
    data = calculate_atr(data)

    return data