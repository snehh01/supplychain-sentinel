# SupplyChain Sentinel interview guide

## 30-second explanation

SupplyChain Sentinel predicts whether a retail product may stock out in the next seven days. It validates inventory-history data, creates time-aware demand and inventory features, runs a saved classification model, and converts the probability into an explainable risk score and replenishment action in Streamlit.

## 60-second explanation

I built it as an end-to-end alternative to a notebook-only ML project. A reproducible simulator generates daily inventory, sales, promotion, and supplier behavior. The pipeline cleans deliberate quality issues, creates rolling features using only past information, and defines a future seven-day stockout target. I compared three models using chronological splits and selected Logistic Regression by validation F1 and recall. On the untouched synthetic test period it achieved 0.865 recall, 0.649 F1, and 0.871 ROC-AUC. The saved pipeline powers a Streamlit app where users can upload their own CSV, map columns, inspect risks, and download an action plan. The action recommendation is deterministic business logic, not ML.

## Two-minute explanation

The business question is: which products are likely to run out before the next replenishment can arrive? The default dataset contains 36,500 simulated daily records for 100 products. Demand includes seasonal, promotion, trend, and product effects; inventory is reduced by sales and replenished by delayed orders, so stockouts arise from the simulated operation.

After validation, the cleaner removes exact duplicates, repairs negative inventory, imputes missing lead times, and records every decision. Feature engineering calculates inventory coverage, shifted 7- and 30-day sales, demand growth, safety-stock gap, reorder risk, promotion lift, and prior stockout rate. The target looks forward from tomorrow through seven days ahead. The last seven rows per product remain unlabeled.

Training uses chronological periods, so future rows never train a model evaluated on the past. Logistic Regression, Random Forest, and Gradient Boosting are compared. The selected saved pipeline produces real probabilities in the app. A separate transparent formula combines 60% probability contribution with inventory, lead-time, and trend components to create a 0–100 risk score and deterministic replenishment suggestion. SQLite stores reporting tables, while Streamlit provides dataset upload, dashboard, product drill-down, analytics, and model evidence. The main limitation is synthetic data; real deployment requires calibration, cost-based thresholds, drift monitoring, and planner validation.

## Complete workflow

1. Generate demo data or upload a CSV.
2. Normalize headers, map fields, validate dates/numbers, and enforce file limits.
3. Clean duplicates, invalid inventory, missing lead time, and extreme sensor values.
4. Engineer past-only operational features and the future target.
5. Split chronologically and compare three classifiers.
6. Save the selected preprocessing-and-model pipeline.
7. Score the latest row for each product.
8. Calculate risk level, urgency, date, quantity, and action with deterministic rules.
9. Persist batch results to SQLite and display interactive decisions in Streamlit.

## Architecture and major files

- `run_pipeline.py`: executes the reproducible batch build.
- `src/data_generation.py`: simulates products, demand, orders, inventory, and stockouts.
- `src/data_collection.py`: reads uploaded or local CSV data safely.
- `src/user_data.py`: maps user fields and creates the model-ready schema.
- `src/data_preprocessing.py`: applies auditable cleaning decisions.
- `src/feature_engineering.py`: builds past-only features and future labels.
- `src/train_model.py`: preprocesses, compares, evaluates, and saves models.
- `src/predict.py`: loads the saved model and scores current product states.
- `src/risk_engine.py`: implements the explainable rule-based decision layer.
- `src/database.py`: builds SQL tables and runs business queries.
- `streamlit_app.py`, `app_pages/`, `components/`, `state.py`: user interface and session lifecycle.
- `tests/`: unit, integration, and page-level verification.

## Technology choices

- **Pandas/NumPy:** readable tabular transformations appropriate to this dataset size.
- **Scikit-learn:** consistent preprocessing and classical models in one persisted pipeline.
- **Logistic Regression:** interpretable baseline that delivered the best validation F1 here.
- **Streamlit:** fast, Python-native portfolio interface without a separate frontend API.
- **SQLAlchemy/SQLite:** real relational persistence locally with a PostgreSQL upgrade path.
- **Pytest/AppTest:** pure-logic tests plus deterministic Streamlit page tests.

I did not choose deep learning because the dataset is modest tabular data and complexity would not be justified. I did not add FastAPI or React because Streamlit directly calls the local backend modules and no separate service boundary is currently needed.

## Dataset, model, and evaluation

- **Dataset:** synthetic daily retail inventory operations; 36,500 cleaned rows and 100 products.
- **Target:** whether any stockout occurs during t+1 through t+7.
- **Features:** current inventory, demand, receipts, lead time, price/promotion/calendar data, ratios, shifted rolling demand, trend, safety gap, reorder risk, and shifted history.
- **Preprocessing:** median imputation, scaling for Logistic Regression, and one-hot encoding with unknown-category handling.
- **Training:** chronological 70%/15%/15% periods; fixed random seed for stochastic models.
- **Test result:** precision 0.519, recall 0.865, F1 0.649, ROC-AUC 0.871.
- **Inference:** load `stockout_model.joblib`, score the most recent row for every product, then apply risk rules.

## Five design decisions

1. Chronological rather than random splitting to reflect future prediction.
2. Shift rolling features so they never contain same-day or future demand.
3. Persist preprocessing and model together to prevent training/inference mismatch.
4. Keep ML probability separate from the deterministic operational decision layer.
5. Require explicit column mapping instead of silently guessing unfamiliar user schemas.

## Challenges and solutions

1. **Leakage:** shifted history and future-only targets.
2. **Schema variation:** aliases plus user-confirmed mapping and validation.
3. **Actionability:** a documented score and downloadable replenishment queue.

## Limitations and future improvements

Synthetic behavior may not reflect a real retailer. The probability is not calibrated for a specific business cost. Products have one warehouse, and replenishment does not optimize constrained multi-location inventory. Next steps are real ERP/POS data, probability calibration, cost-based thresholds, drift monitoring, product-location modeling, and planner feedback.

## Why this is more than a tutorial

It joins reproducible operations simulation, explicit data quality, leakage controls, model comparison, saved inference, rule transparency, SQL persistence, user-defined schemas, exportable actions, and automated UI/integration tests. Unlike a typical single-dataset notebook, it supports a traceable input-to-decision workflow.

## What I learned

The hardest part of applied ML is protecting the time boundary, keeping inference consistent, validating messy inputs, and presenting uncertainty honestly. A model becomes useful only when users can understand and act on its output.

## Interview questions and beginner-friendly answers

1. **What problem does the model solve?** Binary classification: whether a product will stock out in the next seven days.
2. **Why is ML appropriate?** Multiple nonlinear and interacting signals affect risk; model comparison tests whether learned patterns improve prioritization. The action rule itself does not require ML.
3. **What is the target?** The maximum stockout event from t+1 through t+7.
4. **Why exclude the current day?** Including it would answer whether the item is already out, not predict the future.
5. **How did you prevent leakage?** Shifted historical features, future-only labels, and chronological splits.
6. **Why chronological splitting?** It simulates training on the past and evaluating on later unseen periods.
7. **Why Logistic Regression?** It had the best validation F1 and recall tie-breaker and is easy to explain.
8. **Why not select Random Forest by ROC-AUC?** The declared business selection rule prioritized the operating threshold’s F1 and recall; ROC-AUC measures ranking across all thresholds.
9. **What does recall 0.865 mean?** The model caught about 86.5% of actual seven-day stockouts in the synthetic test period.
10. **What does precision 0.519 mean?** About 51.9% of model alerts at threshold 0.5 were true future stockouts.
11. **Why accept false positives?** Missing a shortage may cost more than reviewing an extra alert, but real cost data should set the threshold.
12. **What is ROC-AUC?** The probability that a random positive is ranked above a random negative, across thresholds.
13. **How is class imbalance handled?** Logistic Regression uses balanced class weights; precision, recall, F1, and ROC-AUC supplement accuracy.
14. **How is preprocessing reused?** It is stored in the same Scikit-learn Pipeline as the model.
15. **How are unknown categories handled?** OneHotEncoder uses `handle_unknown="ignore"`.
16. **Is the risk score ML?** Partly: probability comes from ML, while operational adjustments and actions are deterministic rules.
17. **How is replenishment calculated?** Expected demand over supplier lead time plus seven days, minus current inventory, bounded at zero.
18. **How do uploads work?** CSV bytes are size-checked, parsed, normalized, mapped, validated, cleaned, featured, and scored in the browser session.
19. **Is uploaded data saved?** Not by the Streamlit workflow; it remains in session memory. Batch demo results are stored locally.
20. **What is stored in SQLite?** Products, inventory, sales, supplier information, predictions, and alerts.
21. **How did you test it?** Unit tests cover generation, cleaning, features, risk, and upload errors; integration tests load the model and rebuild/query SQL; AppTest loads every page.
22. **What happens with invalid data?** Users receive specific errors for empty files, oversized files, missing/duplicate columns, invalid dates, or nonnumeric required values.
23. **What would fail first in production?** Data/schema drift and probability calibration; monitoring and retraining policies are needed.
24. **How would you deploy it?** Commit required generated artifacts, install pinned requirements, and run `streamlit run streamlit_app.py` on Streamlit Community Cloud.
25. **How would you secure a public demo?** Limit upload size/type, avoid persistence, exclude secrets, show safe columns only, and add authentication for private operational data.
26. **Why no API?** The current single-process Streamlit app can call Python modules directly; an API is useful only when other clients or independent scaling require it.
27. **How do you know the displayed prediction is real?** Integration tests load the saved model and verify bounded probabilities and one latest prediction per product.
28. **What would you change with real data?** Validate labels, include product-location and purchase-order detail, tune thresholds by business cost, calibrate probabilities, and monitor drift.
29. **Did you train on user uploads?** No. Uploads are inference-only and must match the meaning of the training schema.
30. **What did you personally build?** Answer only with the components you can explain and reproduce from this guide.

## Topics to learn before claiming expertise

- **Must learn:** precision–recall trade-off and threshold tuning.
- **Must learn:** time-series leakage and chronological validation.
- **Must learn:** Scikit-learn Pipeline and ColumnTransformer.
- **Must learn:** probability calibration and data/model drift.
- **Must learn:** SQL normalization, joins, and parameterized queries.
