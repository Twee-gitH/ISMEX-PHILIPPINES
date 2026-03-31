import streamlit as st
import json
import os
import shutil
from datetime import datetime, timedelta
import time
import pandas as pd

# --- 1. SESSION INITIALIZER ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "main"
if 'is_boss' not in st.session_state: st.session_state.is_boss = False
if 'confirm_amt' not in st.session_state: st.session_state.confirm_amt = False

if not os.path.exists("receipts"):
    os.makedirs("receipts")

# --- 2. DATA ENGINE ---
REGISTRY_FILE = "bpsm_registry.json"
BACKUP_FILE = "bpsm_backup.json"

def load_registry():
    for file in [REGISTRY_FILE, BACKUP_FILE]:
        if os.path.exists(file):
            try:
                with open(file, "r") as f:
                    return json.load(f)
            except: continue
    return {}

def update_user(name, data):
    reg = load_registry()
    reg[name] = data
    with open(REGISTRY_FILE, "w") as f:
        json.dump(reg, f, default=str)
    shutil.copy(REGISTRY_FILE, BACKUP_FILE)

# --- 3. UI STYLING ---
st.set_page_config(page_title="BPSM Official", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .stApp { background-color: #0b0c0e; color: white; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .user-box { text-align: center; padding: 30px 10px; background: #111217; border-bottom: 1px solid #2a2b30; }
    .balance-val { color: #0dcf70; font-size: 3.5rem; font-weight: 900; margin: 5px 0; }
    .section-header { background: #1c1e24; padding: 12px 20px; margin-top: 25px; border-left: 5px solid #0dcf70; font-weight: bold; text-transform: uppercase; color: #0dcf70; }
    .ticker-wrap { background: #000; color: #0dcf70; padding: 12px 0; position: fixed; bottom: 0; width: 100%; font-size: 0.85rem; border-top: 1px solid #2a2b30; z-index: 999; overflow: hidden; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-text { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; font-weight: bold; }
    .stButton>button { border-radius: 12px !important; height: 3.5rem !important; font-weight: bold !important; width: 100%; }
    .roi-text { color: #0dcf70; font-weight: bold; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ACCESS CONTROL ---
if st.session_state.user is None and not st.session_state.is_boss:
    st.markdown("<div style='background: linear-gradient(135deg, #0038a8 0%, #ce1126 100%); padding: 40px 20px; text-align: center;'><h1>BAGONG PILIPINAS<br>STOCK MARKET</h1><p>Automatic Weekly Payouts | 20% Weekly ROI</p></div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 SIGN-IN", "📝 REGISTER"])
    
    with t1:
        ln = st.text_input("INVESTOR NAME", key="login_name").upper()
        lp = st.text_input("SECURE PIN", type="password", max_chars=6, key="login_pin")
        if st.button("VERIFY & ACCESS"):
            reg = load_registry()
            if ln in reg and reg[ln].get('pin') == lp:
                st.session_state.user = ln
                st.rerun()
            else:
                st.error("Invalid Credentials")
    
    with t2:
        rn = st.text_input("FULL LEGAL NAME", key="reg_name").upper()
        rp = st.text_input("CREATE 6-DIGIT PIN", type="password", max_chars=6, key="reg_pin")
        referrer = st.text_input("REFERRER NAME (REQUIRED)", key="reg_ref").upper()
        if st.button("CREATE ACCOUNT"):
            reg = load_registry()
            if not referrer: st.error("Referrer required.")
            elif referrer not in reg: st.error("Referrer not found.")
            elif rn in reg: st.error("Already registered.")
            elif rn and len(rp) == 6:
                # Initialize bonus tracking flags
                new_data = {"pin": rp, "wallet": 0.0, "inv": [], "tx": [], "ref_by": referrer, "bonus_claimed": False}
                update_user(rn, new_data)
                st.success("Account Created!")
                time.sleep(1.5); st.rerun()
    
    st.divider()
    with st.expander("MASTER ACCESS"):
        key = st.text_input("Admin Key", type="password", key="admin_key")
        if st.button("ENTER CONTROL PANEL"):
            if key == "Orange01!":
                st.session_state.is_boss = True
                st.rerun()
    st.stop()

# --- 5. INVESTOR PORTAL ---
if st.session_state.user:
    name = st.session_state.user
    reg = load_registry()
    data = reg[name]
    now = datetime.now()

    # ROI Processor
    payout_triggered = False
    for i in data.get('inv', []):
        try:
            end_time = datetime.fromisoformat(i['end'])
            if now >= end_time: 
                profit_amt = i['amt'] * 0.20
                data['wallet'] += profit_amt
                i['start'] = now.isoformat()
                i['end'] = (now + timedelta(days=7)).isoformat()
                data.setdefault('tx', []).append({"date": now.strftime("%Y-%m-%d %H:%M"), "type": "WEEKLY ROI", "amt": profit_amt, "status": "SUCCESSFUL"})
                payout_triggered = True
        except: continue
    if payout_triggered: update_user(name, data); st.rerun()

    st.markdown(f"<div class='user-box'><p style='color:#8c8f99;'>BALANCE</p><h1 class='balance-val'>₱{data['wallet']:,.2f}</h1></div>", unsafe_allow_html=True)

    if st.session_state.page == "dep":
        st.markdown("<div class='section-header'>📥 DEPOSIT</div>", unsafe_allow_html=True)
        d_amt = st.number_input("Amount", min_value=1000.0, step=100.0)
        receipt = st.file_uploader("Receipt", type=['jpg','png'])
        if st.button("SUBMIT"):
            if receipt:
                f_path = f"receipts/{name}_{int(time.time())}.png"
                with open(f_path, "wb") as f: f.write(receipt.getbuffer())
                data.setdefault('tx', []).append({"date": now.strftime("%Y-%m-%d %H:%M"), "type": "DEPOSIT", "amt": d_amt, "status": "PENDING_DEP", "receipt_path": f_path})
                update_user(name, data); st.session_state.page = "main"; st.rerun()
        if st.button("⬅️ BACK"): st.session_state.page = "main"; st.rerun()

    elif st.session_state.page == "wd":
        st.markdown("<div class='section-header'>📤 WITHDRAW</div>", unsafe_allow_html=True)
        w_amt = st.number_input("Amount", min_value=1000.0, max_value=max(1000.0, data['wallet']))
        if st.button("SUBMIT"):
            data['wallet'] -= w_amt
            data.setdefault('tx', []).append({"date": now.strftime("%Y-%m-%d %H:%M"), "type": "WITHDRAWAL", "amt": w_amt, "status": "PENDING_WD"})
            update_user(name, data); st.session_state.page = "main"; st.rerun()
        if st.button("⬅️ BACK"): st.session_state.page = "main"; st.rerun()

    else:
        col1, col2 = st.columns(2)
        with col1: 
            if st.button("📥 DEPOSIT"): st.session_state.page = "dep"; st.rerun()
        with col2: 
            if st.button("📤 WITHDRAW"): st.session_state.page = "wd"; st.rerun()

        # --- UPDATED: REFERRAL BONUS CLAIM SECTION ---
        st.markdown("<div class='section-header'>👥 MY REFERRALS & 20% BONUSES</div>", unsafe_allow_html=True)
        for u_name, u_info in reg.items():
            if u_info.get('ref_by') == name:
                first_dep = 0.0
                for tx in u_info.get('tx', []):
                    if tx['type'] == "DEPOSIT" and tx['status'] == "SUCCESSFUL_DEP":
                        first_dep = tx['amt']
                        break
                
                bonus_amt = first_dep * 0.20
                status = "NO DEPOSIT YET"
                if first_dep > 0:
                    if u_info.get('bonus_claimed') == "APPROVED":
                        status = f"✅ BONUS CLAIMED (₱{bonus_amt:,.2f})"
                    elif u_info.get('bonus_claimed') == "PENDING":
                        status = "⏳ PENDING ADMIN APPROVAL"
                    else:
                        status = f"🎁 BONUS AVAILABLE: ₱{bonus_amt:,.2f}"
                        if st.button(f"CLAIM BONUS FROM {u_name}", key=f"claim_{u_name}"):
                            u_info['bonus_claimed'] = "PENDING"
                            update_user(u_name, u_info)
                            st.success("Claim submitted to Admin!")
                            time.sleep(1); st.rerun()
                
                st.write(f"**{u_name}** | First Deposit: ₱{first_dep:,.2f} | Status: {status}")

        st.markdown("<div class='section-header'>⏳ ACTIVE CYCLES</div>", unsafe_allow_html=True)
        for idx, t in enumerate(reversed(data.get('inv', []))):
            rem = datetime.fromisoformat(t['end']) - now
            st.write(f"Capital: ₱{t['amt']:,} | Time Left: {str(rem).split('.')[0]}")

    if st.sidebar.button("LOGOUT"): st.session_state.user = None; st.rerun()

# --- 6. BOSS PANEL ---
elif st.session_state.is_boss:
    all_users = load_registry()
    st.markdown("### 👑 MASTER CONTROL")

    # --- NEW: REFERRAL BONUS APPROVAL ---
    st.markdown("<div class='section-header'>🎁 PENDING REFERRAL BONUSES (20%)</div>", unsafe_allow_html=True)
    for u_name, u_info in all_users.items():
        if u_info.get('bonus_claimed') == "PENDING":
            referrer_name = u_info.get('ref_by')
            # Calculate bonus from first deposit
            first_dep = 0.0
            for tx in u_info.get('tx', []):
                if tx['type'] == "DEPOSIT" and tx['status'] == "SUCCESSFUL_DEP":
                    first_dep = tx['amt']
                    break
            bonus_amt = first_dep * 0.20
            
            if st.button(f"APPROVE ₱{bonus_amt:,.2f} BONUS for {referrer_name} (Invited {u_name})"):
                # Credit the Referrer
                if referrer_name in all_users:
                    all_users[referrer_name]['wallet'] += bonus_amt
                    all_users[referrer_name].setdefault('tx', []).append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "type": "REFERRAL BONUS",
                        "amt": bonus_amt,
                        "status": "SUCCESSFUL"
                    })
                # Mark the bonus as approved in the Invitee's record
                all_users[u_name]['bonus_claimed'] = "APPROVED"
                # Save both updates
                with open(REGISTRY_FILE, "w") as f: json.dump(all_users, f, default=str)
                st.success("Bonus Approved!"); time.sleep(1); st.rerun()

    st.markdown("<div class='section-header'>🔔 PENDING DEPOSITS/WITHDRAWALS</div>", unsafe_allow_html=True)
    for u_name, u_info in all_users.items():
        for idx, tx in enumerate(u_info.get('tx', [])):
            if tx['status'] == "PENDING_DEP":
                if st.button(f"Approve ₱{tx['amt']:,} Deposit: {u_name}"):
                    all_users[u_name]['tx'][idx]['status'] = "SUCCESSFUL_DEP"
                    st_t = datetime.now()
                    all_users[u_name].setdefault('inv', []).append({"amt": tx['amt'], "start": st_t.isoformat(), "end": (st_t + timedelta(days=7)).isoformat()})
                    update_user(u_name, all_users[u_name]); st.rerun()
            elif tx['status'] == "PENDING_WD":
                if st.button(f"Approve ₱{tx['amt']:,} Withdrawal: {u_name}"):
                    all_users[u_name]['tx'][idx]['status'] = "SUCCESSFUL_WD"
                    update_user(u_name, all_users[u_name]); st.rerun()
    
    if st.button("EXIT ADMIN"): st.session_state.is_boss = False; st.rerun()
                        
