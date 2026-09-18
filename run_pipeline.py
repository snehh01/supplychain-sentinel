"""Run the full reproducible SupplyChain Sentinel build pipeline."""

from src.data_generation import generate_supply_chain_data, save_generated_data
from src.config import DEFAULT_GENERATION_CONFIG, PROCESSED_DATA_DIR, ensure_project_directories
from src.data_preprocessing import clean_supply_chain_data
from src.database import build_database
from src.eda import run_eda
from src.feature_engineering import engineer_features
from src.predict import score_latest_products
from src.train_model import train_and_evaluate


def main() -> None:
    ensure_project_directories()
    daily, products = generate_supply_chain_data(DEFAULT_GENERATION_CONFIG)
    save_generated_data(daily, products, DEFAULT_GENERATION_CONFIG)
    clean, _ = clean_supply_chain_data(daily)
    clean.to_csv(PROCESSED_DATA_DIR / "supply_chain_clean.csv", index=False)
    run_eda(clean)
    featured = engineer_features(clean)
    featured.to_csv(PROCESSED_DATA_DIR / "supply_chain_features.csv", index=False)
    train_and_evaluate(featured)
    predictions = score_latest_products(featured)
    predictions.to_csv(PROCESSED_DATA_DIR / "latest_predictions.csv", index=False)
    build_database()
    print("Pipeline complete: data, reports, model, predictions, and database are ready.")


if __name__ == "__main__":
    main()
