"""Central configuration for reproducible project pipelines."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"


@dataclass(frozen=True)
class DataGenerationConfig:
    """Controls synthetic data size and reproducibility."""

    random_seed: int = 42
    start_date: str = "2024-01-01"
    number_of_days: int = 365
    number_of_products: int = 100
    inject_quality_issues: bool = True


DEFAULT_GENERATION_CONFIG = DataGenerationConfig()


def ensure_project_directories() -> None:
    """Create all runtime output directories if they do not exist."""

    for path in (
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        DATABASE_DIR,
        MODELS_DIR,
        REPORTS_DIR / "figures",
        REPORTS_DIR / "metrics",
    ):
        path.mkdir(parents=True, exist_ok=True)

