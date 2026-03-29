import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

# --- 1. DATA PERSISTENCE ---
DB_FILE = "bpsm_official_data.json"
DAILY_ROI = 0.20 

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, default=str)

# --- 2. MOBILE-FIRST UI SETUP ---
st.set_page_config(page_title="BPSM - Bagong Pilipinas", page_icon="🇵🇭", layout="centered")

st.markdown("""
    <style>
    .main-header { text-align: center; color: #0038a8; font-family: 'Arial Black', sans-serif; margin-bottom: 0; }
    .sub-header { text-align: center; color: #ce1126; font-size: 0.8rem; letter-spacing: 2px; margin-top: -5px; margin-bottom: 20px; }
    [data-testid="stMetric"] { background: #ffffff; border-radius: 12px; padding: 15px; border: 1px solid #0038a8; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .stButton>button { height: 3.5rem; border-radius: 10px; background-color: #0038a8 !important; color: white !important; font-weight: bold; width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 10px 10px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION & AUTH ---
if 'user' not in st.session_state:
    st.session_state.user = load_db()

if st.session_state.user is None:
    st.markdown("<h1 class='main-header'>BAGONG PILIPINAS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>STOCK MARKET PORTAL</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("🏦 Investor Registration")
        name = st.text_input("FULL NAME").upper()
        pin = st.text_input("6-DIGIT TRANSACTION PIN", type="password", max_chars=6)
        
        if st.button("CREATE ACCOUNT"):
            if name and len(pin) == 6 and pin.isdigit():
                user_data = {
                    "name": name, 
                    "pin": pin, 
                    "wallet_balance": 0.0, 
                    "investments": [], 
                    "transactions": []
                }
                save_db(user_data)
                st.session_state.user = user_data
                st.rerun()
            else:
                st.error("Please enter your name and a 6-digit numeric PIN.")
    st.stop()

# --- 4. DASHBOARD LOGIC ---
user = st.session_state.user

# Calculate Matured vs Active
now = datetime.now()
matured_amt = 0.0
active_amt = 0.0

for inv in user['investments']:
    end_time = datetime.fromisoformat(inv['release_time'])
    if now >= end_time:
        matured_amt += (inv['amount'] + inv['profit'])
    else:
        active_amt += inv['amount']

total_liquid = user['wallet_balance'] + matured_amt

# --- 5. TOP DISPLAY ---
st.markdown("<h2 class='main-header' style='font-size: 1.4rem;'>BPSM DASHBOARD</h2>", unsafe_allow_html=True)
st.caption(f"Welcome, {user['name']} | Portfolio Status: Active")

col1, col2 = st.columns(2)
col1.metric("LIQUID CASH", f"₱{total_liquid:,.2f}")
col2.metric("ACTIVE TRADES", f"₱{active_amt:,.2f}")

st.divider()

# --- 6. NAVIGATION TABS ---
tab_trade, tab_wallet, tab_history = st.tabs(["📊 TRADE", "💳 WALLET", "📄 LOGS"])

with tab_trade:
    st.write("### Execute Buy Order")
    st.info("Dividend Rate: **20% Daily** | Maturity: **24 Hours**")
    
    trade_amt = st.number_input("Amount to Invest (PHP)", min_value=100.0, step=100.0)
    
    if st.button("CONFIRM PURCHASE"):
        if total_liquid >= trade_amt:
            new_trade = {
                "amount": trade_amt,
                "profit": trade_amt * DAILY_ROI,
                "start_time": datetime.now().isoformat(),
                "release_time": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            # Deduct from cash balance first
            if user['wallet_balance'] >= trade_amt:
                user['wallet_balance'] -= trade_amt
            else:
                # If buying with matured funds, we just remove the old investment record later
                st.toast("Re-investing matured funds...")
            
            user['investments'].append(new_trade)
            save_db(user)
            st.success("Trade Placed! Your dividends are growing.")
            st.rerun()
        else:
            st.error("Insufficient Funds. Please top up your wallet.")

    st.write("---")
    st.write("### Current Positions")
    if not user['investments']:
        st.caption("No active trades.")
    for inv in user['investments']:
        end = datetime.fromisoformat(inv['release_time'])
        if now < end:
            st.info(f"📈 **₱{inv['amount']:,}** maturing in {str(end-now).split('.')[0]}")
        else:
            st.success(f"✅ **₱{inv['amount']:,}** + ₱{inv['profit']:,} Matured")

with tab_wallet:
    mode = st.radio("Action", ["Deposit Funds", "Request Payout"], horizontal=True)
    
    if mode == "Deposit Funds":
        st.write("### 📥 Official Deposit")
        st.warning("GCASH / MAYA: **0912-345-6789**")
        ref_id = st.text_input("Transaction Reference No.")
        dep_amt = st.number_input("Amount Deposited", min_value=100.0)
        
        if st.button("NOTIFY ADMIN"):
            user['transactions'].append({
                "date": datetime.now().isoformat(),
                "type": "DEPOSIT",
                "amt": dep_amt,
                "status": "PENDING",
                "ref": ref_id
            })
            save_db(user)
            st.toast("Deposit reported. Verification in progress.")
            
    else:
        st.write("### 📤 Request Payout")
        out_amt = st.number_input("Withdraw Amount", min_value=500.0)
        verify_pin = st.text_input("Enter Transaction PIN", type="password")
        
        if st.button("SUBMIT WITHDRAWAL"):
            if verify_pin == user['pin'] and total_liquid >= out_amt:
                user['transactions'].append({
                    "date": datetime.now().isoformat(),
                    "type": "WITHDRAW",
                    "amt": out_amt,
                    "status": "PENDING"
                })
                # Lock the funds
                user['wallet_balance'] -= out_amt
                save_db(user)
                st.warning("Withdrawal processing. Expect arrival within 12-24h.")
            else:
                st.error("Incorrect PIN or Insufficient Balance.")

with tab_history:
    if user['transactions']:
        df = pd.DataFrame(user['transactions'])
        st.table(df[['type', 'amt', 'status', 'ref']])
    else:
        st.write("No transaction history.")

# --- 7. FOOTER & REFRESH ---
st.divider()
if st.button("🔒 EXIT SYSTEM"):
    st.session_state.user = None
    st.rerun()

# Timer refresh to keep clocks updated
time.sleep(10)
st.rerun()
