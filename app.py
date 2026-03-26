import streamlit as st
import time

# --- APP CONFIGURATION ---
st.set_page_config(page_title="BP Market", page_icon="🇵🇭", layout="centered")

# CSS to force ALL CAPS and make buttons big for thumbs
st.markdown("""
    <style>
    input { text-transform: uppercase; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #0038a8;
        color: white;
        font-weight: bold;
        border: none;
        margin-top: 10px;
    }
    /* Reduce padding for mobile screens */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "signup"

# --- 1. REGISTRATION PAGE ---
if st.session_state.page == "signup":
    st.markdown("<h2 style='text-align: center;'>🇵🇭 REGISTRATION</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8em;'>ALL FIELDS ARE REQUIRED</p>", unsafe_allow_html=True)

    # Simplified inputs for speed and data saving
    full_name = st.text_input("FULL NAME (SURNAME, FIRST NAME)").upper()
    age = st.number_input("AGE", min_value=18, max_value=100, step=1)
    
    # Static Country (Saves data/time)
    st.text_input("COUNTRY", value="PHILIPPINES", disabled=True)

    # Short list of Regions
    region = st.selectbox("REGION", [
        "NCR", "CAR", "REGION I", "REGION II", "REGION III", "REGION IV-A", 
        "MIMAROPA", "REGION V", "REGION VI", "REGION VII", "REGION VIII", 
        "REGION IX", "REGION X", "REGION XI", "REGION XII", "REGION XIII", "BARMM"
    ])

    # Text inputs are more "Data Friendly" than loading 40,000 barangay options
    city = st.text_input("CITY / MUNICIPALITY").upper()
    barangay = st.text_input("BARANGAY").upper()
    
    email = st.text_input("EMAIL ADDRESS").upper()
    password = st.text_input("CREATE PASSWORD", type="password")

    if st.button("CREATE ACCOUNT"):
        if full_name and city and barangay and email and password:
            # Short local loading effect (Uses 0 extra data)
            with st.status("VERIFYING...", expanded=False) as status:
                time.sleep(1.5)
                status.update(label="VERIFIED!", state="complete", expanded=False)
            
            st.session_state.user_name = full_name
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("MISSING INFORMATION")

# --- 2. DASHBOARD ---
elif st.session_state.page == "dashboard":
    st.markdown(f"### WELCOME, {st.session_state.user_name}")
    st.caption("INVESTOR STATUS: ACTIVE ✅")
    
    # Compact metrics for phone screens
    st.metric("BALANCE", "$4,250.00", "+$150.00")
    
    st.markdown("---")
    
    # Big touch-friendly buttons
    if st.button("📥 ADD FUNDS"):
        st.info("SECURE PAYMENT PORTAL OPENING...")
        
    if st.button("📤 WITHDRAW"):
        st.warning("PROCESSING WITHDRAWAL...")

    if st.button("LOGOUT"):
        st.session_state.page = "signup"
        st.rerun()
        
