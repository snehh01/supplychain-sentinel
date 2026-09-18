"""Validate generated raw data and emit a machine-readable quality report."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_DIR, REPORTS_DIR, ensure_project_directories

REQUIRED_COLUMNS = {
    "date", "product_id", "product_name", "category", "warehouse", "region",
    "beginning_inventory", "current_inventory", "daily_sales", "units_sold",
    "lost_sales", "inventory_received", "supplier_lead_time", "reorder_point",
    "unit_price", "discount", "promotion", "day_of_week", "month", "season",
    "demand_forecast", "stockout_event",
}


def build_validation_report(data: pd.DataFrame) -> dict[str, object]:
    missing_columns = sorted(REQUIRED_COLUMNS - set(data.columns))
    duplicate_count = int(data.duplicated().sum())
    negative_inventory_count = int((data["current_inventory"] < 0).sum())
    invalid_sales_count = int((data["units_sold"] > data["beginning_inventory"]).sum())
    invalid_discount_count = int((~data["discount"].between(0, 1)).sum())
    stockout_rate = float(data["stockout_event"].mean())
    missing_values = {key: int(value) for key, value in data.isna().sum().items() if value}
    checks = {
        "required_columns_present": not missing_columns,
        "record_count_in_requested_range": 20_000 <= len(data) <= 50_000,
        "product_count_in_requested_range": 50 <= data["product_id"].nunique() <= 150,
        "date_order_parseable": bool(pd.to_datetime(data["date"], errors="coerce").notna().all()),
        "stockout_target_has_both_classes": data["stockout_event"].nunique() == 2,
        "units_sold_respects_available_inventory": invalid_sales_count == 0,
        "discount_in_valid_range": invalid_discount_count == 0,
    }
    return {
        "status": "PASS_WITH_EXPECTED_RAW_QUALITY_ISSUES" if all(checks.values()) else "FAIL",
        "shape": {"rows": len(data), "columns": len(data.columns)},
        "unique_products": int(data["product_id"].nunique()),
        "date_range": {
            "start": str(pd.to_datetime(data["date"]).min().date()),
            "end": str(pd.to_datetime(data["date"]).max().date()),
        },
        "stockout_rate": round(stockout_rate, 4),
        "missing_columns": missing_columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_count,
        "negative_inventory_rows": negative_inventory_count,
        "invalid_units_sold_rows": invalid_sales_count,
        "invalid_discount_rows": invalid_discount_count,
        "checks": checks,
    }


def main() -> None:
    ensure_project_directories()
    input_path = RAW_DATA_DIR / "supply_chain_daily.csv"
    if not input_path.exists():
        raise FileNotFoundError(f"Generate the dataset first: {input_path}")
    data = pd.read_csv(input_path)
    report = build_validation_report(data)
    output_path = REPORTS_DIR / "metrics" / "raw_data_validation.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

