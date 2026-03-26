import streamlit as st
from datetime import datetime

# --- 1. MOBILE-FIRST UI ---
st.set_page_config(page_title="BP Market", page_icon="🇵🇭")
st.markdown("""<style>
    .stApp { margin: 0; padding: 0; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background: #0038a8; color: white; }
    input { text-transform: uppercase; }
    .card { background: #f1f5f9; padding: 10px; border-radius: 8px; border-left: 4px solid #0038a8; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

# --- 2. LOGO ---
st.markdown("<h2 style='text-align:center; color:#0038a8;'>🇵🇭 BAGONG PILIPINAS</h2>", unsafe_allow_html=True)
st.caption("AUTHORIZED STOCK MARKET PORTAL")

# --- 3. SESSION STATE ---
for key in ['pg', 'users', 'user', 'pending']:
    if key not in st.session_state:
        st.session_state.pg = 'login'
        st.session_state.users = []
        st.session_state.user = None
        st.session_state.pending = []

# --- 4. PAGES ---
if st.session_state.pg == "login":
    name = st.text_input("FULL NAME").upper()
    pin = st.text_input("PIN / PASSWORD", type="password")
    if st.button("ENTER"):
        if name == "ADMIN" and pin == "090807":
            st.session_state.pg = "admin"
            st.rerun()
        user = next((u for u in st.session_state.users if u['n'] == name and u['p'] == pin), None)
        if user:
            st.session_state.user = user
            st.session_state.pg = "dash"
            st.rerun()
    if st.button("SIGN UP"):
        st.session_state.pg = "signup"
        st.rerun()

elif st.session_state.pg == "signup":
    n = st.text_input("NAME").upper()
    p = st.text_input("6-DIGIT PIN", type="password", max_chars=6)
    if st.button("REGISTER"):
        if n and len(p) == 6:
            st.session_state.users.append({"n": n, "p": p, "inv": []})
            st.session_state.pg = "login"
            st.rerun()

elif st.session_state.pg == "admin":
    st.subheader("👑 OWNER")
    total = sum(sum(i for i in u['inv']) for u in st.session_state.users)
    st.metric("TOTAL CAPITAL", f"₱{total:,.2f}")
    
    t1, t2 = st.tabs(["INVESTORS", "PENDING"])
    with t1:
        for u in st.session_state.users:
            p = sum(u['inv'])
            st.markdown(f"<div class='card'><b>{u['n']}</b><br>Bal: ₱{p*1.2:,.2f} (Int: ₱{p*0.2:,.2f})</div>", unsafe_allow_html=True)
    with t2:
        for i, d in enumerate(st.session_state.pending):
            st.write(f"{d['u']}: ₱{d['a']:,}")
            if st.button("APPROVE", key=f"ap{i}"):
                for u in st.session_state.users:
                    if u['n'] == d['u']: u['inv'].append(d['a'])
                st.session_state.pending.pop(i)
                st.rerun()
    if st.button("LOGOUT"):
        st.session_state.pg = "login"
        st.rerun()

elif st.session_state.pg == "dash":
    u = st.session_state.user
    st.info("YOUR EVERY PENNY IS USED TO TRADE IN THE STOCK MARKET OR BLACK MARKET INTERNATIONAL TRADING OF COMMODITIES.")
    p = sum(u['inv'])
    st.metric("TOTAL BALANCE", f"₱{p*1.2:,.2f}", f"+₱{p*0.2:,.2f}")
    
    amt = st.selectbox("AMOUNT", [500, 1000, 5000, 10000])
    if st.button(f"INVEST ₱{amt:,}"):
        st.session_state.pending.append({"u": u['n'], "a": float(amt)})
        st.success("Sent to Admin!")
    
    if st.button("LOGOUT"):
        st.session_state.pg = "login"
        st.rerun()
