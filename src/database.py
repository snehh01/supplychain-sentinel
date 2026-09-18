"""SQLite persistence layer, designed for an easy PostgreSQL URL swap."""

from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import DATABASE_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_project_directories


def get_engine(database_url: str | None = None) -> Engine:
    ensure_project_directories()
    url = database_url or os.getenv("SUPPLYCHAIN_DATABASE_URL") or f"sqlite:///{DATABASE_DIR / 'supplychain_sentinel.db'}"
    return create_engine(url, future=True)


def build_database(engine: Engine | None = None) -> Engine:
    engine = engine or get_engine()
    products = pd.read_csv(RAW_DATA_DIR / "products.csv")
    daily = pd.read_csv(PROCESSED_DATA_DIR / "supply_chain_clean.csv")
    predictions = pd.read_csv(PROCESSED_DATA_DIR / "latest_predictions.csv")
    products[["product_id", "product_name", "category", "unit_price"]].to_sql("products", engine, if_exists="replace", index=False)
    daily[["date", "product_id", "warehouse", "region", "beginning_inventory", "current_inventory", "inventory_received", "reorder_point", "stockout_event"]].to_sql("daily_inventory", engine, if_exists="replace", index=False, chunksize=2000)
    daily[["date", "product_id", "daily_sales", "units_sold", "lost_sales", "discount", "promotion", "demand_forecast"]].to_sql("daily_sales", engine, if_exists="replace", index=False, chunksize=2000)
    products[["product_id", "category", "nominal_lead_time", "supplier_reliability"]].rename(columns={"nominal_lead_time": "supplier_lead_time"}).to_sql("supplier_information", engine, if_exists="replace", index=False)
    prediction_columns = ["date", "product_id", "stockout_probability", "risk_score", "risk_level", "days_until_stockout", "expected_stockout_date", "units_required"]
    predictions[prediction_columns].to_sql("model_predictions", engine, if_exists="replace", index=False)
    alerts = predictions.loc[predictions["risk_level"].isin(["HIGH", "CRITICAL"]), ["date", "product_id", "risk_level", "urgency", "recommended_action"]]
    alerts.to_sql("stockout_alerts", engine, if_exists="replace", index=False)
    return engine


QUERIES = {
    "highest_risk_products": """SELECT p.product_name, p.category, mp.risk_score, mp.stockout_probability FROM model_predictions mp JOIN products p USING(product_id) ORDER BY mp.risk_score DESC LIMIT 10""",
    "category_stockout_rate": """SELECT p.category, AVG(di.stockout_event) AS stockout_rate FROM daily_inventory di JOIN products p USING(product_id) GROUP BY p.category ORDER BY stockout_rate DESC""",
    "warehouse_stockout_events": """SELECT warehouse, SUM(stockout_event) AS stockout_events FROM daily_inventory GROUP BY warehouse ORDER BY stockout_events DESC""",
    "immediate_replenishment": """SELECT p.product_name, mp.risk_level, mp.units_required, mp.expected_stockout_date FROM model_predictions mp JOIN products p USING(product_id) WHERE mp.risk_level IN ('HIGH','CRITICAL') ORDER BY mp.risk_score DESC""",
    "average_lead_time_by_category": """SELECT category, AVG(supplier_lead_time) AS average_lead_time FROM supplier_information GROUP BY category ORDER BY average_lead_time DESC""",
}


def run_query(name: str, engine: Engine | None = None) -> pd.DataFrame:
    if name not in QUERIES:
        raise KeyError(f"Unknown query: {name}")
    with (engine or get_engine()).connect() as connection:
        return pd.read_sql(text(QUERIES[name]), connection)


def main() -> None:
    engine = build_database()
    for name in QUERIES:
        result = run_query(name, engine)
        print(f"{name}: {len(result)} rows")


if __name__ == "__main__":
    main()

