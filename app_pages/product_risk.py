import altair as alt
import streamlit as st

from app_utils import active_features, active_predictions
from components.common import kpi, risk_badge
from ui import render_page_intro, style_chart

history = active_features()
predictions = active_predictions()
render_page_intro("Product-level intelligence", "One product. Every signal.", "Move from probability to action with a focused view of inventory coverage, demand momentum and supplier timing.")
options = predictions.sort_values("product_name")["product_name"].tolist()
selected = st.selectbox("Select a product", options, key="product_selector", persist_state="session")
row = predictions.loc[predictions["product_name"] == selected].iloc[0]
product_history = history.loc[history["product_id"] == row["product_id"]].copy()

st.markdown(f"### {selected} &nbsp; {risk_badge(row['risk_level'])}")
with st.container(horizontal=True):
    kpi("Current inventory", f"{row['current_inventory']:,.0f}")
    kpi("Stockout probability", f"{row['stockout_probability']:.1%}")
    kpi("Days remaining", f"{row['days_until_stockout']:.1f}")
    kpi("Supplier lead time", f"{row['supplier_lead_time']:.0f} days")
    kpi("Expected stockout", f"{row['expected_stockout_date']:%Y-%m-%d}")

st.markdown(f"**Risk score — {int(row['risk_score'])}/100**")
st.progress(int(row["risk_score"]) / 100)

signal_left, signal_right = st.columns([1, 1.25])
with signal_left, st.container(border=True):
    st.subheader("Risk signal breakdown", icon=":material/monitoring:")
    signals = {
        "Inventory coverage": f"{row['days_until_stockout']:.1f} days remaining",
        "Lead-time pressure": f"{row['supplier_lead_time']:.0f}-day supplier lead time",
        "Demand momentum": f"{row['demand_growth_rate']:+.1%} versus 30-day baseline",
        "Reorder status": "At or below reorder point" if row["reorder_risk"] else "Above reorder point",
        "Promotion": "Active" if row["promotion"] else "Inactive",
    }
    st.table(signals, border="horizontal")
with signal_right, st.container(border=True):
    st.subheader("Recommended action", icon=":material/assignment_turned_in:")
    st.metric("Replenishment quantity", f"{row['units_required']:,.0f} units")
    st.badge(row["urgency"], icon=":material/schedule:", color="red" if row["risk_level"] == "CRITICAL" else "orange")
    st.write(row["recommended_action"])

plot = product_history.melt("date", value_vars=["current_inventory", "daily_sales", "demand_forecast"], var_name="Measure", value_name="Units")
plot["Measure"] = plot["Measure"].replace({"current_inventory": "Inventory", "daily_sales": "Actual demand", "demand_forecast": "Demand forecast"})
chart = alt.Chart(plot).mark_line(strokeWidth=2.4).encode(x="date:T", y="Units:Q", color=alt.Color("Measure:N", scale=alt.Scale(range=["#A9422B", "#D8B98E", "#ECA98D"])), tooltip=["date:T", "Measure:N", alt.Tooltip("Units:Q", format=".1f")]).properties(height=390).interactive()
st.altair_chart(style_chart(chart))
