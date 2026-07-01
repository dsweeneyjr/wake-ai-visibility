import streamlit as st

st.set_page_config(
    page_title="Roadmap",
    layout="wide"
)

st.title("Roadmap")

with open("ROADMAP.md", "r") as file:
    roadmap = file.read()

st.markdown(roadmap)