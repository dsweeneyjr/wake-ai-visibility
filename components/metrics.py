import streamlit as st

def show_metrics(df):

    col1, col2, col3, col4 = st.columns(4)

    avg_score = round(df["score"].mean(), 1) if not df.empty else 0
    mention_rate = round((df["wake_tech_mentioned"] == "Yes").mean() * 100, 1) if not df.empty else 0
    prompts = df["prompt_id"].nunique()
    platforms = df["platform"].nunique()

    col1.metric("Average Visibility", avg_score)
    col2.metric("Mention Rate", f"{mention_rate}%")
    col3.metric("Prompts", prompts)
    col4.metric("AI Platforms", platforms)