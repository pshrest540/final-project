import streamlit as st
import session

st.set_page_config(
    page_title="Add Vehicle — VEHIDOC",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_user    = st.session_state.get("user", {})
_is_biz  = isinstance(_user, dict) and _user.get("account_type") == "business"

if _is_biz:
    st.switch_page("pages/Home.py")


def _request_vehicle_save():
    st.session_state["add_vehicle_save_requested_v2"] = True

# ── Theme tokens ──────────────────────────────────────────────────────────────
_bg      = "#f0f4f8"  if _is_biz else "#070707"
_accent  = "#0066b3"  if _is_biz else "#ffffff"
_fg      = "#1a2a3a"  if _is_biz else "#f0f0f0"
_fg2     = "#4a6a8a"  if _is_biz else "#888888"
_border  = "#d0dce8"  if _is_biz else "#2a2a2a"
_inp_bg  = "#f8fafc"  if _is_biz else "#111111"
_card_g  = "#ffffff"  if _is_biz else "#111111"
_btn_g   = "linear-gradient(135deg,#0066b3 0%,#004d8c 100%)" if _is_biz else "#f5f5f5"
_btn_c   = "#ffffff"  if _is_biz else "#080808"
_shadow  = "rgba(0,102,179,0.25)" if _is_biz else "rgba(255,255,255,0.07)"
_shadow_h= "rgba(0,102,179,0.5)"  if _is_biz else "rgba(255,255,255,0.14)"
_top     = f"linear-gradient(90deg,transparent,{_accent},transparent)"
_select_bg     = "#f8fafc"
_select_fg     = "#1a2a3a"
_select_muted  = "#4a5568"
_select_border = "#d0dce8"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {"radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%)" if not _is_biz else _bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2.5rem; padding-bottom: 2rem; max-width: 560px; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.form-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.8rem; margin: 1rem 0; position: relative; overflow: hidden; }}
.form-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.stSelectbox > div > div, [data-testid="stSelectbox"] > div > div {{ background: transparent !important; border: none !important; padding: 0 !important; }}
.stSelectbox label, .stNumberInput label, .stTextInput label {{ color: {_fg} !important; font-family: 'Rajdhani', sans-serif !important; font-size: 0.9rem !important; margin-bottom: 0.4rem !important; font-weight: 600 !important; }}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    background: {_select_bg} !important;
    border: 1px solid {_select_border} !important;
    border-radius: 8px !important;
    color: {_select_fg} !important;
    min-height: 50px !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] p {{
    color: {_select_fg} !important;
    -webkit-text-fill-color: {_select_fg} !important;
    opacity: 1 !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] input {{
    color: {_select_fg} !important;
    -webkit-text-fill-color: {_select_fg} !important;
    background: transparent !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] svg {{ fill: {_select_fg} !important; color: {_select_fg} !important; }}
[data-baseweb="single-value"] {{ color: {_select_fg} !important; -webkit-text-fill-color: {_select_fg} !important; opacity: 1 !important; }}
[data-baseweb="placeholder"] {{ color: {_select_muted} !important; -webkit-text-fill-color: {_select_muted} !important; }}
[data-baseweb="popover"] {{ background: {_select_bg} !important; border: 1px solid {_select_border} !important; }}
[data-baseweb="menu"] {{ background: {_select_bg} !important; }}
[role="option"] {{ background: {_select_bg} !important; color: {_select_fg} !important; -webkit-text-fill-color: {_select_fg} !important; }}
[role="option"]:hover, [aria-selected="true"] {{ background: #e8eef5 !important; color: {_select_fg} !important; -webkit-text-fill-color: {_select_fg} !important; }}
.stNumberInput > div > div > input {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; padding: 0.6rem 0.8rem !important; }}
.stNumberInput > div > div > input::placeholder {{ color: {_fg2} !important; opacity: 0.6 !important; }}
.stTextInput > div > div > input {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; padding: 0.6rem 0.8rem !important; }}
.stTextInput > div > div > input::placeholder {{ color: {_fg2} !important; opacity: 0.6 !important; }}
[data-testid="stForm"] {{ border: none !important; padding: 0 !important; background: transparent !important; }}
[data-testid="stFormSubmitButton"] > button {{ width: 100%; background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; text-transform: uppercase !important; box-shadow: 0 2px 12px {_shadow} !important; }}
[data-testid="stFormSubmitButton"] > button:hover {{ box-shadow: 0 4px 20px {_shadow_h} !important; transform: translateY(-1px); }}
.stButton > button {{ background: transparent !important; border: 1px solid {_border} !important; color: {_fg2} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.1em !important; border-radius: 8px !important; padding: 0.4rem 1rem !important; text-transform: uppercase !important; }}
.stButton > button:hover {{ border-color: {_accent} !important; color: {_accent} !important; background: {"rgba(0,102,179,0.05)" if _is_biz else "rgba(255,255,255,0.04)"} !important; }}
[data-testid="InputInstructions"] {{ display: none !important; }}
[data-testid="stWarning"], [data-testid="stError"], [data-testid="stInfo"], [data-testid="stSuccess"] {{ border-radius: 8px !important; margin: 0.8rem 0 !important; }}
</style>
""", unsafe_allow_html=True)


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

brands_data = session.fetch_brands()
if not brands_data:
    st.error("Could not load brand data from API.")
    st.stop()

brand_map  = {b["brand"]: {m["model"]: m for m in b["models"]} for b in brands_data}
brand_list = sorted(brand_map.keys())

brand      = st.selectbox("Brand", brand_list, key="add_brand")
model_list = sorted(brand_map[brand].keys())

with st.form("add_vehicle_form"):
    model = st.selectbox("Model", model_list, key="add_model")
    col_y, col_m = st.columns(2)
    with col_y:
        year = st.number_input("Year", min_value=2000, max_value=2025, value=2020, step=1, key="add_year")
    with col_m:
        mileage = st.number_input(
            "Current Mileage",
            min_value=0,
            value=0,
            step=1000,
            key="add_mileage",
        )
    vin = st.text_input("VIN (optional)", placeholder="17-character identifier", max_chars=17, key="add_vin")

    customer_name = ""
    if _is_biz:
        customer_name = st.text_input(
            "Customer Name",
            placeholder="Customer or fleet asset name",
            help="Associate this vehicle with a specific customer.",
            key="add_customer_name",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.form_submit_button("SAVE VEHICLE", on_click=_request_vehicle_save)

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.pop("add_vehicle_save_requested_v2", False):
    # Validate inputs
    errors = []
    if year < 2000 or year > 2025:
        errors.append("Year must be between 2000 and 2025")
    if mileage < 0 or mileage > 400000:
        errors.append("Mileage must be between 0 and 400,000 miles")
    if vin.strip() and len(vin.strip()) > 17:
        errors.append("VIN must be 17 characters or less")

    if errors:
        for error in errors:
            st.error(error)
    else:
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
            r = session.post("/vehicles", json=payload, token=st.session_state["token"])
            if r.status_code == 201:
                session.fetch_vehicles.clear()
                st.success("Vehicle added!")
                st.switch_page("pages/Home.py")
            else:
                st.error(r.json().get("detail", "Failed to add vehicle."))
        except Exception as e:
            st.error(f"Could not reach API: {e}")
