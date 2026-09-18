"""Clean raw operational data with an auditable decision log."""

from __future__ import annotations

import json
import logging

import numpy as np
import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, REPORTS_DIR, ensure_project_directories

LOGGER = logging.getLogger(__name__)


def clean_supply_chain_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Clean raw rows while recording each mutation and its rationale."""

    data = raw.copy()
    report: dict[str, object] = {"input_rows": len(data), "decisions": []}
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    invalid_dates = int(data["date"].isna().sum())
    if invalid_dates:
        data = data.loc[data["date"].notna()].copy()
    report["decisions"].append({
        "issue": "unparseable_dates", "affected_rows": invalid_dates,
        "action": "removed because time order cannot be recovered safely",
    })

    duplicates = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()
    report["decisions"].append({
        "issue": "exact_duplicate_rows", "affected_rows": duplicates,
        "action": "kept first exact record to prevent double-counting",
    })

    negative_inventory = int((data["current_inventory"] < 0).sum())
    expected_ending = (data["beginning_inventory"] - data["units_sold"]).clip(lower=0)
    data.loc[data["current_inventory"] < 0, "current_inventory"] = expected_ending
    report["decisions"].append({
        "issue": "negative_current_inventory", "affected_rows": negative_inventory,
        "action": "reconstructed from beginning inventory minus units sold",
    })

    lead_time_missing = int(data["supplier_lead_time"].isna().sum())
    medians = data.groupby(["category", "warehouse"])["supplier_lead_time"].transform("median")
    data["supplier_lead_time"] = data["supplier_lead_time"].fillna(medians).fillna(data["supplier_lead_time"].median())
    data["supplier_lead_time"] = data["supplier_lead_time"].round().astype(int)
    report["decisions"].append({
        "issue": "missing_supplier_lead_time", "affected_rows": lead_time_missing,
        "action": "imputed category-warehouse median, then global median fallback",
    })

    nonnegative_columns = [
        "beginning_inventory", "current_inventory", "daily_sales", "units_sold",
        "lost_sales", "inventory_received", "reorder_point", "unit_price", "demand_forecast",
    ]
    invalid_nonnegative = int((data[nonnegative_columns] < 0).sum().sum())
    data[nonnegative_columns] = data[nonnegative_columns].clip(lower=0)
    report["decisions"].append({
        "issue": "other_negative_operational_values", "affected_cells": invalid_nonnegative,
        "action": "clipped to zero where negative values are not logically valid",
    })

    # Preserve genuine demand spikes; cap only impossible/extreme sensor values by product.
    demand_cap = data.groupby("product_id")["daily_sales"].transform(lambda series: series.quantile(0.999))
    demand_outliers = int((data["daily_sales"] > demand_cap).sum())
    data["daily_sales"] = np.minimum(data["daily_sales"], np.ceil(demand_cap)).astype(int)
    data["units_sold"] = np.minimum(data["units_sold"], data["daily_sales"]).astype(int)
    data["lost_sales"] = (data["daily_sales"] - data["units_sold"]).clip(lower=0)
    report["decisions"].append({
        "issue": "extreme_daily_sales", "affected_rows": demand_outliers,
        "action": "winsorized within product at 99.9th percentile; seasonal peaks retained",
    })

    data = data.sort_values(["product_id", "date"], ignore_index=True)
    report["output_rows"] = len(data)
    report["rows_removed"] = int(report["input_rows"] - len(data))
    report["remaining_missing_values"] = int(data.isna().sum().sum())
    return data, report


def main() -> None:
    ensure_project_directories()
    raw = pd.read_csv(RAW_DATA_DIR / "supply_chain_daily.csv")
    clean, report = clean_supply_chain_data(raw)
    clean.to_csv(PROCESSED_DATA_DIR / "supply_chain_clean.csv", index=False)
    (REPORTS_DIR / "metrics" / "cleaning_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    LOGGER.info("Cleaned %s rows into %s rows", len(raw), len(clean))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()

