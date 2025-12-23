import pandas as pd

# ============================================================
# This script extracts the "Commands" sheet from the CCRB
# data dictionary Excel file, selects the abbreviation and
# full command name columns, renames them to match the DB
# schema, and saves the result as commands.csv for loading
# into the MySQL staging table.
# ============================================================

# 1) Read the "Commands" sheet from the Excel file
df = pd.read_excel("CCRBComplaintsDatabaseDataDictionary_20251112.xlsx", sheet_name="Commands")

# 2) Select only the required columns and rename them
df = df[["Command Name Abbreviation", "Command Name Long"]].rename(
    columns={
        "Command Name Abbreviation": "Command_Code",
        "Command Name Long": "Command_Name"
    }
)

# 3) Save the cleaned DataFrame as commands.csv
df.to_csv("commands.csv", index=False, encoding="utf-8-sig")

print("Successfully saved commands.csv")
