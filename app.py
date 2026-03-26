import streamlit as st
import time
from datetime import datetime, timedelta

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="BP Market", page_icon="🇵🇭")

# --- 2. THEME & UI ---
st.markdown("""
<style>
    .stApp { margin-top: 20px; }
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
    .logo-text {
        text-align: center;
        color: #0038a8;
        font-weight: 900;
        font-size: 2.2em;
        line-height: 1.2;
    }
    .payment-box {
        background-color: #e0f2fe;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #0038a8;
        margin-top: 10px;
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

# --- 3. LOGO ---
st.markdown('<p class="logo-text">🇵🇭 BAGONG<br>PILIPINAS</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-weight: bold;'>AUTHORIZED STOCK MARKET PORTAL</p>", unsafe_allow_html=True)

# --- 4. SESSION STATE (MEMORY) ---
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'db_user' not in st.session_state:
    st.session_state.db_user = None
if 'deposits' not in st.session_state:
    st.session_state.deposits = []
if 'show_payment' not in st.session_state:
    st.session_state.show_payment = False

# --- 5. PAGE: LOGIN ---
if st.session_state.page == "login":
    st.subheader("LOGIN")
    l_name = st.text_input("FULL NAME").upper()
    l_pin = st.text_input("6-DIGIT PIN", type="password", max_chars=6)
    
    if st.button("ENTER MARKET"):
        if st.session_state.db_user and l_name == st.session_state.db_user['name'] and l_pin == st.session_state.db_user['pin']:
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("INVALID CREDENTIALS")
    
    st.write("---")
    if st.button("NO ACCOUNT? SIGN UP HERE"):
        st.session_state.page = "signup"
        st.rerun()

# --- 6. PAGE: SIGN UP ---
elif st.session_state.page == "signup":
    st.subheader("CREATE ACCOUNT")
    reg_name = st.text_input("FULL NAME").upper()
    reg_address = st.text_input("FULL ADDRESS").upper()
    st.markdown("---")
    pin1 = st.text_input("CREATE 6-DIGIT PIN", type="password", max_chars=6)
    pin2 = st.text_input("VERIFY 6-DIGIT PIN", type="password", max_chars=6)

    if st.button("COMPLETE REGISTRATION"):
        if not reg_name or not reg_address:
            st.error("PLEASE FILL ALL FIELDS")
        elif pin1 != pin2:
            st.error("❌ PINS DO NOT MATCH")
        elif len(pin1) != 6 or not pin1.isdigit():
            st.error("❌ PIN MUST BE 6 NUMBERS")
        else:
            st.session_state.db_user = {"name": reg_name, "pin": pin1, "address": reg_address}
            st.success("✅ SUCCESS! REDIRECTING TO LOGIN...")
            time.sleep(1.5)
            st.session_state.page = "login"
            st.rerun()

# --- 7. PAGE: DASHBOARD ---
elif st.session_state.page == "dashboard":
    # Calculate Profit: 20% return (e.g., ₱100 turns into ₱120)
    total_principal = sum(d['amount'] for d in st.session_state.deposits)
    total_profit = sum(d['amount'] * 0.20 for d in st.session_state.deposits)
    total_balance = total_principal + total_profit

    st.markdown(f"### WELCOME, {st.session_state.db_user['name']}!")
    st.metric("TOTAL BALANCE", f"₱{total_balance:,.2f}")

    st.markdown("---")
    st.subheader("📥 INVEST (GCASH / BANK)")
    selected_amt = st.selectbox("PESO AMOUNT", [100, 500, 1000, 5000, 10000, 20000, 30000, 50000])
    
    if st.button(f"PROCEED TO PAY ₱{selected_amt:,}"):
        st.session_state.show_payment = True
        st.session_state.pending_amt = selected_amt

    if st.session_state.show_payment:
        st.markdown(f"""
        <div class="payment-box">
            <b>STEP 1:</b> Send ₱{st.session_state.pending_amt:,} to GCASH: <b>[YOUR NUMBER HERE]</b><br>
            <b>STEP 2:</b> Keep your receipt screenshot.<br>
            <b>STEP 3:</b> Click 'CONFIRM' once sent.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ I HAVE SENT THE PAYMENT"):
            new_dep = {
                "amount": float(st.session_state.pending_amt),
                "release_time": datetime.now() + timedelta(hours=24),
                "profit": float(st.session_state.pending_amt) * 0.20
            }
            st.session_state.deposits.append(new_dep)
            st.session_state.show_payment = False
            st.success("PAYMENT REGISTERED! INVESTMENT ACTIVE.")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.subheader("⏳ ACTIVE INVESTMENTS")
    for d in st.session_state.deposits:
        rem = d['release_time'] - datetime.now()
        timer = f"🕒 {int(rem.total_seconds()//3600)}h {int((rem.total_seconds()%3600)//60)}m left" if rem.total_seconds() > 0 else "✅ READY"
        st.markdown(f'<div class="deposit-card"><b>₱{d["amount"]:,}</b><br><span style="color:green;">+₱{d["profit"]:,} (20%)</span><br><small>{timer}</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📤 WITHDRAW")
    st.caption("MINIMUM WITHDRAWAL: ₱500.00")
    w_amt = st.number_input("AMOUNT", min_value=0.0)
    w_pin = st.text_input("CONFIRM PIN TO WITHDRAW", type="password", max_chars=6)
    
    if st.button("WITHDRAW"):
        if total_balance < 500 or w_amt < 500:
            st.error("⚠️ MINIMUM ₱500.00")
        elif w_pin != st.session_state.db_user['pin']:
            st.error("❌ INCORRECT PIN")
        elif w_amt > total_balance:
            st.error("❌ INSUFFICIENT BALANCE")
        else:
            st.success("SUCCESS! REQUEST SENT TO ADMIN.")

    if st.button("LOGOUT"):
        st.session_state.page = "login"
        st.rerun()
