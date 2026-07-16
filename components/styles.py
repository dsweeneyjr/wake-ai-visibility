import streamlit as st


def apply_wake_tech_style():
    st.markdown(
        """
        <style>

        /* ========================================
           MAIN APP
        ======================================== */

        .stApp {
            background-color: #ffffff;
        }

        h1,
        h2,
        h3 {
            color: #003057 !important;
        }


        /* ========================================
           SIDEBAR
        ======================================== */

        section[data-testid="stSidebar"] {
            background-color: #003057 !important;
        }

        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }


        /* ========================================
           SIDEBAR NAVIGATION
        ======================================== */

        section[data-testid="stSidebar"] a[aria-current="page"] {
            background-color: #00b5e2 !important;
            color: #ffffff !important;
            border-radius: 6px !important;
        }

        section[data-testid="stSidebar"] a[aria-current="page"] * {
            color: #ffffff !important;
            font-weight: 700 !important;
            text-transform: capitalize !important;
        }


        /* ========================================
           SIDEBAR SELECT / MULTISELECT
        ======================================== */

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #003057 !important;
        }

                /* ========================================
           SIDEBAR TEXT INPUTS
        ======================================== */

        section[data-testid="stSidebar"]
        div[data-testid="stTextInput"] input {
            color: #003057 !important;
            background-color: #ffffff !important;
            caret-color: #003057 !important;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stTextInput"] input::placeholder {
            color: #6b7280 !important;
            opacity: 1 !important;
        }


        /* ========================================
           SIDEBAR MULTISELECT PILLS
        ======================================== */

        section[data-testid="stSidebar"]
        span[data-baseweb="tag"] {
            background-color: #00b5e2 !important;
            color: #ffffff !important;
            border: 1px solid #00b5e2 !important;
            border-radius: 4px !important;
        }

        section[data-testid="stSidebar"]
        span[data-baseweb="tag"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"]
        span[data-baseweb="tag"] svg {
            fill: #ffffff !important;
            color: #ffffff !important;
        }


        /* ========================================
           SIDEBAR CHECKBOX
        ======================================== */

        section[data-testid="stSidebar"]
        div[data-testid="stCheckbox"] label span {
            color: #ffffff !important;
        }


        /* ========================================
           METRIC CARDS
        ======================================== */

        div[data-testid="stMetric"] {
            background-color: #f4f6f8;
            border-left: 5px solid #eaaa00;
            padding: 18px;
            border-radius: 6px;
        }

        div[data-testid="stMetricLabel"] {
            color: #003057 !important;
            font-weight: 700 !important;
        }


        /* ========================================
           STANDARD BUTTONS
        ======================================== */

        div.stButton > button {
            background-color: #003057 !important;
            color: #ffffff !important;
            border: 2px solid #003057 !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
        }

        div.stButton > button * {
            color: #ffffff !important;
        }

        div.stButton > button:hover {
            background-color: #00b5e2 !important;
            color: #ffffff !important;
            border-color: #00b5e2 !important;
        }

        div.stButton > button:hover * {
            color: #ffffff !important;
        }


        /* ========================================
           FORM SUBMIT BUTTONS
        ======================================== */

        div[data-testid="stFormSubmitButton"] > button {
            background-color: #003057 !important;
            color: #ffffff !important;
            border: 2px solid #003057 !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
        }

        div[data-testid="stFormSubmitButton"] > button * {
            color: #ffffff !important;
        }

        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #00b5e2 !important;
            color: #ffffff !important;
            border-color: #00b5e2 !important;
        }

        div[data-testid="stFormSubmitButton"] > button:hover * {
            color: #ffffff !important;
        }


        /* ========================================
           EXPANDERS
        ======================================== */

        div[data-testid="stExpander"] {
            border-left: 5px solid #eaaa00 !important;
            border-radius: 0 8px 8px 0 !important;
            overflow: hidden !important;
        }

        div[data-testid="stExpander"] details {
            border-radius: 0 8px 8px 0 !important;
        }

        div[data-testid="stExpander"] summary {
            border-radius: 0 8px 8px 0 !important;
        }

        div[data-testid="stExpander"] > details {
            border-top-left-radius: 0 !important;
            border-bottom-left-radius: 0 !important;
        }

        /* ========================================
           LINKS
        ======================================== */

        a {
            color: #005eb8;
        }

        </style>
        """,
        unsafe_allow_html=True
    )