
#Run with: streamlit run app/Vehicle_Input.py

import os
import streamlit as st
import requests

st.set_page_config(
    page_title="Vehicle Health Predictor",
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
_inp_bg  = "#f8fafc"  if _is_biz else "#0d1526"
_card_g  = "#ffffff"  if _is_biz else "linear-gradient(135deg,#0f1628 0%,#111827 100%)"
_btn_g   = "linear-gradient(135deg,#0066b3 0%,#004d8c 100%)" if _is_biz else "linear-gradient(135deg,#00d4ff 0%,#0099cc 100%)"
_btn_c   = "#ffffff"  if _is_biz else "#0a0e1a"
_shadow  = "rgba(0,102,179,0.3)"  if _is_biz else "rgba(0,212,255,0.3)"
_shadow_h= "rgba(0,102,179,0.55)" if _is_biz else "rgba(0,212,255,0.6)"
_top     = f"linear-gradient(90deg,transparent,{_accent},transparent)"
_hero_glow   = "rgba(0,102,179,0.35)" if _is_biz else "rgba(0,212,255,0.4)"
_status_dot  = "#0066b3" if _is_biz else "#00ff88"
_status_c    = "#2a4a6a" if _is_biz else "#3a6a4a"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {_bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
.hero {{ text-align: center; padding: 3rem 0 2rem 0; }}
.hero-title {{ font-family: 'Share Tech Mono', monospace; font-size: 3.2rem; color: {_accent}; letter-spacing: 0.08em; text-shadow: 0 0 30px {_hero_glow}; margin-bottom: 0.3rem; }}
.hero-sub {{ font-size: 1.1rem; color: {_fg2}; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 500; }}
.hero-line {{ width: 120px; height: 2px; background: {_top}; margin: 1.2rem auto; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; padding-left: 2px; }}
.input-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.8rem; margin-bottom: 1.2rem; position: relative; overflow: hidden; }}
.input-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.stSelectbox > div > div {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
.stNumberInput > div > div > input {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
.stSlider > div > div > div > div {{ background: {_accent} !important; }}
[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
[data-testid="stFormSubmitButton"] > button {{ width: 100%; background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 1rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.8rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 0 20px {_shadow} !important; }}
[data-testid="stFormSubmitButton"] > button:hover {{ box-shadow: 0 0 35px {_shadow_h} !important; }}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.1em !important; border: none !important; border-radius: 8px !important; padding: 0.5rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 12px {_shadow} !important; }}
.scale-row {{ display: flex; justify-content: space-between; font-size: 0.7rem; color: {_fg2}; margin-top: -0.6rem; margin-bottom: 0.4rem; padding: 0 2px; }}
.status-bar {{ display: flex; align-items: center; gap: 0.5rem; font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: {_status_c}; margin-bottom: 1rem; }}
.status-dot {{ width: 6px; height: 6px; border-radius: 50%; background: {_status_dot}; box-shadow: 0 0 6px {_status_dot}; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300,show_spinner=False)
def fetch_brands():
    try:
        r = requests.get(f"{API_BASE}/brands", timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json()["brands"]
    except Exception:
        return None

_, _hdr_r = st.columns([3, 3])
with _hdr_r:
    _email = _user.get("email", "") if isinstance(_user, dict) else ""
    st.markdown(
        f'<p style="text-align:right;font-family:\'Share Tech Mono\',monospace;'
        f'font-size:0.7rem;color:{_fg2};margin:0">{_email}</p>',
        unsafe_allow_html=True,
    )
    _btn_h, _btn_lo = st.columns(2)
    with _btn_h:
        if st.button("← HOME", key="back_home"):
            st.switch_page("pages/Home.py")
    with _btn_lo:
        if st.button("LOGOUT", key="logout"):
            st.session_state.pop("token", None)
            st.session_state.pop("user", None)
            st.switch_page("pages/Login.py")

st.markdown("""
<div class="hero">
    <div class="hero-title">name=MIA</div>
    <div class="hero-line"></div>
    <div class="hero-sub">Predictive Maintenance </div>
</div>
""", unsafe_allow_html=True)

try:
    health = requests.get(f"{API_BASE}/health", timeout=API_TIMEOUT)
    api_ok = health.status_code == 200
except Exception:
    api_ok = False

if api_ok:
    st.markdown('<div class="status-bar"><div class="status-dot"></div>SYSTEM ONLINE — API CONNECTED</div>', unsafe_allow_html=True)
else:
    st.error(f"Cannot reach API at {API_BASE}. The Render API may still be waking up; try again in about a minute.")
    st.stop()

brands_data = fetch_brands()
if not brands_data:
    st.error("Failed to load brand data from API.")
    st.stop()

brand_map  = {b["brand"]: {m["model"]: m for m in b["models"]} for b in brands_data}
brand_list = sorted(brand_map.keys())

# Pre-fill from selected_vehicle if one was chosen on the dashboard
sv = st.session_state.get("selected_vehicle")
if sv:
    _sv_brand = sv.get("brand")
    if _sv_brand in brand_list and st.session_state.get("brand") not in brand_list:
        st.session_state["brand"] = _sv_brand
sv_year    = int(sv.get("year",            2015))  if sv else 2015
sv_mileage = int(sv.get("current_mileage", 85000)) if sv else 85000

left, right = st.columns([1, 1], gap="large")

# ── LEFT col ──────────────────────────────────────────────────────────────────
with left:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">// Vehicle Identity</div>', unsafe_allow_html=True)

    brand      = st.selectbox("Brand", brand_list, key="brand")
    model_list = sorted(brand_map[brand].keys())
    _sv_model  = sv.get("model") if sv else None
    _model_idx = model_list.index(_sv_model) if _sv_model and _sv_model in model_list else 0

    with st.form("vehicle_form"):
        model   = st.selectbox("Model", model_list, index=_model_idx)
        col_y, col_m = st.columns(2)
        with col_y:
            year    = st.number_input("Year",    min_value=2000, max_value=2025, value=sv_year,    step=1)
        with col_m:
            mileage = st.number_input("Mileage", min_value=0, max_value=400000, value=sv_mileage, step=1000)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">// Driving Conditions</div>', unsafe_allow_html=True)

        rough_scale  = st.slider("Road Roughness",         0.0, 1.0, 0.4, 0.05)
        st.markdown('<div class="scale-row"><span>Smooth</span><span>Rough</span></div>', unsafe_allow_html=True)
        torque_scale = st.slider("Towing / Heavy Load",    0.0, 1.0, 0.3, 0.05)
        st.markdown('<div class="scale-row"><span>None</span><span>Heavy</span></div>', unsafe_allow_html=True)
        stop_scale   = st.slider("Stop-and-Go Traffic",    0.0, 1.0, 0.4, 0.05)
        st.markdown('<div class="scale-row"><span>Highway</span><span>City</span></div>', unsafe_allow_html=True)
        temp_scale   = st.slider("Extreme Temperatures",   0.0, 1.0, 0.4, 0.05)
        st.markdown('<div class="scale-row"><span>Mild</span><span>Extreme</span></div>', unsafe_allow_html=True)
        habit_scale  = st.slider("Driving Aggressiveness", 0.0, 1.0, 0.3, 0.05)
        st.markdown('<div class="scale-row"><span>Gentle</span><span>Aggressive</span></div>', unsafe_allow_html=True)
        idle_scale   = st.slider("Extended Idling",        0.0, 1.0, 0.3, 0.05)
        st.markdown('<div class="scale-row"><span>Rarely</span><span>Frequent</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            submitted = st.form_submit_button("⚡  ANALYZE VEHICLE HEALTH")

# ── Handle submission ─────────────────────────────────────────────────────────
if submitted:
    payload = {
        "brand": brand, "model": model,
        "year": int(year), "mileage": int(mileage),
        "rough_scale": rough_scale, "torque_scale": torque_scale,
        "stop_scale": stop_scale,   "temp_scale": temp_scale,
        "habit_scale": habit_scale, "idle_scale": idle_scale,
    }
    if sv and "vehicle_id" in sv:
        payload["vehicle_id"] = sv["vehicle_id"]
    with st.spinner("Running diagnostics..."):
        try:
            r = requests.post(f"{API_BASE}/predict", json=payload, timeout=API_TIMEOUT)
            r.raise_for_status()
            st.session_state["results"]       = r.json()
            st.session_state["vehicle_label"] = f"{year} {brand} {model}"
            st.switch_page("pages/Results.py")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
