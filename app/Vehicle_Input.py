
#Run with: streamlit run app/Vehicle_Input.py

import streamlit as st
import requests

st.set_page_config(
    page_title="Vehicle Health Predictor",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "http://localhost:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0a0e1a; color: #c8d8e8; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.hero { text-align: center; padding: 3rem 0 2rem 0; }
.hero-title { font-family: 'Share Tech Mono', monospace; font-size: 3.2rem; color: #00d4ff; letter-spacing: 0.08em; text-shadow: 0 0 30px rgba(0,212,255,0.4); margin-bottom: 0.3rem; }
.hero-sub { font-size: 1.1rem; color: #5a7a9a; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 500; }
.hero-line { width: 120px; height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1.2rem auto; }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #00d4ff; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; padding-left: 2px; }
.input-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 1.8rem; margin-bottom: 1.2rem; position: relative; overflow: hidden; }
.input-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.stSelectbox > div > div { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stNumberInput > div > div > input { background: #0d1526 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #c8d8e8 !important; }
.stSlider > div > div > div > div { background: #00d4ff !important; }
[data-testid="stForm"] { border: none !important; padding: 0 !important; }
[data-testid="stFormSubmitButton"] > button { width: 100%; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important; color: #0a0e1a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 1rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.8rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 0 20px rgba(0,212,255,0.3) !important; }
[data-testid="stFormSubmitButton"] > button:hover { box-shadow: 0 0 35px rgba(0,212,255,0.6) !important; }
.scale-row { display: flex; justify-content: space-between; font-size: 0.7rem; color: #3a5a7a; margin-top: -0.6rem; margin-bottom: 0.4rem; padding: 0 2px; }
.status-bar { display: flex; align-items: center; gap: 0.5rem; font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #3a6a4a; margin-bottom: 1rem; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #00ff88; box-shadow: 0 0 6px #00ff88; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300,show_spinner=False)
def fetch_brands():
    try:
        r = requests.get(f"{API_BASE}/brands", timeout=5)
        r.raise_for_status()
        return r.json()["brands"]
    except Exception:
        return None

st.markdown("""
<div class="hero">
    <div class="hero-title">name=MIA</div>
    <div class="hero-line"></div>
    <div class="hero-sub">Predictive Maintenance </div>
</div>
""", unsafe_allow_html=True)

try:
    health = requests.get(f"{API_BASE}/health", timeout=3)
    api_ok = health.status_code == 200
except Exception:
    api_ok = False

if api_ok:
    st.markdown('<div class="status-bar"><div class="status-dot"></div>SYSTEM ONLINE — API CONNECTED</div>', unsafe_allow_html=True)
else:
    st.error("⚠️ Cannot reach API at localhost:8000 — make sure uvicorn is running.")
    st.stop()

brands_data = fetch_brands()
if not brands_data:
    st.error("Failed to load brand data from API.")
    st.stop()

brand_map  = {b["brand"]: {m["model"]: m for m in b["models"]} for b in brands_data}
brand_list = sorted(brand_map.keys())

left, right = st.columns([1, 1], gap="large")

# ── LEFT col ──────────────────────────────────────────────────────────────────
with left:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">// Vehicle Identity</div>', unsafe_allow_html=True)

    # Brand ONLY outside form — triggers rerun to update model list
    brand      = st.selectbox("Brand", brand_list, key="brand")
    model_list = sorted(brand_map[brand].keys())

    # Everything else inside form — no dimming on change
    with st.form("vehicle_form"):
        model   = st.selectbox("Model", model_list)
        col_y, col_m = st.columns(2)
        with col_y:
            year    = st.number_input("Year",    min_value=2000, max_value=2025, value=2015, step=1)
        with col_m:
            mileage = st.number_input("Mileage", min_value=0, max_value=400000, value=85000, step=1000)

        st.markdown('</div>', unsafe_allow_html=True)  # close input-card visually

        # ── RIGHT col content — sliders inside same form ───────────────────────
        # We render the right column's content here since both cols share one form
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

# ── Handle submission ──────────────────────────────────────────────────────────
if submitted:
    payload = {
        "brand": brand, "model": model,
        "year": int(year), "mileage": int(mileage),
        "rough_scale": rough_scale, "torque_scale": torque_scale,
        "stop_scale": stop_scale,   "temp_scale": temp_scale,
        "habit_scale": habit_scale, "idle_scale": idle_scale,
    }
    with st.spinner("Running diagnostics..."):
        try:
            r = requests.post(f"{API_BASE}/predict", json=payload, timeout=10)
            r.raise_for_status()
            st.session_state["results"]       = r.json()
            st.session_state["vehicle_label"] = f"{year} {brand} {model}"
            st.switch_page("pages/Results.py")
        except Exception as e:
            st.error(f"Prediction failed: {e}")