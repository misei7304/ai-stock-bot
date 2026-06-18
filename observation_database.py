from database import save_recommendation_to_database


def save_observation_candidate(stock, market_result):
    try:
        save_recommendation_to_database(stock, market_result)
        print("관찰 후보 DB 저장 완료")
    except Exception as error:
        print(f"관찰 후보 DB 저장 실패: {error}")