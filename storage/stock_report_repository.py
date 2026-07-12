import csv


STOCK_REPORT_FILE_NAME = "stock_report.csv"


def save_stock_report_rows(
    fieldnames,
    rows,
):
    with open(
        STOCK_REPORT_FILE_NAME,
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