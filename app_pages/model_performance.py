import altair as alt
import pandas as pd
import streamlit as st

from app_utils import load_metrics
from ui import render_page_intro, style_chart

metrics = load_metrics()
test = metrics["test_metrics"]
render_page_intro("Evidence before confidence", "A model you can defend.", "Compare candidates, inspect errors and understand which signals shape each seven-day stockout decision.")
st.caption(f"Selected model: **{metrics['selected_model']}** · {metrics['selection_rule']}")
model_names = list(metrics["validation_model_comparison"])
view_model = st.selectbox("Compare validation model", model_names, index=model_names.index(metrics["selected_model"]), key="performance_model", persist_state="session")
view_metrics = metrics["validation_model_comparison"][view_model]
with st.container(horizontal=True):
    for key in ["precision", "recall", "f1", "roc_auc"]:
        st.metric(key.replace("_", " ").title(), f"{view_metrics[key]:.3f}", border=True)

left, right = st.columns(2)
with left, st.container(border=True):
    st.subheader("Validation model comparison")
    comparison = pd.DataFrame(metrics["validation_model_comparison"]).T.reset_index(names="Model")
    comparison_long = comparison.melt("Model", value_vars=["precision", "recall", "f1", "roc_auc"], var_name="Metric", value_name="Score")
    st.bar_chart(comparison_long, x="Model", y="Score", color="Metric", stack=False)
with right, st.container(border=True):
    st.subheader("Test confusion matrix")
    matrix = test["confusion_matrix"]
    confusion = pd.DataFrame([{"Actual": "No stockout", "Predicted": "No stockout", "Count": matrix[0][0]}, {"Actual": "No stockout", "Predicted": "Stockout", "Count": matrix[0][1]}, {"Actual": "Stockout", "Predicted": "No stockout", "Count": matrix[1][0]}, {"Actual": "Stockout", "Predicted": "Stockout", "Count": matrix[1][1]}])
    heatmap = alt.Chart(confusion).mark_rect(cornerRadius=7).encode(x="Predicted:N", y="Actual:N", color=alt.Color("Count:Q", scale=alt.Scale(range=["#F3E6D5", "#9E3C28"])), tooltip=["Actual", "Predicted", "Count"]).properties(height=300)
    labels = heatmap.mark_text(color="white", fontSize=18).encode(text="Count:Q")
    st.altair_chart(style_chart(heatmap + labels))

with st.container(border=True):
    st.subheader("ROC curve")
    roc = pd.DataFrame({"False-positive rate": metrics["test_roc_curve"]["false_positive_rate"], "True-positive rate": metrics["test_roc_curve"]["true_positive_rate"]})
    line = alt.Chart(roc).mark_line(color="#C75236", strokeWidth=3).encode(x="False-positive rate:Q", y="True-positive rate:Q").properties(height=300)
    diagonal = alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]})).mark_line(strokeDash=[5, 5], color="gray").encode(x="x", y="y")
    st.altair_chart(style_chart(line + diagonal))

with st.container(border=True):
    st.subheader("Most influential features")
    importance = pd.DataFrame(metrics["top_features"][:12]).sort_values("importance")
    st.bar_chart(importance, x="importance", y="feature", horizontal=True)

with st.expander("How to interpret these results and limitations", icon=":material/info:"):
    st.markdown(
        """
        - **Recall** shows how many future stockouts the model catches; **precision** shows how many alerts are correct.
        - The selected model prioritizes F1 and recall because a missed stockout can be costly, so some false alerts are expected.
        - Feature influence shows association within the fitted model, not proof that a feature causes a stockout.
        - Results come from synthetic data. Performance must be re-evaluated, calibrated, and monitored before use with real operational decisions.
        - Replenishment quantities are deterministic planning guidance, not an optimized purchase order.
        """
    )
