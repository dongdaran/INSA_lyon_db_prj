import pandas as pd
from sqlalchemy import create_engine

# 1) load
df = pd.read_csv("allegations.csv")

# 2) normalize columns
df.columns = (
    df.columns
      .str.lower()
      .str.replace(" ", "_")
      .str.replace("/", "_")
)

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

# 4) upload
df.to_sql(
    "ccrb_allegations",
    engine,
    if_exists="replace",
    index=False,
    chunksize=20000
)

# 5) check unique disposition
disp = pd.read_sql(
    "SELECT DISTINCT board_disposition FROM ccrb_allegations ORDER BY board_disposition;",
    engine
)
print(disp)
