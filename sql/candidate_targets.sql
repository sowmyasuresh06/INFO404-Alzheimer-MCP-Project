-- Candidate target results table
-- Stores the genes identified by the analysis as having the largest AD vs Control expression differences.

CREATE TABLE IF NOT EXISTS candidate_targets (
    id SERIAL PRIMARY KEY,
    gene_symbol TEXT,
    ad_avg NUMERIC,
    control_avg NUMERIC,
    diff NUMERIC,
    abs_diff NUMERIC,
    has_drug_link TEXT,
    drug_name TEXT,
    mechanism TEXT,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
