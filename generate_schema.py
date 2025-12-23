import csv
import re
import os
import mysql.connector
from dotenv import load_dotenv
from config import CSV_MAP, OUTPUT_DIR, CSV_ENCODING, DEFAULT_COLUMN_TYPE, TABLE_OPTIONS, SQL_PATH

# 03_generate_schema.py
# ==============================================================
# This script generates SQL CREATE TABLE statements for each
# cleaned CCRB CSV file, using header-based schema inference.
#
# - Uses CSV_MAP from config.py to find CSV inputs
# - Generates one .sql file per table (saved in OUTPUT_DIR)
# - All columns default to TEXT unless configured otherwise
#
# Purpose:
#   Automatically create MySQL staging table schemas matching
#   the cleaned CSV structure.
# ==============================================================

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB")

def clean_column_name(col):
    col = col.strip()
    col = re.sub(r'[^0-9a-zA-Z_]', '_', col)
    col = re.sub(r'_+', '_', col)
    if re.match(r'^[0-9]', col):
        col = "_" + col
    return col


def generate_create_table_sql(table_name, csv_file):
    with open(csv_file, mode='r', encoding=CSV_ENCODING) as f:
        reader = csv.reader(f)
        header = next(reader)

    clean_cols = [clean_column_name(col) for col in header]

    sql_lines = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    for col in clean_cols:
        sql_lines.append(f"  `{col}` {DEFAULT_COLUMN_TYPE},")
    sql_lines[-1] = sql_lines[-1].rstrip(",")
    sql_lines.append(f") {TABLE_OPTIONS};")

    return "\n".join(sql_lines)


def generate_all():
    # Create output directory if not exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for table, file in CSV_MAP.items():
        sql = generate_create_table_sql(table, file)
        output_file = f"{OUTPUT_DIR}/{table}.sql"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(sql)

        print(f"✔ Generated: {output_file}")


def execute_single_sql_file(sql_path):
    """Execute a single .sql file inside MySQL."""
    print(f"🔹 Executing SQL file: {sql_path}")

    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        database=DB_NAME
    )
    cursor = conn.cursor()

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    for stmt in sql_script.split(";"):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✔ Done: {sql_path}")

def execute_all_sql():
    print("🚀 Running all SQL schema files...\n")

    for table_name, sql_path in SQL_PATH.items():
        if os.path.exists(sql_path):
            execute_single_sql_file(sql_path)
        else:
            print(f"⚠ WARNING: SQL file not found → {sql_path}")

    print("\n🎉 All SQL files executed successfully!\n")


def run_generate_schema():
    generate_all()
    execute_all_sql()

if __name__ == "__main__":
    run_generate_schema()

