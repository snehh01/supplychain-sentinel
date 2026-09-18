"""Tests for deterministic and logically consistent synthetic data."""

from dataclasses import replace

import pandas as pd

from src.config import DEFAULT_GENERATION_CONFIG
from src.data_generation import generate_supply_chain_data
from src.validate_data import build_validation_report


def test_generation_is_reproducible() -> None:
    config = replace(DEFAULT_GENERATION_CONFIG, number_of_products=3, number_of_days=20, inject_quality_issues=False)
    first, first_products = generate_supply_chain_data(config)
    second, second_products = generate_supply_chain_data(config)
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(first_products, second_products)


def test_inventory_flow_and_sales_constraints() -> None:
    config = replace(DEFAULT_GENERATION_CONFIG, number_of_products=4, number_of_days=50, inject_quality_issues=False)
    daily, _ = generate_supply_chain_data(config)
    assert (daily["units_sold"] <= daily["beginning_inventory"]).all()
    assert (daily["current_inventory"] == daily["beginning_inventory"] - daily["units_sold"]).all()
    assert (daily["lost_sales"] == daily["daily_sales"] - daily["units_sold"]).all()


def test_validation_accepts_requested_shape() -> None:
    config = replace(DEFAULT_GENERATION_CONFIG, inject_quality_issues=False)
    daily, _ = generate_supply_chain_data(config)
    report = build_validation_report(daily)
    assert all(report["checks"].values())

