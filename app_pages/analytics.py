import altair as alt
import streamlit as st

from app_utils import active_features
from ui import render_page_intro, style_chart

data = active_features()
render_page_intro("Patterns beneath the pressure", "Understand where risk gathers.", "See how categories, locations, promotions and seasons shape the stockout landscape—without losing the operational context.")
with st.container(horizontal=True):
    selected_categories = st.multiselect("Category", sorted(data["category"].unique()), key="analytics_categories", persist_state="session")
    selected_warehouses = st.multiselect("Warehouse", sorted(data["warehouse"].unique()), key="analytics_warehouses", persist_state="session")
    selected_seasons = st.multiselect("Season", sorted(data["season"].unique()), key="analytics_seasons", persist_state="session")
    promotion_filter = st.segmented_control("Promotion", ["All", "Active", "Inactive"], default="All", key="analytics_promotion", persist_state="session")
if selected_categories:
    data = data[data["category"].isin(selected_categories)]
if selected_warehouses:
    data = data[data["warehouse"].isin(selected_warehouses)]
if selected_seasons:
    data = data[data["season"].isin(selected_seasons)]
if promotion_filter == "Active":
    data = data[data["promotion"] == 1]
elif promotion_filter == "Inactive":
    data = data[data["promotion"] == 0]
if data.empty:
    st.warning("No records match this filter combination. Remove one or more filters to continue.")
    st.stop()
category_risk = data.groupby("category")["stockout_event"].mean().sort_values(ascending=False)
warehouse_risk = data.groupby("warehouse")["stockout_event"].mean().sort_values(ascending=False)
promotion_risk = data.groupby("promotion")["stockout_event"].mean()
season_risk = data.groupby("season")["stockout_event"].mean().sort_values(ascending=False)
promotion_lift = float(promotion_risk.get(1, 0) / max(promotion_risk.get(0, 0), 1e-9))
with st.container(horizontal=True):
    st.metric("Highest-risk category", category_risk.index[0], f"{category_risk.iloc[0]:.1%} event rate", border=True)
    st.metric("Highest-risk warehouse", warehouse_risk.index[0], f"{warehouse_risk.iloc[0]:.1%} event rate", border=True)
    st.metric("Promotion risk lift", f"{promotion_lift:.2f}×", border=True)
    st.metric("Highest-risk season", season_risk.index[0], border=True)

left, right = st.columns(2)
with left, st.container(border=True):
    st.subheader("Stockout rate by category")
    category = data.groupby("category", as_index=False)["stockout_event"].mean().sort_values("stockout_event", ascending=False)
    st.bar_chart(category, x="category", y="stockout_event", horizontal=True)
    st.caption(f"Highest observed category rate: {category.iloc[0]['category']} at {category.iloc[0]['stockout_event']:.1%}.")
with right, st.container(border=True):
    st.subheader("Stockout events by warehouse")
    warehouse = data.groupby("warehouse", as_index=False)["stockout_event"].sum().sort_values("stockout_event", ascending=False)
    st.bar_chart(warehouse, x="warehouse", y="stockout_event")
    st.caption(f"Highest event volume in the current segment: {warehouse.iloc[0]['warehouse']} with {int(warehouse.iloc[0]['stockout_event'])} events.")

with st.container(border=True):
    st.subheader("Seasonality and promotions")
    monthly = data.groupby(["month", "promotion"], as_index=False)["stockout_event"].mean()
    monthly["Promotion"] = monthly["promotion"].map({0: "No promotion", 1: "Promotion"})
    chart = alt.Chart(monthly).mark_line(point=alt.OverlayMarkDef(size=65), strokeWidth=2.5).encode(x=alt.X("month:O", title="Month"), y=alt.Y("stockout_event:Q", title="Stockout rate", axis=alt.Axis(format="%")), color=alt.Color("Promotion:N", scale=alt.Scale(range=["#D8B98E", "#C75236"])), tooltip=["month:O", "Promotion:N", alt.Tooltip("stockout_event:Q", format=".1%")]).properties(height=320)
    st.altair_chart(style_chart(chart))
    st.caption("Promotion and calendar effects are computed from the active filtered dataset, not hardcoded conclusions.")

with st.expander("Top products by historical stockout events"):
    st.dataframe(data.groupby(["product_id", "product_name", "category"], as_index=False)["stockout_event"].sum().sort_values("stockout_event", ascending=False).head(20), hide_index=True)
