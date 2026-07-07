import pandas as pd
import streamlit as st
from components.styles import apply_wake_tech_style


st.set_page_config(
    page_title="Recommendations",
    layout="wide"
)

apply_wake_tech_style()

st.title("Recommendations")
st.caption("Priority actions based on AI visibility results.")

df = pd.read_csv("data/results.csv")
df["_row_order"] = range(len(df))
df["run_date"] = pd.to_datetime(df["run_date"], errors="coerce")


def format_competitors(value):
    if pd.isna(value) or not str(value).strip():
        return "No competitors listed"
    return str(value).replace("|", " • ")


def get_latest_scan(data):
    if data.empty or "scan_id" not in data.columns:
        return data

    latest_scan_id = (
        data
        .sort_values("_row_order")["scan_id"]
        .iloc[-1]
    )

    return data[data["scan_id"] == latest_scan_id]


def get_priority(row):
    if row["wake_tech_mentioned"] == "No":
        return "High"
    if row["score"] < 55:
        return "High"
    if row["score"] < 70:
        return "Medium"
    return "Low"


def get_recommendations(row):
    actions = []

    if row["wake_tech_mentioned"] == "No":
        actions.append(
            "Create or strengthen content that directly answers this exact question."
        )
        actions.append(
            "Compare Wake Tech’s page content against the competitors AI tools are already mentioning."
        )
    else:
        actions.append(
            "Improve the existing page so Wake Tech is described more clearly and confidently."
        )

    if row["position"] > 1:
        actions.append(
            "Add stronger comparison-friendly content so Wake Tech appears earlier in AI-generated answers."
        )

    if pd.isna(row["wake_tech_url"]) or not str(row["wake_tech_url"]).strip():
        actions.append(
            "Make the most relevant Wake Tech page easier for AI tools to identify, cite, and summarize."
        )

    if row["score"] < 70:
        actions.append(
            "Add plain-language FAQs, outcomes, costs, admissions steps, internal links, and structured headings."
        )

    if pd.notna(row["competitors"]) and str(row["competitors"]).strip():
        actions.append(
            f"Review competitor visibility for: {format_competitors(row['competitors'])}."
        )

    return actions


latest = get_latest_scan(df)

opportunities = latest[
    (latest["wake_tech_mentioned"] == "No") |
    (latest["score"] < 70)
].copy()

if opportunities.empty:
    st.success("No major recommendations found in the latest scan.")
else:
    st.subheader("Recommended Action Plan")

    opportunities["priority"] = opportunities.apply(get_priority, axis=1)

    priority_rank = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    opportunities["priority_rank"] = opportunities["priority"].map(priority_rank)

    opportunities["severity"] = 100 - opportunities["score"]

    opportunities.loc[
        opportunities["wake_tech_mentioned"] == "No",
        "severity"
    ] += 100

    opportunities.loc[
        opportunities["position"] > 1,
        "severity"
    ] += 25

    opportunities = opportunities.sort_values(
        ["priority_rank", "severity", "score"],
        ascending=[True, False, True]
    )

    category_summary = (
        opportunities
        .groupby("category")
        .agg(
            avg_score=("score", "mean"),
            issues=("prompt_id", "count"),
            missed_mentions=("wake_tech_mentioned", lambda x: (x == "No").sum()),
            severity=("severity", "sum")
        )
        .reset_index()
        .sort_values(
            ["missed_mentions", "severity", "avg_score"],
            ascending=[False, False, True]
        )
    )

    top_category = category_summary.iloc[0]["category"]

    st.warning(
        f"Start with **{top_category}**. It has the highest-priority visibility issues "
        "in the latest scan."
    )

    summary_cols = st.columns(4)

    summary_cols[0].metric("Priority Category", top_category)
    summary_cols[1].metric("Issues Found", int(category_summary.iloc[0]["issues"]))
    summary_cols[2].metric("Missed Mentions", int(category_summary.iloc[0]["missed_mentions"]))
    summary_cols[3].metric("Avg Score", round(category_summary.iloc[0]["avg_score"], 1))

    for _, row in opportunities.iterrows():
        competitors = format_competitors(row["competitors"])

        with st.container(border=True):
            st.markdown(f"### {row['priority']} Priority: {row['category']}")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Platform", row["platform"])
            col2.metric("Visibility Score", row["score"])
            col3.metric("Mentioned", row["wake_tech_mentioned"])
            col4.metric(
                "Position",
                int(row["position"]) if row["position"] > 0 else "N/A"
            )

            st.markdown("**Prompt**")
            st.write(row["prompt"])

            st.markdown("**What happened**")

            if row["wake_tech_mentioned"] == "No":
                st.error(
                    f"Wake Tech was not mentioned. Competitors surfaced instead: {competitors}."
                )
            elif row["position"] > 1:
                st.warning(
                    f"Wake Tech was mentioned, but appeared in position {int(row['position'])}. "
                    f"Competitors mentioned: {competitors}."
                )
            else:
                st.warning(
                    f"Wake Tech was mentioned, but the visibility score was weak. "
                    f"Competitors mentioned: {competitors}."
                )

            st.markdown("**Recommended actions**")

            for action in get_recommendations(row):
                st.write(f"- {action}")

            st.markdown("**Why this matters**")
            st.write(
                "This is a content opportunity because AI tools are either skipping Wake Tech, "
                "placing competitors ahead of Wake Tech, or not describing Wake Tech strongly enough."
            )