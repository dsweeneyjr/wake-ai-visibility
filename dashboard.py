import time
from datetime import datetime
from pathlib import Path
from services.scan import run_demo_scan

import pandas as pd
import streamlit as st

from components.executive_summary import show_executive_summary
from components.metrics import show_metrics
from components.charts import show_charts
from components.prompt_explorer import show_prompt_explorer
from components.insights import show_competitors, show_insights


st.set_page_config(
    page_title="Wake Tech AI Search Intelligence",
    layout="wide"
)

RESULTS_FILE = Path("data/results.csv")
df = pd.read_csv(RESULTS_FILE)

df["run_date"] = pd.to_datetime(df["run_date"], errors="coerce")

st.title("Wake Tech AI Search Intelligence")
st.caption("Decision-support prototype for tracking how AI tools recommend Wake Tech.")

with st.sidebar:
    st.header("Filters")

    selected_platforms = st.multiselect(
        "AI Platforms",
        sorted(df["platform"].dropna().unique()),
        default=sorted(df["platform"].dropna().unique())
    )

    selected_categories = st.multiselect(
        "Categories",
        sorted(df["category"].dropna().unique()),
        default=sorted(df["category"].dropna().unique())
    )

filtered_all = df[
    df["platform"].isin(selected_platforms) &
    df["category"].isin(selected_categories)
]

with st.sidebar:
    show_history = st.checkbox("Show all historical runs", value=False)

if show_history:
    filtered = filtered_all
else:
    filtered = (
        filtered_all
        .sort_values("run_date")
        .drop_duplicates(
            subset=["platform", "prompt_id"],
            keep="last"
        )
    )

latest_date = filtered_all["run_date"].max() if not filtered_all.empty else None
latest_scan = filtered_all[filtered_all["run_date"] == latest_date] if latest_date is not None else pd.DataFrame()

with st.container(border=True):
    st.markdown("### Executive Summary")
    st.write(
        "This prototype measures how AI search engines recommend Wake Tech, "
        "tracks competitors, identifies content opportunities, and provides "
        "actionable recommendations for improving AI visibility."
    )

    st.warning(
        "Prototype note: live AI scanning is not enabled yet. Current scan button simulates the workflow."
    )
if st.button("▶ Run Demo Scan", type="primary"):
    progress = st.progress(0)
    status = st.empty()

    status.write("🤖 Simulating ChatGPT scan...")
    time.sleep(.8)
    progress.progress(25)

    status.write("🧠 Simulating Gemini scan...")
    time.sleep(.8)
    progress.progress(50)

    status.write("🔍 Simulating Perplexity scan...")
    time.sleep(.8)
    progress.progress(75)

    status.write("📊 Updating dashboard preview...")
    time.sleep(.8)
    progress.progress(100)

    status.empty()

    st.success("Demo scan complete.")
    st.info(
        "This is still simulated. Real AI scans will run once API billing/quota is available."
    )

with st.container(border=True):
    st.subheader("Latest Scan")

    col1, col2, col3, col4 = st.columns(4)

    if latest_scan.empty:
        col1.metric("Latest Date", "N/A")
        col2.metric("Platforms", 0)
        col3.metric("Responses", 0)
        col4.metric("Avg Score", 0)
    else:
        col1.metric("Latest Date", latest_date.strftime("%b %d, %Y"))
        col2.metric("Platforms", latest_scan["platform"].nunique())
        col3.metric("Responses", len(latest_scan))
        col4.metric("Avg Score", round(latest_scan["score"].mean(), 1))

show_executive_summary(filtered)

st.divider()
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
st.subheader("Results Data")
st.dataframe(filtered, width="stretch")