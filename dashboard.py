import time

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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

df = pd.read_csv("data/results.csv")

st.title("Wake Tech AI Search Intelligence")
st.caption("Decision-support prototype for tracking how AI tools recommend Wake Tech.")

with st.container(border=True):

    st.markdown("### Executive Summary")

    st.write("""
This prototype measures how AI search engines recommend Wake Tech,
tracks competitors, identifies content opportunities, and provides
actionable recommendations for improving AI visibility.
""")

    if st.button("▶ Run AI Scan", type="primary"):

        progress = st.progress(0)

        status = st.empty()

        status.write("🤖 Connecting to ChatGPT...")
        time.sleep(.8)
        progress.progress(20)

        status.write("✨ Collecting ChatGPT response...")
        time.sleep(.8)
        progress.progress(40)

        status.write("🧠 Querying Gemini...")
        time.sleep(.8)
        progress.progress(60)

        status.write("🔍 Querying Perplexity...")
        time.sleep(.8)
        progress.progress(80)

        status.write("📊 Analyzing responses...")
        time.sleep(1)
        progress.progress(100)

        status.empty()

        st.success("AI Scan Complete")

        st.info("""
3 AI platforms scanned

1 prompt analyzed

Wake Tech mentioned on 2 of 3 platforms

1 new recommendation generated

Dashboard refreshed
""")
        
with st.container(border=True):

    st.subheader("Latest Scan")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "Scan Time",
        "07:42 AM"
    )

    col2.metric(
        "Platforms",
        "3"
    )

    col3.metric(
        "Responses",
        "3"
    )

    col4.metric(
        "Duration",
        "18 sec"
    )

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
st.subheader("Raw Data")
st.dataframe(filtered, width="stretch")