# config.py


# CSV cleaning configuration (input → output) (step 1)
CLEAN_CSV_MAP = {
    "csv/allegations_clean.csv": "csv/allegations.csv",
    "csv/penalties_clean.csv": "csv/penalties.csv",
}

# CSV → SQL table mapping after csv cleaning (step 2)
CSV_MAP = {
    "staging_allegations": "csv/allegations_clean.csv",
    "staging_penalties": "csv/penalties_clean.csv",
    "staging_complaints": "csv/complaints.csv",
    "staging_officers": "csv/officer_info.csv",
    "staging_ranksystem": "csv/rank_system.csv",
    "staging_commands" : "csv/commands.csv",
}

# Where to save the generated .sql files
OUTPUT_DIR = "sql_outputs"
SQL_PATH = {
    table: f"{OUTPUT_DIR}/{table}.sql"
    for table in CSV_MAP.keys()
}

# CSV encoding
CSV_ENCODING = "utf-8-sig"

# Default MySQL column type
DEFAULT_COLUMN_TYPE = "TEXT"

# CREATE TABLE options
TABLE_OPTIONS = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

# extract_*.py configuration
EXTRACT_CONFIG = {
    "extract_command": {
        "dictionary_file": "csv/CCRBComplaintsDatabaseDataDictionary_20251112.xlsx",
        "sheet_name": "Commands",
        "column_map": {
            "Command Name Abbreviation": "Command_Code",
            "Command Name Long": "Command_Name"
        },
        "output_csv": "csv/commands.csv"
    },

    "extract_ranksystem": {
        "dictionary_file": "csv/CCRBComplaintsDatabaseDataDictionary_20251112.xlsx",
        "sheet_name": "Ranks",
        "column_map": {
            "Rank Abbreviation": "Abbreviation",
            "Rank Desc": "Rank_Name"
        },
        "output_csv": "csv/rank_system.csv"
    }
}
