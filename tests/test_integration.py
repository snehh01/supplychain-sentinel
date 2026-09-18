from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect

from src.database import QUERIES, build_database, run_query
from src.predict import score_latest_products


ROOT = Path(__file__).resolve().parents[1]


def test_saved_model_scores_real_feature_rows() -> None:
    features = pd.read_csv(ROOT / "data" / "processed" / "supply_chain_features.csv", parse_dates=["date"])
    predictions = score_latest_products(features)
    assert len(predictions) == features["product_id"].nunique()
    assert predictions["stockout_probability"].between(0, 1).all()
    assert predictions["risk_score"].between(0, 100).all()
    assert predictions["recommended_action"].str.len().gt(20).all()


def test_database_build_and_business_queries(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'audit.db'}", future=True)
    build_database(engine)
    expected_tables = {
        "products", "daily_inventory", "daily_sales", "supplier_information",
        "model_predictions", "stockout_alerts",
    }
    assert expected_tables <= set(inspect(engine).get_table_names())
    for query_name in QUERIES:
        assert not run_query(query_name, engine).empty
