import pandas as pd
import streamlit as st


def show_executive_summary(df):
    st.subheader("Executive Summary")

    if df.empty:
        st.info("No data available for the selected filters.")
        return

    avg_score = round(df["score"].mean(), 1)
    mention_rate = round((df["wake_tech_mentioned"] == "Yes").mean() * 100, 1)

    strongest = (
        df.groupby("category")["score"]
        .mean()
        .sort_values(ascending=False)
        .head(1)
    )

    weakest = (
        df.groupby("category")["score"]
        .mean()
        .sort_values(ascending=True)
        .head(1)
    )

    competitor_rows = []

    for competitors in df["competitors"].dropna():
        for competitor in str(competitors).split("|"):
            competitor = competitor.strip()
            if competitor:
                competitor_rows.append(competitor)

    top_competitor = "None yet"

    if competitor_rows:
        top_competitor = pd.Series(competitor_rows).value_counts().index[0]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### What the data says")

        st.write(f"Wake Tech's current average AI visibility is **{avg_score}**.")
        st.write(f"Wake Tech is mentioned in **{mention_rate}%** of evaluated AI responses.")

        if not strongest.empty:
            st.write(f"Strongest area: **{strongest.index[0]}**.")

        if not weakest.empty:
            st.write(f"Area needing attention: **{weakest.index[0]}**.")

        st.write(f"Most-mentioned competitor: **{top_competitor}**.")

    with col2:
        st.markdown("### Recommended next move")

        if avg_score >= 80:
            st.success(
                "Wake Tech is performing well in this dataset. Next step: expand the prompt set and track changes over time."
            )
        elif avg_score >= 60:
            st.warning(
                "Wake Tech has moderate visibility. Next step: review low-scoring prompts and compare competitor content."
            )
        else:
            st.error(
                "Wake Tech visibility is weak in this dataset. Next step: prioritize content improvements for missing or low-scoring topics."
            )