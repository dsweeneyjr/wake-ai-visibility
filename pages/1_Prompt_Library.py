import pandas as pd
import streamlit as st
from pathlib import Path

PROMPTS_FILE = Path("prompts/prompts.csv")

st.set_page_config(
    page_title="Prompt Library",
    layout="wide"
)

st.title("Prompt Library")
st.caption("Questions we want the AI tools to monitor over time.")

prompts = pd.read_csv(PROMPTS_FILE)

st.subheader("Current Prompts")
st.dataframe(prompts, width="stretch")

st.divider()

st.subheader("Add New Prompt")

existing_categories = sorted(prompts["category"].dropna().unique().tolist())
category_options = existing_categories + ["Add new category..."]

with st.form("add_prompt_form"):
    category_choice = st.selectbox(
        "Category",
        category_options,
        index=0 if existing_categories else len(category_options) - 1
    )

    if category_choice == "Add new category...":
        category = st.text_input(
            "New Category",
            placeholder="Example: Cybersecurity"
        )
    else:
        category = category_choice

    priority = st.selectbox("Priority", ["High", "Medium", "Low"])

    prompt = st.text_area(
        "Prompt",
        placeholder="Example: Which community college has the best cybersecurity program in North Carolina?"
    )

    submitted = st.form_submit_button("Add Prompt")

    if submitted:
        if not category.strip() or not prompt.strip():
            st.error("Category and prompt are required.")
        else:
            new_id = f"P{len(prompts) + 1:03d}"

            new_row = pd.DataFrame([{
                "prompt_id": new_id,
                "category": category.strip(),
                "priority": priority,
                "prompt": prompt.strip()
            }])

            updated = pd.concat([prompts, new_row], ignore_index=True)
            updated.to_csv(PROMPTS_FILE, index=False)

            st.success(f"Added prompt {new_id}.")
            st.rerun()