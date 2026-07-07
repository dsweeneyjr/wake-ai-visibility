import pandas as pd
import streamlit as st
from pathlib import Path
from components.styles import apply_wake_tech_style

PROMPTS_FILE = Path("prompts/prompts.csv")

st.set_page_config(
    page_title="Prompt Library",
    layout="wide"
)

apply_wake_tech_style()

st.title("Prompt Library")
st.caption("Questions we want the AI tools to monitor over time.")

prompts = pd.read_csv(PROMPTS_FILE)

st.metric("Total Prompts", len(prompts))

st.subheader("Current Prompts")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input("Search prompts", placeholder="Search by keyword...")

with col2:
    category_filter = st.selectbox(
        "Category",
        ["All"] + sorted(prompts["category"].dropna().unique().tolist())
    )

with col3:
    priority_filter = st.selectbox(
        "Priority",
        ["All"] + sorted(prompts["priority"].dropna().unique().tolist())
    )

filtered_prompts = prompts.copy()

if search:
    filtered_prompts = filtered_prompts[
        filtered_prompts["prompt"].str.contains(search, case=False, na=False) |
        filtered_prompts["category"].str.contains(search, case=False, na=False)
    ]

if category_filter != "All":
    filtered_prompts = filtered_prompts[
        filtered_prompts["category"] == category_filter
    ]

if priority_filter != "All":
    filtered_prompts = filtered_prompts[
        filtered_prompts["priority"] == priority_filter
    ]

st.dataframe(filtered_prompts, use_container_width=True)

st.divider()

st.subheader("Add New Prompt")

existing_categories = sorted(prompts["category"].dropna().unique().tolist())
category_options = existing_categories + ["Add new category..."]

category_choice = st.selectbox(
    "Category",
    category_options,
    key="category_choice"
)

with st.form("add_prompt_form", clear_on_submit=True):

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
        existing_ids = prompts["prompt_id"].astype(str).str.replace("P", "", regex=False)
        existing_ids = pd.to_numeric(existing_ids, errors="coerce").dropna()

        next_id_number = int(existing_ids.max()) + 1 if not existing_ids.empty else 1
        new_id = f"P{next_id_number:03d}"

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

        st.divider()

st.divider()

st.subheader("Edit Prompt")

edit_options = {
    f"{row['prompt_id']} — {row['prompt']}": row["prompt_id"]
    for _, row in prompts.iterrows()
}

edit_label = st.selectbox(
    "Select prompt to edit",
    list(edit_options.keys()),
    key="edit_prompt_select"
)

edit_id = edit_options[edit_label]
edit_row = prompts[prompts["prompt_id"] == edit_id].iloc[0]

with st.form("edit_prompt_form"):
    edited_category = st.text_input(
        "Category",
        value=edit_row["category"]
    )

    edited_priority = st.selectbox(
        "Priority",
        ["High", "Medium", "Low"],
        index=["High", "Medium", "Low"].index(edit_row["priority"])
        if edit_row["priority"] in ["High", "Medium", "Low"] else 1
    )

    edited_prompt = st.text_area(
        "Prompt",
        value=edit_row["prompt"]
    )

    edit_submitted = st.form_submit_button("Save Changes")

if edit_submitted:
    prompts.loc[prompts["prompt_id"] == edit_id, "category"] = edited_category.strip()
    prompts.loc[prompts["prompt_id"] == edit_id, "priority"] = edited_priority
    prompts.loc[prompts["prompt_id"] == edit_id, "prompt"] = edited_prompt.strip()

    prompts.to_csv(PROMPTS_FILE, index=False)

    st.success(f"Updated prompt {edit_id}.")
    st.rerun()

st.subheader("Remove Prompt")

prompt_options = {
    f"{row['prompt_id']} — {row['prompt']}": row["prompt_id"]
    for _, row in prompts.iterrows()
}

prompt_to_delete_label = st.selectbox(
    "Select prompt to remove",
    list(prompt_options.keys())
)

prompt_to_delete_id = prompt_options[prompt_to_delete_label]

if st.button("Delete Prompt", type="primary"):
    updated = prompts[
        prompts["prompt_id"] != prompt_to_delete_id
    ]

    updated.to_csv(PROMPTS_FILE, index=False)

    st.success(f"Deleted prompt {prompt_to_delete_id}.")
    st.rerun()