def analyze_stock(data, company_name):

    current_price = data["Close"].iloc[-1]

    ma5 = data["MA5"].iloc[-1]
    ma20 = data["MA20"].iloc[-1]

    volume_ma5 = data["Volume_MA5"].iloc[-1]
    volume_ma20 = data["Volume_MA20"].iloc[-1]

    rsi = data["RSI"].iloc[-1]

    macd = data["MACD"].iloc[-1]
    macd_signal = data["MACD_SIGNAL"].iloc[-1]
    macd_histogram = data["MACD_HISTOGRAM"].iloc[-1]

    bollinger_upper = data["BOLLINGER_UPPER"].iloc[-1]
    bollinger_middle = data["BOLLINGER_MIDDLE"].iloc[-1]
    bollinger_lower = data["BOLLINGER_LOWER"].iloc[-1]

    price_score = ((ma5 - ma20) / ma20) * 100
    volume_score = ((volume_ma5 - volume_ma20) / volume_ma20) * 100

    macd_score = 0

    if macd > macd_signal:
        macd_score = 5

    bollinger_score = 0

    if current_price <= bollinger_lower * 1.05:
        bollinger_score = 3
    elif current_price >= bollinger_upper * 0.95:
        bollinger_score = -3

    total_score = (
        price_score
        + (volume_score * 0.3)
        + macd_score
        + bollinger_score
    )

    is_buy_candidate = (
        current_price > ma5
        and ma5 > ma20
        and total_score > 0
        and rsi < 70
        and macd > macd_signal
    )

    return {
        "company_name": company_name,
        "current_price": current_price,
        "price_score": price_score,
        "volume_score": volume_score,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_histogram": macd_histogram,
        "macd_score": macd_score,
        "bollinger_upper": bollinger_upper,
        "bollinger_middle": bollinger_middle,
        "bollinger_lower": bollinger_lower,
        "bollinger_score": bollinger_score,
        "total_score": total_score,
        "rsi": rsi,
        "is_buy_candidate": is_buy_candidate,
    }