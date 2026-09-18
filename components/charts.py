"""Shared Altair chart builders using the single risk palette."""

from __future__ import annotations

import altair as alt
import pandas as pd

from components.theme import RISK_COLORS, RISK_ORDER
from ui import style_chart


def risk_distribution_chart(predictions: pd.DataFrame) -> alt.Chart:
    counts = predictions["risk_level"].value_counts().reindex(RISK_ORDER, fill_value=0).rename_axis("Risk level").reset_index(name="Products")
    chart = alt.Chart(counts).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("Risk level:N", sort=RISK_ORDER), y="Products:Q",
        color=alt.Color("Risk level:N", scale=alt.Scale(domain=RISK_ORDER, range=[RISK_COLORS[level] for level in RISK_ORDER]), legend=None),
        tooltip=["Risk level:N", "Products:Q"],
    ).properties(height=310)
    return style_chart(chart)

