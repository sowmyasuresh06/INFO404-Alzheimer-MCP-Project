-- Generate and save top candidate genes by AD vs Control expression difference

INSERT INTO candidate_targets (
    gene_symbol,
    ad_avg,
    control_avg,
    diff,
    abs_diff,
    has_drug_link,
    drug_name,
    mechanism
)
WITH ranked_genes AS (
    SELECT
        g.gene AS gene_symbol,
        AVG(CASE WHEN b.diagnosis = 'AD' THEN g.expression_value END) AS ad_avg,
        AVG(CASE WHEN b.diagnosis = 'Control' THEN g.expression_value END) AS control_avg,
        AVG(CASE WHEN b.diagnosis = 'AD' THEN g.expression_value END) -
        AVG(CASE WHEN b.diagnosis = 'Control' THEN g.expression_value END) AS diff
    FROM brain_samples b
    JOIN gene_expression g
        ON b.gsm_id = g.sample_id
    GROUP BY g.gene
    ORDER BY ABS(
        AVG(CASE WHEN b.diagnosis = 'AD' THEN g.expression_value END) -
        AVG(CASE WHEN b.diagnosis = 'Control' THEN g.expression_value END)
    ) DESC
    LIMIT 20
)
SELECT
    r.gene_symbol,
    r.ad_avg,
    r.control_avg,
    r.diff,
    ABS(r.diff) AS abs_diff,
    CASE
        WHEN d.gene_symbol IS NOT NULL THEN 'Yes'
        ELSE 'No'
    END AS has_drug_link,
    d.drug_name,
    d.mechanism
FROM ranked_genes r
LEFT JOIN drug_targets d
    ON r.gene_symbol = d.gene_symbol
ORDER BY abs_diff DESC;
