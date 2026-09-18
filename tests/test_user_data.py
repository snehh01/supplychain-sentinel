from pathlib import Path

import pandas as pd
import pytest

from src.user_data import prepare_uploaded_csv, suggest_column_mapping


ROOT = Path(__file__).resolve().parents[1]


def test_bundled_data_can_be_uploaded_and_featured() -> None:
    sample = pd.read_csv(ROOT / "data" / "processed" / "supply_chain_clean.csv").head(1000)
    features, report = prepare_uploaded_csv(sample.to_csv(index=False).encode())
    assert len(features) == 1000
    assert "days_of_inventory_remaining" in features
    assert report["products"] > 0


def test_upload_reports_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="Missing required columns"):
        prepare_uploaded_csv(b"date,product_id\n2024-01-01,P1\n")


def test_common_supply_chain_aliases_are_suggested() -> None:
    mapping = suggest_column_mapping(["Date", "SKU", "Stock_On_Hand", "Demand", "Lead_Days"])
    assert mapping["product_id"] == "SKU"
    assert mapping["current_inventory"] == "Stock_On_Hand"
    assert mapping["daily_sales"] == "Demand"
    assert mapping["supplier_lead_time"] == "Lead_Days"


def test_alias_mapped_upload_without_optional_columns_is_processed() -> None:
    sample = pd.read_csv(ROOT / "data" / "processed" / "supply_chain_clean.csv").head(50)
    required = {
        "date": "Date", "product_id": "SKU", "product_name": "Item_Name",
        "category": "Department", "warehouse": "Location", "region": "Market",
        "current_inventory": "Stock_On_Hand", "daily_sales": "Demand",
        "supplier_lead_time": "Lead_Days", "reorder_point": "ROP", "unit_price": "Price",
    }
    renamed = sample[list(required)].rename(columns=required)
    mapping = {target: source for target, source in required.items()}
    features, report = prepare_uploaded_csv(renamed.to_csv(index=False).encode(), column_mapping=mapping)
    assert len(features) == 50
    assert report["optional_columns_supplied"] == []
    assert {"promotion", "demand_forecast", "stockout_event"} <= set(features.columns)


def test_upload_rejects_invalid_date() -> None:
    sample = pd.read_csv(ROOT / "data" / "processed" / "supply_chain_clean.csv").head(10)
    sample.loc[0, "date"] = "not-a-date"
    with pytest.raises(ValueError, match="invalid date"):
        prepare_uploaded_csv(sample.to_csv(index=False).encode())


def test_kaggle_style_core_columns_activate_with_recorded_assumptions() -> None:
    sample = pd.read_csv(ROOT / "data" / "processed" / "supply_chain_clean.csv").head(50)
    kaggle = sample[["date", "product_id", "category", "warehouse", "region", "current_inventory", "daily_sales", "unit_price"]].rename(
        columns={
            "date": "Date", "product_id": "Product ID", "warehouse": "Store ID",
            "current_inventory": "Inventory Level", "daily_sales": "Units Sold", "unit_price": "Price",
        }
    )
    mapping = {
        "date": "Date", "product_id": "Product ID", "category": "category",
        "warehouse": "Store ID", "region": "region", "current_inventory": "Inventory Level",
        "daily_sales": "Units Sold", "unit_price": "Price",
    }
    features, report = prepare_uploaded_csv(
        kaggle.to_csv(index=False).encode(), column_mapping=mapping, default_lead_time_days=9
    )
    assert len(features) == 50
    assert (features["supplier_lead_time"] == 9).all()
    assert (features["product_name"] == features["product_id"]).all()
    assert len(report["assumptions"]) == 3
