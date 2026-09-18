# LinkedIn launch post

Stockouts are rarely caused by one number. Inventory, recent demand, promotions, reorder points, and supplier lead time all matter together.

I built **SupplyChain Sentinel** to learn how an ML prediction can become an explainable operational decision—not just a score in a notebook.

The project accepts inventory-history CSV files, validates and maps unfamiliar column names, engineers time-aware features, and predicts whether each product may stock out within seven days. It then converts the probability into a transparent risk score, expected stockout date, and replenishment recommendation.

Technical highlights:

- Leakage-safe rolling features and chronological train/validation/test splits
- Comparison of Logistic Regression, Random Forest, and Gradient Boosting
- A persisted Scikit-learn pipeline connected to a multi-page Streamlit application
- SQLite tables and reusable SQL queries for operational reporting
- Unit, integration, upload-validation, and Streamlit page tests

The selected Logistic Regression model achieved 0.865 recall, 0.649 F1, and 0.871 ROC-AUC on the synthetic test period. I report these as synthetic-data results—not production performance.

The hardest part was preventing future information from entering the model. I solved this by shifting historical features by one day, defining the target only from t+1 through t+7, and splitting by date.

Explore the code: `[ADD_GITHUB_URL]`  
Try the demo: `[ADD_LIVE_DEMO_URL]`

#DataScience #MachineLearning #Python #Streamlit #SupplyChain #PortfolioProject #OpenToWork

## Short alternative

I built **SupplyChain Sentinel**, an end-to-end Python project that predicts seven-day inventory stockout risk and turns model probabilities into explainable replenishment actions.

It includes CSV upload and column mapping, leakage-safe feature engineering, chronological evaluation of three classifiers, saved-model inference, SQLite reporting, a Streamlit dashboard, and automated tests. The selected Logistic Regression reached 0.865 recall and 0.649 F1 on the synthetic test period.

My biggest learning: a useful ML product needs reliable data validation, honest evaluation, and clear decisions—not only a model.

GitHub: `[ADD_GITHUB_URL]` | Demo: `[ADD_LIVE_DEMO_URL]`

#DataScience #MachineLearning #Python #Streamlit #SupplyChain
