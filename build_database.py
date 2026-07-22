"""
Loads cs-training.csv into a SQLite database (credit_risk.db) so
exploration_queries.sql can be run against it.
"""
import pandas as pd
import sqlite3

print("Loading cs-training.csv ...")
df = pd.read_csv('cs-training.csv', index_col=0)
print(f"Loaded {len(df)} rows")

conn = sqlite3.connect('credit_risk.db')
df.to_sql('customers', conn, if_exists='replace', index=False)
conn.close()

print("Done — credit_risk.db created with a 'customers' table.")
