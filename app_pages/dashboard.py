import altair as alt
import streamlit as st

from app_utils import active_dataset_name, active_features, active_predictions
from components.charts import risk_distribution_chart
from components.common import getting_started, kpi, risk_dataframe_config
from ui import render_hero, render_workflow, style_chart

predictions = active_predictions()
history = active_features()
latest_date = predictions["date"].max()
render_hero()
render_workflow()
getting_started()
st.caption(f"{active_dataset_name()} · Decision snapshot as of {latest_date:%d %b %Y} · Seven-day prediction horizon")

with st.container(horizontal=True, vertical_alignment="bottom"):
    categories = st.multiselect("Category", sorted(history["category"].unique()), key="dashboard_categories", persist_state="session")
    warehouses = st.multiselect("Warehouse", sorted(history["warehouse"].unique()), key="dashboard_warehouses", persist_state="session")
    date_range = st.date_input("Date range", value=(history["date"].min().date(), history["date"].max().date()), key="dashboard_date_range", persist_state="session")
filtered_history = history.copy()
if categories:
    filtered_history = filtered_history[filtered_history["category"].isin(categories)]
    predictions = predictions[predictions["category"].isin(categories)]
if warehouses:
    filtered_history = filtered_history[filtered_history["warehouse"].isin(warehouses)]
    predictions = predictions[predictions["warehouse"].isin(warehouses)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_history = filtered_history[filtered_history["date"].between(str(date_range[0]), str(date_range[1]))]

with st.container(horizontal=True):
    kpi("Products monitored", f"{predictions['product_id'].nunique():,}")
    kpi("Critical risk", f"{(predictions['risk_level'] == 'CRITICAL').sum():,}")
    kpi("High risk", f"{(predictions['risk_level'] == 'HIGH').sum():,}")
    kpi("Average days remaining", f"{predictions['days_until_stockout'].mean():.1f}")
    kpi("Replenishment units", f"{predictions['units_required'].sum():,.0f}")
    kpi("Model coverage", "100.0%" if len(predictions) else "0.0%")

left, right = st.columns([1.35, 1])
with left, st.container(border=True):
    st.subheader("Inventory and demand trajectory")
    trend = filtered_history.groupby("date", as_index=False)[["current_inventory", "daily_sales"]].mean().melt("date", var_name="Measure", value_name="Daily average")
    trend["Measure"] = trend["Measure"].replace({"current_inventory": "Inventory", "daily_sales": "Demand"})
    chart = alt.Chart(trend).mark_line(strokeWidth=2.6).encode(x=alt.X("date:T", title="Date"), y=alt.Y("Daily average:Q"), color=alt.Color("Measure:N", scale=alt.Scale(range=["#C75236", "#D8B98E"])), tooltip=["date:T", "Measure:N", alt.Tooltip("Daily average:Q", format=".1f")]).properties(height=310).interactive()
    st.altair_chart(style_chart(chart))
with right, st.container(border=True):
    st.subheader("Current risk distribution")
    st.altair_chart(risk_distribution_chart(predictions))

with st.container(border=True):
    st.subheader("Priority action queue")
    queue = predictions.sort_values(["risk_score", "stockout_probability"], ascending=False).head(12)
    action_columns = ["product_name", "category", "warehouse", "risk_level", "risk_score", "stockout_probability", "days_until_stockout", "expected_stockout_date", "units_required", "urgency", "recommended_action"]
    st.dataframe(queue[action_columns[:-1]], hide_index=True, column_config=risk_dataframe_config())
    st.download_button(
        "Download action plan",
        data=queue[action_columns].to_csv(index=False).encode("utf-8"),
        file_name=f"stockout_action_plan_{latest_date:%Y-%m-%d}.csv",
        mime="text/csv",
        icon=":material/download:",
    )

st.info("Next: open **Product risk** to understand why a product is at risk and see the recommended replenishment action.", icon=":material/lightbulb:")
st.page_link("app_pages/product_risk.py", label="Investigate a product", icon=":material/search_insights:")
