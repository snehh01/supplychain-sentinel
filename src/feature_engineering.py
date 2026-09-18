"""Create leakage-safe model features and the seven-day future stockout label."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src.config import PROCESSED_DATA_DIR, REPORTS_DIR, ensure_project_directories


def engineer_features(clean: pd.DataFrame, horizon_days: int = 7) -> pd.DataFrame:
    """Build features using only information available at each row's timestamp."""

    data = clean.sort_values(["product_id", "date"]).copy()
    groups = data.groupby("product_id", group_keys=False)

    # All demand-history features are shifted by one day, preventing same-day/future leakage.
    prior_sales = groups["daily_sales"].shift(1)
    data["sales_rolling_mean_7_days"] = prior_sales.groupby(data["product_id"]).transform(
        lambda series: series.rolling(7, min_periods=3).mean()
    )
    data["sales_rolling_mean_30_days"] = prior_sales.groupby(data["product_id"]).transform(
        lambda series: series.rolling(30, min_periods=7).mean()
    )
    baseline_demand = data["sales_rolling_mean_7_days"].fillna(data["demand_forecast"]).clip(lower=1)
    long_demand = data["sales_rolling_mean_30_days"].fillna(baseline_demand).clip(lower=1)
    data["inventory_to_demand_ratio"] = data["current_inventory"] / baseline_demand
    data["days_of_inventory_remaining"] = data["inventory_to_demand_ratio"]
    data["demand_growth_rate"] = ((baseline_demand - long_demand) / long_demand).clip(-2, 3)
    data["inventory_change"] = groups["current_inventory"].diff().fillna(0)
    data["lead_time_demand"] = baseline_demand * data["supplier_lead_time"]
    data["safety_stock_gap"] = data["current_inventory"] - data["lead_time_demand"]
    data["reorder_risk"] = (data["current_inventory"] <= data["reorder_point"]).astype(int)

    prior_promo_sales = prior_sales.where(groups["promotion"].shift(1).eq(1))
    prior_regular_sales = prior_sales.where(groups["promotion"].shift(1).eq(0))
    promo_mean = prior_promo_sales.groupby(data["product_id"]).transform(lambda s: s.expanding().mean())
    regular_mean = prior_regular_sales.groupby(data["product_id"]).transform(lambda s: s.expanding().mean())
    data["promotion_demand_change"] = ((promo_mean - regular_mean) / regular_mean.clip(lower=1)).fillna(0).clip(-2, 4)

    prior_stockouts = groups["stockout_event"].shift(1)
    data["historical_stockout_rate"] = prior_stockouts.groupby(data["product_id"]).transform(
        lambda series: series.expanding(min_periods=1).mean()
    ).fillna(0)

    # Future target uses t+1 through t+7. Rows lacking a complete horizon are excluded.
    future_columns = [groups["stockout_event"].shift(-offset) for offset in range(1, horizon_days + 1)]
    future_frame = pd.concat(future_columns, axis=1)
    data["stockout_within_next_7_days"] = future_frame.max(axis=1).astype("Int64")
    incomplete_horizon = groups.cumcount(ascending=False) < horizon_days
    data.loc[incomplete_horizon, "stockout_within_next_7_days"] = pd.NA

    numeric_fill_columns = ["sales_rolling_mean_7_days", "sales_rolling_mean_30_days"]
    data[numeric_fill_columns] = data[numeric_fill_columns].fillna(data["demand_forecast"])
    return data


def main() -> None:
    ensure_project_directories()
    clean = pd.read_csv(PROCESSED_DATA_DIR / "supply_chain_clean.csv", parse_dates=["date"])
    featured = engineer_features(clean)
    output = PROCESSED_DATA_DIR / "supply_chain_features.csv"
    featured.to_csv(output, index=False)
    summary = {
        "rows": len(featured),
        "labeled_rows": int(featured["stockout_within_next_7_days"].notna().sum()),
        "positive_label_rate": round(float(featured["stockout_within_next_7_days"].dropna().mean()), 4),
        "horizon_days": 7,
        "leakage_controls": [
            "rolling sales and historical stockout features shifted by one day",
            "chronological splitting required by training pipeline",
            "last seven observations per product left unlabeled",
            "stockout_event excluded from model predictors",
        ],
    }
    (REPORTS_DIR / "metrics" / "feature_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

