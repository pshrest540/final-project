import html as _html
from datetime import datetime
import streamlit as st
import session

st.set_page_config(
    page_title="Customers — VEHIDOC",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_user = st.session_state.get("user", {})
if not (isinstance(_user, dict) and _user.get("account_type") == "business"):
    st.switch_page("pages/Home.py")

_token = st.session_state["token"]

_bg         = "#f0f4f8"
_accent     = "#0066b3"
_fg         = "#1a2a3a"
_fg2        = "#4a6a8a"
_border     = "#d0dce8"
_card_g     = "#ffffff"
_inp_bg     = "#ddeaf5"
_inp_border = "#85aac7"
_btn_g      = "linear-gradient(135deg,#0066b3 0%,#004d8c 100%)"
_btn_c      = "#ffffff"
_shadow     = "rgba(0,102,179,0.25)"
_shadow_h   = "rgba(0,102,179,0.5)"
_top        = f"linear-gradient(90deg,transparent,{_accent},transparent)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {_bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.page-title {{ font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: {_accent}; letter-spacing: 0.1em; text-shadow: 0 0 20px {_shadow}; }}
.divider {{ height: 1px; background: linear-gradient(90deg,{_accent} 0%,transparent 60%); margin: 0.5rem 0 1.5rem; opacity: 0.3; }}
.filter-panel {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.2rem 1.6rem 1rem; margin-bottom: 1.5rem; }}
.cust-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.1rem 1.4rem 0.9rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }}
.cust-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.cust-name {{ font-size: 1.2rem; font-weight: 700; color: {_fg}; margin-bottom: 0.15rem; }}
.cust-id {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.2em; margin-bottom: 0.15rem; }}
.cust-meta {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.1em; }}
.empty-state {{ background: #f8fafc; border: 1px dashed #c0d0e0; border-radius: 10px; padding: 3rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }}
.stTextInput > div > div > input {{
    background: {_inp_bg} !important; border: 1px solid {_inp_border} !important;
    border-radius: 6px !important; color: {_fg} !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {_accent} !important;
    box-shadow: 0 0 0 3px rgba(0,102,179,0.12) !important; outline: none !important;
}}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 28px {_shadow_h} !important; }}
[data-testid="InputInstructions"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
_col_back, _col_title = st.columns([1, 5])
with _col_back:
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/Home.py")
with _col_title:
    st.markdown('<div class="page-title">// CUSTOMERS</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Load all linked customers ──────────────────────────────────────────────────
all_customers = session.fetch_linked_customers(_token) or []

# ── Filter panel ──────────────────────────────────────────────────────────────
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown('<div class="section-label">// FILTER</div>', unsafe_allow_html=True)
_f1, _f2, _f3 = st.columns(3)
with _f1:
    _fname = st.text_input("Name or email", placeholder="Search name or email", key="cf_name")
with _f2:
    _fid = st.text_input("Customer ID", placeholder="ABC123", max_chars=6, key="cf_id")
with _f3:
    _fdate = st.date_input("Linked on or after", value=None, key="cf_date")
st.markdown('</div>', unsafe_allow_html=True)

# ── Apply filters (client-side) ────────────────────────────────────────────────
filtered = all_customers
if _fname.strip():
    _q = _fname.strip().lower()
    filtered = [
        c for c in filtered
        if _q in (c.get("full_name") or "").lower() or _q in (c.get("email") or "").lower()
    ]
if _fid.strip():
    _q = _fid.strip().upper()
    filtered = [c for c in filtered if _q in (c.get("share_code") or "").upper()]
if _fdate:
    filtered = [
        c for c in filtered
        if c.get("linked_at") and datetime.fromisoformat(
            c["linked_at"].replace("Z", "+00:00")
        ).date() >= _fdate
    ]

# ── Customer list ──────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="section-label">{len(filtered)} CUSTOMER{"S" if len(filtered) != 1 else ""}</div>',
    unsafe_allow_html=True,
)

if not filtered:
    if all_customers:
        st.markdown('<div class="empty-state">NO CUSTOMERS MATCH YOUR FILTER</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty-state">NO LINKED CUSTOMERS YET<br>'
            '<span style="font-size:0.7rem;opacity:0.6">Use ADD CUSTOMER on the dashboard to link a customer via their connection code.</span></div>',
            unsafe_allow_html=True,
        )
else:
    for c in filtered:
        _cname = _html.escape(c.get("full_name") or c.get("email") or c["user_id"])
        _cid   = c.get("share_code") or "—"
        _vcount = c.get("shared_vehicle_count", 0)
        _lat   = c.get("linked_at") or ""
        if _lat:
            try:
                _lat = datetime.fromisoformat(_lat.replace("Z", "+00:00")).strftime("%b %d, %Y")
            except Exception:
                pass

        _col_card, _col_btn = st.columns([5, 1])
        with _col_card:
            st.markdown(f"""
<div class="cust-card">
  <div class="cust-name">{_cname}</div>
  <div class="cust-id">ID: {_cid}</div>
  <div class="cust-meta">LINKED: {_lat or "—"} &nbsp;·&nbsp; {_vcount} SHARED VEHICLE{"S" if _vcount != 1 else ""}</div>
</div>""", unsafe_allow_html=True)
        with _col_btn:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("DETAILS", key=f"cdet_{c['user_id']}", use_container_width=True):
                st.session_state["selected_customer"] = c
                st.switch_page("pages/CustomerDetail.py")
