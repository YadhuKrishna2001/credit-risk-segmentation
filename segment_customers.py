"""
Credit Risk Segmentation & Data Quality Audit
================================================
Dataset: "Give Me Some Credit" (150,000 customers, Kaggle)
Target: SeriousDlqin2yrs (1 = serious delinquency within 2 years)

This script:
1. Documents and fixes data quality issues found during SQL audit
2. Trains a simple risk model
3. Segments customers into risk tiers based on predicted probability
4. Saves everything needed for the dashboard
"""

import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

RANDOM_STATE = 42

df = pd.read_csv('cs-training.csv', index_col=0)
n_original = len(df)

quality_log = {}

# ---- 1. Missing value audit ----
quality_log['missing_monthly_income'] = int(df['MonthlyIncome'].isnull().sum())
quality_log['missing_dependents'] = int(df['NumberOfDependents'].isnull().sum())

# Impute: median income (robust to skew), 0 dependents (most common value)
df['MonthlyIncome_was_missing'] = df['MonthlyIncome'].isnull().astype(int)
df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df['MonthlyIncome'].median())
df['NumberOfDependents'] = df['NumberOfDependents'].fillna(0)

# ---- 2. Impossible age values ----
quality_log['age_zero_count'] = int((df['age'] == 0).sum())
df = df[df['age'] >= 18].copy()  # drop the impossible record(s)

# ---- 3. Sentinel error codes (96/98) in past-due columns ----
# These values (96, 98) are known data-entry artifacts in this dataset, not real
# payment counts. We cap them at a realistic max (assumed 17, the highest genuine
# value observed) rather than dropping — these customers are real and their
# elevated risk (54.65% default rate in this bucket, per SQL audit) is genuine signal.
sentinel_cols = ['NumberOfTime30-59DaysPastDueNotWorse',
                  'NumberOfTime60-89DaysPastDueNotWorse',
                  'NumberOfTimes90DaysLate']
sentinel_count = 0
for col in sentinel_cols:
    mask = df[col].isin([96, 98])
    sentinel_count = max(sentinel_count, mask.sum())
    df.loc[mask, col] = 18  # cap at just above the highest genuine value
quality_log['sentinel_code_rows'] = int(sentinel_count)

# ---- 4. RevolvingUtilization out-of-range values ----
quality_log['utilization_over_1'] = int((df['RevolvingUtilizationOfUnsecuredLines'] > 1).sum())
# Cap at 2 (allow some legitimate over-limit cases, but remove the extreme 50,708 outlier)
df['RevolvingUtilizationOfUnsecuredLines'] = df['RevolvingUtilizationOfUnsecuredLines'].clip(upper=2)

# ---- 5. DebtRatio extreme outliers ----
quality_log['debtratio_over_1000'] = int((df['DebtRatio'] > 1000).sum())
# Cap at the 99th percentile to remove clearly corrupted values (329,664 max) while
# preserving genuine high-debt-ratio signal
debt_cap = df['DebtRatio'].quantile(0.99)
df['DebtRatio'] = df['DebtRatio'].clip(upper=debt_cap)

quality_log['rows_after_cleaning'] = int(len(df))
quality_log['rows_removed'] = int(n_original - len(df))

print("Data quality summary:", json.dumps(quality_log, indent=2))

# ---- Train a risk model ----
feature_cols = [c for c in df.columns if c != 'SeriousDlqin2yrs']
X = df[feature_cols]
y = df['SeriousDlqin2yrs']

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
)

model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=RANDOM_STATE)
model.fit(X_train, y_train)
auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print(f"\nModel ROC-AUC: {auc:.4f}")

# ---- Segment ALL customers into risk tiers based on predicted probability ----
df['risk_score'] = model.predict_proba(X_scaled)[:, 1]
df['risk_tier'] = pd.qcut(
    df['risk_score'], q=5,
    labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
)

tier_summary = df.groupby('risk_tier', observed=True).agg(
    n_customers=('SeriousDlqin2yrs', 'count'),
    defaults=('SeriousDlqin2yrs', 'sum'),
).reset_index()
tier_summary['default_rate_pct'] = round(100 * tier_summary['defaults'] / tier_summary['n_customers'], 2)
print("\nRisk tier summary:")
print(tier_summary)

# ---- Feature importance (coefficients) ----
coef_importance = pd.Series(model.coef_[0], index=feature_cols).sort_values(key=abs, ascending=False)
print("\nTop feature coefficients (standardized):")
print(coef_importance.head(8))

# ---- Save everything for the dashboard ----
output = {
    'quality_log': quality_log,
    'model_auc': round(auc, 4),
    'risk_tier_summary': tier_summary.to_dict('records'),
    'top_features': coef_importance.head(8).round(4).to_dict(),
    'original_default_rate_pct': round(100 * y.mean(), 2),
}

with open('segmentation_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nSaved segmentation_results.json")
