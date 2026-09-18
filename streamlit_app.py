"""Main entry point for the SupplyChain Sentinel product experience."""

import streamlit as st

from state import initialize_state
from ui import inject_global_styles

st.set_page_config(
    page_title="SupplyChain Sentinel",
    page_icon=":material/inventory_2:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
initialize_state()
inject_global_styles()

page = st.navigation(
    [
        st.Page("app_pages/data_workspace.py", title="Data workspace", icon=":material/upload_file:"),
        st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
        st.Page("app_pages/product_risk.py", title="Product risk", icon=":material/search_insights:"),
        st.Page("app_pages/analytics.py", title="Analytics", icon=":material/query_stats:"),
        st.Page("app_pages/model_performance.py", title="Model performance", icon=":material/model_training:"),
    ],
    position="top",
)
page.run()
