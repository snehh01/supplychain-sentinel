"""Generate a realistic, reproducible retail supply-chain dataset.

Demand is driven by product/category baselines, weekends, annual seasonality,
promotions, price discounts, trends, and autocorrelated demand shocks. Inventory
evolves through sales and lead-time-delayed replenishment rather than being drawn
independently. A small set of known data-quality defects is injected into the raw
export so that the cleaning pipeline has realistic work to perform.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    DEFAULT_GENERATION_CONFIG,
    RAW_DATA_DIR,
    DataGenerationConfig,
    ensure_project_directories,
)

LOGGER = logging.getLogger(__name__)

CATEGORY_CONFIG = {
    "Electronics": (34, 1.35, 85, 420),
    "Home & Kitchen": (25, 1.15, 32, 190),
    "Beauty": (42, 1.05, 12, 85),
    "Sports": (29, 1.25, 20, 150),
    "Grocery": (58, 0.95, 4, 28),
    "Fashion": (37, 1.30, 18, 120),
}

CATEGORY_PRODUCTS = {
    "Electronics": ["Wireless Headphones", "Smart Speaker", "Power Bank", "Fitness Tracker"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Storage Set"],
    "Beauty": ["Face Serum", "Shampoo", "Body Lotion", "Makeup Kit"],
    "Sports": ["Yoga Mat", "Running Shoes", "Dumbbell Set", "Water Bottle"],
    "Grocery": ["Organic Coffee", "Protein Bar", "Breakfast Cereal", "Olive Oil"],
    "Fashion": ["Cotton T-Shirt", "Denim Jeans", "Winter Jacket", "Backpack"],
}

WAREHOUSE_REGIONS = {
    "Mumbai DC": "West",
    "Delhi DC": "North",
    "Bengaluru DC": "South",
    "Kolkata DC": "East",
}


def _make_product_catalog(config: DataGenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    categories = np.array(list(CATEGORY_CONFIG))
    category_choices = rng.choice(categories, config.number_of_products, p=[0.18, 0.17, 0.17, 0.15, 0.18, 0.15])
    warehouses = np.array(list(WAREHOUSE_REGIONS))
    rows: list[dict[str, object]] = []
    name_counts: dict[str, int] = {}

    for index, category in enumerate(category_choices, start=1):
        base_demand, _, low_price, high_price = CATEGORY_CONFIG[str(category)]
        root_name = str(rng.choice(CATEGORY_PRODUCTS[str(category)]))
        name_counts[root_name] = name_counts.get(root_name, 0) + 1
        warehouse = str(rng.choice(warehouses, p=[0.30, 0.25, 0.28, 0.17]))
        supplier_reliability = float(rng.beta(12, 3))
        nominal_lead_time = int(rng.integers(4, 15))
        product_demand = max(8.0, float(base_demand * rng.lognormal(0, 0.30)))
        reorder_point = int(np.ceil(product_demand * (nominal_lead_time + rng.integers(2, 6))))
        rows.append(
            {
                "product_id": f"P{index:04d}",
                "product_name": f"{root_name} {name_counts[root_name]}",
                "category": str(category),
                "warehouse": warehouse,
                "region": WAREHOUSE_REGIONS[warehouse],
                "base_daily_demand": round(product_demand, 2),
                "unit_price": round(float(rng.uniform(low_price, high_price)), 2),
                "nominal_lead_time": nominal_lead_time,
                "supplier_reliability": round(supplier_reliability, 4),
                "reorder_point": reorder_point,
            }
        )
    return pd.DataFrame(rows)


def _seasonal_multiplier(category: str, month: int) -> float:
    if category == "Electronics":
        return 1.40 if month in (10, 11, 12) else 1.0
    if category == "Fashion":
        return 1.35 if month in (10, 11, 12) else (0.88 if month in (4, 5, 6) else 1.0)
    if category == "Sports":
        return 1.28 if month in (1, 2, 6, 7) else 1.0
    if category == "Beauty":
        return 1.18 if month in (2, 10, 11, 12) else 1.0
    if category == "Grocery":
        return 1.14 if month in (10, 11, 12) else 1.0
    return 1.12 if month in (10, 11, 12) else 1.0


def _season_name(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def generate_supply_chain_data(config: DataGenerationConfig = DEFAULT_GENERATION_CONFIG) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return daily operational records and the product catalog."""

    rng = np.random.default_rng(config.random_seed)
    products = _make_product_catalog(config, rng)
    dates = pd.date_range(config.start_date, periods=config.number_of_days, freq="D")
    records: list[dict[str, object]] = []

    for product in products.itertuples(index=False):
        inventory = int(np.ceil(product.base_daily_demand * rng.uniform(12, 24)))
        open_orders: list[tuple[pd.Timestamp, int]] = []
        demand_shock = 1.0
        recent_demand: list[int] = []

        for day_number, date in enumerate(dates):
            received = sum(quantity for arrival, quantity in open_orders if arrival == date)
            open_orders = [(arrival, quantity) for arrival, quantity in open_orders if arrival > date]
            inventory += received

            promotion = bool(rng.random() < (0.09 if date.month in (10, 11, 12) else 0.055))
            discount = float(rng.choice([0.10, 0.15, 0.20, 0.25])) if promotion else 0.0
            weekend_factor = 1.18 if date.dayofweek >= 5 else 1.0
            seasonal_factor = _seasonal_multiplier(product.category, date.month)
            trend_factor = 1.0 + rng.uniform(-0.00025, 0.00055) * day_number
            demand_shock = float(np.clip(0.72 * demand_shock + 0.28 * rng.lognormal(0, 0.16), 0.65, 1.55))
            promotion_factor = 1.0 + (discount * rng.uniform(1.5, 2.4) if promotion else 0.0)
            expected_demand = max(
                1.0,
                product.base_daily_demand * weekend_factor * seasonal_factor * trend_factor * demand_shock * promotion_factor,
            )
            daily_sales = int(rng.poisson(expected_demand))
            beginning_inventory = inventory
            units_sold = min(daily_sales, beginning_inventory)
            lost_sales = max(0, daily_sales - units_sold)
            stockout_event = int(lost_sales > 0 or (daily_sales > 0 and beginning_inventory == 0))
            inventory = max(0, beginning_inventory - units_sold)
            recent_demand.append(daily_sales)
            recent_demand = recent_demand[-14:]

            delay_probability = 1.0 - product.supplier_reliability
            supplier_lead_time = int(product.nominal_lead_time + (rng.integers(2, 7) if rng.random() < delay_probability else 0))
            inventory_position = inventory + sum(quantity for _, quantity in open_orders)
            if inventory_position <= product.reorder_point and not open_orders:
                target_stock = int(np.ceil(np.mean(recent_demand) * (supplier_lead_time + rng.integers(10, 18))))
                order_quantity = max(product.reorder_point, target_stock - inventory)
                open_orders.append((date + pd.offsets.Day(int(supplier_lead_time)), order_quantity))

            forecast_noise = rng.normal(0, max(1.0, expected_demand * 0.08))
            demand_forecast = max(0.0, expected_demand + forecast_noise)
            records.append(
                {
                    "date": date,
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "category": product.category,
                    "warehouse": product.warehouse,
                    "region": product.region,
                    "beginning_inventory": beginning_inventory,
                    "current_inventory": inventory,
                    "daily_sales": daily_sales,
                    "units_sold": units_sold,
                    "lost_sales": lost_sales,
                    "inventory_received": received,
                    "supplier_lead_time": supplier_lead_time,
                    "reorder_point": product.reorder_point,
                    "unit_price": product.unit_price,
                    "discount": discount,
                    "promotion": int(promotion),
                    "day_of_week": date.day_name(),
                    "month": date.month,
                    "season": _season_name(date.month),
                    "demand_forecast": round(demand_forecast, 2),
                    "stockout_event": stockout_event,
                }
            )

    daily = pd.DataFrame.from_records(records).sort_values(["product_id", "date"], ignore_index=True)
    if config.inject_quality_issues:
        daily = inject_raw_data_quality_issues(daily, rng)
    return daily, products


def inject_raw_data_quality_issues(data: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Inject controlled issues documented in the generated metadata."""

    raw = data.copy()
    missing_count = max(1, round(len(raw) * 0.003))
    missing_indices = rng.choice(raw.index, size=missing_count, replace=False)
    raw.loc[missing_indices, "supplier_lead_time"] = np.nan

    negative_count = max(1, round(len(raw) * 0.001))
    candidate_indices = raw.index[raw["current_inventory"] > 0]
    negative_indices = rng.choice(candidate_indices, size=negative_count, replace=False)
    raw.loc[negative_indices, "current_inventory"] *= -1

    duplicate_count = max(1, round(len(raw) * 0.002))
    duplicates = raw.loc[rng.choice(raw.index, size=duplicate_count, replace=False)]
    return pd.concat([raw, duplicates], ignore_index=True)


def save_generated_data(daily: pd.DataFrame, products: pd.DataFrame, config: DataGenerationConfig) -> dict[str, Path]:
    ensure_project_directories()
    paths = {
        "daily": RAW_DATA_DIR / "supply_chain_daily.csv",
        "products": RAW_DATA_DIR / "products.csv",
        "metadata": RAW_DATA_DIR / "generation_metadata.json",
    }
    daily.to_csv(paths["daily"], index=False)
    products.to_csv(paths["products"], index=False)
    metadata = {
        "configuration": asdict(config),
        "daily_rows": len(daily),
        "unique_products": int(daily["product_id"].nunique()),
        "date_min": str(pd.to_datetime(daily["date"]).min().date()),
        "date_max": str(pd.to_datetime(daily["date"]).max().date()),
        "injected_quality_issues": {
            "missing_supplier_lead_time_rate": 0.003 if config.inject_quality_issues else 0,
            "negative_inventory_rate": 0.001 if config.inject_quality_issues else 0,
            "duplicate_rate": 0.002 if config.inject_quality_issues else 0,
        },
        "generation_notes": [
            "Demand depends on category, weekend, season, promotion, discount, trend, and autocorrelated shocks.",
            "Units sold are capped by available beginning inventory; unmet demand is stored as lost_sales.",
            "Replenishment orders arrive after supplier-specific stochastic lead times.",
            "Stockouts occur from inventory constraints and are never sampled independently.",
        ],
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_GENERATION_CONFIG.random_seed)
    parser.add_argument("--products", type=int, default=DEFAULT_GENERATION_CONFIG.number_of_products)
    parser.add_argument("--days", type=int, default=DEFAULT_GENERATION_CONFIG.number_of_days)
    parser.add_argument("--no-quality-issues", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = DataGenerationConfig(
        random_seed=args.seed,
        number_of_products=args.products,
        number_of_days=args.days,
        inject_quality_issues=not args.no_quality_issues,
    )
    daily, products = generate_supply_chain_data(config)
    paths = save_generated_data(daily, products, config)
    LOGGER.info("Generated %s rows for %s products", len(daily), len(products))
    for name, path in paths.items():
        LOGGER.info("Saved %s to %s", name, path)


if __name__ == "__main__":
    main()
