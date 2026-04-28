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

_token  = st.session_state["token"]
_user   = st.session_state.get("user", {})
_is_biz = isinstance(_user, dict) and _user.get("account_type") == "business"

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
.vh-customer {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; margin-top: 0.35rem; letter-spacing: 0.08em; }}
.vh-vin {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_vin_c}; margin-top: 0.4rem; }}

/* maintenance cards */
.maint-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 10px; padding: 1rem 1.1rem 0.7rem; margin-bottom: 0.4rem; position: relative; overflow: hidden; }}
.maint-title {{ font-size: 0.88rem; font-weight: 700; color: {_fg}; margin-bottom: 0.15rem; }}
.maint-interval {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_fg2}; margin-bottom: 0.5rem; }}
.maint-detail {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_fg2}; margin-bottom: 0.2rem; }}
.maint-remaining {{ font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; font-weight: 700; margin-bottom: 0.15rem; }}
.maint-unknown {{ font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; color: {_fg2}; margin-bottom: 0.3rem; font-style: italic; }}

/* prediction history rows */
.pred-row {{ background: {_row_bg}; border: 1px solid {_border}; border-radius: 10px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }}
.pred-date {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; min-width: 90px; }}
.pred-overall {{ font-family: 'Share Tech Mono', monospace; font-size: 1.4rem; font-weight: 700; min-width: 70px; }}
.pred-sys {{ font-size: 0.82rem; color: {_sub_score_c}; }}
.pred-sys span {{ font-family: 'Share Tech Mono', monospace; }}
.empty-state {{ background: {_empty_bg}; border: {_empty_border}; border-radius: 10px; padding: 2rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }}

/* recommendation cards */
.rec-card {{ background: {_empty_bg}; border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; border-left: 3px solid; display: flex; align-items: flex-start; gap: 0.7rem; }}
.rec-icon {{ font-size: 1rem; margin-top: 0.1rem; flex-shrink: 0; }}
.rec-system {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.15rem; }}
.rec-text {{ font-size: 0.88rem; color: {_fg}; line-height: 1.4; }}

/* buttons */
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.78rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.45rem 0.8rem !important; text-transform: uppercase !important; box-shadow: 0 0 12px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 22px {_shadow_h} !important; }}
.stNumberInput > div > div > input {{ background: {_inp_bg} !important; border: 1px solid {_border} !important; border-radius: 8px !important; color: {_fg} !important; }}
</style>
""", unsafe_allow_html=True)


def score_color(s):
    if s >= 65:   return "#00c864"
    elif s >= 40: return "#f59e0b"
    return "#ef4444"


def _get_recommendations(dt, el, en):
    recs = []
    checks = [
        (dt["cv_wellness"],       "DRIVETRAIN", "CV Joints",      "CV joints are worn. Inspect for clicking sounds during turns.",      "#00d4ff"),
        (dt["wb_wellness"],       "DRIVETRAIN", "Wheel Bearings", "Wheel bearings degraded. Listen for humming at highway speed.",      "#00d4ff"),
        (dt["brk_wellness"],      "DRIVETRAIN", "Brakes",         "Brake system needs attention. Schedule inspection immediately.",     "#00d4ff"),
        (el["bat_wellness"],      "ELECTRICAL", "Battery",        "Battery health low. Consider replacement before cold season.",       "#a78bfa"),
        (el["alt_wellness"],      "ELECTRICAL", "Alternator",     "Alternator output low. Monitor charging voltage.",                   "#a78bfa"),
        (el["sta_wellness"],      "ELECTRICAL", "Starter",        "Starter motor worn. Watch for slow cranking on startup.",            "#a78bfa"),
        (en["coolant_wellness"],  "ENGINE",     "Coolant System", "Coolant system degraded. Schedule a flush and inspection.",          "#f59e0b"),
        (en["ignition_wellness"], "ENGINE",     "Ignition",       "Ignition system worn. Replace spark plugs and check coils.",         "#f59e0b"),
        (en["fuel_wellness"],     "ENGINE",     "Fuel System",    "Fuel system needs attention. Inspect injectors and fuel pump.",      "#f59e0b"),
    ]
    for score, system, component, msg, color in checks:
        if score < 40:
            recs.append(("🔴", system, component, msg, "#ef4444", color))
        elif score < 65:
            recs.append(("🟡", system, component, f"{component} showing wear. {msg}", "#f59e0b", color))
    if not recs:
        recs.append(("🟢", "ALL SYSTEMS", "Overall", "Vehicle health looks great. Keep up with regular maintenance intervals.", "#00c864", "#00c864"))
    return recs


_STATUS_COLOR = {
    "ok":       "#00c864",
    "due_soon": "#f59e0b",
    "overdue":  "#ef4444",
    "unknown":  _fg2,
}
_STATUS_LABEL = {
    "ok":       "OK",
    "due_soon": "DUE SOON",
    "overdue":  "OVERDUE",
    "unknown":  "NOT LOGGED",
}

# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _, _col_analyze = st.columns([1, 4, 1])
with _col_back:
    if st.button("← BACK", key="back"):
        st.switch_page("pages/Home.py")
with _col_analyze:
    if st.button("⚡ ANALYZE", key="analyze"):
        st.switch_page("Vehicle_Input.py")

# ── Vehicle header card ───────────────────────────────────────────────────────
_vin  = f'<div class="vh-vin">VIN: {html.escape(sv["vin"])}</div>' if sv.get("vin") else ""
_cust = f'<div class="vh-customer">CUSTOMER: {html.escape(sv["customer_name"])}</div>' if (_is_biz and sv.get("customer_name")) else ""
st.markdown(
    f'<div class="vh-card">'
    f'<div class="vh-label">// VEHICLE PROFILE</div>'
    f'<div class="vh-title">{sv["year"]} {html.escape(sv["brand"])} {html.escape(sv["model"])}</div>'
    f'<div class="vh-mileage">{sv["current_mileage"]:,} miles</div>'
    f'{_cust}{_vin}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Mileage update ────────────────────────────────────────────────────────────
with st.expander("DELETE VEHICLE", expanded=False):
    st.warning("This permanently deletes this vehicle and all saved analyses, maintenance records, and replacement records.")
    confirm_key = f"confirm_delete_vehicle_{sv['vehicle_id']}"
    if not st.session_state.get(confirm_key):
        if st.button("DELETE VEHICLE", key="delete_vehicle_start"):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        st.error("Click confirm to permanently delete this vehicle and all related information.")
        c_confirm, c_cancel = st.columns(2)
        with c_confirm:
            if st.button("CONFIRM DELETE", key="delete_vehicle_confirm"):
                try:
                    r = session.delete(f"/vehicles/{sv['vehicle_id']}", token=_token)
                    r.raise_for_status()
                    st.session_state.pop(confirm_key, None)
                    st.session_state.pop("selected_vehicle", None)
                    st.session_state.pop("results", None)
                    st.session_state.pop("results_return_page", None)
                    session.fetch_vehicles.clear()
                    session.fetch_predictions.clear()
                    session.fetch_maintenance.clear()
                    session.fetch_replacements.clear()
                    st.success("Vehicle deleted.")
                    st.switch_page("pages/Home.py")
                except Exception as e:
                    st.error(f"Could not delete vehicle: {e}")
        with c_cancel:
            if st.button("CANCEL", key="delete_vehicle_cancel"):
                st.session_state.pop(confirm_key, None)
                st.rerun()

with st.expander("UPDATE CURRENT MILEAGE", expanded=False):
    mi_col, btn_col = st.columns([3, 1])
    with mi_col:
        new_mileage = st.number_input(
            "New mileage (must be ≥ current)",
            min_value=sv["current_mileage"],
            max_value=2_000_000,
            value=sv["current_mileage"],
            step=100,
            key="new_mileage_input",
            label_visibility="visible",
        )
    with btn_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SAVE", key="save_mileage"):
            if new_mileage == sv["current_mileage"]:
                st.info("No change — enter a higher mileage.")
            else:
                try:
                    r = session.patch(
                        f"/vehicles/{sv['vehicle_id']}/mileage",
                        token=_token,
                        json={"current_mileage": new_mileage},
                    )
                    r.raise_for_status()
                    updated = r.json()
                    st.session_state["selected_vehicle"] = updated
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
        status     = task.get("status", "unknown")
        sc         = _STATUS_COLOR[status]
        sl         = _STATUS_LABEL[status]
        task_key   = task["task_key"]
        log_key    = f"log_form_{task_key}"

        with cols4[i % 4]:
            # ── Status header line ──
            if task["miles_remaining"] is None:
                remaining_html = f'<div class="maint-unknown">No service on record</div>'
            elif task["miles_remaining"] > 0:
                remaining_html = f'<div class="maint-remaining" style="color:{sc}">{task["miles_remaining"]:,} mi left</div>'
            else:
                remaining_html = f'<div class="maint-remaining" style="color:{sc}">{abs(task["miles_remaining"]):,} mi overdue</div>'

            detail_html = ""
            if task.get("last_service_mileage") is not None:
                detail_html = (
                    f'<div class="maint-detail">'
                    f'Last: {task["last_service_mileage"]:,} mi &nbsp;→&nbsp; '
                    f'Due: {task["next_due_mileage"]:,} mi'
                    f'</div>'
                )

            st.markdown(
                f'<div class="maint-card" style="border-top:2px solid {sc}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem">'
                f'<div class="maint-title">{task["task_name"]}</div>'
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.58rem;color:{sc};letter-spacing:0.1em">{sl}</div>'
                f'</div>'
                f'<div class="maint-interval">Every {task["interval_miles"]:,} mi</div>'
                f'{detail_html}{remaining_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # ── Log service interaction ──
            if log_key not in st.session_state:
                if st.button("LOG SERVICE", key=f"log_btn_{task_key}"):
                    st.session_state[log_key] = True
                    st.rerun()
            else:
                svc_mi = st.number_input(
                    "Service mileage",
                    min_value=0,
                    max_value=2_000_000,
                    value=sv["current_mileage"],
                    step=100,
                    key=f"svc_mi_{task_key}",
                    label_visibility="visible",
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("CONFIRM", key=f"confirm_{task_key}"):
                        try:
                            r = session.post(
                                f"/vehicles/{sv['vehicle_id']}/maintenance/{task_key}",
                                token=_token,
                                json={"service_mileage": svc_mi},
                            )
                            r.raise_for_status()
                            st.session_state.pop(log_key, None)
                            session.fetch_maintenance.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with c2:
                    if st.button("CANCEL", key=f"cancel_{task_key}"):
                        st.session_state.pop(log_key, None)
                        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Component Replacements ────────────────────────────────────────────────────
st.markdown('<div class="section-label">// Component Replacements</div>', unsafe_allow_html=True)

_SYSTEMS = [
    ("Drivetrain", [("cv_joints", "CV Joints"), ("wheel_bearings", "Wheel Bearings"), ("brakes", "Brakes")]),
    ("Electrical", [("battery", "Battery"), ("alternator", "Alternator"), ("starter", "Starter Motor")]),
    ("Engine",     [("coolant_system", "Coolant System"), ("ignition", "Ignition"), ("fuel_system", "Fuel System")]),
]

replacements_raw = session.fetch_replacements(sv["vehicle_id"], _token)
replacements_map  = {r["component_key"]: r for r in (replacements_raw or [])}

rep_cols = st.columns(3, gap="medium")
for col_idx, (sys_name, components) in enumerate(_SYSTEMS):
    with rep_cols[col_idx]:
        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:{_accent};'
            f'letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.6rem">// {sys_name}</div>',
            unsafe_allow_html=True,
        )
        for comp_key, comp_name in components:
            rec = replacements_map.get(comp_key)
            form_key = f"rep_form_{comp_key}"

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
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("UPDATE", key=f"rep_update_{comp_key}"):
                        st.session_state[form_key] = True
                        st.rerun()
                with c2:
                    if st.button("CLEAR", key=f"rep_del_{comp_key}"):
                        try:
                            r = session.delete(
                                f"/vehicles/{sv['vehicle_id']}/replacements/{comp_key}",
                                token=_token,
                            )
                            r.raise_for_status()
                            session.fetch_replacements.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
            else:
                st.markdown(f"""
<div class="maint-card" style="border-top:2px solid {_border}">
    <div class="maint-title">{comp_name}</div>
    <div class="maint-unknown">No replacement on record</div>
</div>""", unsafe_allow_html=True)
                if form_key not in st.session_state:
                    if st.button("LOG REPLACEMENT", key=f"rep_log_{comp_key}"):
                        st.session_state[form_key] = True
                        st.rerun()

            if st.session_state.get(form_key):
                rep_mi = st.number_input(
                    "Replaced at mileage",
                    min_value=0,
                    max_value=sv["current_mileage"],
                    value=rec["replaced_at_mileage"] if rec else sv["current_mileage"],
                    step=100,
                    key=f"rep_mi_{comp_key}",
                )
                rep_notes = st.text_input(
                    "Notes (optional)",
                    value=rec.get("notes", "") if rec else "",
                    max_chars=255,
                    key=f"rep_notes_{comp_key}",
                )
                cf1, cf2 = st.columns(2)
                with cf1:
                    if st.button("SAVE", key=f"rep_save_{comp_key}"):
                        try:
                            r = session.post(
                                f"/vehicles/{sv['vehicle_id']}/replacements/{comp_key}",
                                token=_token,
                                json={"replaced_at_mileage": rep_mi, "notes": rep_notes or None},
                            )
                            r.raise_for_status()
                            st.session_state.pop(form_key, None)
                            session.fetch_replacements.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with cf2:
                    if st.button("CANCEL", key=f"rep_cancel_{comp_key}"):
                        st.session_state.pop(form_key, None)
                        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Prediction history ────────────────────────────────────────────────────────
predictions = session.fetch_predictions(sv["vehicle_id"], _token)

# ── Latest analysis recommendations ──────────────────────────────────────────
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
                    f'</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-label">// Prediction History</div>', unsafe_allow_html=True)

if predictions is None:
    st.error("Could not load predictions — check API connection.")
elif len(predictions) == 0:
    st.markdown(
        '<div class="empty-state">NO ANALYSES RUN YET<br>'
        '<span style="font-size:0.7rem;opacity:0.6">Use the ANALYZE button above to run your first diagnostic.</span></div>',
        unsafe_allow_html=True,
    )
else:
    for i, p in enumerate(predictions):
        date_str = p["calculated_at"][:10] if p.get("calculated_at") else "—"
        ov_color = score_color(p["overall_score"])
        en_color = score_color(p["engine_score"])
        dt_color = score_color(p["drivetrain_score"])
        el_color = score_color(p["electrical_score"])
        has_details = p.get("cv_wellness") is not None

        row_c, btn_c, del_c = st.columns([6, 1, 1])
        with row_c:
            st.markdown(
                f'<div class="pred-row">'
                f'<span class="pred-date">{date_str}</span>'
                f'<span class="pred-overall" style="color:{ov_color}">{p["overall_score"]:.0f}'
                f'<span style="font-size:0.65rem;color:{_fg2}">/100</span></span>'
                f'<span class="pred-sys">Engine <span style="color:{en_color}">{p["engine_score"]:.0f}</span></span>'
                f'<span class="pred-sys">Drivetrain <span style="color:{dt_color}">{p["drivetrain_score"]:.0f}</span></span>'
                f'<span class="pred-sys">Electrical <span style="color:{el_color}">{p["electrical_score"]:.0f}</span></span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with btn_c:
            if has_details:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("DETAILS", key=f"view_pred_{i}"):
                    st.session_state["results"] = {
                        "drivetrain": {
                            "cv_wellness":  p["cv_wellness"],
                            "wb_wellness":  p["wb_wellness"],
                            "brk_wellness": p["brk_wellness"],
                            "system_avg":   p["drivetrain_score"],
                        },
                        "electrical": {
                            "bat_wellness": p["bat_wellness"],
                            "alt_wellness": p["alt_wellness"],
                            "sta_wellness": p["sta_wellness"],
                            "system_avg":   p["electrical_score"],
                        },
                        "engine": {
                            "coolant_wellness":  p["coolant_wellness"],
                            "ignition_wellness": p["ignition_wellness"],
                            "fuel_wellness":     p["fuel_wellness"],
                            "system_avg":        p["engine_score"],
                        },
                        "overall_avg": p["overall_score"],
                        "replacements_applied": [],
                    }
                    st.session_state["vehicle_label"] = f'{sv["year"]} {sv["brand"]} {sv["model"]} — {date_str}'
                    st.session_state["results_return_page"] = "pages/VehicleDetail.py"
                    st.session_state["results_source"] = "history"
                    st.switch_page("pages/Results.py")
            else:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button("DETAILS", key=f"view_pred_disabled_{i}", disabled=True)
        with del_c:
            st.markdown("<br>", unsafe_allow_html=True)
            prediction_id = p["prediction_id"]
            delete_key = f"confirm_delete_prediction_{prediction_id}"
            if not st.session_state.get(delete_key):
                if st.button("DELETE", key=f"delete_pred_{prediction_id}"):
                    st.session_state[delete_key] = True
                    st.rerun()
            else:
                if st.button("CONFIRM", key=f"confirm_pred_{prediction_id}"):
                    try:
                        r = session.delete(
                            f"/vehicles/{sv['vehicle_id']}/predictions/{prediction_id}",
                            token=_token,
                        )
                        r.raise_for_status()
                        st.session_state.pop(delete_key, None)
                        session.fetch_predictions.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not delete analysis: {e}")
                if st.button("CANCEL", key=f"cancel_pred_{prediction_id}"):
                    st.session_state.pop(delete_key, None)
                    st.rerun()
