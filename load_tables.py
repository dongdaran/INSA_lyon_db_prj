import mysql.connector

# 05_load_tables.py
# ==============================================================
# This script executes the SQL files generated in step 03 to
# actually create the MySQL staging tables, then loads normalized
# or transformed data if applicable.
#
# - Connects to MySQL and runs each .sql file in OUTPUT_DIR
# - Ensures database structure is ready before data loading
# - Typically executed before 04_import_staging.py
#
# Purpose:
#   Set up the MySQL schema for the CCRB project.
# ==============================================================

# ------------------------------------------------------------
# Execute SQL file in MySQL
# ------------------------------------------------------------
def execute_sql_file(path, message=""):
    if message:
        print(f"\n===== {message} =====")
    print(f"▶ Executing SQL file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Uyechan0613*",
        port=3306,
        database="ccrb_db"
    )
    cursor = conn.cursor()

    # Split by semicolon safely
    statements = sql_script.split(";")

    for stmt in statements:
        stmt = stmt.strip()

        if not stmt:
            continue
        if stmt.startswith("--") or stmt.startswith("#") or stmt.startswith("/*"):
            continue

        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"\n❌ Error executing SQL:\n{stmt}\n")
            print(f"Exception: {e}")
            conn.rollback()
            raise


    conn.commit()
    cursor.close()
    conn.close()

    print("✔ Done\n")



# ------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------
def run_load_tables():
    print("===== [STEP 2] CREATE NORMALIZED TABLES + LOAD DATA =====")

    # 1. making 13 tables
    execute_sql_file("sql_outputs/create_tables.sql", "Creating 13 Normalized Tables")

    # 2. staging → normalized load
    execute_sql_file("sql_outputs/load_normalized_tables.sql", "Loading Normalized Tables")

    print("🎉 All normalized tables successfully populated!")

if __name__ == "__main__":
    run_load_tables()
