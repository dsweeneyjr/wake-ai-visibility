import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Recommendations",
    layout="wide"
)

st.title("Recommendations")
st.caption("Priority actions based on AI visibility results.")

df = pd.read_csv("data/results.csv")
df["run_date"] = pd.to_datetime(df["run_date"], errors="coerce")

latest_scan_id = (
    df.sort_values(["run_date", "scan_id"])["scan_id"].iloc[-1]
    if not df.empty
    else None
)

latest = df[df["scan_id"] == latest_scan_id] if latest_scan_id else df

opportunities = latest[
    (latest["wake_tech_mentioned"] == "No") |
    (latest["score"] < 70)
].sort_values(["wake_tech_mentioned", "score"])

if opportunities.empty:
    st.success("No major recommendations found in the latest scan.")
else:
    st.subheader("Recommended Action Plan")

    scored_opportunities = opportunities.copy()

    scored_opportunities["severity"] = scored_opportunities.apply(
        lambda row: 100 if row["wake_tech_mentioned"] == "No" else 0,
        axis=1
    )

    scored_opportunities["severity"] += 100 - scored_opportunities["score"]

    category_summary = (
        scored_opportunities
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
        f"Start with **{top_category}**. It has the weakest visibility in the latest scan "
        "and should be treated as the first content improvement priority."
    )

    summary_cols = st.columns(4)

    summary_cols[0].metric(
        "Priority Category",
        top_category
    )

    summary_cols[1].metric(
        "Issues Found",
        int(category_summary.iloc[0]["issues"])
    )

    summary_cols[2].metric(
        "Missed Mentions",
        int(category_summary.iloc[0]["missed_mentions"])
    )

    summary_cols[3].metric(
        "Avg Score",
        round(category_summary.iloc[0]["avg_score"], 1)
    )

    for _, row in opportunities.iterrows():
        priority = "High" if row["wake_tech_mentioned"] == "No" else "Medium"
        competitors = row["competitors"] if pd.notna(row["competitors"]) else "No competitors listed"

        with st.container(border=True):
            st.markdown(f"### {priority} Priority: {row['category']}")

            col1, col2, col3 = st.columns(3)

            col1.metric("Platform", row["platform"])
            col2.metric("Visibility Score", row["score"])
            col3.metric("Wake Tech Mentioned", row["wake_tech_mentioned"])

            st.markdown("**Prompt**")
            st.write(row["prompt"])

            st.markdown("**What happened**")

            if row["wake_tech_mentioned"] == "No":
                st.error(
                    f"Wake Tech was not mentioned. The response mentioned: {competitors}."
                )
            else:
                st.warning(
                    f"Wake Tech was mentioned, but visibility was weak. Competitors mentioned: {competitors}."
                )

            st.markdown("**Recommended action**")

            if row["category"] == "Nursing":
                st.write(
                    "- Strengthen nursing program pages with admissions steps, clinical experience, outcomes, and FAQs.\n"
                    "- Add comparison-friendly content for students evaluating Raleigh-area nursing programs.\n"
                    "- Make NCLEX, accreditation, cost, and application information easier for AI tools to extract."
                )
            elif row["category"] == "Cybersecurity":
                st.write(
                    "- Add clearer cybersecurity program pathways, certifications, career outcomes, and employer relevance.\n"
                    "- Build FAQ content around cybersecurity careers, cost, transfer options, and job readiness.\n"
                    "- Compare Wake Tech’s offering against nearby community college programs."
                )
            elif row["category"] == "Transfer":
                st.write(
                    "- Strengthen transfer pathway pages with NC State, UNC, ECU, and other destination examples.\n"
                    "- Add plain-language transfer FAQs and internal links to advising resources.\n"
                    "- Add student success stories or sample pathways."
                )
            elif row["category"] == "Financial Aid":
                st.write(
                    "- Improve financial aid pages with plain-language answers about FAFSA, scholarships, deadlines, and eligibility.\n"
                    "- Add FAQs for affordability, aid timelines, and how Wake Tech compares with other NC community colleges.\n"
                    "- Make cost and aid information easier to cite and summarize."
                )
            else:
                st.write(
                    "- Compare Wake Tech content against the competitors AI tools are mentioning.\n"
                    "- Add clearer FAQs, outcomes, costs, internal links, and structured content.\n"
                    "- Create concise answer-style sections that directly address this prompt."
                )

            st.markdown("**Why this matters**")
            st.write(
                "This is a content opportunity because AI tools are either skipping Wake Tech "
                "or not describing it strongly enough compared with competitors."
            )