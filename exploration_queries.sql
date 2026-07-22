-- ============================================================
-- Credit Risk Segmentation: Data Quality Audit & Exploration
-- Dataset: "Give Me Some Credit" (150,000 customers)
-- Target: SeriousDlqin2yrs (1 = serious delinquency within 2 years)
-- ============================================================

-- 1. Overall default rate
SELECT
    COUNT(*) AS total_customers,
    SUM(SeriousDlqin2yrs) AS defaulted,
    ROUND(100.0 * SUM(SeriousDlqin2yrs) / COUNT(*), 2) AS default_rate_pct
FROM customers;

-- 2. Missing value audit
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN MonthlyIncome IS NULL THEN 1 ELSE 0 END) AS missing_monthly_income,
    ROUND(100.0 * SUM(CASE WHEN MonthlyIncome IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_missing_income,
    SUM(CASE WHEN NumberOfDependents IS NULL THEN 1 ELSE 0 END) AS missing_dependents,
    ROUND(100.0 * SUM(CASE WHEN NumberOfDependents IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_missing_dependents
FROM customers;

-- 3. Impossible / sentinel-value audit: age
SELECT
    SUM(CASE WHEN age = 0 THEN 1 ELSE 0 END) AS age_zero_count,
    SUM(CASE WHEN age > 100 THEN 1 ELSE 0 END) AS age_over_100_count,
    MIN(age) AS min_age,
    MAX(age) AS max_age
FROM customers;

-- 4. Sentinel error codes in past-due columns (96/98 are not real payment counts)
SELECT
    SUM(CASE WHEN "NumberOfTime30-59DaysPastDueNotWorse" IN (96, 98) THEN 1 ELSE 0 END) AS bad_30_59,
    SUM(CASE WHEN "NumberOfTime60-89DaysPastDueNotWorse" IN (96, 98) THEN 1 ELSE 0 END) AS bad_60_89,
    SUM(CASE WHEN NumberOfTimes90DaysLate IN (96, 98) THEN 1 ELSE 0 END) AS bad_90_plus
FROM customers;

-- 5. RevolvingUtilization out-of-range (should logically be 0-1 as a ratio)
SELECT
    SUM(CASE WHEN RevolvingUtilizationOfUnsecuredLines > 1 THEN 1 ELSE 0 END) AS over_1,
    SUM(CASE WHEN RevolvingUtilizationOfUnsecuredLines > 10 THEN 1 ELSE 0 END) AS over_10,
    MAX(RevolvingUtilizationOfUnsecuredLines) AS max_value
FROM customers;

-- 6. DebtRatio extreme outliers
SELECT
    SUM(CASE WHEN DebtRatio > 10 THEN 1 ELSE 0 END) AS over_10,
    SUM(CASE WHEN DebtRatio > 1000 THEN 1 ELSE 0 END) AS over_1000,
    MAX(DebtRatio) AS max_value
FROM customers;

-- 7. Default rate by age band (risk segmentation preview)
SELECT
    CASE
        WHEN age < 30 THEN '18-29'
        WHEN age < 40 THEN '30-39'
        WHEN age < 50 THEN '40-49'
        WHEN age < 60 THEN '50-59'
        WHEN age < 70 THEN '60-69'
        ELSE '70+'
    END AS age_band,
    COUNT(*) AS n_customers,
    SUM(SeriousDlqin2yrs) AS defaults,
    ROUND(100.0 * SUM(SeriousDlqin2yrs) / COUNT(*), 2) AS default_rate_pct
FROM customers
WHERE age >= 18
GROUP BY age_band
ORDER BY MIN(age);

-- 8. Default rate by number of times 90+ days late (strongest risk signal)
SELECT
    CASE
        WHEN NumberOfTimes90DaysLate = 0 THEN '0'
        WHEN NumberOfTimes90DaysLate BETWEEN 1 AND 2 THEN '1-2'
        WHEN NumberOfTimes90DaysLate BETWEEN 3 AND 5 THEN '3-5'
        WHEN NumberOfTimes90DaysLate NOT IN (96, 98) THEN '6+'
        ELSE 'data error (96/98)'
    END AS late_90_band,
    COUNT(*) AS n_customers,
    SUM(SeriousDlqin2yrs) AS defaults,
    ROUND(100.0 * SUM(SeriousDlqin2yrs) / COUNT(*), 2) AS default_rate_pct
FROM customers
GROUP BY late_90_band
ORDER BY default_rate_pct;
