def analyze_stock(data, company_name):

    current_price = data["Close"].iloc[-1]

    ma5 = data["MA5"].iloc[-1]
    ma20 = data["MA20"].iloc[-1]

    volume_ma5 = data["Volume_MA5"].iloc[-1]
    volume_ma20 = data["Volume_MA20"].iloc[-1]

    rsi = data["RSI"].iloc[-1]

    price_score = ((ma5 - ma20) / ma20) * 100
    volume_score = ((volume_ma5 - volume_ma20) / volume_ma20) * 100

    total_score = price_score + (volume_score * 0.3)

    is_buy_candidate = (
        current_price > ma5
        and ma5 > ma20
        and total_score > 0
        and rsi < 70
    )

    return {
        "company_name": company_name,
        "current_price": current_price,
        "price_score": price_score,
        "volume_score": volume_score,
        "total_score": total_score,
        "rsi": rsi,
        "is_buy_candidate": is_buy_candidate,
    }