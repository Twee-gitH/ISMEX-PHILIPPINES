import streamlit as st
import json
import os
from datetime import datetime, timedelta
import time
import random

# --- 1. CORE DATA ENGINE ---
REGISTRY_FILE = "bpsm_registry.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def update_user(name, data):
    reg = load_registry()
    reg[name] = data
    with open(REGISTRY_FILE, "w") as f:
        json.dump(reg, f, default=str)

# --- 2. MOBILE-FIRST UI (ONE-PAGE SCROLL) ---
st.set_page_config(page_title="BPSM Official", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .stApp { background-color: #0b0c0e; color: white; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* AD BANNER */
    .banner {
        background: linear-gradient(135deg, #0038a8 0%, #ce1126 100%);
        padding: 40px 20px; text-align: center; border-bottom: 5px solid #0dcf70;
    }
    .banner h1 { font-family: 'Arial Black'; font-size: 2.2rem; color: white; margin: 0; line-height: 1.1; text-shadow: 2px 2px #000; }
    
    /* USER BOX */
    .user-box { text-align: center; padding: 30px 10px; background: #111217; border-bottom: 1px solid #2a2b30; }
    .balance-val { color: #0dcf70; font-size: 3.5rem; font-weight: 900; margin: 5px 0; }

    /* SECTION HEADERS */
    .section-header { 
        background: #1c1e24; padding: 12px 20px; margin-top: 25px; 
        border-left: 5px solid #0dcf70; font-weight: bold; font-size: 1.2rem;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* BUTTONS */
    .stButton>button {
        width: 100% !important; border-radius: 15px !important; height: 4.5rem !important;
        background: #1c1e24 !important; color: #ffffff !important;
        border: 1px solid #3a3d46 !important; font-weight: bold !important; font-size: 1.1rem !important;
    }
    
    /* DEPLOY BUTTON */
    div[data-testid="stButton"] > button:contains("DEPLOY") {
        background: #0dcf70 !important; color: #0b0c0e !important;
        font-size: 1.4rem !important; font-weight: 900 !important; border: none !important;
    }

    /* TIMER CARD */
    .timer-card {
        background: #1c1e24; padding: 25px; border-radius: 20px;
        border: 2px solid #2a2b30; margin: 15px; text-align: center;
    }
    .timer-val { color: #0dcf70; font-family: monospace; font-size: 2.5rem; font-weight: bold; }

    /* TICKER */
    .ticker-wrap {
        background: #000; color: #0dcf70; padding: 12px 0;
        position: fixed; bottom: 0; width: 100%; font-size: 0.85rem;
        border-top: 1px solid #2a2b30; font-weight: bold; z-index: 999;
    }

    /* INPUTS */
    .stNumberInput input, .stTextInput input {
        color: #000000 !important; -webkit-text-fill-color: #000000 !important;
        background-color: #ffffff !important; border-radius: 12px !important; 
        height: 4rem !important; font-size: 18px !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & ADS ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "main"

if st.session_state.user is None:
    st.markdown("""<div class="banner"><h1>BAGONG PILIPINAS<br>STOCK MARKET</h1>
    <p>Wholesale Liquidity Protocol: We move high-demand goods. You provide the capital. 10% daily ROI guaranteed.</p></div>""", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 SIGN-IN", "📝 REGISTER"])
    with t1:
        ln = st.text_input("NAME", key="l_name").upper()
        lp = st.text_input("PIN", type="password", max_chars=6, key="l_pin")
        if st.button("VERIFY & ACCESS"):
            reg = load_registry()
            if ln in reg and reg[ln]['pin'] == lp:
                st.session_state.user = ln
                st.rerun()
            else: st.error("Access Denied.")
    with t2:
        rn = st.text_input("FULL NAME", key="r_name").upper()
        rp = st.text_input("SET PIN", type="password", max_chars=6, key="r_pin")
        if st.button("CREATE ACCOUNT"):
            if rn and len(rp) == 6:
                update_user(rn, {"pin": rp, "wallet": 0.0, "inv": [], "tx": []})
                st.success("Account Created! Sign in above.")

# --- 4. INVESTOR PORTAL (SCROLLABLE) ---
else:
    name = st.session_state.user
    reg = load_registry()
    data = reg[name]
    now = datetime.now()

    # Auto-Payout Logic
    active_inv = []
    payout = 0
    for i in data.get('inv', []):
        if now >= datetime.fromisoformat(i['end']): payout += (i['amt'] + i['prof'])
        else: active_inv.append(i)
    if payout > 0:
        data['wallet'] += payout
        data['inv'] = active_inv
        update_user(name, data)

    # 1. HEADER
    st.markdown(f"<div class='user-box'><p style='color:#8c8f99; letter-spacing:2px;'>TOTAL ASSETS</p><h1 class='balance-val'>₱{data['wallet']:,.2f}</h1><p style='color:#8c8f99;'>{name}</p></div>", unsafe_allow_html=True)

    # 2. QUICK ACTIONS
    col_a, col_b = st.columns(2)
    if col_a.button("📥 DEPOSIT"): st.session_state.page = "dep"
    if col_b.button("📤 WITHDRAW"): st.session_state.page = "wd"
    
    if st.session_state.page != "main":
        if st.button("⬅️ RETURN TO DASHBOARD"): 
            st.session_state.page = "main"
            st.rerun()

    if st.session_state.page == "dep":
        st.info("GCash Account: 0912-345-6789")
        d_amt = st.number_input("Amount Sent", min_value=100.0)
        ref = st.text_input("Reference #")
        if st.button("SUBMIT DEPOSIT REPORT"):
            data.setdefault('tx', []).append({"date": now.strftime("%m/%d %H:%M"), "type": "DEP", "amt": d_amt, "status": "PENDING"})
            update_user(name, data)
            st.success("Sent for verification.")
            st.session_state.page = "main"
            st.rerun()

    elif st.session_state.page == "wd":
        w_amt = st.number_input("Amount to Cash-out", min_value=100.0)
        if st.button("REQUEST CASHOUT"):
            if data['wallet'] >= w_amt:
                data['wallet'] -= w_amt
                data.setdefault('tx', []).append({"date": now.strftime("%m/%d %H:%M"), "type": "WD", "amt": w_amt, "status": "PENDING"})
                update_user(name, data)
                st.warning("Payout processing...")
                st.session_state.page = "main"
                st.rerun()
            else: st.error("Insufficient Funds.")

    # 3. THE INFINITY SCROLL (DEPLOY -> ACTIVE -> LOGS -> CONTACT)
    else:
        # DEPLOY SECTION
        st.markdown("<div class='section-header'>🚀 DEPLOY CAPITAL</div>", unsafe_allow_html=True)
        st.write("Current Black Market Commodity Cycle (10% Profit)")
        inv_a = st.number_input("Capital PHP", min_value=100.0, step=100.0, key="main_inv")
        if st.button("CONFIRM DEPLOYMENT"):
            if data['wallet'] >= inv_a:
                data['wallet'] -= inv_a
                data.setdefault('inv', []).append({"amt": inv_a, "prof": inv_a*0.1, "end": (now + timedelta(hours=24)).isoformat()})
                update_user(name, data)
                st.rerun()
            else: st.error("Low Balance.")

        # ACTIVE SECTION
        st.markdown("<div class='section-header'>⏳ ACTIVE 24H TIMERS</div>", unsafe_allow_html=True)
        if not active_inv: 
            st.write("No active capital cycles.")
        else:
            for t in active_inv:
                rem = datetime.fromisoformat(t['end']) - now
                st.markdown(f"""<div class="timer-card"><p style="color:#8c8f99; margin:0;">CAPITAL: ₱{t['amt']:,} (+10%)</p>
                <p style="margin:5px 0;">MATURING IN:</p><div class="timer-val">{str(rem).split(".")[0]}</div></div>""", unsafe_allow_html=True)

        # LOGS SECTION
        st.markdown("<div class='section-header'>📜 TRANSACTION HISTORY</div>", unsafe_allow_html=True)
        if not data.get('tx'): 
            st.write("No transaction history yet.")
        else:
            for t in reversed(data.get('tx', [])):
                st.write(f"**{t['date']}** | {t['type']} | ₱{t['amt']:,} | `{t['status']}`")

        # CONTACT SECTION (NEW!)
        st.markdown("<div class='section-header'>📞 SUPPORT</div>", unsafe_allow_html=True)
        st.write("Need help with a deposit or withdrawal?")
        if st.button("💬 CONTACT ADMIN (TELEGRAM)"):
            st.write("Redirecting to Support...") # In a real app, use st.markdown with a link

    # --- 5. LIVE TICKER ---
    payout_msg = f"🔥 LIVE PAYOUT: {random.choice(['Juan D.', 'Maria S.', 'Rico P.', 'Liza M.', 'Kiko V.'])} just received ₱{random.randint(500, 5000):,} profit!"
    st.markdown(f"""<div class="ticker-wrap"><marquee>{payout_msg} &nbsp;&nbsp;&nbsp; ✅ WITHDRAWAL: User {random.randint(100, 999)} approved!</marquee></div>""", unsafe_allow_html=True)

    st.write("<br><br><br><br>", unsafe_allow_html=True)
    if st.sidebar.button("LOGOUT"):
        st.session_state.user = None
        st.rerun()

    time.sleep(1)
    st.rerun()
    
