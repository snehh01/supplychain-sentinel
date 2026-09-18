"""Shared status, metric, and empty-state components."""

from __future__ import annotations

import streamlit as st


def kpi(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label, value, delta, border=True)


def getting_started() -> None:
    """Explain the shortest path from data to an inventory decision."""

    with st.container(border=True):
        st.subheader("Get a decision in three steps", icon=":material/route:")
        st.caption("The app predicts which products may run out within seven days, explains why, and recommends how many units to replenish.")
        first, second, third = st.columns(3)
        with first:
            st.markdown("#### 1 · Add your data")
            st.write("Upload a CSV, match your column names, then activate it. You can also explore the built-in demo.")
        with second:
            st.markdown("#### 2 · Review priorities")
            st.write("Use the Dashboard to find critical and high-risk products that need attention first.")
        with third:
            st.markdown("#### 3 · Take action")
            st.write("Open Product risk to see the causes, expected stockout date, and replenishment recommendation.")
        st.page_link("app_pages/data_workspace.py", label="Start with your dataset", icon=":material/arrow_forward:")


def risk_badge(level: str) -> str:
    color = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "orange", "CRITICAL": "red"}.get(level, "gray")
    return f":{color}-badge[{level}]"


def risk_dataframe_config() -> dict[str, object]:
    return {
        "risk_score": st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100),
        "stockout_probability": st.column_config.NumberColumn("Probability", format="percent"),
        "days_until_stockout": st.column_config.NumberColumn("Days remaining", format="%.1f"),
        "expected_stockout_date": st.column_config.DateColumn("Expected stockout", format="YYYY-MM-DD"),
        "units_required": st.column_config.NumberColumn("Replenishment units", format="localized"),
    }
