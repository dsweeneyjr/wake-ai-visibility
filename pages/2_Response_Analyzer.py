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

    wake_terms = [
        "wake tech",
        "wake technical",
        "wake technical community college"
    ]

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

    school_mentions = []

    for term in wake_terms:
        match = re.search(re.escape(term), text)
        if match:
            school_mentions.append({
                "name": "Wake Tech",
                "start": match.start()
            })
            break

    competitors = []

    for competitor in known_competitors:
        match = re.search(re.escape(competitor.lower()), text)
        if match:
            competitors.append(competitor)
            school_mentions.append({
                "name": competitor,
                "start": match.start()
            })

    school_mentions = sorted(school_mentions, key=lambda x: x["start"])

    wake_mentioned = any(item["name"] == "Wake Tech" for item in school_mentions)

    if wake_mentioned:
        position = next(
            index + 1
            for index, item in enumerate(school_mentions)
            if item["name"] == "Wake Tech"
        )
    else:
        position = 0

    urls = re.findall(r"https?://\S+", response_text)

    wake_urls = [url for url in urls if "waketech.edu" in url.lower()]
    competitor_urls = [url for url in urls if "waketech.edu" not in url.lower()]

    wake_mentions_count = sum(text.count(term) for term in wake_terms)

    positive_terms = [
        "recommended",
        "strong",
        "best",
        "top",
        "good option",
        "excellent",
        "well-regarded",
        "affordable",
        "comprehensive"
    ]

    positive_context = any(term in text for term in positive_terms)

    score = 0

    if wake_mentioned:
        score += 30

        if position == 1:
            score += 20
        elif position == 2:
            score += 10
        elif position == 3:
            score += 5

        score += min(wake_mentions_count * 5, 15)

    if wake_urls:
        score += 20

    if positive_context and wake_mentioned:
        score += 15

    competitors_before_wake = 0

    if wake_mentioned:
        wake_start = next(
            item["start"]
            for item in school_mentions
            if item["name"] == "Wake Tech"
        )

        competitors_before_wake = len([
            item for item in school_mentions
            if item["name"] != "Wake Tech" and item["start"] < wake_start
        ])

        score -= competitors_before_wake * 10
    else:
        score -= min(len(competitors) * 5, 20)

    score = max(0, min(score, 100))

    if not wake_mentioned:
        notes = "Wake Tech was not mentioned."
    elif position > 3:
        notes = "Wake Tech was mentioned, but appeared behind several competitors."
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

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Wake Tech Mentioned",
           analysis["wake_tech_mentioned"]
        )

        col2.metric(
            "Detected Position",
            analysis["position"] if analysis["position"] > 0 else "N/A"
        )

        col3.metric(
            "Visibility Score",
            analysis["score"]
        )

        col4.metric(
            "Wake Tech URLs",
            len(analysis["wake_tech_url"].split("|"))
            if analysis["wake_tech_url"]
            else 0
        )

        st.write("**Competitors Mentioned:**")

        competitor_display = (
            analysis["competitors"].replace("|", " • ")
            if analysis["competitors"]
            else "None detected"
        )

        st.write(competitor_display)

        st.write("**Recommendation:**")
        if analysis["wake_tech_mentioned"] == "No":
            st.error("Review this topic and compare Wake Tech content against mentioned competitors.")
        elif analysis["score"] < 70:
            st.warning("Wake Tech was mentioned, but visibility is weak. Review citations, FAQs, and page depth.")
        else:
            st.success("Wake Tech has strong visibility in this response.")

        st.write("**Analysis Notes:**")
        st.write(analysis["notes"])

        st.session_state["latest_analysis"] = analysis
        st.session_state["latest_response"] = response

        with st.expander("View analyzed response"):
            st.write(st.session_state["latest_response"])


if "latest_analysis" in st.session_state:
    st.divider()
    st.subheader("Save Result")

    if st.button("Save to Results"):
        analysis = st.session_state["latest_analysis"]
        now = datetime.now()

        new_row = {
            "run_date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "scan_id": f"manual_{now.strftime('%Y%m%d_%H%M%S')}",
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