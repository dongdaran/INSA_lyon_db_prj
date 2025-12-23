# 07_pipeline.py
# ==============================================================
# FULL CCRB ETL PIPELINE (import-based)
#
# This script imports each ETL step as a function and executes
# them sequentially without using subprocess. This is the cleanest
# and most maintainable version of the pipeline.
# ==============================================================

import sys
import mysql.connector
import os
import glob
from dotenv import load_dotenv
# from extract_ccrb_dict import run_extract_dictionary
from clean_csv_headers import run_clean_csv
from generate_schema import run_generate_schema
from import_staging import run_import_staging 
from run_query import run_query


def ensure_ccrb_database():
    load_dotenv()

    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute("SHOW DATABASES LIKE 'ccrb_db';")
    exists = cursor.fetchone()

    if exists:
        print("✅ Database 'ccrb_db' exists. Using existing database.")
    else:
        print("🆕 Database 'ccrb_db' not found. Creating database...")
        cursor.execute("CREATE DATABASE ccrb_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("✅ Database 'ccrb_db' created.")

    cursor.close()
    conn.close()

def reset_setting():
    load_dotenv()

    # connect to DB
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database="ccrb_db"
    )
    cursor = conn.cursor()

    # delete staging_tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'ccrb_db'
          AND table_name LIKE 'staging_%';
    """)

    tables = cursor.fetchall()

    if not tables:
        print("No staging tables found to drop.")
    else:
        print("🧹 Dropping staging tables:")
        for (table_name,) in tables:
            print(f"   - {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")

        conn.commit()
        print("✅ All staging tables dropped.")

    cursor.close()
    conn.close()

    # delete staging SQL files
    sql_pattern = os.path.join("sql_outputs", "staging_*.sql")
    sql_files = glob.glob(sql_pattern)

    # delete csv files
    csv_pattern = os.path.join("csv", "*_clean.csv")
    csv_files = glob.glob(csv_pattern)

    if not sql_files:
        print("No staging SQL files found to delete.")
    if not csv_files:
        print("No cleaned CSV files found to delete.")

    else:
        print("🧹 Removing staging SQL files:")
        for file_path in sql_files:
            print(f"   - {file_path}")
            os.remove(file_path)

        print("✅ All staging SQL files removed.")
        print("🧹 Removing cleaned CSV files:")
        for file_path in csv_files:
            print(f"   - {file_path}")
            os.remove(file_path)

def run_pipeline(run_query_flag):
    if run_query_flag:
        print("🔹 Step — Run Query Mode (Skipping ETL)")
        run_query()
        return
    
    if delete_staging_flag:
        reset_setting()
        return

    print("\n🚀 Starting CCRB ETL Pipeline...\n")

    ensure_ccrb_database()

    # print("🔹 Step 1 — Extract Dictionary")
    # un_extract_dictionary()

    print("🔹 Step 1— Clean CSV Headers")
    run_clean_csv()

    print("🔹 Step 2 — Generate SQL Schema")
    run_generate_schema()

    print("🔹 Step 3 — Load Cleaned CSVs Into Staging Tables")
    run_import_staging()

    # stpe 4 run file create_table.sql -> load_normalized_tables.sql
    print("\n🎉 Dataset successfully uploaded into database!\n")




if __name__ == "__main__":
    run_query_flag = "--run-query" in sys.argv
    delete_staging_flag = "--reset-setting" in sys.argv
    run_pipeline(run_query_flag)
