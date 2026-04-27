import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Dashboard — MIA",
    page_icon="🔧",
    layout="wide",
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
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #00d4ff; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }
.page-title { font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: #00d4ff; letter-spacing: 0.1em; text-shadow: 0 0 20px rgba(0,212,255,0.3); margin-bottom: 0; }
.welcome-block { padding: 1.5rem 0 2rem; }
.welcome-text { font-family: 'Share Tech Mono', monospace; font-size: 1rem; color: #5a7a9a; letter-spacing: 0.15em; }
.welcome-name { color: #00d4ff; }
.divider { height: 1px; background: linear-gradient(90deg, #00d4ff 0%, transparent 60%); margin: 0.5rem 0 1.5rem; opacity: 0.3; }
.v-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 1.2rem 1.4rem 0.8rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }
.v-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.v-year { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: #5a7a9a; letter-spacing: 0.2em; margin-bottom: 0.2rem; }
.v-name { font-size: 1.25rem; font-weight: 700; color: #c8d8e8; letter-spacing: 0.03em; margin-bottom: 0.2rem; }
.v-mileage { font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: #00d4ff; margin-bottom: 0.4rem; }
.v-vin { font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: #3a5a7a; letter-spacing: 0.1em; }
.empty-state { background: #0d1526; border: 1px dashed #1e3a5f; border-radius: 10px; padding: 2rem; text-align: center; color: #5a7a9a; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; margin: 1rem 0; }
.stButton > button { background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important; color: #0a0e1a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px rgba(0,212,255,0.25) !important; }
.stButton > button:hover { box-shadow: 0 0 28px rgba(0,212,255,0.55) !important; }
</style>
""", unsafe_allow_html=True)


def fetch_vehicles():
    try:
        r = requests.get(
            f"{API_BASE}/vehicles",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ── Top bar ───────────────────────────────────────────────────────────────────
_tl, _tr = st.columns([4, 2])
with _tl:
    st.markdown('<div class="page-title">// DASHBOARD</div>', unsafe_allow_html=True)
with _tr:
    _user = st.session_state.get("user", {})
    _email = _user.get("email", "") if isinstance(_user, dict) else ""
    st.markdown(
        f'<p style="text-align:right;font-family:\'Share Tech Mono\',monospace;'
        f'font-size:0.7rem;color:#5a7a9a;margin:0;padding-top:0.35rem">{_email}</p>',
        unsafe_allow_html=True,
    )
    if st.button("LOGOUT", key="logout"):
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        st.session_state.pop("selected_vehicle", None)
        st.switch_page("pages/Login.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────────────────────────
_user = st.session_state.get("user", {})
_name = (_user.get("full_name") or _user.get("email", "")) if isinstance(_user, dict) else ""
st.markdown(
    f'<div class="welcome-block"><div class="welcome-text">WELCOME BACK, '
    f'<span class="welcome-name">{_name.upper()}</span></div></div>',
    unsafe_allow_html=True,
)

# ── Vehicles section ──────────────────────────────────────────────────────────
_vh, _vadd = st.columns([3, 1])
with _vh:
    st.markdown('<div class="section-label">// YOUR VEHICLES</div>', unsafe_allow_html=True)
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
            vin_line = f'<div class="v-vin">VIN: {v["vin"]}</div>' if v.get("vin") else ""
            st.markdown(f"""
            <div class="v-card">
                <div class="v-year">// {v['year']}</div>
                <div class="v-name">{v['brand']} {v['model']}</div>
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
