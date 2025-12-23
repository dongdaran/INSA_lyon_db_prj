import csv
import re
from config import CLEAN_CSV_MAP, CSV_ENCODING

# 02_clean_csv_headers.py
# ============================================================
# This script cleans column names in CSV files by:
#   - removing special characters
#   - normalizing multiple underscores
#   - preventing numeric-starting column names
#
# The input/output CSV paths are controlled by CLEAN_CSV_MAP
# defined in config.py. Each key is the output file, and each
# value is the raw input CSV to process.
# ============================================================

def clean_column_name(col):
    """Normalize column name by removing special chars and fixing invalid names."""
    col = col.strip()
    col = re.sub(r'[^0-9a-zA-Z_]', '_', col)   # Replace non-alphanumeric chars
    col = re.sub(r'_+', '_', col)              # Collapse consecutive underscores
    if re.match(r'^[0-9]', col):               # Column names cannot start with a digit
        col = "_" + col
    return col


def clean_csv(input_file, output_file):
    """Read a CSV file, clean its header, and save as a new CSV."""
    with open(input_file, 'r', encoding=CSV_ENCODING) as f_in:
        reader = csv.reader(f_in)
        rows = list(reader)

    header = rows[0]
    cleaned_header = [clean_column_name(c) for c in header]

    with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(cleaned_header)
        writer.writerows(rows[1:])

    print(f"✔ Cleaned CSV saved → {output_file}")


def run_all():
    """Clean all CSV files defined in CLEAN_CSV_MAP."""
    for output_file, input_file in CLEAN_CSV_MAP.items():
        clean_csv(input_file, output_file)


def run_clean_csv():
    run_all()

if __name__ == "__main__":
    run_clean_csv()


