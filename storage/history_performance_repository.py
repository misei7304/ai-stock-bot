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