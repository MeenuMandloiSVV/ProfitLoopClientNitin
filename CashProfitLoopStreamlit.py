import streamlit as st
import pandas as pd
import asyncio
import motor.motor_asyncio

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Strategy Symbol Profit Input",
    layout="centered"
)

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #eef2ff, #fdf2f8);
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
    }

    .header-card {
        background: linear-gradient(90deg, #6366f1, #ec4899);
        padding: 18px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
    }

    div[data-testid="stForm"] {
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }

    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #1e1b4b !important;
        color: white !important;
        font-weight: 700 !important;
        text-align: center !important;
        justify-content: center !important;
    }

    div[data-testid="stDataFrame"] div[role="row"] > div:nth-child(1) {
        background-color: #e0e7ff !important;
        color: #1e1b4b !important;
        font-weight: 600 !important;
        text-align: center !important;
        justify-content: center !important;
    }

    div[data-testid="stDataFrame"] div[role="row"] > div:nth-child(2) {
        background-color: #fce7f3 !important;
        color: #831843 !important;
        font-weight: 600 !important;
        text-align: center !important;
        justify-content: center !important;
    }

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

# ---------------- LOAD SECRETS ----------------


# ---------------- LOAD SECRETS ----------------
MONGO_URI = st.secrets["MONGO_URI"]
COLLECTION_NAME = st.secrets["COLLECTION_NAME"]
STRATEGY_ID = st.secrets["STRATEGY_ID"]

# ---------------- CLIENT ID ----------------
client_id = st.text_input("Client ID", autocomplete="off")
if not client_id:
    st.stop()

# ---------------- MONGO CONNECTION ----------------
@st.cache_resource
def get_mongo_client():
    return motor.motor_asyncio.AsyncIOMotorClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

client = get_mongo_client()
db = client[client_id]
collection = db[COLLECTION_NAME]

# ---------------- FETCH DATA (SYNC WRAPPER) ----------------
doc = collection.delegate.find_one(  # 🔥 Use delegate (sync call)
    {"StrategyID": STRATEGY_ID},
    {"_id": 0, "Symbol": 1}
)

if not doc or not doc.get("Symbol"):
    st.error("No symbols found")
    st.stop()

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
    collection.delegate.update_one(   # 🔥 Sync update
        {"StrategyID": STRATEGY_ID},
        {
            "$set": {
                "Symbol": dict(zip(edited_df["Symbol"], edited_df["Amount"]))
            }
        }
    )

    st.success("✅ Saved successfully")

