import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from components.metrics import show_metrics
from components.charts import show_charts
from components.prompt_explorer import show_prompt_explorer
from components.insights import show_competitors, show_insights


st.set_page_config(
    page_title="Wake Tech AI Search Intelligence",
    layout="wide"
)

df = pd.read_csv("data/results.csv")

st.title("Wake Tech AI Search Intelligence")
st.caption("Prototype for measuring Wake Tech visibility across AI search engines")

with st.sidebar:
    st.header("Filters")

    selected_platforms = st.multiselect(
        "AI Platforms",
        sorted(df["platform"].unique()),
        default=sorted(df["platform"].unique())
    )

    selected_categories = st.multiselect(
        "Categories",
        sorted(df["category"].unique()),
        default=sorted(df["category"].unique())
    )

filtered = df[
    df["platform"].isin(selected_platforms) &
    df["category"].isin(selected_categories)
]

show_metrics(filtered)

st.divider()
show_charts(filtered)

st.divider()
show_prompt_explorer(filtered)

st.divider()
show_competitors(filtered)

st.divider()
show_insights(filtered)

st.divider()
st.subheader("Raw Data")
st.dataframe(filtered, width="stretch")