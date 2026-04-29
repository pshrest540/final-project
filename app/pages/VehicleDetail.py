import html
import streamlit as st
import session

st.set_page_config(
    page_title="Vehicle Detail — MIA",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

sv = st.session_state.get("selected_vehicle")
if not sv:
    st.switch_page("pages/Home.py")

_token    = st.session_state["token"]
_user     = st.session_state.get("user", {})
_is_biz   = isinstance(_user, dict) and _user.get("account_type") == "business"
_is_shared = bool(sv.get("is_shared"))

# ── Theme tokens ──────────────────────────────────────────────────────────────
_bg      = "#f0f4f8"  if _is_biz else "#070707"
_accent  = "#0066b3"  if _is_biz else "#ffffff"
_fg      = "#1a2a3a"  if _is_biz else "#f0f0f0"
_fg2     = "#4a6a8a"  if _is_biz else "#555555"
_border  = "#d0dce8"  if _is_biz else "#1e1e1e"
_card_g  = "#ffffff"  if _is_biz else "#0c0c0c"
_btn_g   = "linear-gradient(135deg,#0066b3 0%,#004d8c 100%)" if _is_biz else "#f5f5f5"
_btn_c   = "#ffffff"  if _is_biz else "#080808"
_shadow  = "rgba(0,102,179,0.25)" if _is_biz else "rgba(255,255,255,0.07)"
_shadow_h= "rgba(0,102,179,0.5)"  if _is_biz else "rgba(255,255,255,0.14)"
_top     = f"linear-gradient(90deg,transparent,{_accent},transparent)"
_row_bg       = "#f8fafc"            if _is_biz else "#0e0e0e"
_vin_c        = "#7a9abc"            if _is_biz else "#3a3a3a"
_sub_score_c  = "#4a6a8a"            if _is_biz else "#6a6a6a"
_empty_bg     = "#f8fafc"            if _is_biz else "#0e0e0e"
_empty_border = "1px dashed #c0d0e0" if _is_biz else "1px dashed #222222"
_inp_bg       = "#f8fafc"            if _is_biz else "#111111"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {"radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%)" if not _is_biz else _bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.vh-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 14px; padding: 1.8rem 2rem; margin: 1rem 0 1rem; position: relative; overflow: hidden; }}
.vh-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {_top}; }}
.vh-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.3rem; }}
.vh-title {{ font-size: 2rem; font-weight: 700; color: {_fg}; letter-spacing: 0.04em; margin-bottom: 0.3rem; }}
.vh-mileage {{ font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: {_accent}; }}
.vh-customer {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; margin-top: 0.35rem; }}
.vh-vin {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_vin_c}; margin-top: 0.4rem; }}
.maint-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 10px; padding: 1rem 1.1rem 0.7rem; margin-bottom: 0.4rem; position: relative; overflow: hidden; }}
.maint-title {{ font-size: 0.88rem; font-weight: 700; color: {_fg}; margin-bottom: 0.15rem; }}
.maint-interval {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_fg2}; margin-bottom: 0.5rem; }}
.maint-detail {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_fg2}; margin-bottom: 0.2rem; }}
.maint-remaining {{ font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; font-weight: 700; margin-bottom: 0.15rem; }}
.maint-unknown {{ font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; color: {_fg2}; margin-bottom: 0.3rem; font-style: italic; }}
.prop-card {{ background: {"rgba(0,102,179,0.06)" if _is_biz else "rgba(255,255,255,0.04)"}; border: 1px solid {"#b3cce8" if _is_biz else "#2a2a2a"}; border-left: 3px solid {_accent}; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }}
.prop-from {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.15em; margin-bottom: 0.3rem; }}
.prop-title {{ font-size: 0.95rem; font-weight: 700; color: {_fg}; margin-bottom: 0.2rem; }}
.prop-detail {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; margin-bottom: 0.15rem; }}
.prop-meta {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_fg2}; margin-bottom: 0.1rem; }}
.prop-note {{ font-size: 0.8rem; color: {_fg2}; font-style: italic; margin-top: 0.2rem; }}
.prop-pending {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: #f59e0b; letter-spacing: 0.12em; }}
.pred-row {{ background: {_row_bg}; border: 1px solid {_border}; border-radius: 10px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }}
.pred-date {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; min-width: 90px; }}
.pred-overall {{ font-family: 'Share Tech Mono', monospace; font-size: 1.4rem; font-weight: 700; min-width: 70px; }}
.pred-sys {{ font-size: 0.82rem; color: {_sub_score_c}; }}
.pred-sys span {{ font-family: 'Share Tech Mono', monospace; }}
.empty-state {{ background: {_empty_bg}; border: {_empty_border}; border-radius: 10px; padding: 2rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }}
.rec-card {{ background: {_empty_bg}; border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; border-left: 3px solid; display: flex; align-items: flex-start; gap: 0.7rem; }}
.rec-icon {{ font-size: 1rem; margin-top: 0.1rem; flex-shrink: 0; }}
.rec-system {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.15rem; }}
.rec-text {{ font-size: 0.88rem; color: {_fg}; line-height: 1.4; }}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.45rem 0.8rem !important; text-transform: uppercase !important; box-shadow: 0 0 12px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 22px {_shadow_h} !important; }}
.stButton > button:disabled {{ opacity: 0.35 !important; box-shadow: none !important; cursor: not-allowed !important; }}
.stNumberInput > div > div > input, .stTextInput > div > div > input, .stTextArea textarea {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
</style>
""", unsafe_allow_html=True)


def score_color(s):
    if s >= 65:   return "#00c864"
    elif s >= 40: return "#f59e0b"
    return "#ef4444"


def _get_recommendations(dt, el, en):
    recs = []
    checks = [
        (dt["cv_wellness"],       "DRIVETRAIN", "CV Joints",      "CV joints are worn. Inspect for clicking sounds during turns.",   "#00d4ff"),
        (dt["wb_wellness"],       "DRIVETRAIN", "Wheel Bearings", "Wheel bearings degraded. Listen for humming at highway speed.",   "#00d4ff"),
        (dt["brk_wellness"],      "DRIVETRAIN", "Brakes",         "Brake system needs attention. Schedule inspection immediately.",  "#00d4ff"),
        (el["bat_wellness"],      "ELECTRICAL", "Battery",        "Battery health low. Consider replacement before cold season.",    "#a78bfa"),
        (el["alt_wellness"],      "ELECTRICAL", "Alternator",     "Alternator output low. Monitor charging voltage.",                "#a78bfa"),
        (el["sta_wellness"],      "ELECTRICAL", "Starter",        "Starter motor worn. Watch for slow cranking on startup.",         "#a78bfa"),
        (en["coolant_wellness"],  "ENGINE",     "Coolant System", "Coolant system degraded. Schedule a flush and inspection.",       "#f59e0b"),
        (en["ignition_wellness"], "ENGINE",     "Ignition",       "Ignition system worn. Replace spark plugs and check coils.",      "#f59e0b"),
        (en["fuel_wellness"],     "ENGINE",     "Fuel System",    "Fuel system needs attention. Inspect injectors and fuel pump.",   "#f59e0b"),
    ]
    for score, system, component, msg, color in checks:
        if score < 40:
            recs.append(("🔴", system, component, msg, "#ef4444", color))
        elif score < 65:
            recs.append(("🟡", system, component, f"{component} showing wear. {msg}", "#f59e0b", color))
    if not recs:
        recs.append(("🟢", "ALL SYSTEMS", "Overall", "Vehicle health looks great. Keep up with regular maintenance intervals.", "#00c864", "#00c864"))
    return recs


_STATUS_COLOR = {"ok": "#00c864", "due_soon": "#f59e0b", "overdue": "#ef4444", "unknown": _fg2}
_STATUS_LABEL = {"ok": "OK", "due_soon": "DUE SOON", "overdue": "OVERDUE", "unknown": "NOT LOGGED"}

_vehicle_label = f'{sv["year"]} {html.escape(sv["brand"])} {html.escape(sv["model"])}'

# ── Load proposals + service log ──────────────────────────────────────────────
_vehicle_proposals: list = []
if _is_biz and _is_shared:
    _vehicle_proposals = [p for p in (session.fetch_outgoing_proposals(_token) or []) if p["vehicle_id"] == sv["vehicle_id"]]
elif not _is_shared:
    _vehicle_proposals = [p for p in (session.fetch_incoming_proposals(_token) or []) if p["vehicle_id"] == sv["vehicle_id"]]

_service_log: list = session.fetch_vehicle_service_log(sv["vehicle_id"], _token) or []

def _has_log(entry_type: str, task_key: str) -> bool:
    return any(e["entry_type"] == entry_type and e["task_key"] == task_key for e in _service_log)

def _nav_log(entry_type: str, task_key: str, task_name: str):
    st.session_state["log_target"] = {
        "vehicle_id":      sv["vehicle_id"],
        "vehicle_label":   _vehicle_label,
        "current_mileage": sv["current_mileage"],
        "entry_type":      entry_type,
        "task_key":        task_key,
        "task_name":       task_name,
    }
    st.switch_page("pages/ServiceLog.py")

def _nav_history(entry_type: str, task_key: str, task_name: str):
    st.session_state["history_target"] = {
        "vehicle_id":    sv["vehicle_id"],
        "vehicle_label": _vehicle_label,
        "entry_type":    entry_type,
        "task_key":      task_key,
        "task_name":     task_name,
        "is_shared":     _is_shared,
    }
    st.switch_page("pages/ServiceHistory.py")

# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _, _col_analyze = st.columns([1, 4, 1])
with _col_back:
    if st.button("← BACK", key="back"):
        st.switch_page("pages/Home.py")
with _col_analyze:
    if st.button("⚡ ANALYZE", key="analyze", disabled=_is_shared):
        st.switch_page("Vehicle_Input.py")

# ── Vehicle header card ───────────────────────────────────────────────────────
_vin  = f'<div class="vh-vin">VIN: {html.escape(sv["vin"])}</div>' if sv.get("vin") else ""
_cust_name = sv.get("customer_name") or (sv.get("owner_name") or sv.get("owner_email") if _is_shared else None)
_cust = f'<div class="vh-customer">CUSTOMER: {html.escape(_cust_name)}</div>' if (_is_biz and _cust_name) else ""
st.markdown(
    f'<div class="vh-card">'
    f'<div class="vh-label">// VEHICLE PROFILE</div>'
    f'<div class="vh-title">{_vehicle_label}</div>'
    f'<div class="vh-mileage">{sv["current_mileage"]:,} miles</div>'
    f'{_cust}{_vin}'
    f'</div>',
    unsafe_allow_html=True,
)

if _is_shared:
    st.info("Shared customer vehicle — you can propose service updates below. The customer must approve before any data changes.")

# ── Pending proposals for customer (owner side) ───────────────────────────────
_pending = [p for p in _vehicle_proposals if p["status"] == "pending"] if not _is_shared else []
if _pending:
    st.markdown('<div class="section-label">// Pending Service Proposals</div>', unsafe_allow_html=True)
    for p in _pending:
        p_type = "Maintenance service" if p["proposal_type"] == "maintenance" else "Part replacement"
        extras = []
        if p.get("replacement_info"): extras.append(f'<div class="prop-meta">PART INFO: {html.escape(p["replacement_info"])}</div>')
        if p.get("technician_name"):  extras.append(f'<div class="prop-meta">TECHNICIAN: {html.escape(p["technician_name"])}</div>')
        if p.get("cost") is not None: extras.append(f'<div class="prop-meta">COST: ${p["cost"]:.2f}</div>')
        note_html = f'<div class="prop-note">Note: {html.escape(p["notes"])}</div>' if p.get("notes") else ""
        st.markdown(
            f'<div class="prop-card">'
            f'<div class="prop-from">{p_type.upper()} PROPOSAL FROM {html.escape(p["business_name"]).upper()}</div>'
            f'<div class="prop-title">{html.escape(p["task_name"])}</div>'
            f'<div class="prop-detail">Logged at: {p["service_mileage"]:,} mi</div>'
            f'{"".join(extras)}{note_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
        _pa, _pd = st.columns(2)
        with _pa:
            if st.button("ACCEPT", key=f"accept_{p['id']}"):
                try:
                    r = session.patch(f"/sharing/proposals/{p['id']}/accept", token=_token)
                    r.raise_for_status()
                    session.fetch_incoming_proposals.clear()
                    session.fetch_maintenance.clear()
                    session.fetch_replacements.clear()
                    session.fetch_vehicle_service_log.clear()
                    st.success(f"{p['task_name']} logged. Your records have been updated.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with _pd:
            if st.button("DENY", key=f"deny_{p['id']}"):
                try:
                    r = session.patch(f"/sharing/proposals/{p['id']}/deny", token=_token)
                    r.raise_for_status()
                    session.fetch_incoming_proposals.clear()
                    st.success("Proposal denied. No data was changed.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    st.markdown("<br>", unsafe_allow_html=True)

# ── Owner-only controls ───────────────────────────────────────────────────────
if not _is_shared:
    with st.expander("DELETE VEHICLE", expanded=False):
        st.warning("Permanently deletes this vehicle, all analyses, maintenance records, and log history.")
        confirm_key = f"confirm_del_v_{sv['vehicle_id']}"
        if not st.session_state.get(confirm_key):
            if st.button("DELETE VEHICLE", key="del_v_start"):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            st.error("This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("CONFIRM DELETE", key="del_v_confirm"):
                    try:
                        session.delete(f"/vehicles/{sv['vehicle_id']}", token=_token).raise_for_status()
                        for k in (confirm_key, "selected_vehicle", "results", "results_return_page"):
                            st.session_state.pop(k, None)
                        for fn in (session.fetch_vehicles, session.fetch_predictions,
                                   session.fetch_maintenance, session.fetch_replacements,
                                   session.fetch_vehicle_service_log):
                            fn.clear()
                        st.switch_page("pages/Home.py")
                    except Exception as e:
                        st.error(f"Could not delete vehicle: {e}")
            with c2:
                if st.button("CANCEL", key="del_v_cancel"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

    with st.expander("UPDATE CURRENT MILEAGE", expanded=False):
        mi_col, btn_col = st.columns([3, 1])
        with mi_col:
            new_mileage = st.number_input("New mileage (must be ≥ current)",
                min_value=sv["current_mileage"], max_value=2_000_000,
                value=sv["current_mileage"], step=100, key="new_mi")
        with btn_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("SAVE", key="save_mi"):
                if new_mileage == sv["current_mileage"]:
                    st.info("No change.")
                else:
                    try:
                        r = session.patch(f"/vehicles/{sv['vehicle_id']}/mileage", token=_token,
                                          json={"current_mileage": new_mileage})
                        r.raise_for_status()
                        st.session_state["selected_vehicle"] = r.json()
                        session.fetch_vehicles.clear()
                        session.fetch_maintenance.clear()
                        st.success(f"Mileage updated to {new_mileage:,} mi.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not update mileage: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Scheduled Maintenance ─────────────────────────────────────────────────────
st.markdown('<div class="section-label">// Scheduled Maintenance</div>', unsafe_allow_html=True)

tasks = session.fetch_maintenance(sv["vehicle_id"], _token)
if tasks is None:
    st.error("Could not load maintenance data.")
else:
    cols4 = st.columns(4, gap="medium")
    for i, task in enumerate(tasks):
        sv_val   = task.get("status", "unknown")
        sc       = _STATUS_COLOR[sv_val]
        sl       = _STATUS_LABEL[sv_val]
        task_key = task["task_key"]
        prop_key = f"prop_maint_{task_key}"

        with cols4[i % 4]:
            if task["miles_remaining"] is None:
                rem_html = '<div class="maint-unknown">No service on record</div>'
            elif task["miles_remaining"] > 0:
                rem_html = f'<div class="maint-remaining" style="color:{sc}">{task["miles_remaining"]:,} mi left</div>'
            else:
                rem_html = f'<div class="maint-remaining" style="color:{sc}">{abs(task["miles_remaining"]):,} mi overdue</div>'

            det_html = ""
            if task.get("last_service_mileage") is not None:
                det_html = (f'<div class="maint-detail">Last: {task["last_service_mileage"]:,} mi'
                            f' &nbsp;→&nbsp; Due: {task["next_due_mileage"]:,} mi</div>')

            st.markdown(
                f'<div class="maint-card" style="border-top:2px solid {sc}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem">'
                f'<div class="maint-title">{task["task_name"]}</div>'
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.58rem;color:{sc};letter-spacing:0.1em">{sl}</div>'
                f'</div>'
                f'<div class="maint-interval">Every {task["interval_miles"]:,} mi</div>'
                f'{det_html}{rem_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            if not _is_shared:
                # Owner: LOG MAINTENANCE + HISTORY buttons
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("LOG", key=f"log_m_{task_key}"):
                        _nav_log("maintenance", task_key, task["task_name"])
                with b2:
                    has_h = _has_log("maintenance", task_key)
                    if st.button("HISTORY", key=f"hist_m_{task_key}", disabled=not has_h):
                        _nav_history("maintenance", task_key, task["task_name"])

            elif _is_biz:
                # Business: propose update
                pending = next((p for p in _vehicle_proposals
                                if p["proposal_type"] == "maintenance"
                                and p["task_key"] == task_key
                                and p["status"] == "pending"), None)
                if pending:
                    st.markdown(f'<div class="prop-pending">PROPOSAL SENT → {pending["service_mileage"]:,} mi</div>',
                                unsafe_allow_html=True)
                elif prop_key not in st.session_state:
                    pb1, pb2 = st.columns(2)
                    with pb1:
                        if st.button("PROPOSE", key=f"propbtn_m_{task_key}"):
                            st.session_state[prop_key] = True
                            st.rerun()
                    with pb2:
                        has_h = _has_log("maintenance", task_key)
                        if st.button("HISTORY", key=f"hist_m_biz_{task_key}", disabled=not has_h):
                            _nav_history("maintenance", task_key, task["task_name"])
                else:
                    with st.form(key=f"prop_form_m_{task_key}"):
                        prop_mi   = st.number_input("Mileage at service", min_value=0, max_value=2_000_000,
                                                    value=sv["current_mileage"], step=100)
                        prop_info = st.text_input("Part / product info (optional)", max_chars=500,
                                                 placeholder="e.g. Fully synthetic 5W-30")
                        prop_tech = st.text_input("Technician name (optional)", max_chars=100)
                        prop_cost = st.number_input("Cost ($, optional)", min_value=0.0, step=0.01,
                                                    value=0.0, format="%.2f")
                        prop_note = st.text_input("Note to customer (optional)", max_chars=500)
                        c1, c2 = st.columns(2)
                        with c1:
                            send = st.form_submit_button("SEND", use_container_width=True)
                        with c2:
                            cancel = st.form_submit_button("CANCEL", use_container_width=True)
                    if cancel:
                        st.session_state.pop(prop_key, None)
                        st.rerun()
                    if send:
                        try:
                            r = session.post("/sharing/proposals", token=_token, json={
                                "vehicle_id":      sv["vehicle_id"],
                                "proposal_type":   "maintenance",
                                "task_key":        task_key,
                                "service_mileage": prop_mi,
                                "replacement_info": prop_info or None,
                                "technician_name":  prop_tech or None,
                                "cost":             prop_cost if prop_cost > 0 else None,
                                "notes":            prop_note or None,
                            })
                            if r.status_code in (200, 201):
                                st.session_state.pop(prop_key, None)
                                session.fetch_outgoing_proposals.clear()
                                st.success("Proposal sent.")
                                st.rerun()
                            else:
                                st.error(r.json().get("detail", "Could not send proposal."))
                        except Exception as e:
                            st.error(str(e))

st.markdown("<br>", unsafe_allow_html=True)

# ── Component Replacements ────────────────────────────────────────────────────
st.markdown('<div class="section-label">// Component Replacements</div>', unsafe_allow_html=True)

_SYSTEMS = [
    ("Drivetrain", [("cv_joints", "CV Joints"), ("wheel_bearings", "Wheel Bearings"), ("brakes", "Brakes")]),
    ("Electrical", [("battery", "Battery"), ("alternator", "Alternator"), ("starter", "Starter Motor")]),
    ("Engine",     [("coolant_system", "Coolant System"), ("ignition", "Ignition"), ("fuel_system", "Fuel System")]),
]

replacements_raw = session.fetch_replacements(sv["vehicle_id"], _token)
replacements_map = {r["component_key"]: r for r in (replacements_raw or [])}

rep_cols = st.columns(3, gap="medium")
for col_idx, (sys_name, components) in enumerate(_SYSTEMS):
    with rep_cols[col_idx]:
        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:{_accent};'
            f'letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.6rem">// {sys_name}</div>',
            unsafe_allow_html=True,
        )
        for comp_key, comp_name in components:
            rec        = replacements_map.get(comp_key)
            prop_r_key = f"prop_rep_{comp_key}"

            if rec:
                eff = max(sv["current_mileage"] - rec["replaced_at_mileage"], 0)
                notes_html = f'<div class="maint-detail">Note: {html.escape(rec["notes"])}</div>' if rec.get("notes") else ""
                st.markdown(
                    f'<div class="maint-card" style="border-top:2px solid #00c864">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem">'
                    f'<div class="maint-title">{comp_name}</div>'
                    f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.58rem;color:#00c864;letter-spacing:0.1em">REPLACED</div>'
                    f'</div>'
                    f'<div class="maint-detail">At: {rec["replaced_at_mileage"]:,} mi</div>'
                    f'<div class="maint-remaining" style="color:{_accent}">{eff:,} mi on new part</div>'
                    f'{notes_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="maint-card" style="border-top:2px solid {_border}">'
                    f'<div class="maint-title">{comp_name}</div>'
                    f'<div class="maint-unknown">No replacement on record</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            if not _is_shared:
                # Owner: LOG MAINTENANCE + HISTORY
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("LOG", key=f"log_r_{comp_key}"):
                        _nav_log("replacement", comp_key, comp_name)
                with b2:
                    has_h = _has_log("replacement", comp_key)
                    if st.button("HISTORY", key=f"hist_r_{comp_key}", disabled=not has_h):
                        _nav_history("replacement", comp_key, comp_name)

            elif _is_biz:
                # Business: propose replacement
                pending_rep = next((p for p in _vehicle_proposals
                                    if p["proposal_type"] == "replacement"
                                    and p["task_key"] == comp_key
                                    and p["status"] == "pending"), None)
                if pending_rep:
                    st.markdown(f'<div class="prop-pending">PROPOSAL SENT → {pending_rep["service_mileage"]:,} mi</div>',
                                unsafe_allow_html=True)
                elif prop_r_key not in st.session_state:
                    pb1, pb2 = st.columns(2)
                    with pb1:
                        if st.button("PROPOSE", key=f"propbtn_r_{comp_key}"):
                            st.session_state[prop_r_key] = True
                            st.rerun()
                    with pb2:
                        has_h = _has_log("replacement", comp_key)
                        if st.button("HISTORY", key=f"hist_r_biz_{comp_key}", disabled=not has_h):
                            _nav_history("replacement", comp_key, comp_name)
                else:
                    with st.form(key=f"prop_form_r_{comp_key}"):
                        prop_mi   = st.number_input("Replaced at mileage", min_value=0, max_value=2_000_000,
                                                    value=sv["current_mileage"], step=100)
                        prop_info = st.text_input("Part info (optional)", max_chars=500,
                                                 placeholder="e.g. OEM CV joint, aftermarket battery")
                        prop_tech = st.text_input("Technician name (optional)", max_chars=100)
                        prop_cost = st.number_input("Cost ($, optional)", min_value=0.0, step=0.01,
                                                    value=0.0, format="%.2f")
                        prop_note = st.text_input("Note to customer (optional)", max_chars=500)
                        c1, c2 = st.columns(2)
                        with c1:
                            send = st.form_submit_button("SEND", use_container_width=True)
                        with c2:
                            cancel = st.form_submit_button("CANCEL", use_container_width=True)
                    if cancel:
                        st.session_state.pop(prop_r_key, None)
                        st.rerun()
                    if send:
                        try:
                            r = session.post("/sharing/proposals", token=_token, json={
                                "vehicle_id":       sv["vehicle_id"],
                                "proposal_type":    "replacement",
                                "task_key":         comp_key,
                                "service_mileage":  prop_mi,
                                "replacement_info": prop_info or None,
                                "technician_name":  prop_tech or None,
                                "cost":             prop_cost if prop_cost > 0 else None,
                                "notes":            prop_note or None,
                            })
                            if r.status_code in (200, 201):
                                st.session_state.pop(prop_r_key, None)
                                session.fetch_outgoing_proposals.clear()
                                st.success("Proposal sent.")
                                st.rerun()
                            else:
                                st.error(r.json().get("detail", "Could not send proposal."))
                        except Exception as e:
                            st.error(str(e))

st.markdown("<br>", unsafe_allow_html=True)

# ── Prediction history ────────────────────────────────────────────────────────
predictions = session.fetch_predictions(sv["vehicle_id"], _token)

if predictions and len(predictions) > 0:
    latest = predictions[0]
    if latest.get("cv_wellness") is not None:
        st.markdown('<div class="section-label">// Latest Analysis Recommendations</div>', unsafe_allow_html=True)
        _dt = {"cv_wellness": latest["cv_wellness"], "wb_wellness": latest["wb_wellness"], "brk_wellness": latest["brk_wellness"]}
        _el = {"bat_wellness": latest["bat_wellness"], "alt_wellness": latest["alt_wellness"], "sta_wellness": latest["sta_wellness"]}
        _en = {"coolant_wellness": latest["coolant_wellness"], "ignition_wellness": latest["ignition_wellness"], "fuel_wellness": latest["fuel_wellness"]}
        recs = _get_recommendations(_dt, _el, _en)
        rec_cols = st.columns(2, gap="medium")
        for _ri, (_icon, _sys, _comp, _msg, _ac, _sc) in enumerate(recs):
            with rec_cols[_ri % 2]:
                st.markdown(
                    f'<div class="rec-card" style="border-color:{_ac}">'
                    f'<div class="rec-icon">{_icon}</div>'
                    f'<div><div class="rec-system" style="color:{_sc}">{_sys} — {_comp}</div>'
                    f'<div class="rec-text">{_msg}</div></div>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-label">// Prediction History</div>', unsafe_allow_html=True)

if predictions is None:
    st.error("Could not load predictions — check API connection.")
elif len(predictions) == 0:
    st.markdown('<div class="empty-state">NO ANALYSES RUN YET</div>', unsafe_allow_html=True)
else:
    for i, p in enumerate(predictions):
        date_str    = p["calculated_at"][:10] if p.get("calculated_at") else "—"
        ov_color    = score_color(p["overall_score"])
        has_details = p.get("cv_wellness") is not None

        if _is_shared:
            row_c, btn_c = st.columns([7, 1])
            del_c = None
        else:
            row_c, btn_c, del_c = st.columns([6, 1, 1])

        with row_c:
            st.markdown(
                f'<div class="pred-row">'
                f'<span class="pred-date">{date_str}</span>'
                f'<span class="pred-overall" style="color:{ov_color}">{p["overall_score"]:.0f}'
                f'<span style="font-size:0.65rem;color:{_fg2}">/100</span></span>'
                f'<span class="pred-sys">Engine <span style="color:{score_color(p["engine_score"])}">{p["engine_score"]:.0f}</span></span>'
                f'<span class="pred-sys">Drivetrain <span style="color:{score_color(p["drivetrain_score"])}">{p["drivetrain_score"]:.0f}</span></span>'
                f'<span class="pred-sys">Electrical <span style="color:{score_color(p["electrical_score"])}">{p["electrical_score"]:.0f}</span></span>'
                f'</div>', unsafe_allow_html=True)

        with btn_c:
            if has_details:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("DETAILS", key=f"view_pred_{i}"):
                    st.session_state["results"] = {
                        "drivetrain": {"cv_wellness": p["cv_wellness"], "wb_wellness": p["wb_wellness"],
                                       "brk_wellness": p["brk_wellness"], "system_avg": p["drivetrain_score"]},
                        "electrical": {"bat_wellness": p["bat_wellness"], "alt_wellness": p["alt_wellness"],
                                       "sta_wellness": p["sta_wellness"], "system_avg": p["electrical_score"]},
                        "engine":     {"coolant_wellness": p["coolant_wellness"], "ignition_wellness": p["ignition_wellness"],
                                       "fuel_wellness": p["fuel_wellness"], "system_avg": p["engine_score"]},
                        "overall_avg": p["overall_score"], "replacements_applied": [],
                    }
                    st.session_state["vehicle_label"] = f'{_vehicle_label} — {date_str}'
                    st.session_state["results_return_page"] = "pages/VehicleDetail.py"
                    st.session_state["results_source"] = "history"
                    st.switch_page("pages/Results.py")
            else:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button("DETAILS", key=f"view_pred_dis_{i}", disabled=True)

        if not _is_shared and del_c:
            with del_c:
                st.markdown("<br>", unsafe_allow_html=True)
                pid      = p["prediction_id"]
                del_key  = f"cdp_{pid}"
                if not st.session_state.get(del_key):
                    if st.button("DELETE", key=f"dp_{pid}"):
                        st.session_state[del_key] = True
                        st.rerun()
                else:
                    if st.button("CONFIRM", key=f"cdp_yes_{pid}"):
                        try:
                            session.delete(f"/vehicles/{sv['vehicle_id']}/predictions/{pid}", token=_token).raise_for_status()
                            st.session_state.pop(del_key, None)
                            session.fetch_predictions.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not delete: {e}")
                    if st.button("CANCEL", key=f"cdp_no_{pid}"):
                        st.session_state.pop(del_key, None)
                        st.rerun()
