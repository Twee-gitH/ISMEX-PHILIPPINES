import streamlit as st
import json
import os
from datetime import datetime

# --- 1. SESSION INITIALIZER (CRITICAL FIX FOR 8367.JPG) ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- 2. DATA ENGINE ---
REGISTRY_FILE = "bpsm_registry.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_all(data):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, default=str)

# --- 3. ADMIN UI ---
st.set_page_config(page_title="BPSM MASTER ADMIN", layout="wide")

# Sidebar Login
st.sidebar.title("🔐 Admin Login")
admin_pw = st.sidebar.text_input("Enter Admin Key", type="password")

if admin_pw == "MASTER123": # <--- CHANGE THIS PASSWORD
    st.session_state.admin_logged_in = True
    st.title("👨‍💼 BPSM MASTER CONTROL")
    reg = load_registry()

    # --- TABBED VIEW FOR MOBILE ---
    tab1, tab2, tab3 = st.tabs(["🔔 APPROVALS", "🛠️ ADJUST", "👥 USERS"])

    with tab1:
        st.subheader("📥 Pending Deposits")
        for user, d in reg.items():
            for i, tx in enumerate(d.get('tx', [])):
                if tx['type'] == 'DEP' and tx['status'] == 'PENDING':
                    st.warning(f"{user} deposited ₱{tx['amt']:,}")
                    if st.button(f"Approve {user}", key=f"app_{user}_{i}"):
                        reg[user]['wallet'] += tx['amt']
                        reg[user]['tx'][i]['status'] = 'APPROVED'
                        save_all(reg)
                        st.rerun()

    with tab2:
        st.subheader("🛠️ Manual Balance Edit")
        target = st.selectbox("Select User", list(reg.keys()) if reg else ["No Users"])
        amount = st.number_input("Amount (PHP)", step=100.0)
        mode = st.radio("Action", ["Add (+)", "Deduct (-)"])
        if st.button("Execute Change"):
            if mode == "Add (+)": reg[target]['wallet'] += amount
            else: reg[target]['wallet'] -= amount
            save_all(reg)
            st.success("Done!")

    with tab3:
        st.subheader("👥 Investor Directory")
        for user, d in reg.items():
            with st.expander(f"👤 {user} | ₱{d['wallet']:,.2f}"):
                st.write(f"**PIN:** {d['pin']}")
                st.write("**History:**")
                st.write(d.get('tx', []))

else:
    st.info("Enter Admin Key in the sidebar to access the panel.")
    
