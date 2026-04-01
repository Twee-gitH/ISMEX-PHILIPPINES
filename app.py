import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta
import time
import pandas as pd

# --- 1. DATA ENGINE ---
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
    with open(REGISTRY_FILE, "w") as f: json.dump(reg, f, default=str)

# --- 2. UI & SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'is_boss' not in st.session_state: st.session_state.is_boss = False
st.set_page_config(page_title="BPSM Official", layout="wide")

st.markdown("""
    <style>
    input[type="text"] { text-transform: uppercase !important; }
    input[type="password"] { text-transform: none !important; -webkit-text-transform: none !important; }
    .balance-card { background: linear-gradient(135deg, #1c1e24 0%, #2d313a 100%); padding: 25px; border-radius: 15px; border: 1px solid #3a3d46; text-align: center; margin-bottom: 20px; }
    .balance-label { color: #8c8f99; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; }
    .balance-val { color: #00ff88; font-size: 42px; font-weight: 900; margin: 0; }
    .news-box { background: #ce112615; border-left: 4px solid #ce1126; padding: 10px 15px; margin-bottom: 20px; border-radius: 0 10px 10px 0; }
    .user-box { background-color: #1c1e24; padding: 15px; border-radius: 10px; border: 1px solid #3a3d46; margin-bottom: 5px; border-left: 5px solid #00ff88; }
    .ref-box { background-color: #16181d; padding: 12px; border-radius: 8px; border: 1px solid #2d313a; margin-bottom: 10px; }
    .roi-text { color: #00ff88; font-family: monospace; font-size: 26px; font-weight: bold; }
    .section-header { background: #252830; padding: 8px; border-radius: 5px; margin-top: 15px; font-weight: bold; border-left: 5px solid #ce1126; }
    .stButton>button { width: 100%; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. NEWS & ACCESS ---
NEWS_HEADLINES = ["📈 PSEi index climbs as blue-chip stocks rally.", "🚀 Tech sector sees 5% growth.", "🏦 Bangko Sentral hints at steady interest rates.", "📊 Market analysts predict a bullish trend."]

if st.session_state.user is None and not st.session_state.is_boss:
    st.title("BAGONG PILIPINAS STOCK MARKET")
    t1, t2 = st.tabs(["SIGN-IN", "REGISTER"])
    with t1:
        ln, lp = st.text_input("NAME").upper(), st.text_input("PIN", type="password")
        if st.button("LOGIN"):
            reg = load_registry()
            if ln in reg and str(reg[ln].get('pin')) == str(lp): st.session_state.user = ln; st.rerun()
    with t2:
        rn, rp, ref = st.text_input("FULL NAME", key="r1").upper(), st.text_input("CREATE PIN", type="password", key="r2"), st.text_input("REFERRER", key="r3").upper()
        if st.button("REGISTER ACCOUNT"):
            update_user(rn, {"pin": rp, "wallet": 0.0, "inv": [], "tx": [], "ref_by": ref, "bonus_status": {}})
            st.success("SUCCESS"); st.rerun()
    with st.expander("🔐 ADMIN"):
        ap = st.text_input("ADMIN PIN", type="password")
        if st.button("ENTER BOSS MODE"):
            if ap == "0102030405": st.session_state.is_boss = True; st.rerun()
    st.stop()

# --- 4. INVESTOR DASHBOARD ---
if st.session_state.user:
    name = st.session_state.user
    data = load_registry().get(name)
    now = datetime.now()

    # ROI ENGINE
    MINUTE_RATE = (0.20 / 7) / 1440 
    changed = False
    for i in data.get('inv', []):
        st_t, et_t = datetime.fromisoformat(i['start']), datetime.fromisoformat(i['end'])
        calc_now = min(now, et_t)
        mins_passed = (calc_now - st_t).total_seconds() / 60
        i['accumulated_roi'] = max(0, i['amt'] * (mins_passed * MINUTE_RATE))
        if now >= et_t and not i.get('roi_paid', False):
            p = i['amt'] * 0.20; data['wallet'] += p; i['roi_paid'] = True
            data.setdefault('tx', []).append({"date": now.strftime("%Y-%m-%d %H:%M"), "type": "WEEKLY ROI", "amt": p, "status": "SUCCESSFUL"})
            changed = True
        if now >= (et_t + timedelta(hours=1)):
            i.update({"start": now.isoformat(), "end": (now + timedelta(days=7)).isoformat(), "roi_paid": False})
            data.setdefault('tx', []).append({"date": now.strftime("%Y-%m-%d %H:%M"), "type": "AUTO-REINVEST", "amt": i['amt'], "status": "SUCCESSFUL"})
            changed = True
    if changed: update_user(name, data); st.rerun()

    # BALANCE & NEWS
    st.markdown(f'<div class="balance-card"><p class="balance-label">Withdrawable Balance</p><p class="balance-val">₱{data["wallet"]:,.2f}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="news-box"><small style="color:#ce1126; font-weight:bold;">LIVE MARKET UPDATE:</small><br><span style="font-size:14px; color:#fff;">{random.choice(NEWS_HEADLINES)}</span></div>', unsafe_allow_html=True)

    # ACTIVE CYCLES
    st.markdown("<div class='section-header'>⏳ ACTIVE CYCLES</div>", unsafe_allow_html=True)
    inv_list = data.get('inv', [])
    for idx, t in enumerate(reversed(inv_list)):
        actual_idx = len(inv_list) - 1 - idx
        st_t, et_t = datetime.fromisoformat(t['start']), datetime.fromisoformat(t['end'])
        grace_end = et_t + timedelta(hours=1)
        st.markdown(f"<div class='user-box'><b>Capital: ₱{t['amt']:,}</b><br><span class='roi-text'>Accumulated ROI: ₱{t.get('accumulated_roi', 0):,.4f}</span><br><b>Approved:</b> {st_t.strftime('%Y-%m-%d %I:%M %p')}<br><b>Maturity:</b> {et_t.strftime('%Y-%m-%d %I:%M %p')}</div>", unsafe_allow_html=True)
        if et_t <= now < grace_end:
            if st.button(f"✅ PULL CAPITAL (₱{t['amt']:,})", key=f"p{actual_idx}"):
                data['wallet'] += t['amt']; data['inv'].pop(actual_idx); update_user(name, data); st.rerun()
        else:
            st.button(f"PULL AVAILABLE: {et_t.strftime('%b %d, %I:%M %p')}", key=f"lock_{actual_idx}", disabled=True)

    # --- REFERRAL BONUS DISPLAY ---
    st.markdown("<div class='section-header'>👥 REFERRAL COMMISSIONS</div>", unsafe_allow_html=True)
    all_users = load_registry()
    for u_n, u_i in all_users.items():
        if u_i.get('ref_by') == name:
            # Find the very first successful deposit this invitee ever made
            first_dep = 0
            for tx in u_i.get('tx', []):
                if tx['status'] == "SUCCESSFUL_DEP":
                    first_dep = tx['amt']
                    break
            
            comm = first_dep * 0.20
            b_status = data.get('bonus_status', {}).get(u_n, "AVAILABLE")
            
            st.markdown(f"""
                <div class='ref-box'>
                    <b style='color:#00ff88;'>Invitee: {u_n}</b><br>
                    <span style='font-size:13px; color:#8c8f99;'>First Deposit: ₱{first_dep:,.2f}</span><br>
                    <span style='font-size:15px;'>Your Bonus: <b>₱{comm:,.2f}</b></span>
                </div>
            """, unsafe_allow_html=True)
            
            if comm > 0:
                if b_status == "AVAILABLE":
                    if st.button(f"Request Bonus for {u_n}", key=f"req_{u_n}"):
                        data.setdefault('bonus_status', {})[u_n] = "REQUESTED"; update_user(name, data); st.rerun()
                else:
                    st.write(f"📌 Status: **{b_status}**")

    if st.button("LOGOUT"): st.session_state.user = None; st.rerun()

# --- 5. ADMIN OVERVIEW (STABLE) ---
elif st.session_state.is_boss:
    st.title("👑 ADMIN OVERVIEW")
    all_users = load_registry()
    for u_name, u_data in all_users.items():
        with st.expander(f"Investor: {u_name} | PIN: {u_data.get('pin')} | Wallet: ₱{u_data.get('wallet'):,.2f}"):
            for idx, tx in enumerate(u_data.get('tx', [])):
                ca, cb = st.columns([4, 1])
                ca.write(f"{tx['date']} | {tx['type']} | ₱{tx['amt']:,} | {tx['status']}")
                if tx['status'] == "PENDING_DEP":
                    if cb.button("APPROVE", key=f"app_{u_name}_{idx}"):
                        st_t = datetime.now()
                        tx['status'] = "SUCCESSFUL_DEP"
                        u_data.setdefault('inv', []).append({"amt": tx['amt'], "start": st_t.isoformat(), "end": (st_t + timedelta(days=7)).isoformat(), "roi_paid": False})
                        update_user(u_name, u_data); st.rerun()
            for inv_name, status in u_data.get('bonus_status', {}).items():
                if status == "REQUESTED":
                    st.write(f"Bonus Request for {inv_name}")
                    c1, c2 = st.columns(2)
                    if c1.button("PAY", key=f"p_{u_name}_{inv_name}"):
                        i_data = all_users.get(inv_name, {}); f_amt = next((t['amt'] for t in i_data.get('tx', []) if t['status'] == "SUCCESSFUL_DEP"), 0)
                        u_data['wallet'] += (f_amt * 0.20); u_data['bonus_status'][inv_name] = "RECEIVED"; update_user(u_name, u_data); st.rerun()
                    if c2.button("FAIL", key=f"f_{u_name}_{inv_name}"):
                        u_data['bonus_status'][inv_name] = "FAILED"; update_user(u_name, u_data); st.rerun()
    if st.button("EXIT"): st.session_state.is_boss = False; st.rerun()
                        
