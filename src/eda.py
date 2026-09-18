"""Business-focused exploratory analysis with computed, non-hardcoded findings."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import PROCESSED_DATA_DIR, REPORTS_DIR, ensure_project_directories


def run_eda(data: pd.DataFrame) -> dict[str, object]:
    ensure_project_directories()
    figures = REPORTS_DIR / "figures"
    sns.set_theme(style="whitegrid")

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    sns.histplot(data=data, x="current_inventory", bins=40, ax=axes[0, 0])
    axes[0, 0].set_title("How is current inventory distributed?")
    sns.histplot(data=data, x="daily_sales", bins=40, ax=axes[0, 1])
    axes[0, 1].set_title("How variable is daily demand?")
    category_demand = data.groupby("category", as_index=False)["daily_sales"].mean().sort_values("daily_sales")
    sns.barplot(data=category_demand, x="daily_sales", y="category", ax=axes[1, 0])
    axes[1, 0].set_title("Which categories have the highest average demand?")
    monthly = data.groupby("date", as_index=False)["current_inventory"].mean()
    sns.lineplot(data=monthly, x="date", y="current_inventory", ax=axes[1, 1])
    axes[1, 1].set_title("How does average inventory change over time?")
    fig.tight_layout()
    fig.savefig(figures / "data_understanding.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    corr_columns = ["current_inventory", "daily_sales", "supplier_lead_time", "reorder_point", "discount", "demand_forecast", "stockout_event"]
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(data[corr_columns].corr(), annot=True, fmt=".2f", cmap="vlag", center=0, ax=ax)
    ax.set_title("Which numeric factors move with stockouts?")
    fig.tight_layout()
    fig.savefig(figures / "correlation_heatmap.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    category_risk = data.groupby("category")["stockout_event"].mean().sort_values(ascending=False)
    warehouse_risk = data.groupby("warehouse")["stockout_event"].mean().sort_values(ascending=False)
    promotion_risk = data.groupby("promotion")["stockout_event"].mean()
    season_risk = data.groupby("season")["stockout_event"].mean().sort_values(ascending=False)
    product_events = data.groupby(["product_id", "product_name"])["stockout_event"].sum().sort_values(ascending=False)
    lead_time_bins = pd.qcut(data["supplier_lead_time"], q=4, duplicates="drop")
    lead_time_risk = data.groupby(lead_time_bins, observed=True)["stockout_event"].mean()

    insights = {
        "shape": [int(data.shape[0]), int(data.shape[1])],
        "duplicate_rows": int(data.duplicated().sum()),
        "missing_values": int(data.isna().sum().sum()),
        "top_stockout_products": [
            {"product_id": idx[0], "product_name": idx[1], "events": int(value)}
            for idx, value in product_events.head(10).items()
        ],
        "highest_risk_category": {"name": category_risk.index[0], "rate": round(float(category_risk.iloc[0]), 4)},
        "highest_risk_warehouse": {"name": warehouse_risk.index[0], "rate": round(float(warehouse_risk.iloc[0]), 4)},
        "promotion_stockout_rates": {str(int(k)): round(float(v), 4) for k, v in promotion_risk.items()},
        "promotion_risk_lift": round(float(promotion_risk.get(1, 0) / max(promotion_risk.get(0, 0), 1e-9)), 2),
        "highest_risk_season": {"name": season_risk.index[0], "rate": round(float(season_risk.iloc[0]), 4)},
        "lead_time_quartile_stockout_rates": {str(k): round(float(v), 4) for k, v in lead_time_risk.items()},
        "inventory_demand_correlation": round(float(data["current_inventory"].corr(data["daily_sales"])), 3),
    }
    (REPORTS_DIR / "metrics" / "eda_insights.json").write_text(json.dumps(insights, indent=2), encoding="utf-8")
    return insights


def main() -> None:
    data = pd.read_csv(PROCESSED_DATA_DIR / "supply_chain_clean.csv", parse_dates=["date"])
    print(json.dumps(run_eda(data), indent=2))


if __name__ == "__main__":
    main()

