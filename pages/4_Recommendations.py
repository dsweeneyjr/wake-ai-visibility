import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Recommendations",
    layout="wide"
)

st.title("Recommendations")
st.caption("Priority actions based on AI visibility results.")

df = pd.read_csv("data/results.csv")

opportunities = df[
    (df["wake_tech_mentioned"] == "No") |
    (df["score"] < 70)
]

if opportunities.empty:
    st.success("No major recommendations found yet.")
else:
    for _, row in opportunities.iterrows():
        priority = "High" if row["wake_tech_mentioned"] == "No" else "Medium"

        with st.container(border=True):
            st.markdown(f"### {row['category']}")

            col1, col2, col3 = st.columns(3)

            col1.metric("Priority", priority)
            col2.metric("Platform", row["platform"])
            col3.metric("Visibility Score", row["score"])

            st.markdown("**Prompt**")
            st.write(row["prompt"])

            st.markdown("**What happened**")

            if row["wake_tech_mentioned"] == "No":
                st.error(
                    f"Wake Tech was not mentioned. The response mentioned: {row['competitors']}."
                )
            else:
                st.warning(
                    f"Wake Tech was mentioned, but visibility was weak. Competitors mentioned: {row['competitors']}."
                )

            st.markdown("**Recommended action**")

            if row["category"] == "Nursing":
                st.write(
                    "- Add or strengthen NCLEX pass-rate content\n"
                    "- Add clinical partnership information\n"
                    "- Add FAQ content for prospective nursing students\n"
                    "- Make the nursing program page more citation-friendly"
                )
            elif row["category"] == "Cybersecurity":
                st.write(
                    "- Add industry certification details\n"
                    "- Add career outcomes and salary information\n"
                    "- Add employer partnership information\n"
                    "- Add FAQ content around cybersecurity careers"
                )
            elif row["category"] == "Transfer":
                st.write(
                    "- Strengthen transfer pathway content\n"
                    "- Add NC State, UNC, and ECU transfer examples\n"
                    "- Add student success stories\n"
                    "- Improve internal links to transfer resources"
                )
            else:
                st.write(
                    "- Compare Wake Tech content against cited competitors\n"
                    "- Add clearer FAQs\n"
                    "- Add career outcomes\n"
                    "- Improve page depth and internal linking"
                )

            st.markdown("**Why this matters**")
            st.write(
                "This is a content opportunity because AI tools are either not recommending Wake Tech "
                "or are recommending competitors more strongly."
            )