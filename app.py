import streamlit as st
import time
from datetime import datetime, timedelta

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="BP Market", page_icon="🇵🇭")

st.markdown("""
    <style>
    .stApp { margin-top: 50px; }
    input[type="text"] { text-transform: uppercase; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #0038a8;
        color: white;
        font-weight: bold;
        border: none;
    }
    .deposit-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE APP MEMORY ---
if 'page' not in st.session_state:
    st.session_state.page = "signup"  # FORCES SIGNUP FIRST
if 'deposits' not in st.session_state:
    st.session_state.deposits = []
if 'user_pin' not in st.session_state:
    st.session_state.user_pin = ""

# --- 3. PAGE 1: SIGN UP (MANDATORY) ---
if st.session_state.page == "signup":
    st.markdown("<h2 style='text-align: center;'>🇵🇭 ACCOUNT REGISTRATION</h2>", unsafe_allow_html=True)
    
    full_name = st.text_input("FULL NAME (SURNAME, FIRST NAME)").upper()
    age = st.number_input("AGE", min_value=18, max_value=100, step=1)
    st.text_input("COUNTRY", value="PHILIPPINES", disabled=True)

    region = st.selectbox("REGION", ["NCR", "CAR", "REGION I", "REGION II", "REGION III", "REGION IV-A", "MIMAROPA", "REGION V", "REGION VI", "REGION VII", "REGION VIII", "REGION IX", "REGION X", "REGION XI", "REGION XII", "REGION XIII", "BARMM"])
    city = st.text_input("CITY / MUNICIPALITY").upper()
    barangay = st.text_input("BARANGAY").upper()
    
    st.markdown("---")
    reg_pin = st.text_input("CREATE 6-DIGIT PIN", type="password", max_chars=6)
    st.caption("⚠️ NUMBERS ONLY - REQUIRED FOR WITHDRAWALS")

    if st.button("REGISTER & ENTER MARKET"):
        if full_name and city and barangay and len(reg_pin) == 6 and reg_pin.isdigit():
            st.session_state.user_name = full_name
            st.session_state.user_pin = reg_pin
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("❌ COMPLETE ALL FIELDS AND USE A 6-DIGIT PIN")

# --- 4. PAGE 2: DASHBOARD ---
elif st.session_state.page == "dashboard":
    # Profit Logic (20% Daily)
    total_principal = sum(d['amount'] for d in st.session_state.deposits)
    total_profit = sum(d['amount'] * 0.20 for d in st.session_state.deposits)
    total_balance = total_principal + total_profit

    st.markdown(f"### WELCOME, {st.session_state.user_name}!")
    st.metric("TOTAL BALANCE", f"₱{total_balance:,.2f}")

    st.markdown("---")
    st.subheader("📥 DEPOSIT")
    amounts = [100, 500, 1000, 5000, 10000, 20000, 30000, 50000]
    selected_amt = st.selectbox("SELECT AMOUNT", amounts)
    
    if st.button(f"INVEST ₱{selected_amt:,}"):
        new_dep = {
            "amount": float(selected_amt),
            "release_time": datetime.now() + timedelta(hours=24),
            "profit": float(selected_amt) * 0.20
        }
        st.session_state.deposits.append(new_dep)
        st.success("INVESTMENT ADDED!")
        st.rerun()

    # --- WITHDRAW ---
    st.markdown("---")
    st.subheader("📤 WITHDRAW")
    w_amount = st.number_input("AMOUNT", min_value=0.0)
    confirm_pin = st.text_input("CONFIRM 6-DIGIT PIN", type="password", max_chars=6)
    
    if st.button("REQUEST WITHDRAWAL"):
        if total_balance < 500 or w_amount < 500:
            st.error("⚠️ MINIMUM WITHDRAWAL IS ₱500.00")
        elif confirm_pin != st.session_state.user_pin:
            st.error("❌ INCORRECT PIN")
        else:
            st.success("WITHDRAWAL REQUEST SENT TO ADMIN")

    if st.button("LOGOUT"):
        st.session_state.page = "signup"
        st.rerun()
