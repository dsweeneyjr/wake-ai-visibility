import streamlit as st


def apply_wake_tech_style():
    st.markdown(
        """
        <style>
        /* MAIN APP */
        .stApp {
            background-color: #ffffff;
        }

        /* HEADINGS */
        h1, h2, h3 {
            color: #003057 !important;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #003057 !important;
        }

        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        /* SIDEBAR INPUT AREAS */
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] span {
            color: #003057 !important;
        }

        /* METRIC CARDS */
        div[data-testid="stMetric"] {
            background-color: #f4f6f8;
            border-left: 5px solid #eaaa00;
            padding: 18px;
            border-radius: 6px;
        }

        div[data-testid="stMetricLabel"] {
            color: #003057 !important;
            font-weight: 700;
        }

        /* BUTTONS */
        div.stButton > button {
            background-color: #003057 !important;
            color: #ffffff !important;
            border: 2px solid #003057 !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
        }

        div.stButton > button:hover {
            background-color: #eaaa00 !important;
            color: #003057 !important;
            border-color: #eaaa00 !important;
        }

        /* CONTAINERS */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #d6dce1;
        }

        /* EXPANDERS */
        div[data-testid="stExpander"] {
            border-left: 5px solid #eaaa00 !important;
        }

        /* LINKS */
        a {
            color: #005eb8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )