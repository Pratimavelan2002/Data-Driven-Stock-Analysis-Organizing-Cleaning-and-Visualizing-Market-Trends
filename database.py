import pandas as pd
from sqlalchemy import create_engine
import os

# --- File Paths ---
data_path = r"C:\Users\prati\OneDrive\Desktop\guvi\project2\merged_output.csv"
sector_path = r"C:\Users\prati\OneDrive\Desktop\guvi\project2\sector_mapping_updated.csv"

# --- Load Data ---
df = pd.read_csv(data_path)
sector_map = pd.read_csv(sector_path)

# --- Preview column names to debug mismatches ---
print("Main Data Columns:", df.columns)
print("Sector Map Columns:", sector_map.columns)

# --- Fix column name mismatches (standardize column names) ---
df.columns = df.columns.str.strip().str.title()
sector_map.columns = sector_map.columns.str.strip().str.title()

# --- Print updated column names ---
print("Fixed Data Columns:", df.columns)
print("Fixed Sector Columns:", sector_map.columns)

# --- Confirm expected key exists ---
if 'Symbol' not in df.columns or 'Symbol' not in sector_map.columns:
    raise KeyError("Column 'Symbol' not found in both dataframes!")

# --- Merge Sector Info using 'Symbol' ---
df = df.merge(sector_map, on='Symbol', how='left')

# --- Create SQLite DB and Save ---
db_path = "sqlite:///stock_data.db"  # Will create stock_data.db in the current working directory
engine = create_engine(db_path, echo=True)
df.to_sql("stock_data", con=engine, if_exists="replace", index=False)

# --- Also Save to CSV (Optional) ---
output_csv = r"C:\Users\prati\OneDrive\Desktop\guvi\project2\converted\merged_output.csv"
df.to_csv(output_csv, index=False)

print("✅ Data merged, saved to database and CSV successfully!")
