"""Cached data loaders and reusable presentation helpers for Streamlit pages."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent


@st.cache_data
def load_features() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "processed" / "supply_chain_features.csv", parse_dates=["date"])


@st.cache_data
def load_predictions() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "processed" / "latest_predictions.csv", parse_dates=["date", "expected_stockout_date"])


def active_features() -> pd.DataFrame:
    """Return this browser session's upload, or the bundled demo dataset."""

    return st.session_state.get("uploaded_features", load_features())


def active_predictions() -> pd.DataFrame:
    """Return predictions matching the active dataset."""

    predictions = st.session_state.get("uploaded_predictions", load_predictions()).copy()
    for column in ("date", "expected_stockout_date"):
        if column in predictions.columns and not pd.api.types.is_datetime64_any_dtype(predictions[column]):
            predictions[column] = pd.to_datetime(predictions[column], errors="coerce")
    return predictions


def active_dataset_name() -> str:
    return st.session_state.get("active_dataset_name", "Built-in demo")


@st.cache_data
def load_metrics() -> dict[str, object]:
    return json.loads((ROOT / "reports" / "metrics" / "model_metrics.json").read_text(encoding="utf-8"))

