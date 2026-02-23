import streamlit as st
import pandas as pd
from pymongo import MongoClient

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Strategy Symbol Profit Input",
    layout="centered"
)

# ---------------- STRONG CSS (DATA_EDITOR FIX) ----------------
st.markdown(
    """
    <style>

    /* Page background */
    .main {
        background: linear-gradient(135deg, #eef2ff, #fdf2f8);
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
    }

    /* Header */
    .header-card {
        background: linear-gradient(90deg, #6366f1, #ec4899);
        padding: 18px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
    }

    /* Form */
    div[data-testid="stForm"] {
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }

    /* -------- DATA EDITOR FIX -------- */

    /* Header cells */
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #1e1b4b !important;
        color: white !important;
        font-weight: 700 !important;
        text-align: center !important;
        justify-content: center !important;
    }

    /* SYMBOL column (1st column) */
    div[data-testid="stDataFrame"] div[role="row"] > div:nth-child(1) {
        background-color: #e0e7ff !important;
        color: #1e1b4b !important;
        font-weight: 600 !important;
        text-align: center !important;
        justify-content: center !important;
    }

    /* AMOUNT column (2nd column) */
    div[data-testid="stDataFrame"] div[role="row"] > div:nth-child(2) {
        background-color: #fce7f3 !important;
        color: #831843 !important;
        font-weight: 600 !important;
        text-align: center !important;
        justify-content: center !important;
    }

    /* Save button */
    button[kind="primary"] {
        background: linear-gradient(90deg, #6366f1, #ec4899);
        color: white;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1.4rem;
        border: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
st.markdown(
    """
    <div class="header-card">
        <h3 style="margin:0">📊 Strategy Symbol Profit Input</h3>
        <p style="margin:0; opacity:0.9">Enter Profit for each symbol</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- CONSTANTS ----------------
MONGO_URI = (
    "mongodb+srv://Akash:Akash%405555@stockvertexventures.fxlf1gk.mongodb.net/"
    "?tls=true&tlsAllowInvalidCertificates=true"
)
COLLECTION_NAME = "Selected_Strategies_Inputs"
STRATEGY_ID = "CST0007"

# ---------------- CLIENT ID ----------------
client_id = st.text_input("Client ID", autocomplete="off")
if not client_id:
    st.stop()

# ---------------- MONGO ----------------
@st.cache_resource
def mongo_client():
    return MongoClient(MONGO_URI)

db = mongo_client()[client_id]
collection = db[COLLECTION_NAME]

doc = collection.find_one(
    {"StrategyID": STRATEGY_ID},
    {"_id": 0, "Symbol": 1}
)

if not doc or not doc.get("Symbol"):
    st.error("No symbols found")
    st.stop()

# ---------------- DATA ----------------
df = (
    pd.DataFrame.from_dict(doc["Symbol"], orient="index", columns=["Amount"])
    .reset_index()
    .rename(columns={"index": "Symbol"})
)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)


# ---------------- FORM ----------------
with st.form("symbol_form"):
    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", disabled=True),
            "Amount": st.column_config.NumberColumn("Amount", min_value=0.0)
        }
    )
    save = st.form_submit_button("💾 Save")

# ---------------- SAVE ----------------
if save:
    collection.update_one(
        {"StrategyID": STRATEGY_ID},
        {"$set": {"Symbol": dict(zip(edited_df["Symbol"], edited_df["Amount"]))}}
    )
    st.success("✅ Saved successfully")
