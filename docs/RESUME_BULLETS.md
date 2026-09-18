# SupplyChain Sentinel — Seven-day inventory stockout decision system

## Data Scientist / AI-ML roles

**Technologies:** Python, Pandas, NumPy, Scikit-learn, Streamlit, SQLAlchemy, SQLite, Pytest

- Built an end-to-end classification pipeline over 36,500 synthetic daily product records, using leakage-safe rolling features and chronological train/validation/test splits.
- Compared Logistic Regression, Random Forest, and Gradient Boosting; selected the validation leader and verified 0.865 recall, 0.649 F1, and 0.871 ROC-AUC on the untouched test period.
- Deployed saved-model inference in a five-page Streamlit app that validates uploaded CSVs and converts probabilities into transparent stockout-risk and replenishment decisions.

## Data Analyst roles

**Technologies:** Python, Pandas, NumPy, SQL, SQLite, Streamlit, Altair

- Analyzed 36,500 synthetic inventory and demand observations across 100 products, six categories, and four warehouses to identify stockout, promotion, seasonality, and supplier patterns.
- Designed normalized SQLite tables and reusable SQL queries for risk ranking, category rates, warehouse events, lead-time analysis, and immediate replenishment needs.
- Created an interactive dashboard with dataset validation, business filters, product drill-downs, interpretable KPIs, and downloadable action plans.

## Python Developer roles

**Technologies:** Python, Pandas, Scikit-learn, SQLAlchemy, Streamlit, Joblib, Pytest

- Engineered a modular Python application spanning data ingestion, validation, preprocessing, feature creation, model training, inference, persistence, and presentation.
- Implemented secure CSV handling with a 10 MB limit, duplicate-header detection, schema mapping, understandable validation errors, and session-scoped uploaded data.
- Added automated unit, integration, database, inference, and Streamlit page tests for critical workflows and reproducibility.
