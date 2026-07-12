from storage.database import get_connection


def analyze_stock_real_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            company_name,
            ticker,
            current_return
        FROM recommendation_performance
        WHERE current_return IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("종목별 실전 성과 랭킹")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 종목별 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    stock_stats = {}

    for company_name, ticker, current_return in rows:
        key = (company_name, ticker)

        if key not in stock_stats:
            stock_stats[key] = []

        stock_stats[key].append(current_return)

    stock_results = []

    for (company_name, ticker), returns in stock_stats.items():
        total_count = len(returns)

        win_count = 0

        for current_return in returns:
            if current_return > 0:
                win_count += 1

        loss_count = total_count - win_count
        success_rate = (win_count / total_count) * 100
        average_return = sum(returns) / total_count
        best_return = max(returns)
        worst_return = min(returns)

        stock_results.append({
            "company_name": company_name,
            "ticker": ticker,
            "total_count": total_count,
            "win_count": win_count,
            "loss_count": loss_count,
            "success_rate": success_rate,
            "average_return": average_return,
            "best_return": best_return,
            "worst_return": worst_return,
        })

    stock_results = sorted(
        stock_results,
        key=lambda x: x["average_return"],
        reverse=True
    )

    rank = 1

    for stock in stock_results:
        print(
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"{stock['ticker']} | "
            f"추천수 {stock['total_count']}회 | "
            f"수익중 {stock['win_count']}회 | "
            f"손실/보합 {stock['loss_count']}회 | "
            f"성공률 {stock['success_rate']:.2f}% | "
            f"평균수익률 {stock['average_return']:.2f}% | "
            f"최고수익률 {stock['best_return']:.2f}% | "
            f"최저수익률 {stock['worst_return']:.2f}%"
        )

        rank += 1

    connection.close()