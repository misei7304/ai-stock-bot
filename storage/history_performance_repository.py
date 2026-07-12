import csv
import os


HISTORY_FILE_NAME = "history.csv"


def history_file_exists():
    return os.path.exists(
        HISTORY_FILE_NAME
    )


def load_history_rows():
    with open(
        HISTORY_FILE_NAME,
        "r",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(file)

        fieldnames = list(
            reader.fieldnames or []
        )

        rows = list(reader)

    return {
        "fieldnames": fieldnames,
        "rows": rows,
    }


def save_history_rows(
    fieldnames,
    rows,
):
    with open(
        HISTORY_FILE_NAME,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def history_contains_recommendation(
    recommendation_date,
    ticker,
):
    if not history_file_exists():
        return False

    history_data = load_history_rows()

    for row in history_data["rows"]:
        same_date = (
            row["날짜"]
            == recommendation_date
        )
        same_ticker = (
            row["종목코드"]
            == ticker
        )

        if same_date and same_ticker:
            return True

    return False


def append_history_row(
    fieldnames,
    row,
):
    file_exists = history_file_exists()

    with open(
        HISTORY_FILE_NAME,
        "a",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)