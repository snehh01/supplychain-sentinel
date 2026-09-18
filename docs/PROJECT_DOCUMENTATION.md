# SupplyChain Sentinel project documentation

## 1. Project overview

SupplyChain Sentinel helps an inventory planner identify retail products that may run out of stock within seven days. It reads inventory and sales history, creates recent-demand and inventory signals, uses a saved classification model to estimate stockout probability, and recommends a replenishment response.

The project can be explored immediately with its built-in synthetic dataset. A user can also upload a CSV and use the same application pages with that data during the current browser session.

## 2. Problem statement

A low inventory value does not always mean that a product will run out soon. The answer also depends on how quickly the product is selling, whether demand is rising, how long a supplier takes to deliver, whether a promotion is active, and when replenishment normally begins.

The project combines these factors so planners can focus on the products that need attention first.

## 3. Proposed solution

The solution has two connected parts:

- A batch pipeline generates and cleans demo data, creates features, compares models, saves the selected model, produces current predictions, and builds a SQLite database.
- A Streamlit application lets a user explore the built-in results or validate and score an uploaded CSV.

The trained model returns a probability. A separate, readable Python risk engine converts that probability and current inventory conditions into a risk score, risk level, expected stockout date, replenishment quantity, urgency, and recommended action.

## 4. Features

### Data workspace

- Uses the built-in dataset by default.
- Downloads either a short upload template or the full built-in CSV.
- Accepts CSV files up to the configured 10 MB validation limit.
- Suggests matches for common field names, including common Kaggle names.
- Lets the user correct each mapping before activation.
- Shows recorded assumptions and cleaning details.

### Dashboard

- Shows current operational KPIs.
- Filters results by category, warehouse, and date.
- Displays inventory and demand trends.
- Displays the current risk distribution.
- Provides a downloadable priority action queue.

### Product risk

- Selects a product by name.
- Shows probability, inventory, days remaining, supplier lead time, and expected stockout date.
- Explains inventory coverage, demand momentum, reorder status, and promotion status.
- Displays the replenishment recommendation and product history.

### Analytics

- Filters historical data by category, warehouse, season, and promotion.
- Compares stockout patterns across business groups.
- Shows category, warehouse, monthly, seasonal, and promotion-related patterns.

### Model performance

- Compares validation precision, recall, F1, and ROC-AUC.
- Shows the untouched test confusion matrix and ROC curve.
- Lists the most influential fitted-model features.
- Explains how to interpret the results and their limitations.

## 5. System workflow

### User action

The user opens the Data workspace and either keeps the built-in demo or uploads a CSV. For an upload, the user reviews field mappings and selects **Validate and activate**.

### Frontend processing

Streamlit reads the uploaded bytes, previews the headers and data types, collects mapping choices, shows validation messages, and stores the activated results in that browser session.

### Backend processing

The upload module normalizes column names, checks essential fields, converts dates and numbers, supplies documented fallback values, and calls the cleaning and feature-engineering functions.

### Data and model processing

```text
CSV or built-in data
        ↓
Validation and cleaning
        ↓
Rolling demand, inventory coverage, and calendar features
        ↓
Saved Logistic Regression preprocessing and prediction pipeline
        ↓
Seven-day stockout probability
        ↓
Transparent risk and replenishment rules
```

Time-based rolling features use earlier records rather than future information. Model evaluation also uses chronological train, validation, and test periods.

### Final output

The activated features and predictions are shared across all five pages. The user receives filters, charts, product explanations, risk scores, expected dates, recommended units, recommended actions, and downloadable CSV files.

## 6. Technology stack

- **Python:** application logic and pipeline orchestration.
- **Pandas:** CSV parsing, cleaning, transformation, grouping, and feature preparation.
- **NumPy:** numerical work and synthetic data generation.
- **scikit-learn:** preprocessing, model comparison, evaluation, and prediction.
- **Joblib:** persistence of the trained model pipeline.
- **Streamlit:** interactive five-page user interface.
- **Altair:** interactive charts.
- **Matplotlib and Seaborn:** batch EDA figures.
- **SQLite and SQLAlchemy:** local relational storage and example SQL queries.
- **Pytest:** automated unit, integration, upload, and UI checks.

## 7. Project structure

- `streamlit_app.py`: configures the application and top navigation.
- `app_pages/`: contains the five visible pages.
- `app_utils.py`: loads shared data and metrics with caching.
- `state.py`: manages the active dataset for one browser session.
- `ui.py` and `components/`: contain the existing shared presentation code.
- `src/`: contains data generation, validation, cleaning, feature engineering, training, prediction, risk logic, and database code.
- `data/`, `models/`, `reports/`, and `database/`: contain generated artifacts used by the application.
- `tests/`: contains automated checks.
- `run_pipeline.py`: rebuilds the complete set of artifacts in order.

## 8. Installation and setup

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501`.

Optional commands:

```powershell
python -m pytest -q
python run_pipeline.py
```

The first command runs the checks. The second rebuilds the synthetic data, reports, model, predictions, and SQLite database.

## 9. User guide

1. Start on the Dashboard to understand the project and view the current built-in results.
2. Open Data workspace to download the built-in data or add a CSV.
3. For an uploaded file, review every suggested mapping.
4. Map the eight essential fields: date, product ID, category, warehouse, region, current inventory, daily sales, and unit price.
5. If lead time is unavailable, choose the assumption shown by the interface.
6. Select **Validate and activate**.
7. Return to Dashboard and use its filters and priority queue.
8. Open Product risk and select a product for an explanation.
9. Open Analytics for historical patterns.
10. Open Model performance to understand how the model was evaluated.
11. Use the available download buttons to save the built-in data or action plan.

To return to the original data after an upload, select **Restore built-in demo** in Data workspace.

## 10. Limitations

- Synthetic data does not prove performance on a real retailer's operations.
- The saved model is not retrained when a CSV is uploaded.
- Uploaded records remain only in the current browser session.
- Risk thresholds and replenishment rules are reasonable demonstrations, not company-specific policy.
- The database is used by the batch demonstration, not as a live application backend.
- There is no authentication, live ERP connection, scheduled prediction, or alert delivery.

## 11. Future improvements

- Test and retrain the model with real anonymized inventory history.
- Calibrate probabilities and choose thresholds using actual business costs.
- Connect the app to a scheduled inventory data source.
- Monitor data drift and prediction performance over time.
- Add user authentication before handling private company data.

## Interview summary

“SupplyChain Sentinel predicts whether a product may stock out in the next seven days. Pandas cleans inventory and sales history and creates time-aware demand and inventory features. I compared three scikit-learn classifiers using chronological splits and selected Logistic Regression. The saved model returns a stockout probability. A separate Python rules layer turns that probability into a risk score, expected date, replenishment quantity, and action. Streamlit presents the results across five pages and also lets a user validate and score an uploaded CSV.”
