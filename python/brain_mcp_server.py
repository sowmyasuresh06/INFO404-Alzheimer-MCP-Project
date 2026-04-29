mcp
matplotlib
scipy
pandas

from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import re
import math
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, normaltest, pearsonr

mcp = FastMCP("brain-mcp")

DB_PATH = r"C:\Users\sowmy\OneDrive\Desktop\INFO404project\brain_samples.sqlite"
PLOT_DIR = r"C:\Users\sowmy\OneDrive\Desktop\INFO404project\plots"

AD_COLOR = "#7FA8D1"
CONTROL_COLOR = "#D8A7B1"
NATURE_BLUE = "#AFCBEA"


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_plot_dir():
    os.makedirs(PLOT_DIR, exist_ok=True)


def safe_filename(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", text.strip())


def get_pvalue(ad, control):
    if len(ad) < 2 or len(control) < 2:
        return None
    _, p = ttest_ind(ad, control, equal_var=False, nan_policy="omit")
    return p


def setup_drug_targets():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS drug_targets (
            gene_symbol TEXT PRIMARY KEY,
            drug_name TEXT,
            mechanism TEXT,
            disease_area TEXT
        );
    """)

    rows = [
        ("APP", "Aducanumab", "Amyloid targeting", "Alzheimer's"),
        ("BACE1", "BACE inhibitors", "Beta-secretase inhibition", "Alzheimer's"),
        ("MAPT", "Tau inhibitors", "Tau aggregation", "Alzheimer's"),
        ("APOE", "Lipid modulators", "Cholesterol pathway", "Alzheimer's"),
        ("TREM2", "Immune modulators", "Microglia activation", "Alzheimer's"),
    ]

    cur.executemany("""
        INSERT OR REPLACE INTO drug_targets
        (gene_symbol, drug_name, mechanism, disease_area)
        VALUES (?, ?, ?, ?);
    """, rows)

    conn.commit()
    conn.close()


setup_drug_targets()


@mcp.tool()
def describe_dataset() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM brain_samples;")
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT diagnosis, COUNT(*)
        FROM brain_samples
        GROUP BY diagnosis
        ORDER BY diagnosis;
    """)
    counts = cur.fetchall()

    cur.close()
    conn.close()

    return f"Total rows: {total}; Diagnosis counts: {counts}"


@mcp.tool()
def list_tables() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def diagnosis_summary() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT diagnosis, COUNT(*)
        FROM brain_samples
        GROUP BY diagnosis
        ORDER BY diagnosis;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def brain_region_summary() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT brain_region, COUNT(*)
        FROM brain_samples
        GROUP BY brain_region
        ORDER BY COUNT(*) DESC;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def samples_by_region(region: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT gsm_id, diagnosis, brain_region
        FROM brain_samples
        WHERE brain_region = ?
        LIMIT 20;
    """, (region,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows) if rows else f"No samples found for region={region}"


@mcp.tool()
def list_sample_ids() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT gsm_id
        FROM brain_samples
        WHERE gsm_id IS NOT NULL
        ORDER BY gsm_id
        LIMIT 10;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def get_sample_info(sample_id: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT gsm_id, diagnosis, brain_region
        FROM brain_samples
        WHERE gsm_id = ?
        LIMIT 1;
    """, (sample_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    return str(row) if row else "Sample not found."


@mcp.tool()
def genes_for_sample(sample_id: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT gene, expression_value
        FROM gene_expression
        WHERE sample_id = ?
        ORDER BY gene
        LIMIT 20;
    """, (sample_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows) if rows else f"No gene expression data found for sample_id={sample_id}"


@mcp.tool()
def search_gene(gene: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT sample_id, expression_value
        FROM gene_expression
        WHERE gene = ?
        ORDER BY sample_id
        LIMIT 20;
    """, (gene,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows) if rows else f"No expression data found for gene={gene}"


@mcp.tool()
def gene_mean_by_diagnosis(gene: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.diagnosis, AVG(g.expression_value), COUNT(*)
        FROM gene_expression g
        JOIN brain_samples b
          ON g.sample_id = b.gsm_id
        WHERE g.gene = ?
        GROUP BY b.diagnosis
        ORDER BY b.diagnosis;
    """, (gene,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows) if rows else f"No summary found for gene={gene}"


@mcp.tool()
def top_genes() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            g.gene,
            AVG(CASE WHEN b.diagnosis='AD' THEN g.expression_value END) AS ad_avg,
            AVG(CASE WHEN b.diagnosis='Control' THEN g.expression_value END) AS control_avg,
            AVG(CASE WHEN b.diagnosis='AD' THEN g.expression_value END) -
            AVG(CASE WHEN b.diagnosis='Control' THEN g.expression_value END) AS diff
        FROM brain_samples b
        JOIN gene_expression g
          ON b.gsm_id = g.sample_id
        GROUP BY g.gene
        ORDER BY ABS(diff) DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows) if rows else "No top genes could be computed."


@mcp.tool()
def upregulated_in_ad() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            g.gene,
            AVG(CASE WHEN b.diagnosis='AD' THEN g.expression_value END) -
            AVG(CASE WHEN b.diagnosis='Control' THEN g.expression_value END) AS diff
        FROM brain_samples b
        JOIN gene_expression g
          ON b.gsm_id = g.sample_id
        GROUP BY g.gene
        ORDER BY diff DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def highest_variance_genes() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            gene,
            AVG(expression_value * expression_value) -
            AVG(expression_value) * AVG(expression_value) AS variance
        FROM gene_expression
        GROUP BY gene
        ORDER BY variance DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def drug_targets_list() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT gene_symbol, drug_name, mechanism, disease_area
        FROM drug_targets
        ORDER BY gene_symbol;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return str(rows) if rows else "No drug target rows found."


@mcp.tool()
def genes_with_drug_links() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        WITH top_ad_genes AS (
            SELECT
                g.gene AS gene_symbol,
                AVG(CASE WHEN b.diagnosis = 'AD' THEN g.expression_value END) AS ad_avg,
                AVG(CASE WHEN b.diagnosis = 'Control' THEN g.expression_value END) AS control_avg,
                AVG(CASE WHEN b.diagnosis = 'AD' THEN g.expression_value END) -
                AVG(CASE WHEN b.diagnosis = 'Control' THEN g.expression_value END) AS diff
            FROM gene_expression g
            JOIN brain_samples b
              ON g.sample_id = b.gsm_id
            GROUP BY g.gene
            ORDER BY ABS(diff) DESC
            LIMIT 10
        )
        SELECT
            t.gene_symbol,
            t.ad_avg,
            t.control_avg,
            t.diff,
            d.drug_name,
            d.mechanism,
            d.disease_area
        FROM top_ad_genes t
        JOIN drug_targets d
          ON t.gene_symbol = d.gene_symbol
        ORDER BY ABS(t.diff) DESC;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return (
            "No overlap found between the top AD vs Control genes and known "
            "Alzheimer’s drug target genes in drug_targets."
        )

    return str(rows)


@mcp.tool()
def run_sql_query(query: str) -> str:
    if not query.strip().lower().startswith("select"):
        return "Only SELECT queries are allowed."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query)
    rows = cur.fetchmany(20)

    cur.close()
    conn.close()

    return str(rows)


@mcp.tool()
def plot_diagnosis_counts() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT diagnosis, COUNT(*)
        FROM brain_samples
        GROUP BY diagnosis
        ORDER BY diagnosis;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return "No diagnosis data found."

    labels = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    colors = [CONTROL_COLOR if x == "Control" else AD_COLOR for x in labels]

    ensure_plot_dir()
    path = os.path.join(PLOT_DIR, "diagnosis_counts.png")

    plt.figure(figsize=(8, 6))
    plt.bar(labels, counts, color=colors)
    plt.xlabel("Diagnosis")
    plt.ylabel("Count")
    plt.title("AD vs Control Sample Counts")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

    return f"Saved: {path}"


@mcp.tool()
def boxplot_gene(gene: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.diagnosis, g.expression_value
        FROM gene_expression g
        JOIN brain_samples b
          ON g.sample_id = b.gsm_id
        WHERE g.gene = ?
          AND g.expression_value IS NOT NULL;
    """, (gene,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return f"No expression data found for gene={gene}"

    ad = [r[1] for r in rows if r[0] == "AD"]
    control = [r[1] for r in rows if r[0] == "Control"]

    if not ad or not control:
        return f"Need both AD and Control values for gene={gene}"

    p = get_pvalue(ad, control)

    ensure_plot_dir()
    path = os.path.join(PLOT_DIR, f"{safe_filename(gene)}_boxplot.png")

    plt.figure(figsize=(8, 6))
    bp = plt.boxplot([control, ad], tick_labels=["Control", "AD"], patch_artist=True)
    bp["boxes"][0].set_facecolor(CONTROL_COLOR)
    bp["boxes"][1].set_facecolor(AD_COLOR)

    plt.scatter([1] * len(control), control, alpha=0.4, s=18)
    plt.scatter([2] * len(ad), ad, alpha=0.4, s=18)

    ymax = max(max(control), max(ad))
    if p is not None:
        plt.text(1.5, ymax * 1.03, f"p = {p:.3e}", ha="center")

    plt.xlabel("Diagnosis")
    plt.ylabel("Expression Value")
    plt.title(f"{gene} Expression by Diagnosis")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

    return f"Saved: {path}"


@mcp.tool()
def histogram_gene(gene: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT expression_value
        FROM gene_expression
        WHERE gene = ?
          AND expression_value IS NOT NULL;
    """, (gene,))
    values = [r[0] for r in cur.fetchall()]

    cur.close()
    conn.close()

    if not values:
        return f"No expression data found for gene={gene}"

    p_value = None
    if len(values) > 8:
        _, p_value = normaltest(values)

    ensure_plot_dir()
    path = os.path.join(PLOT_DIR, f"{safe_filename(gene)}_histogram.png")

    plt.figure(figsize=(8, 6))
    plt.hist(values, bins=20, color=NATURE_BLUE, edgecolor="black")
    title = f"{gene} Expression Distribution"
    if p_value is not None:
        title += f"\nNormality p = {p_value:.3e}"
    plt.title(title)
    plt.xlabel("Expression Value")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

    return f"Saved: {path}"


@mcp.tool()
def scatterplot(gene1: str, gene2: str) -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.diagnosis,
            g1.expression_value,
            g2.expression_value
        FROM gene_expression g1
        JOIN gene_expression g2
          ON g1.sample_id = g2.sample_id
        JOIN brain_samples b
          ON g1.sample_id = b.gsm_id
        WHERE g1.gene = ?
          AND g2.gene = ?
          AND g1.expression_value IS NOT NULL
          AND g2.expression_value IS NOT NULL;
    """, (gene1, gene2))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return f"No paired data found for {gene1} and {gene2}"

    x_all = [r[1] for r in rows]
    y_all = [r[2] for r in rows]

    r_val, p_val = None, None
    if len(x_all) > 2:
        r_val, p_val = pearsonr(x_all, y_all)

    control_x = [r[1] for r in rows if r[0] == "Control"]
    control_y = [r[2] for r in rows if r[0] == "Control"]
    ad_x = [r[1] for r in rows if r[0] == "AD"]
    ad_y = [r[2] for r in rows if r[0] == "AD"]

    ensure_plot_dir()
    path = os.path.join(PLOT_DIR, f"{safe_filename(gene1)}_vs_{safe_filename(gene2)}.png")

    plt.figure(figsize=(8, 6))
    if control_x:
        plt.scatter(control_x, control_y, color=CONTROL_COLOR, alpha=0.6, s=28, label="Control")
    if ad_x:
        plt.scatter(ad_x, ad_y, color=AD_COLOR, alpha=0.6, s=28, label="AD")

    title = f"{gene1} vs {gene2} Expression"
    if r_val is not None:
        title += f"\nr = {r_val:.2f}, p = {p_val:.3e}"

    plt.title(title)
    plt.xlabel(f"{gene1} Expression")
    plt.ylabel(f"{gene2} Expression")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

    return f"Saved: {path}"


@mcp.tool()
def plot_high_variance_genes() -> str:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            gene,
            AVG(expression_value * expression_value) -
            AVG(expression_value) * AVG(expression_value) AS variance
        FROM gene_expression
        GROUP BY gene
        ORDER BY variance DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return "No variance results found."

    genes = [r[0] for r in rows]
    variances = [r[1] for r in rows]

    ensure_plot_dir()
    path = os.path.join(PLOT_DIR, "top_variance_genes.png")

    plt.figure(figsize=(10, 6))
    plt.bar(genes, variances, color=NATURE_BLUE)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Gene")
    plt.ylabel("Variance")
    plt.title("Top 10 Highest Variance Genes")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

    return f"Saved: {path}"


@mcp.tool()
def available_tools() -> str:
    return str([
        "describe_dataset",
        "list_tables",
        "diagnosis_summary",
        "brain_region_summary",
        "samples_by_region",
        "list_sample_ids",
        "get_sample_info",
        "genes_for_sample",
        "search_gene",
        "gene_mean_by_diagnosis",
        "top_genes",
        "upregulated_in_ad",
        "highest_variance_genes",
        "drug_targets_list",
        "genes_with_drug_links",
        "run_sql_query",
        "plot_diagnosis_counts",
        "boxplot_gene",
        "histogram_gene",
        "scatterplot",
        "plot_high_variance_genes",
    ])

@mcp.tool()
def save_candidate_targets() -> str:
    """
    Save top AD vs Control candidate genes into a candidate_targets table.
    This stores analysis results in the database instead of only displaying them.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_symbol TEXT,
            ad_avg REAL,
            control_avg REAL,
            diff REAL,
            abs_diff REAL,
            has_drug_link TEXT,
            drug_name TEXT,
            mechanism TEXT,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("DELETE FROM candidate_targets;")

    cur.execute("""
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
            FROM gene_expression g
            JOIN brain_samples b
              ON g.sample_id = b.gsm_id
            GROUP BY g.gene
            ORDER BY ABS(diff) DESC
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
    """)

    conn.commit()

    cur.execute("""
        SELECT gene_symbol, diff, has_drug_link, drug_name
        FROM candidate_targets
        ORDER BY abs_diff DESC
        LIMIT 20;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return f"Saved candidate targets to candidate_targets table:\n{rows}"


@mcp.tool()
def view_candidate_targets() -> str:
    """
    View saved candidate target genes from the candidate_targets table.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT gene_symbol, ad_avg, control_avg, diff, has_drug_link, drug_name, mechanism
        FROM candidate_targets
        ORDER BY abs_diff DESC
        LIMIT 20;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return "No saved candidate targets found. Run save_candidate_targets first."

    return str(rows)

def main():
    mcp.run()


if __name__ == "__main__":
    main()
