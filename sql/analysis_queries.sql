-- Join brain samples with gene expression
SELECT b.gsm_id, b.brain_region, b.diagnosis, g.gene, g.expression_value
FROM brain_samples b
JOIN gene_expression g
ON b.gsm_id = g.sample_id
LIMIT 10;


-- Average expression for a single gene (A1BG)
SELECT b.diagnosis, AVG(g.expression_value) AS avg_expression
FROM brain_samples b
JOIN gene_expression g
ON b.gsm_id = g.sample_id
WHERE g.gene = 'A1BG'
GROUP BY b.diagnosis;


-- Top 10 genes with largest AD vs Control difference
SELECT
    g.gene,
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
LIMIT 10;


-- Expression values for A1BG across samples
SELECT b.diagnosis, g.expression_value
FROM brain_samples b
JOIN gene_expression g
ON b.gsm_id = g.sample_id
WHERE g.gene = 'A1BG';
