import pandas as pd

DATASET_PATH = "ml/training_dataset.csv"
SCAN_PATH = "ml/scan_results.csv"

thresholds = [0.75, 0.76, 0.77, 0.78, 0.79, 0.80]

df = pd.read_csv(SCAN_PATH)

print("\n" + "#" * 80)
print("AI Threshold 후보 수 비교")
print("#" * 80)

for threshold in thresholds:
    signal_df = df[df["Probability"] >= threshold]

    print(f"\n기준값: {threshold:.2f}")
    print(f"후보 수: {len(signal_df)}")

    if not signal_df.empty:
        print(signal_df[["Ticker", "Date", "Close", "Probability"]].head(10).to_string(index=False))