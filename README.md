# INSA Lyon CCRB Database Project

This repository contains code for building and managing a relational database for the **CCRB (Civilian Complaint Review Board) dataset**.  
The project provides a reproducible pipeline to transform raw CSV files into a normalized MySQL database and execute analytical queries.

---

## 📁 Project Overview

- Build a structured MySQL database from CCRB CSV datasets
- Use staging tables before loading normalized tables
- Provide an end-to-end pipeline for:
  - CSV preprocessing
  - Schema generation
  - Data loading
  - Query execution
  - Pipeline reset

---

## 📦 Prerequisites

- Python 3.8+
- MySQL 8.x
- `csv2db` installed
- Python dependencies:
  ```bash
  pip install -r requirements.txt
🚀 Usage
0. Install csv2db
bash
코드 복사
pip install csv2db
1. Run the main pipeline
bash
코드 복사
python pipeline.py
This step:

Processes CSV files

Generates staging table schemas

Loads CSV data into staging tables

2. Execute SQL files in order (important)
⚠️ The execution order must be respected

Create normalized tables:

sql
코드 복사
create_tables.sql
Load normalized tables:

sql
코드 복사
load_normalized_tables.sql
3. Run query mode
After the database is fully set up, run the pipeline in query mode:

bash
코드 복사
python pipeline.py --mode query
This executes predefined queries located in the query/ directory.

4. Reset the pipeline (optional)
To return to the initial clean state:

bash
코드 복사
python pipeline.py --mode reset
This will:

Drop all staging_* tables

Remove generated SQL files

Reset the pipeline configuration

📂 Project Structure
text
코드 복사
.
├── csv/                    # Raw CSV files (ignored in git)
├── query/                  # SQL query files
├── sql_outputs/            # Generated SQL schemas (ignored in git)
├── pipeline.py             # Main pipeline controller
├── config.py               # Configuration file
├── create_tables.sql       # Normalized table definitions
├── load_normalized_tables.sql
└── README.md
📝 Notes
CSV files and .env are excluded via .gitignore

The default database name is ccrb_db

SQL execution order is critical due to foreign key dependencies

📌 Dataset
The CCRB dataset contains records of civilian complaints against police officers.
This project is intended for academic and educational purposes only.

👤 Author
INSA Lyon Exchange Student
Database Systems Project