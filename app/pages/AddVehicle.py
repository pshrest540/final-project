import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Add Vehicle — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0a0e1a; color: #c8d8e8; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.5rem; padding-bottom: 2rem; max-width: 560px; }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #00d4ff; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }
.form-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 1.8rem; margin: 1rem 0; position: relative; overflow: hidden; }
.form-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.stSelectbox > div > div { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stNumberInput > div > div > input { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stTextInput > div > div > input { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
[data-testid="stForm"] { border: none !important; padding: 0 !important; }
[data-testid="stFormSubmitButton"] > button { width: 100%; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important; color: #0a0e1a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 0 20px rgba(0,212,255,0.3) !important; }
.stButton > button { background: transparent !important; border: 1px solid #1e3a5f !important; color: #5a7a9a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.1em !important; border-radius: 8px !important; padding: 0.4rem 1rem !important; text-transform: uppercase !important; }
.stButton > button:hover { border-color: #00d4ff !important; color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_brands():
    try:
        r = requests.get(f"{API_BASE}/brands", timeout=5)
        r.raise_for_status()
        return r.json()["brands"]
    except Exception:
        return []


# ── Header ────────────────────────────────────────────────────────────────────
_hl, _hr = st.columns([3, 1])
with _hl:
    st.markdown('<div class="section-label">// ADD VEHICLE</div>', unsafe_allow_html=True)
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

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("SAVE VEHICLE")

st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    payload = {
        "brand": brand,
        "model": model,
        "year": int(year),
        "current_mileage": int(mileage),
    }
    if vin.strip():
        payload["vin"] = vin.strip()

    try:
        r = requests.post(
            f"{API_BASE}/vehicles",
            json=payload,
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10,
        )
        if r.status_code == 201:
            st.success("Vehicle added!")
            st.switch_page("pages/Home.py")
        else:
            st.error(r.json().get("detail", "Failed to add vehicle."))
    except Exception as e:
        st.error(f"Could not reach API: {e}")
