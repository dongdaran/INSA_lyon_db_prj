import pandas as pd

# ============================================================
# This script extracts the "Ranks" sheet from the CCRB data
# dictionary Excel file, selects the rank abbreviation and
# full rank description columns, renames them to match the
# database schema, and saves the cleaned result as
# rank_system.csv for loading into MySQL.
# ============================================================

# 1) Read the "Ranks" sheet from the Excel file
df = pd.read_excel("CCRBComplaintsDatabaseDataDictionary_20251112.xlsx", sheet_name="Ranks")

# 2) Select only the required columns and rename them
df = df[["Rank Abbreviation", "Rank Desc"]].rename(
    columns={
        "Rank Abbreviation": "Abbreviation",
        "Rank Desc": "Rank_Name"
    }
)

# 3) Save the cleaned DataFrame as rank_system.csv
df.to_csv("rank_system.csv", index=False, encoding="utf-8-sig")

print("Successfully saved rank_system.csv")
