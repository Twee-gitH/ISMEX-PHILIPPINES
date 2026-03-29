import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

# --- DATABASE & CONSTANTS ---
DB_FILE = "bpsm_data.json"
DAILY_ROI = 0.20 

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return None

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, default=str)

# --- MOBILE-FIRST CSS (BPSM THEME) ---
st.set_page_config(page_title="BPSM - Bagong Pilipinas", page_icon="🇵🇭", layout="centered")

st.markdown("""
    <style>
    /* Official Header Style */
    .main-header {
        text-align: center;
        color: #0038a8;
        font-family: 'Arial Black', sans-serif;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #ce1126;
        font-size: 0.8rem;
        letter-spacing: 2px;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: #fdfdfd;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #0038a8;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    /* Action Buttons */
    .stButton>button {
        height: 3.5rem;
        border-radius: 8px;
        background-color: #0038a8 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTH ---
if 'user' not in st.session_state:
    st.session_state.user = load_db()

if st.session_state.user is None:
    st.markdown("<h1 class='main-header'>BAGONG PILIPINAS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>STOCK MARKET PORTAL</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.write("### 🔑 Investor Access")
        name = st.text_input("FULL NAME (Per Government ID)").upper()
        pin = st.text_input("SECURE 6-DIGIT PIN", type="password", max_chars=6)
        
        if st.button("REGISTER SECURE ACCOUNT", use_container_width=True):
            if name and len(pin) == 6:
                user_data = {"name": name, "pin": pin, "wallet_balance": 0.0, "investments": [], "transactions": []}
                save_db(user_data); st.session_state.user = user_data; st.rerun()
            else:
                st.error("Full name and 6-digit PIN required.")
    st.stop()

# --- MAIN DASHBOARD ---
user = st.session_state.user

st.markdown("<h2 class='main-header' style='font-size: 1.5rem;'>BPSM DASHBOARD</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>Investor: <b>{user['name']}</b></p>", unsafe_allow_html=True)

# Calculation Logic
matured_total = sum((i['amount'] + i['profit']) for i in user['investments'] if datetime.now() >= datetime.fromisoformat(i['release_time']))
active_total = sum(i['amount'] for i in user['investments'] if datetime.now() < datetime.fromisoformat(i['release_time']))
liquid_bal = user['wallet_balance'] + matured_total

# Metrics Stacked for Mobile
st.metric("AVAILABLE LIQUIDITY", f"₱{liquid_bal:,.2f}")
st.metric("MARKET EXPOSURE", f"₱{active_total:,.2f}")

# --- TABS ---
tab_trade, tab_funds, tab_logs = st.tabs(["📊 TRADE", "💰 FUNDS", "📄 OFFICIAL LOGS"])

with tab_trade:
    st.info("📢 **Market Notice:** All stock positions mature in 24 hours with a fixed 20% dividend yield.")
    trade_amt = st.number_input("Purchase Amount (PHP)", min_value=500.0, step=500.0)
    
    if st.button("EXECUTE BUY ORDER", use_container_width=True):
        if liquid_bal >= trade_amt:
            new_inv = {
                "amount": trade_amt, "profit": trade_amt * DAILY_ROI,
                "start_time": datetime.now().isoformat(),
                "release_time": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            user['investments'].append(new_inv)
            if user['wallet_balance'] >= trade_amt: user['wallet_balance'] -= trade_amt
            save_db(user); st.success("Trade Executed Successfully!"); st.rerun()
        else:
            st.error("Insufficient Funds. Visit the FUNDS tab to deposit.")

    st.write("---")
    st.write("### ⏳ Active Positions")
    for i, inv in enumerate(user['investments']):
        end = datetime.fromisoformat(inv['release_time'])
        if datetime.now() < end:
            st.write(f"**Stock Value:** ₱{inv['amount']:,} | **Yield:** +₱{inv['profit']:,}")
            st.caption(f"Status: Trading... {str(end - datetime.now()).split('.')[0]} remaining")
            st.divider()

with tab_funds:
    mode = st.radio("Action", ["Deposit Funds", "Withdraw Dividends"], horizontal=True)
    
    if mode == "Deposit Funds":
        st.write("### Transfer via GCash/Maya")
        st.code("Account: 0912-345-6789\nName: BPSM ADMIN")
        ref = st.text_input("Transaction Reference ID")
        amt = st.number_input("Amount Sent", min_value=100.0)
        if st.button("SUBMIT DEPOSIT PROOF", use_container_width=True):
            user['transactions'].append({"date": datetime.now().isoformat(), "type": "DEPOSIT", "amt": amt, "status": "PENDING", "ref": ref})
            save_db(user); st.toast("Verification request sent.")
            
    else:
        st.write("### Withdraw to Wallet")
        w_amt = st.number_input("Withdrawal Amount", min_value=500.0)
        w_pin = st.text_input("Confirm 6-Digit PIN", type="password")
        if st.button("REQUEST PAYOUT", use_container_width=True):
            if w_pin == user['pin
            
