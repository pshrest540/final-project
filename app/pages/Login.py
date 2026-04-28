import streamlit as st
import session

st.set_page_config(
    page_title="Login — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "token" in st.session_state:
    _at = st.session_state.get("user", {}).get("account_type", "personal")
    st.switch_page("pages/Admin.py" if _at == "admin" else "pages/Home.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background: #070707;
    color: #f0f0f0;
}
.stApp {
    background: radial-gradient(ellipse 120% 60% at 50% 0%, #131313 0%, #070707 65%);
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 5rem; padding-bottom: 2rem; max-width: 420px; }

/* ── Wordmark ─────────────────────────────────────────────────── */
.brand-wrap {
    text-align: center;
    margin-bottom: 3rem;
}
.brand-name {
    font-family: 'Share Tech Mono', monospace;
    font-size: 4.5rem;
    color: #ffffff;
    letter-spacing: 0.55em;
    margin-right: -0.55em;
    line-height: 1;
    display: block;
}
.brand-rule {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
    margin: 0.9rem 0 0.7rem;
}
.brand-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #3d3d3d;
    letter-spacing: 0.38em;
    text-transform: uppercase;
}

/* ── Auth card ────────────────────────────────────────────────── */
.auth-card {
    background: #0c0c0c;
    border: 1px solid #1c1c1c;
    border-radius: 6px;
    padding: 2.2rem 2rem 1.8rem;
    position: relative;
}
.auth-card::before {
    content: '';
    position: absolute;
    top: 0; left: 12%; right: 12%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.55), transparent);
}
.auth-card-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    color: #2e2e2e;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 1.4rem;
}

/* ── Inputs ───────────────────────────────────────────────────── */
.stTextInput label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.6rem !important;
    color: #4a4a4a !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
}
.stTextInput > div > div > input {
    background: #101010 !important;
    border: 1px solid #222222 !important;
    border-radius: 4px !important;
    color: #f0f0f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.6rem 0.85rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #5a5a5a !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.04) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #2a2a2a !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Primary CTA button ───────────────────────────────────────── */
.stButton > button {
    width: 100%;
    background: #f5f5f5 !important;
    color: #050505 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.25em !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.82rem 2rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 2px 16px rgba(255,255,255,0.06) !important;
    transition: background 0.15s, box-shadow 0.15s, transform 0.1s !important;
    margin-top: 0.6rem;
}
.stButton > button:hover {
    background: #ffffff !important;
    box-shadow: 0 6px 28px rgba(255,255,255,0.13) !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(255,255,255,0.06) !important;
}

/* ── Ghost / link button ──────────────────────────────────────── */
[data-testid="stLinkButton"] > a {
    display: block;
    width: 100%;
    text-align: center;
    background: transparent !important;
    border: 1px solid #1e1e1e !important;
    color: #3a3a3a !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.66rem !important;
    letter-spacing: 0.15em !important;
    border-radius: 4px !important;
    padding: 0.68rem 1rem !important;
    margin-top: 0.75rem;
    text-decoration: none !important;
    transition: border-color 0.15s, color 0.15s !important;
}
[data-testid="stLinkButton"] > a:hover {
    border-color: #4a4a4a !important;
    color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Wordmark ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-wrap">
    <span class="brand-name">MIA</span>
    <div class="brand-rule"></div>
    <span class="brand-tag">Predictive Maintenance Intelligence</span>
</div>
""", unsafe_allow_html=True)

# ── Auth card ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="auth-card">
    <div class="auth-card-label">// Authentication required</div>
</div>
""", unsafe_allow_html=True)

email    = st.text_input("Email",    placeholder="you@example.com", key="login_email")
password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("LOGIN"):
    if not email or not password:
        st.error("Please enter your email and password.")
    else:
        try:
            resp = session.post("/auth/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["user"]  = data["user"]
                if data["user"].get("account_type") == "admin":
                    st.switch_page("pages/Admin.py")
                else:
                    st.switch_page("pages/Home.py")
            else:
                st.error(resp.json().get("detail", "Login failed."))
        except Exception as e:
            st.error(f"Could not reach API: {e}")

st.link_button("NO ACCOUNT? REGISTER HERE →", url="/Register")
