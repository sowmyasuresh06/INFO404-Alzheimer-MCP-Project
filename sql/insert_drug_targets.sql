-- Curated Alzheimer’s-related drug target table
-- These genes represent known or commonly studied Alzheimer’s therapeutic targets/pathways.

CREATE TABLE IF NOT EXISTS drug_targets (
    id SERIAL PRIMARY KEY,
    gene_symbol TEXT,
    drug_name TEXT,
    mechanism TEXT,
    disease_area TEXT
);

INSERT INTO drug_targets (gene_symbol, drug_name, mechanism, disease_area)
VALUES
('APP', 'Aducanumab', 'Amyloid targeting', 'Alzheimer''s'),
('BACE1', 'BACE inhibitors', 'Beta-secretase inhibition', 'Alzheimer''s'),
('MAPT', 'Tau inhibitors', 'Tau aggregation', 'Alzheimer''s'),
('APOE', 'Lipid modulators', 'Cholesterol pathway', 'Alzheimer''s'),
('TREM2', 'Immune modulators', 'Microglial activation', 'Alzheimer''s'),
('PSEN1', 'Gamma-secretase modulators', 'Amyloid production regulation', 'Alzheimer''s'),
('PSEN2', 'Gamma-secretase modulators', 'Amyloid pathway', 'Alzheimer''s'),
('CLU', 'Amyloid clearance modulators', 'Protein aggregation control', 'Alzheimer''s'),
('BIN1', 'Endocytosis modulators', 'Tau pathology link', 'Alzheimer''s'),
('CD33', 'Immune checkpoint modulators', 'Microglial activation', 'Alzheimer''s');
