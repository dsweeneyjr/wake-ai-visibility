import streamlit as st
from components.styles import apply_wake_tech_style

st.set_page_config(
    page_title="Roadmap",
    layout="wide"
)

apply_wake_tech_style()

st.title("Roadmap")

with open("ROADMAP.md", "r") as file:
    roadmap = file.read()

st.markdown(roadmap)