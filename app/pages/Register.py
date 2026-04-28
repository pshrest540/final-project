import streamlit as st
import session

st.set_page_config(
    page_title="Register — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "token" in st.session_state:
    st.switch_page("pages/Home.py")

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
.block-container { padding-top: 3rem; padding-bottom: 2rem; max-width: 460px; }

/* ── Wordmark ─────────────────────────────────────────────────── */
.brand-wrap {
    text-align: center;
    margin-bottom: 2rem;
}
.brand-name {
    font-family: 'Share Tech Mono', monospace;
    font-size: 3rem;
    color: #ffffff;
    letter-spacing: 0.55em;
    margin-right: -0.55em;
    line-height: 1;
    display: block;
}
.brand-rule {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    margin: 0.7rem 0 0.55rem;
}
.brand-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    color: #383838;
    letter-spacing: 0.35em;
    text-transform: uppercase;
}

/* ── Auth card ────────────────────────────────────────────────── */
.auth-card {
    background: #0c0c0c;
    border: 1px solid #1c1c1c;
    border-radius: 6px;
    padding: 1.8rem 2rem 1.5rem;
    position: relative;
    margin-bottom: 0;
}
.auth-card::before {
    content: '';
    position: absolute;
    top: 0; left: 12%; right: 12%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
}
.auth-heading {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    color: #d8d8d8;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.auth-card-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.56rem;
    color: #2e2e2e;
    letter-spacing: 0.28em;
    text-transform: uppercase;
}

/* ── Inputs ───────────────────────────────────────────────────── */
.stTextInput label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.6rem !important;
    color: #4a4a4a !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}
.stTextInput > div > div > input {
    background: #101010 !important;
    border: 1px solid #222222 !important;
    border-radius: 4px !important;
    color: #f0f0f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.55rem 0.85rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #5a5a5a !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.04) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #292929 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Selectbox */
.stSelectbox label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.6rem !important;
    color: #4a4a4a !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}
.stSelectbox > div > div {
    background: #101010 !important;
    border: 1px solid #222222 !important;
    border-radius: 4px !important;
    color: #f0f0f0 !important;
}

/* ── Primary CTA ──────────────────────────────────────────────── */
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
    margin-top: 0.5rem;
}
.stButton > button:hover {
    background: #ffffff !important;
    box-shadow: 0 6px 28px rgba(255,255,255,0.13) !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Ghost / link ─────────────────────────────────────────────── */
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

/* Divider */
.field-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1a1a1a, transparent);
    margin: 0.8rem 0;
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

# ── Card header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="auth-card">
    <div class="auth-heading">Create Account</div>
    <div class="auth-card-label">// New user registration</div>
</div>
""", unsafe_allow_html=True)

# ── Fields ────────────────────────────────────────────────────────────────────
full_name = st.text_input("Full Name (optional)", placeholder="Jane Smith",   key="reg_name")
email     = st.text_input("Email",                placeholder="you@example.com", key="reg_email")

col_pw, col_cf = st.columns(2, gap="small")
with col_pw:
    password = st.text_input("Password", type="password", placeholder="Min 8 chars", key="reg_password")
with col_cf:
    confirm  = st.text_input("Confirm",  type="password", placeholder="Repeat",       key="reg_confirm")

st.markdown('<div class="field-divider"></div>', unsafe_allow_html=True)

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
            payload = {"email": email, "password": password, "account_type": account_type}
            if full_name:
                payload["full_name"] = full_name
            if business_name:
                payload["business_name"] = business_name

            resp = session.post("/auth/register", json=payload)
            if resp.status_code == 201:
                data = resp.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["user"]  = data["user"]
                st.switch_page("pages/Home.py")
            else:
                st.error(resp.json().get("detail", "Registration failed."))
        except Exception as e:
            st.error(f"Could not reach API: {e}")

st.link_button("ALREADY HAVE AN ACCOUNT? LOGIN →", url="/Login")
