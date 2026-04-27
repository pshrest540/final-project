import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Vehicle Detail — MIA",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "120"))

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

sv = st.session_state.get("selected_vehicle")
if not sv:
    st.switch_page("pages/Home.py")

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
_row_bg       = "#f8fafc"            if _is_biz else "#0d1526"
_vin_c        = "#7a9abc"            if _is_biz else "#3a5a7a"
_sub_score_c  = "#4a6a8a"            if _is_biz else "#8aabcc"
_empty_bg     = "#f8fafc"            if _is_biz else "#0d1526"
_empty_border = "1px dashed #c0d0e0" if _is_biz else "1px dashed #1e3a5f"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {_bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.vh-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 14px; padding: 1.8rem 2rem; margin: 1rem 0 1.5rem; position: relative; overflow: hidden; }}
.vh-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {_top}; }}
.vh-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.3rem; }}
.vh-title {{ font-size: 2rem; font-weight: 700; color: {_fg}; letter-spacing: 0.04em; margin-bottom: 0.3rem; }}
.vh-mileage {{ font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: {_accent}; }}
.vh-customer {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; margin-top: 0.35rem; letter-spacing: 0.08em; }}
.vh-vin {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_vin_c}; margin-top: 0.4rem; }}
.pred-row {{ background: {_row_bg}; border: 1px solid {_border}; border-radius: 10px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }}
.pred-date {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; min-width: 90px; }}
.pred-overall {{ font-family: 'Share Tech Mono', monospace; font-size: 1.4rem; font-weight: 700; min-width: 70px; }}
.pred-sys {{ font-size: 0.82rem; color: {_sub_score_c}; }}
.pred-sys span {{ font-family: 'Share Tech Mono', monospace; }}
.empty-state {{ background: {_empty_bg}; border: {_empty_border}; border-radius: 10px; padding: 2rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 28px {_shadow_h} !important; }}
</style>
""", unsafe_allow_html=True)


def fetch_predictions():
    try:
        r = requests.get(
            f"{API_BASE}/vehicles/{sv['vehicle_id']}/predictions",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=API_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def score_color(s):
    if s >= 65:
        return "#00c864"
    elif s >= 40:
        return "#f59e0b"
    return "#ef4444"


# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _, _col_analyze = st.columns([1, 4, 1])
with _col_back:
    if st.button("← BACK", key="back"):
        st.switch_page("pages/Home.py")
with _col_analyze:
    if st.button("⚡ ANALYZE", key="analyze"):
        st.switch_page("Vehicle_Input.py")

# ── Vehicle header card ───────────────────────────────────────────────────────
vin_line      = f'<div class="vh-vin">VIN: {sv["vin"]}</div>' if sv.get("vin") else ""
customer_line = f'<div class="vh-customer">CUSTOMER: {sv["customer_name"]}</div>' if (_is_biz and sv.get("customer_name")) else ""
st.markdown(f"""
<div class="vh-card">
    <div class="vh-label">// VEHICLE PROFILE</div>
    <div class="vh-title">{sv['year']} {sv['brand']} {sv['model']}</div>
    <div class="vh-mileage">{sv['current_mileage']:,} miles</div>
    {customer_line}
    {vin_line}
</div>
""", unsafe_allow_html=True)

# ── Prediction history ────────────────────────────────────────────────────────
st.markdown('<div class="section-label">// PREDICTION HISTORY</div>', unsafe_allow_html=True)

predictions = fetch_predictions()

if predictions is None:
    st.error("Could not load predictions — check API connection.")
elif len(predictions) == 0:
    st.markdown(
        '<div class="empty-state">NO ANALYSES RUN YET<br>'
        '<span style="font-size:0.7rem;opacity:0.6">Use the ANALYZE button above to run your first diagnostic.</span></div>',
        unsafe_allow_html=True,
    )
else:
    for p in predictions:
        date_str = p["calculated_at"][:10] if p.get("calculated_at") else "—"
        ov_color = score_color(p["overall_score"])
        en_color = score_color(p["engine_score"])
        dt_color = score_color(p["drivetrain_score"])
        el_color = score_color(p["electrical_score"])
        st.markdown(f"""
        <div class="pred-row">
            <span class="pred-date">{date_str}</span>
            <span class="pred-overall" style="color:{ov_color}">{p['overall_score']:.0f}<span style="font-size:0.65rem;color:{_fg2}">/100</span></span>
            <span class="pred-sys">Engine <span style="color:{en_color}">{p['engine_score']:.0f}</span></span>
            <span class="pred-sys">Drivetrain <span style="color:{dt_color}">{p['drivetrain_score']:.0f}</span></span>
            <span class="pred-sys">Electrical <span style="color:{el_color}">{p['electrical_score']:.0f}</span></span>
        </div>
        """, unsafe_allow_html=True)
