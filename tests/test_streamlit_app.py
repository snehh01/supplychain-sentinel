from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


def test_dashboard_loads_without_exception() -> None:
    app = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    at = AppTest.from_file(str(app), default_timeout=20).run()
    assert not at.exception
    assert len(at.metric) >= 5
    assert len(at.download_button) >= 1


def test_data_workspace_loads_upload_controls() -> None:
    app = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    at = AppTest.from_file(str(app), default_timeout=20).run()
    at.switch_page("app_pages/data_workspace.py").run()
    assert not at.exception
    assert len(at.file_uploader) == 1
    assert len(at.download_button) == 2
    assert at.download_button[1].label == "Download full built-in dataset"


def test_product_risk_accepts_uploaded_prediction_date_strings() -> None:
    root = Path(__file__).resolve().parents[1]
    app = root / "streamlit_app.py"
    features = pd.read_csv(root / "data" / "processed" / "supply_chain_features.csv", parse_dates=["date"])
    predictions = pd.read_csv(root / "data" / "processed" / "latest_predictions.csv")
    at = AppTest.from_file(str(app), default_timeout=30).run()
    at.session_state["uploaded_features"] = features
    at.session_state["uploaded_predictions"] = predictions
    at.switch_page("app_pages/product_risk.py").run(timeout=30)
    assert not at.exception


@pytest.mark.parametrize(
    "page_path",
    [
        "app_pages/product_risk.py",
        "app_pages/analytics.py",
        "app_pages/model_performance.py",
    ],
)
def test_every_analysis_page_loads_without_exception(page_path: str) -> None:
    app = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    at.switch_page(page_path).run(timeout=30)
    assert not at.exception
