from database import get_connection


CURRENT_STRATEGY_VERSION = "v1.0.0"
CURRENT_STRATEGY_NAME = "Base observation learning strategy"
CURRENT_STRATEGY_DESCRIPTION = """
기본 전략 버전입니다.

포함 기능:
- KOSPI MA20 시장 필터
- MA5 / MA20 추세 조건
- RSI < 70 조건
- MACD > Signal 조건
- Bollinger 점수
- ATR 점수
- 섹터 보너스
- 적응 보너스
- 섹터 패널티
- 팩터 패널티
- 추천 이유 점수
- 관찰 모드
- 전략 개선 제안 저장
"""


def initialize_strategy_version():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        SELECT COUNT(*)
        FROM strategy_versions
        WHERE version = ?
    """, (
        CURRENT_STRATEGY_VERSION,
    ))

    existing_count = cursor.fetchone()[0]

    if existing_count == 0:
        cursor.execute("""
            INSERT INTO strategy_versions (
                version,
                name,
                description,
                is_active
            )
            VALUES (?, ?, ?, ?)
        """, (
            CURRENT_STRATEGY_VERSION,
            CURRENT_STRATEGY_NAME,
            CURRENT_STRATEGY_DESCRIPTION,
            1,
        ))

        print(f"전략 버전 등록 완료: {CURRENT_STRATEGY_VERSION}")
    else:
        print(f"전략 버전 이미 등록됨: {CURRENT_STRATEGY_VERSION}")

    connection.commit()
    connection.close()


def get_current_strategy_version():
    return CURRENT_STRATEGY_VERSION