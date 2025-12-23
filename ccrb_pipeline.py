# ============================================================
# ✅ 1. MySQL 엔진 연결 + DDL 실행 + CSV 로드
# ============================================================

from sqlalchemy import create_engine, text
import pandas as pd

# ============================================================
# 0. MySQL 연결 설정 (수정 필요)
# ============================================================
DB_USER = "ccrb_user"
DB_PASS = "1234"
DB_NAME = "ccrb_db"
DB_HOST = "localhost"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
    echo=False,
    future=True
)

# ============================================================
# 1. DDL (Schema 정의)
# ============================================================
schema_sql = """
DROP TABLE IF EXISTS NYPD_Penalty;
DROP TABLE IF EXISTS APU_Penalty;
DROP TABLE IF EXISTS CCRB_Penalty;
DROP TABLE IF EXISTS Penalty;
DROP TABLE IF EXISTS Officer_at_Incid;
DROP TABLE IF EXISTS Victim;
DROP TABLE IF EXISTS Allegation;
DROP TABLE IF EXISTS Complaint;
DROP TABLE IF EXISTS Incident;
DROP TABLE IF EXISTS PoliceOfficer;
DROP TABLE IF EXISTS Command;

CREATE TABLE Command (
  Command_Name VARCHAR(100) PRIMARY KEY,
  Precinct_Of_Incident_Occurrence INT,
  Borough VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE PoliceOfficer (
  Tax_ID INT PRIMARY KEY,
  Active_Per_Last_Reported_Status VARCHAR(100),
  Last_Reported_Active_Date DATETIME,
  Officer_First_Name VARCHAR(100),
  Officer_Last_Name VARCHAR(100),
  Officer_Race VARCHAR(50),
  Officer_Gender VARCHAR(50),
  Current_Rank_Abbreviation VARCHAR(50),
  Current_Rank VARCHAR(100),
  Current_Command VARCHAR(100),
  Shield_No VARCHAR(50),
  Total_Complaints INT,
  Total_Substantiated_Complaints INT,
  FOREIGN KEY (Current_Command) REFERENCES Command(Command_Name)
) ENGINE=InnoDB;

CREATE TABLE Complaint (
  Complaint_ID BIGINT PRIMARY KEY,
  Incident_Date DATE,
  Incident_Hour INT,
  CCRB_Received_Date DATE,
  Close_Date DATE,
  Borough_Of_Incident_Occurrence VARCHAR(255),
  Precinct_Of_Incident_Occurrence VARCHAR(255),
  Location_Type_Of_Incident VARCHAR(255),
  Reason_for_Police_Contact VARCHAR(255),
  Outcome_Of_Police_Encounter VARCHAR(255),
  CCRB_Complaint_Disposition VARCHAR(255),
  BWC_Evidence VARCHAR(10),
  Video_Evidence VARCHAR(10)
) ENGINE=InnoDB;

CREATE TABLE Allegation (
  Allegation_Record_Identity BIGINT PRIMARY KEY,
  Complaint_ID BIGINT NOT NULL,
  Tax_ID INT,
  Complaint_Officer_Number INT,
  FADO_Type VARCHAR(50),
  Allegation TEXT,
  CCRB_Investigations_Division_Recommendation VARCHAR(255),
  CCRB_Allegation_Disposition VARCHAR(100),
  NYPD_Allegation_Disposition VARCHAR(100),
  FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID),
  FOREIGN KEY (Tax_ID) REFERENCES PoliceOfficer(Tax_ID)
) ENGINE=InnoDB;

CREATE TABLE Victim (
  Allegation_Record_Identity BIGINT PRIMARY KEY,
  Victim_Age_Range VARCHAR(50),
  Victim_Gender VARCHAR(50),
  Victim_Race_Legacy VARCHAR(100),
  Victim_Race_Ethnicity VARCHAR(100),
  FOREIGN KEY (Allegation_Record_Identity) REFERENCES Allegation(Allegation_Record_Identity)
) ENGINE=InnoDB;

CREATE TABLE Officer_at_Incid (
  Complaint_ID BIGINT,
  Tax_ID INT,
  Complaint_Officer_Number INT,
  Officer_Rank_Abbreviation_At_Incident VARCHAR(50),
  Officer_Rank_At_Incident VARCHAR(100),
  Officer_Command_At_Incident VARCHAR(100),
  Officer_Days_On_Force_At_Incident INT,
  PRIMARY KEY (Complaint_ID, Tax_ID, Complaint_Officer_Number),
  FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID),
  FOREIGN KEY (Tax_ID) REFERENCES PoliceOfficer(Tax_ID)
) ENGINE=InnoDB;

CREATE TABLE Penalty (
  Complaint_ID BIGINT,
  Tax_ID INT,
  PRIMARY KEY (Complaint_ID, Tax_ID),
  FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID),
  FOREIGN KEY (Tax_ID) REFERENCES PoliceOfficer(Tax_ID)
) ENGINE=InnoDB;

CREATE TABLE CCRB_Penalty (
  Complaint_ID BIGINT,
  Tax_ID INT,
  CCRB_Substantiated_Officer_Disposition VARCHAR(100),
  Board_Discipline_Recommendation VARCHAR(100),
  PRIMARY KEY (Complaint_ID, Tax_ID),
  FOREIGN KEY (Complaint_ID, Tax_ID) REFERENCES Penalty(Complaint_ID, Tax_ID)
) ENGINE=InnoDB;

CREATE TABLE APU_Penalty (
  Complaint_ID BIGINT,
  Tax_ID INT,
  Officer_Is_APU TINYINT,
  APU_Trial_Recommended_Penalty VARCHAR(100),
  APU_Commissioner_Recommended_Penalty VARCHAR(100),
  APU_Plea_Agreed_Penalty VARCHAR(100),
  APU_Closing_Date DATE,
  APU_Case_Status VARCHAR(100),
  PRIMARY KEY (Complaint_ID, Tax_ID),
  FOREIGN KEY (Complaint_ID, Tax_ID) REFERENCES Penalty(Complaint_ID, Tax_ID)
) ENGINE=InnoDB;

CREATE TABLE NYPD_Penalty (
  Complaint_ID BIGINT,
  Tax_ID INT,
  NYPD_Officer_Penalty VARCHAR(100),
  Non_APU_Penalty_Report_Date DATE,
  PRIMARY KEY (Complaint_ID, Tax_ID),
  FOREIGN KEY (Complaint_ID, Tax_ID) REFERENCES Penalty(Complaint_ID, Tax_ID)
) ENGINE=InnoDB;
"""

# ============================================================
# 2. Schema 실행
# ============================================================
def create_schema(engine):
    with engine.begin() as conn:
        for stmt in schema_sql.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
        print("✅ MySQL schema successfully created.")

# ============================================================
# 3. CSV 로드 (pandas + to_sql)
# ============================================================
def load_csvs(engine):
    print("📁 Loading CSV files into MySQL...")

    # ------------------------------------------------------------
    # 1️⃣ officer_info.csv → PoliceOfficer
    # ------------------------------------------------------------
    df_officer = pd.read_csv("officer_info.csv")
    df_officer.columns = df_officer.columns.str.strip().str.replace(" ", "_")
    df_officer = df_officer.drop(columns=[c for c in df_officer.columns if c.lower() in ["as_of_date", "as_ofdate", "as_of_date"]], errors="ignore")

    # 날짜 변환
    if "Last_Reported_Active_Date" in df_officer.columns:
        df_officer["Last_Reported_Active_Date"] = pd.to_datetime(
            df_officer["Last_Reported_Active_Date"], errors="coerce"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    # ✅ Command 테이블 먼저 채우기
    commands = pd.DataFrame(df_officer["Current_Command"].dropna().unique(), columns=["Command_Name"])
    commands["Borough"] = None
    commands["Precinct_Of_Incident_Occurrence"] = None
    commands.to_sql("Command", engine, if_exists="append", index=False)
    print(f"✅ Command: {len(commands)} unique commands inserted")

    # ✅ Officer 테이블 로드
    allowed_officer_cols = [
        "Tax_ID", "Active_Per_Last_Reported_Status", "Last_Reported_Active_Date",
        "Officer_First_Name", "Officer_Last_Name", "Officer_Race", "Officer_Gender",
        "Current_Rank_Abbreviation", "Current_Rank", "Current_Command",
        "Shield_No", "Total_Complaints", "Total_Substantiated_Complaints"
    ]
    df_officer = df_officer[[c for c in df_officer.columns if c in allowed_officer_cols]]

    df_officer.to_sql("PoliceOfficer", engine, if_exists="append", index=False)
    print(f"✅ PoliceOfficer: {len(df_officer)} rows inserted")

    # ------------------------------------------------------------
    # 2️⃣ complaints.csv → Complaint
    # ------------------------------------------------------------
    df_complaints = pd.read_csv("complaints.csv")
    df_complaints.columns = (
        df_complaints.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(".", "_")
    )

    # ✅ Complaint_ID 통일 보정
    if "Complaint_Id" in df_complaints.columns and "Complaint_ID" not in df_complaints.columns:
        df_complaints.rename(columns={"Complaint_Id": "Complaint_ID"}, inplace=True)

    df_complaints = df_complaints.drop(columns=[c for c in df_complaints.columns if c.lower() in ["as_of_date", "as_ofdate", "as_of_date"]], errors="ignore")

    # 날짜 컬럼 변환
    for date_col in ["Incident_Date", "CCRB_Received_Date", "Close_Date"]:
        if date_col in df_complaints.columns:
            df_complaints[date_col] = pd.to_datetime(df_complaints[date_col], errors="coerce").dt.strftime("%Y-%m-%d")

    df_complaints.to_sql("Complaint", engine, if_exists="append", index=False)
    print(f"✅ Complaint: {len(df_complaints)} rows inserted")

        # ------------------------------------------------------------
    # 3️⃣ allegations.csv → Allegation (Chunked & FK-safe)
    # ------------------------------------------------------------
    df_alleg = pd.read_csv("allegations.csv")
    df_alleg.columns = (
        df_alleg.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(".", "_")
    )
    if "Complaint_Id" in df_alleg.columns and "Complaint_ID" not in df_alleg.columns:
        df_alleg.rename(columns={"Complaint_Id": "Complaint_ID"}, inplace=True)
    if "Tax_Id" in df_alleg.columns and "Tax_ID" not in df_alleg.columns:
        df_alleg.rename(columns={"Tax_Id": "Tax_ID"}, inplace=True)

    # 🔗 FK 필터
    valid_complaint_ids = set(df_complaints["Complaint_ID"])
    valid_tax_ids = set(df_officer["Tax_ID"])
    before_len = len(df_alleg)
    df_alleg = df_alleg[
        df_alleg["Complaint_ID"].isin(valid_complaint_ids) &
        df_alleg["Tax_ID"].isin(valid_tax_ids)
    ]
    print(f"🔗 Allegation FK filtered: {before_len} → {len(df_alleg)}")

    # ⚠️ Allegation 테이블 스키마에 존재하지 않는 컬럼 제거
    allowed_cols = [
        "Allegation_Record_Identity",
        "Complaint_ID",
        "Tax_ID",
        "Complaint_Officer_Number",
        "FADO_Type",
        "Allegation",
        "CCRB_Investigations_Division_Recommendation",
        "CCRB_Allegation_Disposition",
        "NYPD_Allegation_Disposition"
    ]
    df_alleg = df_alleg[[c for c in df_alleg.columns if c in allowed_cols]]

    # ✅ Chunk 업로드
    chunk_size = 1000
    for i in range(0, len(df_alleg), chunk_size):
        chunk = df_alleg.iloc[i:i+chunk_size]
        chunk.to_sql("Allegation", engine, if_exists="append", index=False)
        print(f"   → inserted {i+len(chunk)}/{len(df_alleg)} rows")

    print(f"✅ Allegation: {len(df_alleg)} rows inserted (chunk={chunk_size})")

    # ------------------------------------------------------------
    # 4️⃣ penalties.csv → CCRB_Penalty
    # ------------------------------------------------------------
    df_pen = pd.read_csv("penalties.csv")
    df_pen.columns = df_pen.columns.str.strip().str.replace(" ", "_")
    df_pen = df_pen.drop(columns=[c for c in df_pen.columns if c.lower() in ["as_of_date", "as_ofdate", "as_of_date"]], errors="ignore")

    for date_col in ["APU_Closing_Date", "Non-APU_NYPD_Penalty_Report_Date"]:
        if date_col in df_pen.columns:
            df_pen[date_col] = pd.to_datetime(df_pen[date_col], errors="coerce").dt.strftime("%Y-%m-%d")

    df_pen.to_sql("CCRB_Penalty", engine, if_exists="append", index=False)
    print(f"✅ Penalties: {len(df_pen)} rows inserted")

    print("🎯 All CSVs loaded successfully (As_Of_Date removed, date format fixed).")

# ============================================================
# 4. 실행
# ============================================================
if __name__ == "__main__":
    create_schema(engine)
    load_csvs(engine)
    print("🎯 Database setup complete!")
