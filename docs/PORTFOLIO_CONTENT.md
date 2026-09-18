# SupplyChain Sentinel

## Portfolio summary

An end-to-end inventory decision system that predicts seven-day product stockout risk, explains operational drivers, and converts model probabilities into replenishment actions.

## Problem

Retail planners need to identify products likely to run out before replenishment arrives. Reviewing inventory, demand, promotions, and supplier timing manually is slow and inconsistent.

## Solution

SupplyChain Sentinel creates or accepts daily inventory history, validates and cleans it, builds time-aware features, scores each product with a trained classifier, and produces a prioritized action plan through a Streamlit application.

## My contribution

- Designed the synthetic supply-chain simulation and its auditable quality issues.
- Built cleaning, leakage-safe feature engineering, chronological model evaluation, inference, and deterministic risk logic.
- Added SQLite persistence, reusable SQL analysis, CSV upload with column mapping, session-based dataset activation, and a five-page Streamlit interface.
- Added unit, integration, and Streamlit page tests plus reproducible documentation.

## Main features

- User CSV upload with alias detection, explicit field mapping, validation, and a 10 MB safety limit.
- Seven-day stockout probability from a persisted Scikit-learn pipeline.
- Transparent 0–100 operational risk score and deterministic replenishment quantity.
- Filters, product-level explanations, analytics, model evaluation, and downloadable action plan.
- Reproducible synthetic data pipeline and normalized SQLite reporting tables.

## Technical approach and architecture

`CSV/simulator → validation → cleaning → shifted rolling features → chronological model comparison → saved classifier → probability → rule-based risk/action → SQLite + Streamlit`

The ML model estimates future stockout probability. A separate documented rule combines that probability with inventory coverage, lead-time pressure, and demand growth. Recommendations are rules, not ML-generated text.

## Verified outcome

The selected Logistic Regression model achieved 0.865 recall, 0.649 F1, and 0.871 ROC-AUC on the untouched chronological test period. The generated dataset contains 36,500 cleaned daily observations across 100 products. These are synthetic-data results, not production impact claims.

## Challenges and solutions

- **Target leakage:** future labels use days t+1 to t+7; rolling and stockout-history features are shifted.
- **Unfamiliar user schemas:** common aliases are suggested and every required field can be mapped explicitly.
- **Probability is not a decision:** a bounded, documented risk formula produces urgency and replenishment guidance.

## Technologies

Python, Pandas, NumPy, Scikit-learn, SQLAlchemy, SQLite, Streamlit, Altair, Joblib, Pytest.

## Links

- GitHub: `[ADD_GITHUB_URL]`
- Live demo: `[ADD_LIVE_DEMO_URL]`

## Suggested screenshots

1. Dashboard with KPIs and priority queue.
2. Data workspace mapping an uploaded CSV.
3. Product risk explanation and recommended action.
4. Model comparison and confusion matrix.

## Concise case study

I built SupplyChain Sentinel to move beyond a notebook-only classifier. The system simulates realistic inventory operations, cleans known defects, builds time-aware features, compares three classifiers chronologically, and serves actual saved-model predictions. Logistic Regression was selected using validation F1 and recall, then reached 0.649 F1 and 0.865 recall on the test period. A transparent rules layer turns probability into an action queue that users can filter, inspect, and download. Its main limitation is that evaluation uses synthetic rather than real retailer data.
