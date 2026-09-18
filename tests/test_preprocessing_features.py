import pandas as pd

from src.data_preprocessing import clean_supply_chain_data
from src.feature_engineering import engineer_features


def _sample() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=14)
    return pd.DataFrame({
        "date": dates, "product_id": "P1", "product_name": "Item", "category": "Grocery",
        "warehouse": "Mumbai DC", "region": "West", "beginning_inventory": 20,
        "current_inventory": [10] * 14, "daily_sales": range(1, 15), "units_sold": range(1, 15),
        "lost_sales": 0, "inventory_received": 0, "supplier_lead_time": 5,
        "reorder_point": 25, "unit_price": 10.0, "discount": 0.0, "promotion": 0,
        "day_of_week": [d.day_name() for d in dates], "month": 1, "season": "Winter",
        "demand_forecast": range(1, 15), "stockout_event": [0] * 10 + [1, 0, 0, 0],
    })


def test_cleaner_repairs_known_raw_issues() -> None:
    raw = _sample()
    raw.loc[0, "current_inventory"] = -10
    raw.loc[1, "supplier_lead_time"] = None
    raw = pd.concat([raw, raw.iloc[[2]]], ignore_index=True)
    clean, report = clean_supply_chain_data(raw)
    assert not clean.duplicated().any()
    assert (clean["current_inventory"] >= 0).all()
    assert clean["supplier_lead_time"].notna().all()
    assert report["rows_removed"] == 1


def test_target_looks_forward_and_not_at_current_day() -> None:
    featured = engineer_features(_sample(), horizon_days=2)
    assert featured.loc[8, "stockout_within_next_7_days"] == 1
    assert featured.loc[10, "stockout_within_next_7_days"] == 0
    assert pd.isna(featured.loc[13, "stockout_within_next_7_days"])
