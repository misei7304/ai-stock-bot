def calculate_position(stock, capital=1000000, risk_ratio=0.3):

    available_money = capital * risk_ratio
    current_price = stock["current_price"]

    quantity = int(available_money // current_price)
    investment_amount = quantity * current_price

    can_buy = quantity > 0

    return {
        "capital": capital,
        "risk_ratio": risk_ratio,
        "available_money": available_money,
        "quantity": quantity,
        "investment_amount": investment_amount,
        "can_buy": can_buy,
    }