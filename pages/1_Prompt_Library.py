import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Prompt Library",
    layout="wide"
)

st.title("Prompt Library")
st.caption("The prompt library is the AI-search version of a keyword list.")

prompts = pd.read_csv("prompts/prompts.csv")

st.subheader("Current Prompts")
st.dataframe(prompts, width="stretch")

st.divider()

st.subheader("Add New Prompt")

with st.form("add_prompt_form"):
    category = st.text_input("Category")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    prompt = st.text_area("Prompt")

    submitted = st.form_submit_button("Add Prompt")

    if submitted:
        new_id = f"P{len(prompts) + 1:03d}"

        new_row = pd.DataFrame([{
            "prompt_id": new_id,
            "category": category,
            "priority": priority,
            "prompt": prompt
        }])

        updated = pd.concat([prompts, new_row], ignore_index=True)
        updated.to_csv("prompts/prompts.csv", index=False)

        st.success(f"Added prompt {new_id}. Refresh the page to see it.")