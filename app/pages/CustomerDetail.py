import html as _html
import streamlit as st
import session

st.set_page_config(
    page_title="Customer Detail — VEHIDOC",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_cust = st.session_state.get("selected_customer")
if not _cust:
    st.switch_page("pages/Customers.py")

_user = st.session_state.get("user", {})
if not (isinstance(_user, dict) and _user.get("account_type") == "business"):
    st.switch_page("pages/Home.py")

_token      = st.session_state["token"]
_name       = _html.escape(_cust.get("full_name") or _cust.get("email") or _cust["user_id"])
_cid        = _cust.get("share_code") or "—"
_share_code = _cust.get("share_code")
_vcount     = _cust.get("shared_vehicle_count", 0)

_bg         = "#f0f4f8"
_accent     = "#0066b3"
_fg         = "#1a2a3a"
_fg2        = "#4a6a8a"
_border     = "#d0dce8"
_card_g     = "#ffffff"
_vin_color  = "#7a9abc"
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
.cust-header {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 14px; padding: 1.5rem 2rem 1.2rem; margin-bottom: 1.5rem; position: relative; overflow: hidden; }}
.cust-header::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {_top}; }}
.cust-h-name {{ font-size: 1.6rem; font-weight: 700; color: {_fg}; margin-bottom: 0.2rem; }}
.cust-h-id {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.2em; }}
.v-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.2rem 1.4rem 0.8rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }}
.v-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.v-year {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.2rem; }}
.v-name {{ font-size: 1.25rem; font-weight: 700; color: {_fg}; letter-spacing: 0.03em; margin-bottom: 0.2rem; }}
.v-mileage {{ font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: {_accent}; margin-bottom: 0.3rem; }}
.v-vin {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_vin_color}; letter-spacing: 0.1em; }}
.empty-state {{ background: #f8fafc; border: 1px dashed #c0d0e0; border-radius: 10px; padding: 3rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 28px {_shadow_h} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
_col_back, _col_title = st.columns([1, 5])
with _col_back:
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/Customers.py")
with _col_title:
    st.markdown('<div class="page-title">// CUSTOMER DETAIL</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Customer header ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="cust-header">
  <div class="cust-h-name">{_name}</div>
  <div class="cust-h-id">ID: {_cid}</div>
</div>
""", unsafe_allow_html=True)

# ── Load shared vehicles via search endpoint ───────────────────────────────────
vehicles = []
if _share_code:
    try:
        r = session.get(f"/sharing/search?share_code={_share_code}", token=_token)
        if r.status_code == 200:
            vehicles = r.json().get("vehicles", [])
    except Exception:
        st.error("Could not load vehicles.")

st.markdown(
    f'<div class="section-label">{len(vehicles)} SHARED VEHICLE{"S" if len(vehicles) != 1 else ""}</div>',
    unsafe_allow_html=True,
)

if not vehicles:
    st.markdown('<div class="empty-state">NO SHARED VEHICLES</div>', unsafe_allow_html=True)
else:
    cols = st.columns(3, gap="medium")
    for i, v in enumerate(vehicles):
        with cols[i % 3]:
            _vin = f'<div class="v-vin">VIN: {_html.escape(v["vin"])}</div>' if v.get("vin") else ""
            st.markdown(f"""
<div class="v-card">
  <div class="v-year">// {v["year"]}</div>
  <div class="v-name">{_html.escape(v["brand"])} {_html.escape(v["model"])}</div>
  <div class="v-mileage">{v["current_mileage"]:,} miles</div>
  {_vin}
</div>""", unsafe_allow_html=True)
            if st.button("DETAILS", key=f"vdet_{v['vehicle_id']}", use_container_width=True):
                st.session_state["selected_vehicle"] = v
                st.switch_page("pages/VehicleDetail.py")
