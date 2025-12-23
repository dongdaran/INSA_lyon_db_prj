# 06_run_query.py
# ==============================================================
# This script connects to the MySQL CCRB database, loads SQL
# queries stored in query/queries.py, executes a selected query,
# and displays the result as a pandas DataFrame.
#
# - Supports borough-specific query (#1)
# - Uses SQLAlchemy engine for MySQL
# - Clean project structure (queries separated into module)
# ==============================================================

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Import QUERIES + borough_query from query module
from query.queries import QUERIES, borough_query


# --------------------------------------------------------------
# Load MySQL credentials from .env
# --------------------------------------------------------------
load_dotenv()

DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")
DB_NAME = os.getenv("MYSQL_DB")

if not all([DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError("❌ Missing MySQL credentials in .env")


# --------------------------------------------------------------
# Create SQLAlchemy engine
# --------------------------------------------------------------
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo=False,
    future=True
)


# --------------------------------------------------------------
# Query runner logic
# --------------------------------------------------------------
def run_query():
    qn = input("Enter query number (1~10): ").strip()

    if not qn.isdigit():
        print("❌ Invalid input")
        return

    qn = int(qn)

    # ----------------------------------------------------------
    # Query #1 requires borough input
    # ----------------------------------------------------------
    if qn == 1:
        borough = input("Enter borough (e.g., Brooklyn): ").strip()
        print(borough)
        sql = borough_query(borough)

    else:
        if qn not in QUERIES:
            print("❌ Query not found.")
            return

        sql = QUERIES[qn]

    print(f"\n🔍 Running Query {qn}...\n")

    # ----------------------------------------------------------
    # Execute SQL and load into Pandas DataFrame
    # ----------------------------------------------------------
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)

    print("\n📄 Query Result:\n")
    print(df.to_string(index=False))


# --------------------------------------------------------------
# Main Entry
# --------------------------------------------------------------
if __name__ == "__main__":
    run_query()
