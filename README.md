# SupplyChain Sentinel

## Project overview

SupplyChain Sentinel is a Streamlit application that predicts whether retail products may run out of stock within the next seven days. It combines inventory and sales history with a trained machine-learning model, then converts each prediction into a clear risk score and replenishment recommendation.

The project includes a synthetic dataset, a reproducible training pipeline, CSV upload support, five application pages, downloadable action plans, and a local SQLite database.

## Problem statement

Inventory planners need to identify products that may run out before customers are affected. Looking at stock levels alone is not enough because sales speed, supplier lead time, recent demand changes, promotions, and reorder points also influence risk.

This project brings those signals together and answers two practical questions:

- Which products are most likely to stock out during the next seven days?
- What replenishment action should be considered for each product?

## Features

- Built-in synthetic data with 36,500 daily records for 100 products.
- CSV upload with automatic column suggestions and manual column mapping.
- Validation for required fields, dates, numeric values, duplicate product dates, and file size.
- Documented assumptions when product name, supplier lead time, or reorder point is missing.
- Seven-day stockout probabilities from a saved Logistic Regression pipeline.
- Transparent risk levels, risk scores, expected stockout dates, and replenishment quantities.
- Dashboard filters for category, warehouse, and date.
- Product-level explanations and recommended actions.
- Historical analytics for category, warehouse, promotion, and season.
- Model comparison, confusion matrix, ROC curve, and influential-feature views.
- CSV downloads for the built-in dataset and action plans.
- SQLite tables and example SQL queries for generated batch results.

## How it works

```text
User selects the built-in data or uploads a CSV
                         ↓
Streamlit previews the data and collects column mappings
                         ↓
Pandas validates, cleans, and standardizes the records
                         ↓
Pandas and NumPy create time-aware inventory and demand features
                         ↓
The saved scikit-learn model predicts seven-day stockout probability
                         ↓
Python rules calculate risk level, expected date, and replenishment action
                         ↓
The five Streamlit pages display and export the results
```

The model predicts probability. The final replenishment recommendation is produced by documented Python rules, not by the model.

## Application pages

1. **Data workspace** — download the built-in data, upload a CSV, map columns, validate it, and activate it for the current browser session.
2. **Dashboard** — review current KPIs, trends, risk distribution, filters, and the priority action queue.
3. **Product risk** — select one product and inspect its probability, inventory coverage, risk signals, and recommended action.
4. **Analytics** — explore historical stockout patterns by category, warehouse, promotion, and season.
5. **Model performance** — compare trained models and review validation metrics, the test confusion matrix, ROC curve, and feature influence.

## Technology stack

| Technology | Why it is used |
|---|---|
| Python | Pipeline orchestration, validation, prediction, and decision rules |
| Pandas | CSV handling, cleaning, aggregation, and feature preparation |
| NumPy | Numerical calculations and reproducible synthetic data generation |
| scikit-learn | Preprocessing pipelines, model training, evaluation, and prediction |
| Joblib | Saving and loading the trained model pipeline |
| Streamlit | Multi-page interactive application |
| Altair | Interactive charts used by the Streamlit pages |
| Matplotlib and Seaborn | EDA figures produced by the batch pipeline |
| SQLite and SQLAlchemy | Local storage and example analytical queries |
| Pytest | Automated checks for data, model logic, uploads, and pages |

## Project structure

```text
streamlit_app.py          # App setup and top navigation
app_pages/                # Five visible Streamlit pages
app_utils.py              # Shared cached data loaders
state.py                  # Active-dataset session state
ui.py                     # Existing visual style and shared page presentation
components/               # Reusable chart and display helpers
src/                      # Data, ML, prediction, risk, and database logic
data/                     # Built-in raw and processed datasets
models/                   # Saved model pipeline
database/                 # SQLite database and example SQL
reports/                  # Generated metrics and EDA figures
tests/                    # Automated tests
docs/                     # Project and interview documentation
run_pipeline.py           # Rebuilds data, model, predictions, reports, and database
```

## Installation and setup

Python 3.13 is specified in `runtime.txt`.

```powershell
cd supplychain-sentinel
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in a browser.

To run the automated checks:

```powershell
python -m pytest -q
```

To regenerate all included artifacts:

```powershell
python run_pipeline.py
```

## Usage

1. Open **Data workspace**.
2. Keep the **Built-in demo**, or upload a CSV.
3. If uploading, review the suggested column mappings.
4. Map all essential fields and choose a lead-time assumption if needed.
5. Select **Validate and activate**.
6. Open **Dashboard** to review priority risks.
7. Use **Product risk** to understand one recommendation.
8. Use **Analytics** and **Model performance** for deeper analysis.
9. Download the action-plan CSV when needed.

Uploaded data stays in the current Streamlit browser session. The upload workflow does not write it to the SQLite database.

## Screenshots

Add screenshots here when publishing the repository:

- Dashboard and hero section
- Data workspace and column mapping
- Product risk explanation
- Analytics charts
- Model performance page

## Limitations

- The included data is synthetic, so reported model performance is not evidence of real business impact.
- The application scores uploaded data in memory and does not connect to a live inventory system.
- Uploaded data uses the existing trained model; the model is not retrained for each upload.
- Replenishment quantities are rule-based planning guidance, not optimized purchase orders.
- There is no login, scheduled scoring, alert delivery, or public deployment included.

## Future improvements

- Validate the approach with real, anonymized retail data.
- Add probability calibration and cost-based alert thresholds.
- Connect to a real inventory database or scheduled data feed.
- Add model monitoring for data drift and prediction quality.
- Add authenticated roles before using private operational data.

## Model results

Logistic Regression was selected using chronological validation with F1 and recall. On the untouched synthetic test period, it achieved approximately 0.519 precision, 0.865 recall, 0.649 F1, and 0.871 ROC-AUC. These results are generated by the pipeline and stored in `reports/metrics/model_metrics.json`.
