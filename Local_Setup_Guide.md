# Running Project 2 Locally (Credit Risk Segmentation)

You already have Python, VS Code, and your virtual environment set up from Project 1 —
this reuses the same environment, just a new folder.

## 1. Create a new project folder

Same pattern as before: a new folder like `Documents/amex-credit-risk-project`, opened in VS Code.

## 2. Get the dataset

In the VS Code terminal:
```bash
curl -o cs-training.csv "https://raw.githubusercontent.com/JLZml/Credit-Scoring-Data-Sets/master/3.%20Kaggle/Give%20Me%20Some%20Credit/cs-training.csv"
```

Or from Kaggle directly: https://www.kaggle.com/c/GiveMeSomeCredit/data (download `cs-training.csv`)

## 3. Set up the virtual environment

If this is a new folder, you'll need a fresh venv (venvs don't carry across folders):
```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install pandas numpy scikit-learn
```

If you get the execution-policy error again:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 4. Run the pipeline, in this order

```bash
python build_database.py       # loads CSV into credit_risk.db
python run_queries.py          # runs the data quality audit queries
python segment_customers.py    # cleans data, trains model, creates risk tiers
```

## 5. View results

- Open `dashboard.html` directly in your browser (double-click it)
- Open `Credit_Risk_Segmentation_Case_Study.docx` in Word

## 6. Push to GitHub (same process as Project 1)

```bash
git init
git add .
git commit -m "Initial commit: credit risk segmentation pipeline"
git branch -M main
git remote add origin https://github.com/YadhuKrishna2001/credit-risk-segmentation.git
git push -u origin main
```

Remember the `.gitignore` — it should exclude `venv/`, `cs-training.csv`, and `credit_risk.db`
for the same reasons as Project 1 (large/regenerable files shouldn't be committed).
