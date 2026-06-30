import pandas as pd
import streamlit as st


def show_competitors(df):
    st.subheader("Competitor Mentions")

    competitor_rows = []

    for competitors in df["competitors"].dropna():
        for competitor in str(competitors).split("|"):
            competitor = competitor.strip()
            if competitor:
                competitor_rows.append(competitor)

    if not competitor_rows:
        st.info("No competitors found yet.")
        return

    competitor_df = pd.Series(competitor_rows).value_counts().reset_index()
    competitor_df.columns = ["Competitor", "Mentions"]

    st.dataframe(competitor_df, width="stretch")


def show_insights(df):
    st.subheader("Insights")

    opportunities = df[
        (df["wake_tech_mentioned"] == "No") |
        (df["score"] < 70)
    ]

    if opportunities.empty:
        st.success("No major opportunities found in this dataset.")
        return

    for _, row in opportunities.iterrows():
        if row["wake_tech_mentioned"] == "No":
            message = (
                f"🚨 **{row['platform']}** did not recommend Wake Tech for this prompt.\n\n"
                f"Instead it mentioned **{row['competitors']}**.\n\n"
                "Recommendation: Review this topic and compare Wake Tech's content with competitors."
            )
        else:
            message = (
                f"⚠️ Wake Tech appeared in **{row['platform']}**, but visibility is weak "
                f"(Score: {row['score']}).\n\n"
                "Recommendation: Expand content, FAQs, outcomes, citations, and structured data."
            )

        with st.expander(f"{row['platform']} • {row['category']} • Score {row['score']}"):
            st.markdown(message)