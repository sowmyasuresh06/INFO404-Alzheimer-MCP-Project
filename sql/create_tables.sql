CREATE TABLE brain_samples (
    gsm_id VARCHAR(20) PRIMARY KEY,
    raw_label TEXT NOT NULL,
    brain_region VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    age_years NUMERIC,
    diagnosis VARCHAR(20),
    subject_id VARCHAR(50)
);
