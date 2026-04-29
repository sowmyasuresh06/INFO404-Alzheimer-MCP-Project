import pandas as pd
import re
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt

src = Path('Pasted text.txt')
outdir = Path('.')

rows = []
with open(src, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        gsm_id, raw_label = line.split('\t')
        rows.append((gsm_id, raw_label))

df = pd.DataFrame(rows, columns=['gsm_id', 'raw_label'])

def normalize_region(s: str) -> str:
    key = re.sub(r'[\s\-]+', '', s).lower()
    mapping = {
        'entorhinalcortex': 'Entorhinal Cortex',
        'hippocampus': 'Hippocampus',
        'postcentralgyrus': 'Postcentral Gyrus',
        'superiorfrontalgyrus': 'Superior Frontal Gyrus',
    }
    return mapping.get(key, s.strip())

def parse_label(raw: str):
    parts = raw.split('_')
    region = normalize_region(parts[0])
    gender = parts[1].capitalize() if len(parts) > 1 else None
    age = None
    diagnosis = 'Control'
    subject_id = None
    for p in parts[2:]:
        if m := re.fullmatch(r'(\d+)yrs', p, flags=re.I):
            age = int(m.group(1))
        elif p.upper() == 'AD':
            diagnosis = 'AD'
        elif p.lower().startswith('indiv'):
            subject_id = p[5:]
        elif re.fullmatch(r'\d+', p):
            if subject_id is None:
                subject_id = p
    return pd.Series([region, gender, age, diagnosis, subject_id])

df[['brain_region', 'gender', 'age_years', 'diagnosis', 'subject_id']] = df['raw_label'].apply(parse_label)
df = df[['gsm_id', 'raw_label', 'brain_region', 'gender', 'age_years', 'diagnosis', 'subject_id']]
df.to_csv(outdir / 'brain_samples_cleaned.csv', index=False)

conn = sqlite3.connect(outdir / 'brain_samples.sqlite')
df.to_sql('brain_samples', conn, if_exists='replace', index=False)
conn.close()

plot_df = df.groupby(['brain_region', 'diagnosis']).size().unstack(fill_value=0).sort_index()
ax = plot_df.plot(kind='bar', figsize=(10, 6))
ax.set_title('Sample Counts by Brain Region and Diagnosis')
ax.set_xlabel('Brain Region')
ax.set_ylabel('Number of Samples')
ax.legend(title='Diagnosis')
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.savefig(outdir / 'sample_counts_by_region_diagnosis.png', dpi=300, bbox_inches='tight')
print('Done.')
