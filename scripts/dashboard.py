import pandas as pd
import streamlit as st

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

col1, col2, col3, col4 = st.columns(4)

avg_score = round(filtered["score"].mean(), 1) if not filtered.empty else 0
mention_rate = round((filtered["wake_tech_mentioned"] == "Yes").mean() * 100, 1) if not filtered.empty else 0
prompts_evaluated = filtered["prompt_id"].nunique()
platforms_evaluated = filtered["platform"].nunique()

col1.metric("Average Visibility", avg_score)
col2.metric("Mention Rate", f"{mention_rate}%")
col3.metric("Prompts Evaluated", prompts_evaluated)
col4.metric("AI Platforms", platforms_evaluated)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Average Visibility by Platform")
    platform_scores = filtered.groupby("platform")["score"].mean().reset_index()
    st.bar_chart(platform_scores, x="platform", y="score")

with right:
    st.subheader("Average Visibility by Category")
    category_scores = filtered.groupby("category")["score"].mean().reset_index()
    st.bar_chart(category_scores, x="category", y="score")

st.divider()

st.subheader("Prompt Explorer")

prompt_options = filtered[["prompt_id", "prompt"]].drop_duplicates()

if not prompt_options.empty:
    selected_prompt = st.selectbox(
        "Choose a prompt",
        prompt_options["prompt"].tolist()
    )

    prompt_rows = filtered[filtered["prompt"] == selected_prompt]

    for _, row in prompt_rows.iterrows():
        with st.expander(f"{row['platform']} — Score: {row['score']}"):
            st.write(f"**Wake Tech Mentioned:** {row['wake_tech_mentioned']}")
            st.write(f"**Position:** {row['position']}")
            st.write(f"**Competitors:** {row['competitors']}")
            st.write(f"**Wake Tech URL:** {row['wake_tech_url']}")
            st.write(f"**Notes:** {row['notes']}")

            if "response" in row and pd.notna(row["response"]):
                st.markdown("### AI Response")
                st.write(row["response"])
            else:
                st.info("No response text added yet.")
else:
    st.info("No prompts available.")

st.divider()

st.subheader("Competitor Mentions")

competitor_rows = []

for competitors in filtered["competitors"].dropna():
    for competitor in str(competitors).split("|"):
        competitor = competitor.strip()
        if competitor:
            competitor_rows.append(competitor)

if competitor_rows:
    competitor_df = pd.Series(competitor_rows).value_counts().reset_index()
    competitor_df.columns = ["Competitor", "Mentions"]
    st.dataframe(competitor_df, width="stretch")
else:
    st.info("No competitors found yet.")

opportunities = filtered[
    (filtered["wake_tech_mentioned"] == "No") |
    (filtered["score"] < 70)
]

st.subheader("Insights")

for _, row in opportunities.iterrows():

    if row["wake_tech_mentioned"] == "No":
        message = (
            f"🚨 **{row['platform']}** did not recommend Wake Tech for this prompt.\n\n"
            f"Instead it mentioned **{row['competitors']}**.\n\n"
            "Recommendation: Review this topic and compare Wake Tech's content with competitors."
        )

    elif row["score"] < 70:
        message = (
            f"⚠️ Wake Tech appeared in **{row['platform']}**, but visibility is weak "
            f"(Score: {row['score']}).\n\n"
            "Recommendation: Expand content, FAQs, outcomes, and structured data."
        )

    else:
        message = (
            f"✅ Strong visibility in **{row['platform']}**."
        )

    with st.expander(f"{row['platform']} • {row['category']} • Score {row['score']}"):
        st.markdown(message)

st.divider()

st.subheader("Raw Data")

st.dataframe(filtered, width="stretch")