DROP TABLE IF EXISTS brain_samples;

CREATE TABLE brain_samples (
    gsm_id VARCHAR(20) PRIMARY KEY,
    raw_label TEXT NOT NULL,
    brain_region VARCHAR(100) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female')),
    age_years INTEGER,
    diagnosis VARCHAR(20),
    subject_id VARCHAR(50)
);

-- Import after placing the CSV somewhere PostgreSQL can read:
-- \copy brain_samples(gsm_id, raw_label, brain_region, gender, age_years, diagnosis, subject_id)
-- FROM 'brain_samples_cleaned.csv'
-- WITH (FORMAT csv, HEADER true);
