import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


RESULTS_FILE = Path("data/results.csv")
PROMPTS_FILE = Path("prompts/prompts.csv")


st.set_page_config(
    page_title="Response Analyzer",
    layout="wide"
)

st.title("Response Analyzer")
st.caption("Paste an AI response, analyze visibility, and save it to the dataset.")


prompts = pd.read_csv(PROMPTS_FILE)
results = pd.read_csv(RESULTS_FILE)


prompt_choices = {
    f"{row['prompt_id']} — {row['category']} — {row['prompt']}": row
    for _, row in prompts.iterrows()
}

selected_prompt_label = st.selectbox(
    "Select Prompt",
    list(prompt_choices.keys())
)

selected_prompt = prompt_choices[selected_prompt_label]

platform = st.selectbox(
    "AI Platform",
    ["ChatGPT", "Gemini", "Perplexity", "Other"]
)

response = st.text_area("AI Response", height=300)


def analyze_response(response_text):
    text = response_text.lower()

    wake_mentioned = "wake tech" in text or "wake technical" in text

    known_competitors = [
        "Durham Tech",
        "Central Piedmont",
        "CPCC",
        "NC State",
        "UNC",
        "ECU",
        "Fayetteville Tech",
        "Johnston Community College",
        "Wake Forest",
        "Campbell University",
        "Pitt Community College"
    ]

    competitors = []

    for competitor in known_competitors:
        if competitor.lower() in text:
            competitors.append(competitor)

    urls = re.findall(r"https?://\S+", response_text)

    wake_urls = [url for url in urls if "waketech.edu" in url.lower()]
    competitor_urls = [url for url in urls if "waketech.edu" not in url.lower()]

    score = 0

    if wake_mentioned:
        score += 50

    if wake_urls:
        score += 25

    if competitors:
        score -= min(len(competitors) * 5, 20)

    score = max(0, min(score, 100))

    if wake_mentioned:
        position = 1
    else:
        position = 0

    if not wake_mentioned:
        notes = "Wake Tech was not mentioned."
    elif score < 70:
        notes = "Wake Tech was mentioned, but visibility appears weak."
    else:
        notes = "Wake Tech has strong visibility."

    return {
        "wake_tech_mentioned": "Yes" if wake_mentioned else "No",
        "position": position,
        "competitors": "|".join(competitors),
        "wake_tech_url": "|".join(wake_urls),
        "competitor_urls": "|".join(competitor_urls),
        "score": score,
        "notes": notes
    }


if st.button("Analyze Response"):
    if not response.strip():
        st.error("Paste an AI response first.")
    else:
        analysis = analyze_response(response)

        st.divider()
        st.subheader("Analysis")

        col1, col2, col3 = st.columns(3)

        col1.metric("Wake Tech Mentioned", analysis["wake_tech_mentioned"])
        col2.metric("Visibility Score", analysis["score"])
        col3.metric("URLs Found", len(analysis["wake_tech_url"].split("|")) if analysis["wake_tech_url"] else 0)

        st.write("**Competitors Mentioned:**")
        st.write(analysis["competitors"] if analysis["competitors"] else "None detected")

        st.write("**Recommendation:**")
        if analysis["wake_tech_mentioned"] == "No":
            st.error("Review this topic and compare Wake Tech content against mentioned competitors.")
        elif analysis["score"] < 70:
            st.warning("Wake Tech was mentioned, but visibility is weak. Review citations, FAQs, and page depth.")
        else:
            st.success("Wake Tech has strong visibility in this response.")

        st.session_state["latest_analysis"] = analysis
        st.session_state["latest_response"] = response


if "latest_analysis" in st.session_state:
    st.divider()
    st.subheader("Save Result")

    if st.button("Save to Results"):
        analysis = st.session_state["latest_analysis"]

        new_row = {
            "run_date": datetime.now().strftime("%Y-%m-%d"),
            "platform": platform,
            "prompt_id": selected_prompt["prompt_id"],
            "category": selected_prompt["category"],
            "prompt": selected_prompt["prompt"],
            "wake_tech_mentioned": analysis["wake_tech_mentioned"],
            "position": analysis["position"],
            "competitors": analysis["competitors"],
            "wake_tech_url": analysis["wake_tech_url"],
            "competitor_urls": analysis["competitor_urls"],
            "score": analysis["score"],
            "notes": analysis["notes"],
            "response": st.session_state["latest_response"]
        }

        updated_results = pd.concat(
            [results, pd.DataFrame([new_row])],
            ignore_index=True
        )

        updated_results.to_csv(RESULTS_FILE, index=False)

        st.success("Result saved. Go back to the Dashboard to see it included.")