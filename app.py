import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

# --- 1. DATA & REGISTRY ---
REGISTRY_FILE = "bpsm_registry.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_user(name, pin):
    reg = load_registry()
    if name in reg: return False
    reg[name] = {"pin": pin, "wallet": 0.0, "inv": [], "tx": []}
    with open(REGISTRY_FILE, "w") as f:
        json.dump(reg, f, default=str)
    return True

def update_user(name, data):
    reg = load_registry()
    reg[name] = data
    with open(REGISTRY_FILE, "w") as f:
        json.dump(reg, f, default=str)

# --- 2. THEMED DESIGN (NEON DARK) ---
st.set_page_config(page_title="BPSM Official", page_icon="🇵🇭", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0c0e; color: white; }
    
    /* Headers */
    .brand { text-align: center; color: #ffffff; font-family: 'Arial Black'; font-size: 2.2rem; margin-bottom: 0; }
    .sub-brand { text-align: center; color: #ce1126; font-size: 0.8rem; letter-spacing: 3px; margin-top: -10px; margin-bottom: 20px; }

    /* Input Fix: BLACK TEXT ON WHITE BOX */
    .stTextInput input, .stNumberInput input {
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
        background-color: #ffffff !important;
        border-radius: 12px !important;
        height: 4.2rem !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }

    /* Action Icons Row */
    .action-row { display: flex; justify-content: space-around; margin: 20px 0; }
    .icon-circle {
        width: 55px; height: 55px; background-color: #17181c;
        border: 1px solid #2a2b30; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 1.4rem;
    }
    .action-text { font-size: 0.75rem; color: #8c8f99; text-align: center; margin-top: 8px; font-weight: bold; }

    /* Neon Green Button */
    .stButton>button {
        border-radius: 12px; height: 4.5rem; font-size: 1.2rem; font-weight: 900;
        background: #0dcf70 !important; color: #0b0c0e !important;
        border: none !important; box-shadow: 0 5px 20px rgba(13, 207, 112, 0.4);
    }

    /* Labels */
    .id-label { font-size: 0.9rem; color: #8c8f99; font-weight: 900; margin-bottom: 5px; display: block; }
    
    /* Market Box */
    .market-box {
        background-color: #17181c; padding: 15px; border-radius: 12px;
        border: 1px solid #2a2b30; margin-bottom: 10px;
    }
    .change { color: #0dcf70; float: right; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'tab_index' not in st.session_state: st.session_state.tab_index = 0

if st.session_state.user is None:
    st.markdown("<h1 class='brand'>BPSM</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-brand'>BAGONG PILIPINAS STOCK MARKET</p>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 SIGN IN", "📝 REGISTER"])
    with t1:
        st.markdown("<p class='id-label'>INVESTOR FULL NAME</p>", unsafe_allow_html=True)
        l_name = st.text_input("l_n", label_visibility="collapsed").upper()
        st.markdown("<p class='id-label'>6-DIGIT SECURITY PIN</p>", unsafe_allow_html=True)
        l_pin = st.text_input("l_p", type="password", max_chars=6, label_visibility="collapsed")
        if st.button("VERIFY & ENTER"):
            reg = load_registry()
            if l_name in reg and reg[l_name]['pin'] == l_pin:
                st.session_state.user = l_name
                st.rerun()
            else: st.error("Invalid Credentials.")
    with t2:
        r_name = st.text_input("FULL NAME").upper()
        r_pin = st.text_input("PIN (6 DIGITS)", type="password", max_chars=6)
        if st.button("CREATE I.D."):
            if r_name and len(r_pin) == 6:
                if save_user(r_name, r_pin): st.success("Created! Please Sign In.")
                else: st.error("Name already taken.")

# --- 4. DASHBOARD ---
else:
    name = st.session_state.user
    reg = load_registry()
    data = reg[name]

    st.markdown(f"<h3 style='text-align:center;'>Investor: {name}</h3>", unsafe_allow_html=True)

    # Market Overview
    st.markdown("""
        <div class="market-box">
            <span style="color:#8c8f99">BTC/PHP</span> <span class="change">+1.25%</span><br>
            <span style="font-size:1.2rem; font-weight:bold;">₱3,845,210.00</span>
        </div>
    """, unsafe_allow_html=True)

    # Riscoin Action Row
    st.markdown("""
        <div class="action-row">
            <div class="action-item"><div class="icon-circle">📤</div><div class="action-text">Withdraw</div></div>
            <div class="action-item"><div class="icon-circle">📥</div><div class="action-text">Deposit</div></div>
            <div class="action-item"><div class="icon-circle">🔄</div><div class="action-text">Convert</div></div>
            <div class="action-item"><div class="icon-circle">⋯</div><div class="action-text">More</div></div>
        </div>
    """, unsafe_allow_html=True)

    # Balance Logic
    now = datetime.now()
    total_matured = sum((i['amt'] + i['prof']) for i in data['inv'] if now >= datetime.fromisoformat(i['end']))
    liquid = data['wallet'] + total_matured

    st.metric("AVAILABLE BALANCE", f"₱{liquid:,.2f}")

    tab_trade, tab_wallet = st.tabs(["📊 TRADE", "💳 WALLET"])
    
    with tab_trade:
        amt = st.number_input("Trade Amount", min_value=500.0, step=500.0)
        if st.button("EXECUTE BUY ORDER"):
            if liquid >= amt:
                new_inv = {"amt": amt, "prof": amt*0.2, "end": (now + timedelta(hours=24)).isoformat()}
                data['inv'].append(new_inv)
                if data['wallet'] >= amt: data['wallet'] -= amt
                update_user(name, data)
                st.success("Trade Active!")
                st.rerun()
            else: st.error("Low Balance.")

    with tab_wallet:
        st.write("#### GCASH DEPOSIT: 0912-345-6789")
        d_amt = st.number_input("Deposit Amount", min_value=100.0)
        ref = st.text_input("Ref Number")
        if st.button("REPORT DEPOSIT"):
            data['tx'].append({"type": "DEP", "amt": d_amt, "ref": ref, "status": "PENDING"})
            update_user(name, data)
            st.info("Sent to Admin for Approval.")

    if st.sidebar.button("LOGOUT"):
        st.session_state.user = None
        st.rerun()
        
