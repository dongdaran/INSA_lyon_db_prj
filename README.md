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

```bash
pip install -r requirements.txt
```

## 🚀 Usage

1. Run the main pipeline
```bash
    python pipeline.py
```

2. Execute SQL files in order (important)
⚠️ The execution order must be respected
create_tables.sql -> load_normalized_tables.sql

3. Run query mode
After the database is fully set up, run the pipeline in query mode:
```bash
python pipeline.py --mode query
```

4. Reset the pipeline (optional)
To return to the initial clean state:
```bash
python pipeline.py --mode reset
```

## 📂 Project Structure
```bash
.
├── csv/                    # Raw CSV files 
├── query/                  # SQL query files
├── sql_outputs/            # Generated SQL schemas 
├── pipeline.py             # Main pipeline controller
├── config.py               # Configuration file
|-- clean_csv_headers.py    # data preprocessing
├── generate_schema.py      # generate staging table
├── import_staging.py       # csv data -> sql dataset
└── README.md
```

## 📌 Dataset

The CCRB dataset contains records of civilian complaints against police officers.  
This project is intended for academic and educational purposes only.

Dataset source:  
[NYC Civilian Complaint Review Board (CCRB)](https://www.nyc.gov/site/ccrb/index.page)

## 👤 Author
INSA Lyon Exchange Student
Database Systems Project
Kim minjeong Lee jeeun