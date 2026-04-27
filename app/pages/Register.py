import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Register — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "120"))

if "token" in st.session_state:
    st.switch_page("pages/Home.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0a0e1a; color: #c8d8e8; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 3rem; padding-bottom: 2rem; max-width: 520px; }
.auth-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 14px; padding: 2rem 2rem 1.2rem; position: relative; overflow: hidden; margin-bottom: 1.5rem; }
.auth-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.auth-title { font-family: 'Share Tech Mono', monospace; font-size: 2rem; color: #00d4ff; text-align: center; letter-spacing: 0.1em; text-shadow: 0 0 24px rgba(0,212,255,0.4); margin-bottom: 0.2rem; }
.auth-sub { font-size: 0.8rem; color: #5a7a9a; text-align: center; letter-spacing: 0.25em; text-transform: uppercase; }
.auth-divider { width: 60px; height: 1px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1rem auto 0; }
.stTextInput > div > div > input { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stTextInput > div > div > input:focus { border-color: #00d4ff !important; box-shadow: 0 0 10px rgba(0,212,255,0.2) !important; }
.stSelectbox > div > div { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stButton > button { width: 100%; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important; color: #0a0e1a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 0 20px rgba(0,212,255,0.3) !important; margin-top: 0.5rem; }
.stButton > button:hover { box-shadow: 0 0 35px rgba(0,212,255,0.6) !important; }
[data-testid="stLinkButton"] > a { display: block; width: 100%; text-align: center; background: transparent !important; border: 1px solid #1e3a5f !important; color: #5a7a9a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.1em !important; border-radius: 8px !important; padding: 0.6rem 1rem !important; margin-top: 0.8rem; text-decoration: none !important; }
[data-testid="stLinkButton"] > a:hover { border-color: #00d4ff !important; color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-card">
    <div class="auth-title">CREATE ACCOUNT</div>
    <div class="auth-sub">Join MIA — Predictive Maintenance</div>
    <div class="auth-divider"></div>
</div>
""", unsafe_allow_html=True)

full_name = st.text_input("Full Name (optional)", placeholder="Jane Smith", key="reg_name")
email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
password = st.text_input("Password", type="password", placeholder="At least 8 characters", key="reg_password")
confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_confirm")

account_type = st.selectbox(
    "Account Type",
    options=["personal", "business"],
    format_func=lambda x: "Personal" if x == "personal" else "Business",
    key="reg_account_type",
)

business_name = None
if account_type == "business":
    business_name = st.text_input("Business Name", placeholder="Acme Auto Shop", key="reg_business")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("CREATE ACCOUNT"):
    errors = []
    if not email:
        errors.append("Email is required.")
    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")
    if account_type == "business" and not business_name:
        errors.append("Business name is required for business accounts.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        try:
            payload = {
                "email": email,
                "password": password,
                "account_type": account_type,
            }
            if full_name:
                payload["full_name"] = full_name
            if business_name:
                payload["business_name"] = business_name

            resp = requests.post(
                f"{API_BASE}/auth/register",
                json=payload,
                timeout=API_TIMEOUT,
            )
            if resp.status_code == 201:
                data = resp.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                st.switch_page("pages/Home.py")
            else:
                st.error(resp.json().get("detail", "Registration failed."))
        except Exception as e:
            st.error(f"Could not reach API: {e}")

st.link_button("ALREADY HAVE AN ACCOUNT? LOGIN →", url="/Login")
