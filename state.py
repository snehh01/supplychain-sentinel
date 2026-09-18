"""Central Streamlit session-state schema and dataset lifecycle helpers."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st


DEFAULTS = {
    "active_dataset_name": "Built-in demo",
    "dataset_source": "demo",
    "dataset_activated_at": None,
    "upload_validation": None,
    "dashboard_categories": [],
    "dashboard_warehouses": [],
    "analytics_categories": [],
    "analytics_warehouses": [],
    "analytics_seasons": [],
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value.copy() if isinstance(value, list) else value)


def activate_dataset(*, name: str, features, predictions, report: dict[str, object]) -> None:
    st.session_state.uploaded_features = features
    st.session_state.uploaded_predictions = predictions
    st.session_state.upload_report = report
    st.session_state.upload_validation = report
    st.session_state.active_dataset_name = name
    st.session_state.dataset_source = "upload"
    st.session_state.dataset_activated_at = datetime.now(timezone.utc).isoformat()


def reset_dataset() -> None:
    for key in ("uploaded_features", "uploaded_predictions", "upload_report", "upload_validation"):
        st.session_state.pop(key, None)
    st.session_state.active_dataset_name = "Built-in demo"
    st.session_state.dataset_source = "demo"
    st.session_state.dataset_activated_at = None

