import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Dashboard — MIA",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "120"))

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_user   = st.session_state.get("user", {})
_is_biz = isinstance(_user, dict) and _user.get("account_type") == "business"

# ── Theme tokens ──────────────────────────────────────────────────────────────
_bg      = "#f0f4f8"  if _is_biz else "#0a0e1a"
_accent  = "#0066b3"  if _is_biz else "#00d4ff"
_fg      = "#1a2a3a"  if _is_biz else "#c8d8e8"
_fg2     = "#4a6a8a"  if _is_biz else "#5a7a9a"
_border  = "#d0dce8"  if _is_biz else "#1e3a5f"
_card_g  = "#ffffff"  if _is_biz else "linear-gradient(135deg,#0f1628 0%,#111827 100%)"
_btn_g   = "linear-gradient(135deg,#0066b3 0%,#004d8c 100%)" if _is_biz else "linear-gradient(135deg,#00d4ff 0%,#0099cc 100%)"
_btn_c   = "#ffffff"  if _is_biz else "#0a0e1a"
_shadow  = "rgba(0,102,179,0.25)" if _is_biz else "rgba(0,212,255,0.25)"
_shadow_h= "rgba(0,102,179,0.5)"  if _is_biz else "rgba(0,212,255,0.55)"
_top     = f"linear-gradient(90deg,transparent,{_accent},transparent)"
_empty_bg     = "#f8fafc"            if _is_biz else "#0d1526"
_empty_border = "1px dashed #c0d0e0" if _is_biz else "1px dashed #1e3a5f"
_vin_color    = "#7a9abc"            if _is_biz else "#3a5a7a"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {_bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.page-title {{ font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: {_accent}; letter-spacing: 0.1em; text-shadow: 0 0 20px {_shadow}; margin-bottom: 0; }}
.welcome-block {{ padding: 1.5rem 0 2rem; }}
.welcome-text {{ font-family: 'Share Tech Mono', monospace; font-size: 1rem; color: {_fg2}; letter-spacing: 0.15em; }}
.welcome-name {{ color: {_accent}; }}
.divider {{ height: 1px; background: linear-gradient(90deg,{_accent} 0%,transparent 60%); margin: 0.5rem 0 1.5rem; opacity: 0.3; }}
.v-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.2rem 1.4rem 0.8rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }}
.v-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.v-year {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.2rem; }}
.v-name {{ font-size: 1.25rem; font-weight: 700; color: {_fg}; letter-spacing: 0.03em; margin-bottom: 0.2rem; }}
.v-mileage {{ font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: {_accent}; margin-bottom: 0.3rem; }}
.v-customer {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.08em; margin-bottom: 0.3rem; }}
.v-vin {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_vin_color}; letter-spacing: 0.1em; }}
.empty-state {{ background: {_empty_bg}; border: {_empty_border}; border-radius: 10px; padding: 2rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; margin: 1rem 0; }}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 28px {_shadow_h} !important; }}
</style>
""", unsafe_allow_html=True)


def fetch_vehicles():
    try:
        r = requests.get(
            f"{API_BASE}/vehicles",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=API_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ── Top bar ───────────────────────────────────────────────────────────────────
_tl, _tr = st.columns([4, 2])
with _tl:
    _title = "// FLEET DASHBOARD" if _is_biz else "// DASHBOARD"
    st.markdown(f'<div class="page-title">{_title}</div>', unsafe_allow_html=True)
with _tr:
    _email = _user.get("email", "") if isinstance(_user, dict) else ""
    st.markdown(
        f'<p style="text-align:right;font-family:\'Share Tech Mono\',monospace;'
        f'font-size:0.7rem;color:{_fg2};margin:0;padding-top:0.35rem">{_email}</p>',
        unsafe_allow_html=True,
    )
    if st.button("LOGOUT", key="logout"):
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        st.session_state.pop("selected_vehicle", None)
        st.switch_page("pages/Login.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────────────────────────
_name  = (_user.get("business_name") or _user.get("full_name") or _user.get("email", "")) if isinstance(_user, dict) else ""
_greet = "FLEET MANAGER" if _is_biz else "WELCOME BACK"
st.markdown(
    f'<div class="welcome-block"><div class="welcome-text">{_greet}, '
    f'<span class="welcome-name">{_name.upper()}</span></div></div>',
    unsafe_allow_html=True,
)

# ── Vehicles section ──────────────────────────────────────────────────────────
_vh, _vadd = st.columns([3, 1])
with _vh:
    _sec = "// FLEET VEHICLES" if _is_biz else "// YOUR VEHICLES"
    st.markdown(f'<div class="section-label">{_sec}</div>', unsafe_allow_html=True)
with _vadd:
    if st.button("+ ADD VEHICLE", key="add_vehicle"):
        st.switch_page("pages/AddVehicle.py")

vehicles = fetch_vehicles()

if vehicles is None:
    st.error("Could not load vehicles — check API connection.")
elif len(vehicles) == 0:
    st.markdown(
        '<div class="empty-state">NO VEHICLES ADDED YET<br>'
        '<span style="font-size:0.7rem;opacity:0.6">Use the ADD VEHICLE button above to register your first vehicle.</span></div>',
        unsafe_allow_html=True,
    )
else:
    cols = st.columns(3, gap="medium")
    for i, v in enumerate(vehicles):
        with cols[i % 3]:
            vin_line      = f'<div class="v-vin">VIN: {v["vin"]}</div>' if v.get("vin") else ""
            customer_line = f'<div class="v-customer">CUSTOMER: {v["customer_name"]}</div>' if (_is_biz and v.get("customer_name")) else ""
            st.markdown(f"""
            <div class="v-card">
                <div class="v-year">// {v['year']}</div>
                <div class="v-name">{v['brand']} {v['model']}</div>
                {customer_line}
                <div class="v-mileage">{v['current_mileage']:,} miles</div>
                {vin_line}
            </div>
            """, unsafe_allow_html=True)
            _ba, _bd = st.columns(2)
            with _ba:
                if st.button("⚡ ANALYZE", key=f"analyze_{v['vehicle_id']}"):
                    st.session_state["selected_vehicle"] = v
                    st.switch_page("Vehicle_Input.py")
            with _bd:
                if st.button("DETAILS", key=f"detail_{v['vehicle_id']}"):
                    st.session_state["selected_vehicle"] = v
                    st.switch_page("pages/VehicleDetail.py")
