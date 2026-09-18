"""Train, compare, select, and persist stockout classifiers."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import MODELS_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, ensure_project_directories

TARGET = "stockout_within_next_7_days"
NUMERIC_FEATURES = [
    "current_inventory", "daily_sales", "units_sold", "inventory_received", "supplier_lead_time",
    "reorder_point", "unit_price", "discount", "promotion", "month", "demand_forecast",
    "inventory_to_demand_ratio", "days_of_inventory_remaining", "sales_rolling_mean_7_days",
    "sales_rolling_mean_30_days", "demand_growth_rate", "inventory_change", "lead_time_demand",
    "safety_stock_gap", "reorder_risk", "promotion_demand_change", "historical_stockout_rate",
]
CATEGORICAL_FEATURES = ["category", "warehouse", "region", "day_of_week", "season"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def _preprocessor(scale_numeric: bool = False) -> ColumnTransformer:
    numeric_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scale", StandardScaler()))
    return ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), NUMERIC_FEATURES),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
    ])


def _metrics(y_true: pd.Series, probability: np.ndarray, threshold: float = 0.5) -> dict[str, object]:
    prediction = (probability >= threshold).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_true, prediction)), 4),
        "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, prediction, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probability)), 4),
        "confusion_matrix": confusion_matrix(y_true, prediction).tolist(),
        "threshold": threshold,
    }


def train_and_evaluate(data: pd.DataFrame) -> dict[str, object]:
    ensure_project_directories()
    labeled = data.loc[data[TARGET].notna()].copy()
    labeled[TARGET] = labeled[TARGET].astype(int)
    dates = sorted(labeled["date"].unique())
    train_end = dates[int(len(dates) * 0.70)]
    validation_end = dates[int(len(dates) * 0.85)]
    train = labeled[labeled["date"] < train_end]
    validation = labeled[(labeled["date"] >= train_end) & (labeled["date"] < validation_end)]
    test = labeled[labeled["date"] >= validation_end]

    models = {
        "Logistic Regression": Pipeline([("preprocess", _preprocessor(True)), ("model", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42))]),
        "Random Forest": Pipeline([("preprocess", _preprocessor()), ("model", RandomForestClassifier(n_estimators=250, min_samples_leaf=3, class_weight="balanced_subsample", n_jobs=-1, random_state=42))]),
        "Gradient Boosting": Pipeline([("preprocess", _preprocessor()), ("model", GradientBoostingClassifier(n_estimators=180, learning_rate=0.05, max_depth=3, random_state=42))]),
    }
    validation_results: dict[str, object] = {}
    fitted: dict[str, Pipeline] = {}
    for name, model in models.items():
        model.fit(train[FEATURES], train[TARGET])
        probability = model.predict_proba(validation[FEATURES])[:, 1]
        validation_results[name] = _metrics(validation[TARGET], probability)
        fitted[name] = model

    selected_name = max(validation_results, key=lambda name: (validation_results[name]["f1"], validation_results[name]["recall"]))
    selected = fitted[selected_name]
    test_probability = selected.predict_proba(test[FEATURES])[:, 1]
    test_metrics = _metrics(test[TARGET], test_probability)

    false_positive_rate, true_positive_rate, _ = roc_curve(test[TARGET], test_probability)
    transformed_names = selected.named_steps["preprocess"].get_feature_names_out()
    estimator = selected.named_steps["model"]
    importance = getattr(estimator, "feature_importances_", None)
    if importance is None:
        importance = np.abs(estimator.coef_[0])
    top_features = sorted(
        ({"feature": str(name).replace("numeric__", "").replace("categorical__", ""), "importance": float(value)} for name, value in zip(transformed_names, importance)),
        key=lambda item: item["importance"], reverse=True,
    )[:20]

    joblib.dump(selected, MODELS_DIR / "stockout_model.joblib")
    report = {
        "selected_model": selected_name,
        "selection_rule": "highest validation F1; validation recall breaks ties",
        "split": {"train_end_exclusive": str(pd.Timestamp(train_end).date()), "validation_end_exclusive": str(pd.Timestamp(validation_end).date()), "train_rows": len(train), "validation_rows": len(validation), "test_rows": len(test)},
        "validation_model_comparison": validation_results,
        "test_metrics": test_metrics,
        "test_roc_curve": {"false_positive_rate": false_positive_rate.tolist(), "true_positive_rate": true_positive_rate.tolist()},
        "top_features": top_features,
        "feature_columns": FEATURES,
    }
    (REPORTS_DIR / "metrics" / "model_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    data = pd.read_csv(PROCESSED_DATA_DIR / "supply_chain_features.csv", parse_dates=["date"])
    report = train_and_evaluate(data)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

