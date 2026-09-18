from pathlib import Path

import pandas as pd
import streamlit as st

from app_utils import active_dataset_name, active_features, load_features
from components.common import kpi
from src.predict import score_latest_products
from src.data_collection import collect_csv_bytes
from src.user_data import ASSUMPTION_COLUMNS, CORE_UPLOAD_COLUMNS, REQUIRED_UPLOAD_COLUMNS, prepare_uploaded_csv, suggest_column_mapping, upload_template
from state import activate_dataset, reset_dataset
from ui import render_page_intro

BUILTIN_DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "supply_chain_clean.csv"


@st.cache_data
def builtin_dataset_csv() -> bytes:
    """Return the complete built-in dataset without relying on shared module reloads."""

    return BUILTIN_DATASET_PATH.read_bytes()

render_page_intro("Your data · our intelligence", "Bring the signal into focus.", "Upload supply-chain history, validate it in seconds, and activate the trained risk system across the entire product experience.")

with st.container(border=True):
    st.subheader("How to add your data", icon=":material/format_list_numbered:")
    st.markdown("**1. Upload** a CSV → **2. Match** your columns → **3. Validate and activate** → **4. Open the Dashboard**")
    st.caption("Column names do not need to match the example exactly. The app suggests common matches and lets you correct them before activation.")

with st.container(horizontal=True):
    current = active_features()
    kpi("Active source", active_dataset_name())
    kpi("Rows", f"{len(current):,}")
    kpi("Products", f"{current['product_id'].nunique():,}")
    kpi("Date coverage", f"{current['date'].min():%d %b %Y} – {current['date'].max():%d %b %Y}")

left, right = st.columns([1.35, 1])
with left, st.container(border=True):
    st.subheader("Drop in your operating history", icon=":material/upload_file:")
    st.caption("Your upload stays in this browser session and is not written to the project database.")
    uploaded = st.file_uploader("Supply-chain dataset", type=["csv"], key="dataset_file")
    if uploaded is not None:
        st.caption(f"Selected: {uploaded.name} · {uploaded.size / 1024:,.1f} KB")
        try:
            raw_preview, _ = collect_csv_bytes(uploaded.getvalue(), source_name=uploaded.name)
            suggestions = suggest_column_mapping(raw_preview.columns.tolist())
            st.dataframe(pd.DataFrame({"Column": raw_preview.columns, "Type": raw_preview.dtypes.astype(str).values}), hide_index=True, height=210)
            with st.expander("Review column mapping", expanded=any(value is None for value in suggestions.values())):
                st.caption("We detected common names automatically. Review or correct each required business field.")
                mapping: dict[str, str] = {}
                options = ["— Not mapped —"] + raw_preview.columns.tolist()
                for required in sorted(REQUIRED_UPLOAD_COLUMNS):
                    suggested = suggestions.get(required)
                    selected = st.selectbox(required, options, index=options.index(suggested) if suggested in options else 0, key=f"map_{required}")
                    if selected != "— Not mapped —":
                        mapping[required] = selected
            missing_core = sorted(CORE_UPLOAD_COLUMNS - set(mapping))
            fallback_fields = sorted(ASSUMPTION_COLUMNS - set(mapping))
            lead_time_days = 7
            if "supplier_lead_time" in fallback_fields:
                lead_time_days = st.number_input("Assumed supplier lead time (days)", min_value=1, max_value=90, value=7, step=1)
            if missing_core:
                st.error("Map these essential fields before activation: " + ", ".join(missing_core))
            if fallback_fields:
                st.warning(
                    "The file can still be activated. Assumptions will be used for: "
                    + ", ".join(fallback_fields)
                    + ". These will be recorded in the validation report."
                )
            submitted = st.button("Validate and activate", icon=":material/check_circle:", type="primary", disabled=bool(missing_core))
        except ValueError as exc:
            st.error(str(exc), icon=":material/error:")
            submitted = False
        if submitted:
            try:
                with st.spinner("Validating, cleaning, engineering features, and scoring products…"):
                    features, report = prepare_uploaded_csv(
                        uploaded.getvalue(),
                        source_name=uploaded.name,
                        column_mapping=mapping,
                        default_lead_time_days=int(lead_time_days),
                    )
                    predictions = score_latest_products(features)
                activate_dataset(name=uploaded.name, features=features, predictions=predictions, report=report)
                st.toast("Dataset activated", icon=":material/check_circle:")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc), icon=":material/error:")
            except Exception as exc:
                st.error(f"The dataset passed initial checks but could not be scored: {exc}", icon=":material/error:")

with right, st.container(border=True):
    st.subheader("Expected format", icon=":material/table_chart:")
    st.write("Required columns")
    st.code("date, product_id, product_name, category, warehouse, region, current_inventory, daily_sales, supplier_lead_time, reorder_point, unit_price", language=None)
    st.caption("Optional: inventory_received, discount, promotion, demand_forecast, stockout_event. Derived time and inventory fields are created automatically.")
    st.download_button(
        "Download example template",
        data=upload_template(load_features()),
        file_name="supplychain_upload_template.csv",
        mime="text/csv",
        icon=":material/download:",
    )
    st.download_button(
        "Download full built-in dataset",
        data=builtin_dataset_csv(),
        file_name="supplychain_sentinel_builtin_dataset.csv",
        mime="text/csv",
        icon=":material/database:",
        type="primary",
    )
    st.caption("36,500 synthetic daily records for 100 products. Ready to inspect or upload back into the app.")

if "uploaded_features" in st.session_state:
    with st.container(horizontal=True, horizontal_alignment="left"):
        if st.button("Restore built-in demo", icon=":material/restart_alt:"):
            reset_dataset()
            st.rerun()
    report = st.session_state.upload_report
    st.success(f"{report['clean_rows']:,} rows across {report['products']:,} products are ready for scoring.")
    with st.expander("Validation and cleaning details"):
        st.json(report)
    st.page_link("app_pages/dashboard.py", label="View risk results on the Dashboard", icon=":material/dashboard:")

with st.container(border=True):
    st.subheader("Active data preview", icon=":material/preview:")
    preview_columns = ["date", "product_id", "product_name", "category", "warehouse", "current_inventory", "daily_sales", "supplier_lead_time"]
    st.dataframe(active_features()[preview_columns].tail(100), hide_index=True)
