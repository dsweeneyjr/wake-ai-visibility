import pandas as pd
import streamlit as st


def show_charts(df):
    left, right = st.columns(2)

    with left:
        st.subheader("Average Visibility by Platform")
        platform_scores = df.groupby("platform")["score"].mean().reset_index()
        st.bar_chart(platform_scores, x="platform", y="score")

    with right:
        st.subheader("Average Visibility by Category")
        category_scores = df.groupby("category")["score"].mean().reset_index()
        st.bar_chart(category_scores, x="category", y="score")