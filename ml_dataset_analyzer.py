import pandas as pd

DATASET_PATH = "ml/training_dataset.csv"


def analyze_dataset_columns():
    df = pd.read_csv(DATASET_PATH)

    print("\n" + "#" * 80)
    print("ML 학습 데이터 컬럼 분석")
    print("#" * 80)

    print("\n[전체 컬럼]")
    for col in df.columns:
        print(col)

    print("\n[데이터 크기]")
    print(f"행 개수: {len(df)}")
    print(f"컬럼 개수: {len(df.columns)}")

    print("\n[Target 분포]")
    print(df["Target"].value_counts())
    print(df["Target"].value_counts(normalize=True) * 100)

    print("\n[숫자형 컬럼]")
    numeric_cols = df.select_dtypes(include=["number"]).columns

    for col in numeric_cols:
        print(col)


if __name__ == "__main__":
    analyze_dataset_columns()