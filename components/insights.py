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

    st.dataframe(competitor_df, use_container_width=True)


def show_insights(df):
    st.subheader("Insights")

    if df.empty:
        st.info("No results available yet.")
        return

    low_categories = (
        df.groupby("category")["score"]
        .mean()
        .reset_index()
        .sort_values("score")
        .head(3)
    )

    st.markdown("#### Priority Opportunities")

    for _, row in low_categories.iterrows():
        st.warning(
            f"**{row['category']}** is averaging **{round(row['score'], 1)}** visibility. "
            "Review related pages for clearer program descriptions, stronger FAQs, "
            "comparison-friendly content, outcomes, costs, and structured data."
        )

    st.markdown("#### Prompt-Level Issues")

    opportunities = df[
        (df["wake_tech_mentioned"] == "No") |
        (df["score"] < 70)
    ].sort_values("score")

    if opportunities.empty:
        st.success("No major prompt-level opportunities found in this dataset.")
        return

    for _, row in opportunities.iterrows():
        competitors = row["competitors"] if pd.notna(row["competitors"]) else "no clear competitors"

        if row["wake_tech_mentioned"] == "No":
            message = (
                f"🚨 **{row['platform']}** did not recommend Wake Tech for this prompt.\n\n"
                f"Instead it mentioned **{competitors}**.\n\n"
                "Recommendation: Strengthen Wake Tech content for this topic and compare it against "
                "the institutions AI tools are already surfacing."
            )
        else:
            message = (
                f"⚠️ Wake Tech appeared in **{row['platform']}**, but visibility is weak "
                f"(Score: {row['score']}).\n\n"
                "Recommendation: Expand the page with plain-language answers, program outcomes, "
                "cost details, admissions steps, FAQs, and schema-friendly structure."
            )

        with st.expander(f"{row['platform']} • {row['category']} • Score {row['score']}"):
            st.markdown(message)