import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Add Vehicle — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "120"))

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_user    = st.session_state.get("user", {})
_is_biz  = isinstance(_user, dict) and _user.get("account_type") == "business"

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
_shadow  = "rgba(0,102,179,0.25)" if _is_biz else "rgba(0,212,255,0.3)"
_shadow_h= "rgba(0,102,179,0.5)"  if _is_biz else "rgba(0,212,255,0.6)"
_top     = f"linear-gradient(90deg,transparent,{_accent},transparent)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {_bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2.5rem; padding-bottom: 2rem; max-width: 560px; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.form-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.8rem; margin: 1rem 0; position: relative; overflow: hidden; }}
.form-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.stSelectbox > div > div {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
.stNumberInput > div > div > input {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
.stTextInput > div > div > input {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
[data-testid="stFormSubmitButton"] > button {{ width: 100%; background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 0 20px {_shadow} !important; }}
[data-testid="stFormSubmitButton"] > button:hover {{ box-shadow: 0 0 35px {_shadow_h} !important; }}
.stButton > button {{ background: transparent !important; border: 1px solid {_border} !important; color: {_fg2} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.1em !important; border-radius: 8px !important; padding: 0.4rem 1rem !important; text-transform: uppercase !important; }}
.stButton > button:hover {{ border-color: {_accent} !important; color: {_accent} !important; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_brands():
    try:
        r = requests.get(f"{API_BASE}/brands", timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json()["brands"]
    except Exception:
        return []


# ── Header ────────────────────────────────────────────────────────────────────
_hl, _hr = st.columns([3, 1])
with _hl:
    _page_label = "// ADD FLEET VEHICLE" if _is_biz else "// ADD VEHICLE"
    st.markdown(f'<div class="section-label">{_page_label}</div>', unsafe_allow_html=True)
with _hr:
    if st.button("← BACK", key="back"):
        st.switch_page("pages/Home.py")

st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">// Vehicle Details</div>', unsafe_allow_html=True)

brands_data = fetch_brands()
if not brands_data:
    st.error("Could not load brand data from API.")
    st.stop()

brand_map  = {b["brand"]: {m["model"]: m for m in b["models"]} for b in brands_data}
brand_list = sorted(brand_map.keys())

brand      = st.selectbox("Brand", brand_list, key="add_brand")
model_list = sorted(brand_map[brand].keys())

with st.form("add_vehicle_form"):
    model = st.selectbox("Model", model_list)
    col_y, col_m = st.columns(2)
    with col_y:
        year    = st.number_input("Year",            min_value=2000, max_value=2025, value=2020, step=1)
    with col_m:
        mileage = st.number_input("Current Mileage", min_value=0, max_value=400000, value=0,    step=1000)
    vin = st.text_input("VIN (optional)", placeholder="17-character identifier", max_chars=17)

    customer_name = ""
    if _is_biz:
        customer_name = st.text_input(
            "Customer Name",
            placeholder="Customer or fleet asset name",
            help="Associate this vehicle with a specific customer.",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("SAVE VEHICLE")

st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    payload = {
        "brand":           brand,
        "model":           model,
        "year":            int(year),
        "current_mileage": int(mileage),
    }
    if vin.strip():
        payload["vin"] = vin.strip()
    if _is_biz and customer_name.strip():
        payload["customer_name"] = customer_name.strip()

    try:
        r = requests.post(
            f"{API_BASE}/vehicles",
            json=payload,
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=API_TIMEOUT,
        )
        if r.status_code == 201:
            st.success("Vehicle added!")
            st.switch_page("pages/Home.py")
        else:
            st.error(r.json().get("detail", "Failed to add vehicle."))
    except Exception as e:
        st.error(f"Could not reach API: {e}")
