"""
Runs exploration_queries.sql against credit_risk.db and prints results as
clean, aligned tables (using pandas).
"""
import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

conn = sqlite3.connect('credit_risk.db')

raw = open('exploration_queries.sql').read()
lines = [l for l in raw.split('\n') if not l.strip().startswith('--')]
clean = '\n'.join(lines)
queries = [q.strip() for q in clean.split(';') if q.strip()]

titles = [
    "1. Overall default rate",
    "2. Missing value audit",
    "3. Impossible age values",
    "4. Sentinel error codes (96/98) in past-due columns",
    "5. RevolvingUtilization out-of-range values",
    "6. DebtRatio extreme outliers",
    "7. Default rate by age band",
    "8. Default rate by 90+ days late history",
]

for i, q in enumerate(queries):
    title = titles[i] if i < len(titles) else f"Query {i+1}"
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    df = pd.read_sql_query(q, conn)
    print(df.to_string(index=False))

conn.close()
print("\nDone.")
