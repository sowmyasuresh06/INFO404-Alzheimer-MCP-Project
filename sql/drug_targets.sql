CREATE TABLE drug_targets (
    id SERIAL PRIMARY KEY,
    gene_symbol TEXT,
    drug_name TEXT,
    mechanism TEXT,
    disease_area TEXT
);
