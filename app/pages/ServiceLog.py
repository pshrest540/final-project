import html as _html
import streamlit as st
import session

st.set_page_config(
    page_title="Log Service — VEHIDOC",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

lt = st.session_state.get("log_target")
if not lt:
    st.switch_page("pages/Home.py")

_token   = st.session_state["token"]
_user    = st.session_state.get("user", {})
_is_biz  = isinstance(_user, dict) and _user.get("account_type") == "business"
_biz_name = _user.get("business_name", "") if _is_biz else ""

vehicle_id      = lt["vehicle_id"]
vehicle_label   = _html.escape(lt["vehicle_label"])
current_mileage = lt["current_mileage"]
entry_type      = lt["entry_type"]
task_key        = lt["task_key"]
task_name       = _html.escape(lt["task_name"])

# ── Theme tokens ──────────────────────────────────────────────────────────────
_bg     = "#f0f4f8"  if _is_biz else "#070707"
_accent = "#0066b3"  if _is_biz else "#ffffff"
_fg     = "#1a2a3a"  if _is_biz else "#f0f0f0"
_fg2    = "#4a6a8a"  if _is_biz else "#555555"
_border = "#d0dce8"  if _is_biz else "#1e1e1e"
_card_g = "#ffffff"  if _is_biz else "#0c0c0c"
_inp_bg = "#f8fafc"  if _is_biz else "#111111"
_top    = f"linear-gradient(90deg,transparent,{_accent},transparent)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {"radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%)" if not _is_biz else _bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 640px; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.5rem; }}
.log-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 14px; padding: 2rem 2.2rem 2rem; margin: 0.5rem 0 1.5rem; position: relative; overflow: hidden; }}
.log-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {_top}; }}
.log-vehicle {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.3rem; }}
.log-title {{ font-size: 1.5rem; font-weight: 700; color: {_fg}; margin-bottom: 0.1rem; }}
.log-type {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_accent}; letter-spacing: 0.18em; }}
.readonly-field {{ background: {"#eaf0f7" if _is_biz else "#0e0e0e"}; border: 1px solid {_border}; border-radius: 8px; padding: 0.5rem 0.8rem; font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: {_fg2}; margin-bottom: 0.5rem; }}
stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea {{
    background: {_inp_bg} !important; color: {_fg} !important; border-color: {_border} !important;
}}
[data-testid="InputInstructions"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _col_title = st.columns([1, 5])
with _col_back:
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/VehicleDetail.py")
with _col_title:
    st.markdown(
        f'<div class="section-label" style="margin-top:0.5rem">LOG SERVICE EVENT</div>',
        unsafe_allow_html=True,
    )

# ── Header card ───────────────────────────────────────────────────────────────
_type_label = "SCHEDULED MAINTENANCE" if entry_type == "maintenance" else "COMPONENT REPLACEMENT"
st.markdown(f"""
<div class="log-card">
  <div class="log-vehicle">{vehicle_label}</div>
  <div class="log-title">{task_name}</div>
  <div class="log-type">{_type_label}</div>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("service_log_form", clear_on_submit=False):
    st.markdown(f'<div class="section-label">SERVICE DETAILS</div>', unsafe_allow_html=True)

    service_mileage = st.number_input(
        "Mileage at service *",
        min_value=0,
        max_value=2_000_000,
        value=current_mileage,
        step=100,
        help="Odometer reading when service was performed",
    )

    replacement_info = st.text_input(
        "Replacement info",
        placeholder='e.g. "Fully synthetic 5W-30", "OEM brake pads", "Duralast battery"',
        max_chars=500,
        help="Product, spec, or part number used (optional)",
    )

    st.markdown(f'<div class="section-label" style="margin-top:1rem">WHO DID IT</div>', unsafe_allow_html=True)

    if _is_biz and _biz_name:
        st.markdown(
            f'<div class="readonly-field">SHOP &nbsp;·&nbsp; {_biz_name}</div>',
            unsafe_allow_html=True,
        )

    technician_name = st.text_input(
        "Technician name",
        placeholder="Name of the person who performed the service",
        max_chars=100,
    )

    st.markdown(f'<div class="section-label" style="margin-top:1rem">ADDITIONAL INFO</div>', unsafe_allow_html=True)

    cost = st.number_input(
        "Cost ($)",
        min_value=0.0,
        max_value=999_999.0,
        value=None,
        step=1.0,
        format="%.2f",
        help="Total cost for this service (optional)",
    )

    notes = st.text_area(
        "Notes",
        placeholder="Any additional notes about this service event",
        max_chars=500,
        height=100,
    )

    submitted = st.form_submit_button("SAVE SERVICE LOG", use_container_width=True, type="primary")

if submitted:
    payload = {
        "entry_type":       entry_type,
        "task_key":         task_key,
        "service_mileage":  int(service_mileage),
        "replacement_info": replacement_info.strip() or None,
        "technician_name":  technician_name.strip() or None,
        "cost":             float(cost) if cost is not None else None,
        "notes":            notes.strip() or None,
    }
    try:
        r = session.post(f"/vehicles/{vehicle_id}/service-log", token=_token, json=payload)
        if r.status_code == 201:
            session.fetch_vehicle_service_log.clear()
            session.fetch_maintenance.clear()
            session.fetch_replacements.clear()
            del st.session_state["log_target"]
            st.switch_page("pages/VehicleDetail.py")
        else:
            detail = r.json().get("detail", r.text)
            st.error(f"Failed to save: {detail}")
    except Exception as exc:
        st.error(f"Connection error: {exc}")
