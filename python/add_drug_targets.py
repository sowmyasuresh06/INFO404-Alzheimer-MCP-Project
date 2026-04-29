import sqlite3

DB_PATH = r"C:\Users\sowmy\OneDrive\Desktop\INFO404project\brain_samples.sqlite"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# create table
cur.execute("""
CREATE TABLE IF NOT EXISTS drug_targets (
    gene_symbol TEXT,
    drug_name TEXT,
    mechanism TEXT,
    disease_area TEXT
);
""")

# insert data
cur.execute("""
INSERT OR IGNORE INTO drug_targets VALUES
('APP','Aducanumab','Amyloid targeting','Alzheimer''s'),
('BACE1','BACE inhibitors','Beta-secretase inhibition','Alzheimer''s'),
('MAPT','Tau inhibitors','Tau aggregation','Alzheimer''s'),
('APOE','Lipid modulators','Cholesterol pathway','Alzheimer''s'),
('TREM2','Immune modulators','Microglia activation','Alzheimer''s');
('PSEN1', 'Gamma-secretase modulators', 'Amyloid production regulation', 'Alzheimer''s'),
('PSEN2', 'Gamma-secretase modulators', 'Amyloid pathway', 'Alzheimer''s'),
('CLU', 'Amyloid clearance modulators', 'Protein aggregation control', 'Alzheimer''s'),
('BIN1', 'Endocytosis modulators', 'Tau pathology link', 'Alzheimer''s'),
('CD33', 'Immune checkpoint modulators', 'Microglial activation', 'Alzheimer''s');
""")

conn.commit()
conn.close()

print("drug_targets table added successfully ✅")
