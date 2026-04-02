import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ==========================================
# BLOCK 1: DATA STORAGE
# ==========================================
REGISTRY_FILE = "bpsm_registry.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def update_user(name, data):
    reg = load_registry()
    reg[name] = data
    with open(REGISTRY_FILE, "w") as f: 
        json.dump(reg, f, indent=4, default=str)

# ==========================================
# BLOCK 2: EXACT UI STYLING (MATCHING 8848.JPG)
# ==========================================
st.set_page_config(page_title="BPSM Official", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #11141b; }
    
    /* Top Balance Card */
    .balance-card { 
        background: #1c1e26; padding: 25px; border-radius: 12px; 
        border: 1px solid #2d303a; text-align: center; margin-bottom: 25px; 
    }
    .balance-label { color: #8c8f99; font-size: 13px; letter-spacing: 1px; }
    .balance-val { color: #00ff88; font-size: 55px; font-weight: bold; margin: 0; }
    
    /* Section Header */
    .section-header { 
        background: #1c1e26; padding: 10px; border-radius: 4px; 
        margin: 15px 0; font-weight: bold; border-left: 4px solid #ff4b4b; 
        color: white; font-size: 14px; display: flex; align-items: center;
    }
    
    /* ROI CARD DESIGN */
    .cycle-card {
        background-color: #1c1e26; padding: 20px; border-radius: 12px;
        border: 1px solid #2d303a; border-left: 4px solid #00ff88;
        margin-bottom: 15px;
    }
    .cap-label { color: white; font-size: 18px; font-weight: 500; }
    .roi-label { color: #00ff88; font-size: 12px; font-weight: bold; margin-top: 10px; }
    .roi-value { color: #00ff88; font-size: 45px; font-weight: bold; font-family: monospace; line-height: 1.1; }
    .total-receive { color: #8c8f99; font-size: 13px; margin: 5px 0 15px 0; }
    .timer-row { color: #ff4b4b; font-weight: bold; font-size: 16px; margin-bottom: 12px; }
    .status-banner {
        background-color: #252830; color: #8c8f99; padding: 12px;
        border-radius: 6px; font-size: 12px; text-align: center; border: 1px solid #3a3d46;
    }
    .peso { color: #00ff88; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BLOCK 3: AUTH LOGIC
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'is_boss' not in st.session_state: st.session_state.is_boss = False

if st.session_state.user is None and not st.session_state.is_boss:
    st.title("BPSM LOGIN")
    ln = st.text_input("Username")
    lp = st.text_input("PIN", type="password")
    if st.button("ENTER DASHBOARD"):
        reg = load_registry()
        if ln in reg and str(reg[ln].get('pin')) == str(lp):
            st.session_state.user = ln
            st.rerun()
        elif ln == "ADMIN" and lp == "BOSS":
            st.session_state.is_boss = True
            st.rerun()

# ==========================================
# BLOCK 4: THE LIVE DASHBOARD
# ==========================================
if st.session_state.user:
    # REFRESH EVERY 1 SECOND FOR TICKING EFFECT
    st_autorefresh(interval=1000, key="live_roi")
    
    name = st.session_state.user
    data = load_registry().get(name)
    now = datetime.now()
    ROI_PER_SEC = 0.20 / 604800 # 20% in 7 days

    # Header
    st.markdown(f"### Welcome, {name}")
    
    # Balance
    st.markdown(f"""
        <div class="balance-card">
            <p class="balance-label">WITHDRAWABLE BALANCE</p>
            <p class="balance-val"><span class="peso">₱</span>{data['wallet']:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    # Actions
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.expander("📥 Deposit"):
            pending = [t for t in data.get('tx', []) if t['type']=="DEP" and t['status']=="PENDING"]
            if pending: st.warning("WAITING FOR APPROVAL")
            else:
                amt = st.number_input("Amount", min_value=0, step=500)
                if amt > 0:
                    if st.file_uploader("Upload Receipt") and st.button("SEND"):
                        data.setdefault('tx', []).append({"type":"DEP","amt":amt,"status":"PENDING","date":now.isoformat()})
                        update_user(name, data); st.rerun()
    with c2:
        with st.expander("💸 Withdraw"):
            w_amt = st.number_input("Amount", 0.0, max_value=float(data['wallet']))
            if st.button("CONFIRM") and w_amt > 0:
                data['wallet'] -= w_amt
                update_user(name, data); st.rerun()
    with c3:
        if st.button("LOGOUT"):
            st.session_state.user = None
            st.rerun()

    # ==========================================
    # BLOCK 5: THE EXACT ROI CARDS (MATCHING 8448.JPG)
    # ==========================================
    st.markdown('<div class="section-header">⌛ ACTIVE CYCLES</div>', unsafe_allow_html=True)
    
    for idx, inv in enumerate(reversed(data.get('inv', []))):
        start_dt = datetime.fromisoformat(inv['start'])
        end_dt = datetime.fromisoformat(inv['end'])
        
        if now < end_dt:
            # LIVE TICKING MATH
            elapsed = (now - start_dt).total_seconds()
            current_roi = inv['amt'] * ROI_PER_SEC * elapsed
            diff = end_dt - now
            time_str = f"{diff.days}D {diff.seconds//3600:02}H {(diff.seconds//60)%60:02}M {diff.seconds%60:02}S"
            banner_text = f"AVAILABLE TO PULL OUT FROM {end_dt.strftime('%b %d, %I:%M %p')}"
        else:
            current_roi = inv['amt'] * 0.20
            time_str = "MATURED"
            banner_text = "READY TO PULL OUT CAPITAL"

        st.markdown(f"""
            <div class="cycle-card">
                <div class="cap-label">Capital: <span class="peso">₱</span>{inv['amt']:,.1f}</div>
                <div class="roi-label">ACCUMULATED ROI:</div>
                <div class="roi-value"><span class="peso">₱</span>{current_roi:,.4f}</div>
                <div class="total-receive">Total to Receive: ₱{inv['amt']*0.20:,.2f}</div>
                <div class="timer-row">⌛ TIME REMAINING: {time_str}</div>
                <div class="status-banner">{banner_text}</div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# BLOCK 6: ADMIN
# ==========================================
elif st.session_state.is_boss:
    st.title("ADMIN PANEL")
    reg = load_registry()
    for u, d in reg.items():
        for tx in d.get('tx', []):
            if tx['status'] == "PENDING":
                if st.button(f"APPROVE ₱{tx['amt']} for {u}"):
                    tx['status'] = "SUCCESS"
                    d.setdefault('inv', []).append({
                        "amt": tx['amt'], 
                        "start": datetime.now().isoformat(), 
                        "end": (datetime.now()+timedelta(days=7)).isoformat()
                    })
                    update_user(u, d); st.rerun()
    if st.button("EXIT"): st.session_state.is_boss = False; st.rerun()
