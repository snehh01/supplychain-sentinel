"""Validate and normalize user-uploaded CSV files for model scoring."""

from __future__ import annotations

import pandas as pd

from src.data_collection import collect_csv_bytes
from src.data_preprocessing import clean_supply_chain_data
from src.feature_engineering import engineer_features

REQUIRED_UPLOAD_COLUMNS = {
    "date", "product_id", "product_name", "category", "warehouse", "region",
    "current_inventory", "daily_sales", "supplier_lead_time", "reorder_point", "unit_price",
}
CORE_UPLOAD_COLUMNS = {
    "date", "product_id", "category", "warehouse", "region",
    "current_inventory", "daily_sales", "unit_price",
}
ASSUMPTION_COLUMNS = REQUIRED_UPLOAD_COLUMNS - CORE_UPLOAD_COLUMNS
OPTIONAL_UPLOAD_COLUMNS = {
    "inventory_received", "discount", "promotion", "demand_forecast", "stockout_event",
}

COLUMN_ALIASES = {
    "date": {"date", "day", "timestamp", "transaction_date", "record_date"},
    "product_id": {"product_id", "product id", "sku", "sku_id", "item_id", "product_code"},
    "product_name": {"product_name", "item_name", "sku_name", "description"},
    "category": {"category", "product_category", "department"},
    "warehouse": {"warehouse", "warehouse_name", "location", "distribution_center", "store_id", "store id"},
    "region": {"region", "territory", "market"},
    "current_inventory": {"current_inventory", "stock", "stock_on_hand", "inventory", "inventory_level", "inventory level", "quantity_on_hand"},
    "daily_sales": {"daily_sales", "sales", "demand", "units_sold", "units sold", "daily_demand"},
    "supplier_lead_time": {"supplier_lead_time", "lead_time", "lead_days", "delivery_time"},
    "reorder_point": {"reorder_point", "rop", "minimum_stock", "reorder_level"},
    "unit_price": {"unit_price", "price", "selling_price", "item_price"},
}


def suggest_column_mapping(columns: list[str]) -> dict[str, str | None]:
    """Suggest source-to-required mappings using common supply-chain aliases."""

    normalized = {str(column).strip().lower(): str(column) for column in columns}
    suggestions: dict[str, str | None] = {}
    for required, aliases in COLUMN_ALIASES.items():
        match = next((normalized[alias] for alias in aliases if alias in normalized), None)
        suggestions[required] = match
    return suggestions


def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def prepare_uploaded_csv(
    contents: bytes,
    source_name: str = "browser_upload.csv",
    column_mapping: dict[str, str] | None = None,
    default_lead_time_days: int = 7,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Return model-ready features and a validation/cleaning report."""

    raw, source = collect_csv_bytes(contents, source_name=source_name)
    if column_mapping:
        normalized_mapping = {
            str(required).strip().lower(): str(source_column).strip().lower()
            for required, source_column in column_mapping.items()
        }
        selected_sources = list(normalized_mapping.values())
        if len(selected_sources) != len(set(selected_sources)):
            raise ValueError("Each source column can only be mapped once.")
        raw = raw.rename(columns={source_column: required for required, source_column in normalized_mapping.items()})
    missing = sorted(CORE_UPLOAD_COLUMNS - set(raw.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    data = raw.copy()
    assumptions: list[str] = []
    if "product_name" not in data:
        data["product_name"] = data["product_id"].astype(str)
        assumptions.append("product_name copied from product_id")
    if "supplier_lead_time" not in data:
        data["supplier_lead_time"] = int(default_lead_time_days)
        assumptions.append(f"supplier_lead_time set to user-selected {int(default_lead_time_days)} days")
    if "reorder_point" not in data:
        demand_for_reorder = pd.to_numeric(data["daily_sales"], errors="coerce")
        data["reorder_point"] = demand_for_reorder * int(default_lead_time_days)
        assumptions.append("reorder_point estimated as daily_sales × supplier_lead_time")
    data["date"] = pd.to_datetime(data["date"], format="mixed", errors="coerce")
    if data["date"].isna().any():
        raise ValueError(f"{int(data['date'].isna().sum())} row(s) contain an invalid date.")

    numeric = ["current_inventory", "daily_sales", "supplier_lead_time", "reorder_point", "unit_price"]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    invalid_numeric = {column: int(data[column].isna().sum()) for column in numeric if data[column].isna().any()}
    if invalid_numeric:
        details = ", ".join(f"{name} ({count})" for name, count in invalid_numeric.items())
        raise ValueError(f"Non-numeric or missing required values found: {details}.")

    defaults = {"inventory_received": 0, "discount": 0.0, "promotion": 0, "stockout_event": 0}
    for column, default in defaults.items():
        if column not in data:
            data[column] = default
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(default)
    if "demand_forecast" not in data:
        data["demand_forecast"] = data["daily_sales"]
    data["demand_forecast"] = pd.to_numeric(data["demand_forecast"], errors="coerce").fillna(data["daily_sales"])
    data["promotion"] = ((data["promotion"] > 0) | (data["discount"] > 0)).astype(int)
    data["units_sold"] = data["daily_sales"].clip(lower=0)
    data["beginning_inventory"] = data["current_inventory"].clip(lower=0) + data["units_sold"]
    data["lost_sales"] = 0
    data["day_of_week"] = data["date"].dt.day_name()
    data["month"] = data["date"].dt.month
    data["season"] = data["month"].map(_season)

    duplicate_keys = int(data.duplicated(["product_id", "date"]).sum())
    clean, cleaning_report = clean_supply_chain_data(data)
    features = engineer_features(clean)
    report = {
        "data_source": source.as_dict(),
        "input_rows": len(raw),
        "clean_rows": len(clean),
        "products": int(clean["product_id"].nunique()),
        "date_start": clean["date"].min().date().isoformat(),
        "date_end": clean["date"].max().date().isoformat(),
        "duplicate_product_dates": duplicate_keys,
        "optional_columns_supplied": sorted(OPTIONAL_UPLOAD_COLUMNS & set(raw.columns)),
        "assumptions": assumptions,
        "cleaning": cleaning_report,
    }
    return features, report


def upload_template(data: pd.DataFrame) -> bytes:
    columns = sorted(REQUIRED_UPLOAD_COLUMNS) + sorted(OPTIONAL_UPLOAD_COLUMNS)
    available = [column for column in columns if column in data.columns]
    return data[available].head(25).to_csv(index=False).encode("utf-8")
