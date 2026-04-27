import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Login — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

if "token" in st.session_state:
    st.switch_page("pages/Home.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0a0e1a; color: #c8d8e8; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 5rem; padding-bottom: 2rem; max-width: 480px; }
.auth-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 14px; padding: 2.5rem 2rem 1.5rem; position: relative; overflow: hidden; margin-bottom: 1.5rem; }
.auth-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.auth-title { font-family: 'Share Tech Mono', monospace; font-size: 2.4rem; color: #00d4ff; text-align: center; letter-spacing: 0.1em; text-shadow: 0 0 24px rgba(0,212,255,0.4); margin-bottom: 0.2rem; }
.auth-sub { font-size: 0.8rem; color: #5a7a9a; text-align: center; letter-spacing: 0.25em; text-transform: uppercase; }
.auth-divider { width: 60px; height: 1px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1rem auto 0; }
.stTextInput > div > div > input { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stTextInput > div > div > input:focus { border-color: #00d4ff !important; box-shadow: 0 0 10px rgba(0,212,255,0.2) !important; }
.stButton > button { width: 100%; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important; color: #0a0e1a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 0 20px rgba(0,212,255,0.3) !important; margin-top: 0.5rem; }
.stButton > button:hover { box-shadow: 0 0 35px rgba(0,212,255,0.6) !important; }
[data-testid="stLinkButton"] > a { display: block; width: 100%; text-align: center; background: transparent !important; border: 1px solid #1e3a5f !important; color: #5a7a9a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.1em !important; border-radius: 8px !important; padding: 0.6rem 1rem !important; margin-top: 0.8rem; text-decoration: none !important; }
[data-testid="stLinkButton"] > a:hover { border-color: #00d4ff !important; color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-card">
    <div class="auth-title">MIA</div>
    <div class="auth-sub">Predictive Maintenance</div>
    <div class="auth-divider"></div>
</div>
""", unsafe_allow_html=True)

email = st.text_input("Email", placeholder="you@example.com", key="login_email")
password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("LOGIN"):
    if not email or not password:
        st.error("Please enter your email and password.")
    else:
        try:
            resp = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": email, "password": password},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                st.switch_page("pages/Home.py")
            else:
                st.error(resp.json().get("detail", "Login failed."))
        except Exception as e:
            st.error(f"Could not reach API: {e}")

st.link_button("NO ACCOUNT? REGISTER HERE →", url="/Register")
