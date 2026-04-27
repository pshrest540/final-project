import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Vehicle Detail — MIA",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

sv = st.session_state.get("selected_vehicle")
if not sv:
    st.switch_page("pages/Home.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0a0e1a; color: #c8d8e8; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #00d4ff; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }
.vh-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 14px; padding: 1.8rem 2rem; margin: 1rem 0 1.5rem; position: relative; overflow: hidden; }
.vh-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.vh-label { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: #5a7a9a; letter-spacing: 0.2em; margin-bottom: 0.3rem; }
.vh-title { font-size: 2rem; font-weight: 700; color: #c8d8e8; letter-spacing: 0.04em; margin-bottom: 0.3rem; }
.vh-mileage { font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: #00d4ff; }
.vh-vin { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: #3a5a7a; margin-top: 0.4rem; }
.pred-row { background: #0d1526; border: 1px solid #1e3a5f; border-radius: 10px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }
.pred-date { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #5a7a9a; min-width: 90px; }
.pred-overall { font-family: 'Share Tech Mono', monospace; font-size: 1.4rem; font-weight: 700; min-width: 70px; }
.pred-sys { font-size: 0.82rem; color: #8aabcc; }
.pred-sys span { font-family: 'Share Tech Mono', monospace; }
.empty-state { background: #0d1526; border: 1px dashed #1e3a5f; border-radius: 10px; padding: 2rem; text-align: center; color: #5a7a9a; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }
.stButton > button { background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important; color: #0a0e1a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px rgba(0,212,255,0.25) !important; }
.stButton > button:hover { box-shadow: 0 0 28px rgba(0,212,255,0.55) !important; }
</style>
""", unsafe_allow_html=True)


def fetch_predictions():
    try:
        r = requests.get(
            f"{API_BASE}/vehicles/{sv['vehicle_id']}/predictions",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def score_color(s):
    if s >= 65:
        return "#00ff88"
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
vin_line = f'<div class="vh-vin">VIN: {sv["vin"]}</div>' if sv.get("vin") else ""
st.markdown(f"""
<div class="vh-card">
    <div class="vh-label">// VEHICLE PROFILE</div>
    <div class="vh-title">{sv['year']} {sv['brand']} {sv['model']}</div>
    <div class="vh-mileage">{sv['current_mileage']:,} miles</div>
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
            <span class="pred-overall" style="color:{ov_color}">{p['overall_score']:.0f}<span style="font-size:0.65rem;color:#3a5a7a">/100</span></span>
            <span class="pred-sys">Engine <span style="color:{en_color}">{p['engine_score']:.0f}</span></span>
            <span class="pred-sys">Drivetrain <span style="color:{dt_color}">{p['drivetrain_score']:.0f}</span></span>
            <span class="pred-sys">Electrical <span style="color:{el_color}">{p['electrical_score']:.0f}</span></span>
        </div>
        """, unsafe_allow_html=True)
