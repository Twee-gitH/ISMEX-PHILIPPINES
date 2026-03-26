import streamlit as st

# Set Page Config for Mobile
st.set_page_config(page_title="Bagong Pilipinas Stock Market", page_icon="📈")

# Custom CSS to make it look like a Professional App
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 15px;
        height: 3.5em;
        background-color: #1d4ed8;
        color: white;
        font-weight: bold;
        border: none;
    }
    .payout-card {
        background-color: #0f172a;
        padding: 20px;
        border-radius: 20px;
        color: #4ade80;
        text-align: center;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. LOGIN SYSTEM
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🇵🇭 BAGONG PILIPINAS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Authorized Stock Market Portal</p>", unsafe_allow_html=True)
    
    user = st.text_input("Username")
    pas = st.text_input("Password", type="password")
    
    if st.button("ENTER MARKET"):
        if user and pas:
            st.session_state['logged_in'] = True
            st.rerun()
else:
    # 2. DASHBOARD
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["📈 Invest", "💸 Withdraw", "👤 Profile"])

    if choice == "📈 Invest":
        st.header("Select Investment Plan")
        st.info("Guaranteed ROI payout every 24 Hours")
        
        # Creating columns for the buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("$100"):
                st.session_state['amt'] = 110
                st.session_state['tier'] = "Starter"
        with col2:
            if st.button("$500"):
                st.session_state['amt'] = 600
                st.session_state['tier'] = "Silver"
        with col3:
            if st.button("$1000"):
                st.session_state['amt'] = 1300
                st.session_state['tier'] = "Gold"

        if 'amt' in st.session_state:
            st.markdown(f"""
                <div class="payout-card">
                    <p style="color:#94a3b8; font-size:12px; font-weight:bold;">{st.session_state['tier'].upper()} TIER - 24HR PAYOUT</p>
                    <h1 style="margin:0; font-size:45px;">${st.session_state['amt']}</h1>
                </div>
            """, unsafe_allow_html=True)
            if st.button("CONFIRM & STAKE NOW"):
                st.success("Stake Successful! Your profit will be ready in 24 hours.")

    elif choice == "💸 Withdraw":
        st.header("Withdrawal Portal")
        st.metric("Total Balance", "$4,250.00", "+$150.00 today")
        
        address = st.text_input("Wallet Address / GCASH Number")
        w_amt = st.number_input("Amount to Withdraw ($)", min_value=10)
        
        if st.button("PROCESS WITHDRAWAL"):
            if address:
                st.warning("Request Received. Verifying on blockchain... (5-30 mins)")
            else:
                st.error("Please enter a valid address.")

    elif choice == "👤 Profile":
        st.header("Investor Account")
        st.write("Status: **Verified Member**")
        st.write("Join Date: March 2026")
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
