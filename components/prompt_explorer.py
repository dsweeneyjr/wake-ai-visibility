import pandas as pd
import streamlit as st


def show_prompt_explorer(df):
    st.subheader("Prompt Explorer")

    prompt_options = df[["prompt_id", "prompt"]].drop_duplicates()

    if prompt_options.empty:
        st.info("No prompts available.")
        return

    selected_prompt = st.selectbox(
        "Choose a prompt",
        prompt_options["prompt"].tolist()
    )

    prompt_rows = df[df["prompt"] == selected_prompt]

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