import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ==========================================
# BLOCK 1: CORE ENGINE & STATE INIT
# ==========================================
REGISTRY_FILE = "bpsm_registry.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

# Initialize all states at the very top to prevent AttributeErrors
if 'page' not in st.session_state: st.session_state.page = "ad"
if 'user' not in st.session_state: st.session_state.user = None
if 'is_boss' not in st.session_state: st.session_state.is_boss = False
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False

# ==========================================
# BLOCK 2: UI STYLING
# ==========================================
st.set_page_config(page_title="ISMEX Official", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .ad-panel { background: #1c1e26; border-radius: 8px; border: 1px dashed #00eeff; padding: 20px; margin-bottom: 20px; }
    
    /* The Secret Period Button */
    .stButton>button:contains("⛔") {
        background-color: transparent !important;
        border: none !important;
        color: #8c8f99 !important;
        font-size: 15px !important;
        padding: 0 !important;
        margin-left: -5px !important;
        display: inline !important;
        min-height: 0px !important;
        width: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BLOCK 3: PAGE 1 - THE ADVERTISEMENT
# ==========================================
if st.session_state.page == "ad" and not st.session_state.is_boss:
    # Giant Title
    st.markdown('<h1 style="text-align:center; font-size:42px; font-weight:900; background:linear-gradient(90deg, #ff007f, #ffaa00, #00ff88, #00eeff); -webkit-background-clip: text; color: transparent; margin-bottom:30px;">INTERNATIONAL STOCK MARKET EXCHANGE</h1>', unsafe_allow_html=True)

    st.markdown('<div class="ad-panel">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00eeff; font-weight:bold; font-size:18px; text-align:center;">How We Generate Your Profit:</p>', unsafe_allow_html=True)
    
    # Text with Secret Button inside the box
    col_t, col_b = st.columns([0.97, 0.03])
    with col_t:
        st.markdown('<p style="color:#8c8f99; font-size:16px; line-height:1.6;">Your single capital is diversified and cycled multiple times through our advanced AI-managed scalping algorithm every hour. Instead of holding a stock for a year, we take small 0.05% profits from thousands of trades, combining them to provide you with your precise, ticking 20% guaranteed profit over the 7-day cycle. Your money is always moving, never dormant</p>', unsafe_allow_html=True)
    with col_b:
        if st.button("⛔", key="secret_dot"):
            st.session_state.admin_mode = not st.session_state.admin_mode
    st.markdown('</div>', unsafe_allow_html=True)

    # Jump Button to Login Page
    if st.button("🚀 JOIN NOW!", use_container_width=True, key="join_btn"):
        st.session_state.page = "login"
        st.rerun()

    # Secret Admin Gate
    if st.session_state.admin_mode:
        if st.text_input("Security Code", type="password", key="adm_gate") == "0102030405":
            st.session_state.is_boss = True
            st.rerun()

# ==========================================
# BLOCK 4: PAGE 2 - LOGIN & REGISTRATION
# ==========================================
elif st.session_state.page == "login" and not st.session_state.is_boss:
    st.markdown("<h1 style='text-align:center; color:#00eeff;'>ACCESS PORTAL</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["EXISTING USER", "NEW REGISTRATION"])
    
    with tab1:
        ln = st.text_input("Username", key="login_name")
        lp = st.text_input("6-Digit PIN", type="password", key="login_pin")
        if st.button("ENTER DASHBOARD", key="do_login"):
            reg = load_registry()
            if ln in reg and str(reg[ln].get('pin')) == str(lp):
                st.session_state.user = ln
                st.session_state.page = "dashboard"
                st.rerun()
            else: st.error("Access Denied")

    with tab2:
        st.info("Registration is currently handled by authorized ISMEX brokers.")
        if st.button("CONTACT BROKER", key="reg_contact"):
            st.write("Redirecting to support...")

    if st.button("← BACK TO ADVERTISEMENT", key="back_to_ad"):
        st.session_state.page = "ad"
        st.rerun()

# ==========================================
# BLOCK 5: ADMIN & DASHBOARD (Keep your existing logic here)
# ==========================================
if st.session_state.is_boss:
    st.title("👑 ADMIN CONTROL")
    if st.button("LOGOUT ADMIN"): 
        st.session_state.is_boss = False
        st.rerun()

elif st.session_state.user:
    st.title(f"Welcome, {st.session_state.user}")
    if st.button("LOGOUT USER"):
        st.session_state.user = None
        st.session_state.page = "ad"
        st.rerun()
        
