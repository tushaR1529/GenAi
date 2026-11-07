# app/explore.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from app.records import load_records

records = load_records()
df = pd.DataFrame(records)

print("Fact 1: records per category")
cat_col = "category" if "category" in df.columns else "scheme_name"
print(df[cat_col].value_counts().to_string(), "\n")

print("Fact 2: records per scheme")
print(df["scheme_name"].value_counts().to_string(), "\n")

with_income = (
    df["income_limit"].dropna().str.contains("lakh", case=False, na=False).sum()
    if "income_limit" in df.columns
    else 0
)
print(f"Fact 3: {with_income} of {len(df)} records mention an income limit in lakh")
