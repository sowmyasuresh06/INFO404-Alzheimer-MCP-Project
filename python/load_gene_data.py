import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\sowmy\OneDrive\Desktop\INFO404project\brain_samples.sqlite"
CSV_PATH = r"C:\Users\sowmy\OneDrive\Desktop\INFO404project\cleaned_gene_expression.csv"

df = pd.read_csv(CSV_PATH)

print("Columns in CSV:")
print(df.columns.tolist())
print(df.head())

conn = sqlite3.connect(DB_PATH)
df.to_sql("gene_expression", conn, if_exists="replace", index=False)
conn.close()

print("gene_expression table created successfully.")
