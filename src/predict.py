"""Score the latest product state and create actionable inventory decisions."""

from __future__ import annotations

import json

import joblib
import pandas as pd

from src.config import MODELS_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, ensure_project_directories
from src.risk_engine import decision_as_dict
from src.train_model import FEATURES


def score_latest_products(data: pd.DataFrame) -> pd.DataFrame:
    model = joblib.load(MODELS_DIR / "stockout_model.joblib")
    latest = data.sort_values("date").groupby("product_id", as_index=False).tail(1).copy()
    latest["stockout_probability"] = model.predict_proba(latest[FEATURES])[:, 1]
    decisions = latest.apply(
        lambda row: decision_as_dict(
            as_of_date=pd.Timestamp(row["date"]).date(), probability=row["stockout_probability"],
            current_inventory=row["current_inventory"], average_daily_demand=row["sales_rolling_mean_7_days"],
            supplier_lead_time=row["supplier_lead_time"], demand_growth_rate=row["demand_growth_rate"],
        ), axis=1, result_type="expand"
    )
    return pd.concat([latest.reset_index(drop=True), decisions.reset_index(drop=True)], axis=1)


def main() -> None:
    ensure_project_directories()
    data = pd.read_csv(PROCESSED_DATA_DIR / "supply_chain_features.csv", parse_dates=["date"])
    scored = score_latest_products(data)
    path = PROCESSED_DATA_DIR / "latest_predictions.csv"
    scored.to_csv(path, index=False)
    summary = {
        "products_scored": len(scored),
        "high_or_critical": int(scored["risk_level"].isin(["HIGH", "CRITICAL"]).sum()),
        "predicted_stockouts_at_0_5": int((scored["stockout_probability"] >= 0.5).sum()),
        "average_risk_score": round(float(scored["risk_score"].mean()), 1),
    }
    (REPORTS_DIR / "metrics" / "prediction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

