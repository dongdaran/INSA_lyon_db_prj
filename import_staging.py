import os
import subprocess
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
from config import CSV_MAP

# 04_import_staging.py
# ============================================================
# CSV → MySQL STAGING LOAD SCRIPT
#
# This script:
#   1. Creates the MySQL database (ccrb_db) if it doesn't exist
#   2. Loads cleaned CSV files into MySQL staging tables using csv2db
#   3. Uses config.py for all CSV/table mappings
#   4. Loads MySQL login credentials securely via .env
#
# Dependencies:
#   - mysql-connector-python
#   - csv2db CLI
#   - python-dotenv
# ============================================================

# Load environment variables (.env)
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")


def create_db():
    """Create the MySQL database if it does not already exist."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT
        )
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB};")
        print(f"✔ Database '{MYSQL_DB}' ready.")

    except mysql.connector.Error as err:
        print(f"❌ Error creating database: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def load_csv_to_mysql(table_name, csv_path):
    """Load a CSV into MySQL staging using csv2db."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    cmd = [
        "csv2db",
        "load",
        "-f", csv_path,
        "-u", MYSQL_USER,
        "-p", MYSQL_PASSWORD,
        "-m", MYSQL_HOST,
        "-n", MYSQL_PORT,
        "-d", MYSQL_DB,
        "-o", "mysql",
        "-t", table_name,
    ]

    print(f"▶ Loading {csv_path} → {table_name}")
    subprocess.run(cmd, check=True)
    print("✔ Load complete")


def load_all_staging():
    """Load all cleaned CSVs into MySQL staging tables."""
    for table_name, csv_rel_path in CSV_MAP.items():

        # Build full path with INPUT_DIR
        csv_path = os.path.join(csv_rel_path)

        load_csv_to_mysql(table_name, csv_path)
    
def run_import_staging():
    create_db()
    load_all_staging()

if __name__ == "__main__":
    run_import_staging()
