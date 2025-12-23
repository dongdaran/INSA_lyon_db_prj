import pandas as pd
from config import EXTRACT_CONFIG

# 01_extract_ccrb_dict.py
# ============================================================
# This script reads specific sheets from the CCRB data dictionary
# Excel file, extracts selected columns based on a configuration
# (EXTRACT_CONFIG), renames the columns to match the database schema,
# and saves the cleaned result as CSV files.
#
# Tasks currently supported:
#   - extract_command: Generates commands.csv
#   - extract_ranksystem: Generates rank_system.csv
#
# The extraction logic is fully controlled by config.py, allowing
# easy updates to input file paths, sheet names, column mappings,
# and output CSV locations.
# ============================================================

def extract_from_dictionary(task_name):
    """Extracts a specific sheet based on the task configuration."""
    cfg = EXTRACT_CONFIG[task_name]

    # 1) Load the Excel sheet
    df = pd.read_excel(cfg["dictionary_file"], sheet_name=cfg["sheet_name"])

    # 2) Select & rename required columns
    df = df[list(cfg["column_map"].keys())].rename(columns=cfg["column_map"])

    # 3) Save to CSV
    df.to_csv(cfg["output_csv"], index=False, encoding="utf-8-sig")

    print(f"✔ Saved: {cfg['output_csv']}")

def run_extract_dictionary():
    extract_from_dictionary("extract_command")
    extract_from_dictionary("extract_ranksystem")

if __name__ == "__main__":
    run_extract_dictionary()
