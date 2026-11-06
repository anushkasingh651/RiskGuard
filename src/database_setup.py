import sqlite3
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "database"

DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "riskguard.db"

# Connect to SQLite
connection = sqlite3.connect(DB_PATH)

# CSV files and corresponding database tables
datasets = {
    "vendors": "vendors.csv",
    "purchase_orders": "purchase_orders.csv",
    "goods_receipts": "goods_receipts.csv",
    "invoices": "invoices.csv",
    "payments": "payments.csv",
    "approvals": "approvals.csv"
}

print("\n====================================")
print("       RISKGUARD DATABASE SETUP")
print("====================================")

for table_name, filename in datasets.items():

    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False
    )

    print(f"{table_name}: {len(df)} records imported")

connection.commit()

# Verify database tables
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
""")

tables = cursor.fetchall()

print("\nDatabase tables:")

for table in tables:
    print("-", table[0])

connection.close()

print("\nDatabase created successfully!")
print("Location:", DB_PATH)