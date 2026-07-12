from performance_analysis.factor_performance import (
    analyze_atr_performance,
    analyze_bollinger_performance,
    analyze_final_score_performance,
    analyze_macd_performance,
    analyze_rsi_performance,
)


def run_factor_performance_analysis():
    analyze_rsi_performance()
    analyze_macd_performance()
    analyze_atr_performance()
    analyze_bollinger_performance()
    analyze_final_score_performance()