URL:🔗
# Credit Risk Segmentation & Data Quality Audit

Data governance and risk-tier segmentation built on 150,000 real credit customer records
("Give Me Some Credit," Kaggle), leading with a systematic data quality audit before any modeling.

Built as a portfolio project for the American Express Credit & Fraud Risk Apprenticeship application.

## Results

| Metric | Value |
|---|---|
| Customers analyzed | 150,000 |
| Missing income data | 19.8% (imputed) |
| Model ROC-AUC | 0.856 |
| Risk tier spread | 39x (0.60% → 23.38% default rate) |

## Data quality findings

| Issue | Count | Action taken |
|---|---|---|
| Missing MonthlyIncome | 29,731 (19.8%) | Median imputation + missing-flag column |
| Missing NumberOfDependents | 3,924 (2.6%) | Imputed as 0 |
| age = 0 (impossible) | 1 | Row removed |
| Sentinel codes (96/98) in past-due fields | 269 | Capped at 18 — kept as signal (54.65% default rate in this group) |
| Utilization ratio > 1 | 3,321 | Capped at 2 |
| DebtRatio > 1,000 (max was 329,664) | 16,892 | Capped at 99th percentile |

## Key findings

- **Payment history dominates risk**: customers with 6+ instances of 90-day-late payments
  default at 66.48% vs. 4.63% for a clean history — a 14x gap.
- **Age is the second-strongest signal**: default rate falls steadily from 11.73% (18-29)
  to 2.32% (70+).
- **Corrupted codes carry real signal**: the 96/98 sentinel values weren't just noise to
  drop — that group showed a 54.65% default rate, meaning the data corruption itself
  correlated with risk.

## Pipeline

```
cs-training.csv → SQLite (credit_risk.db) → SQL audit → cleaning → Logistic Regression → risk tiers → dashboard
```

1. **`build_database.py`** — loads the CSV into SQLite
2. **`exploration_queries.sql`** / **`run_queries.py`** — data quality audit + exploration
3. **`segment_customers.py`** — cleans data (documented fixes for every issue found),
   trains a Logistic Regression risk model, segments customers into 5 risk tiers
4. **`dashboard.html`** — interactive dashboard (open directly in a browser)
5. **`Credit_Risk_Segmentation_Case_Study.docx`** — one-page written case study

## Tech stack

SQL (SQLite) · Python (pandas, scikit-learn) · Chart.js

## Dataset

["Give Me Some Credit"](https://www.kaggle.com/c/GiveMeSomeCredit/data) — Kaggle.
Not included in this repo; see `Local_Setup_Guide.md` for download instructions.

## Running it locally

See [`Local_Setup_Guide.md`](Local_Setup_Guide.md) for full setup steps.
