import streamlit as st
import session

st.set_page_config(
    page_title="Service History — VEHIDOC",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

ht = st.session_state.get("history_target")
if not ht:
    st.switch_page("pages/Home.py")

_token    = st.session_state["token"]
_user     = st.session_state.get("user", {})
_is_biz   = isinstance(_user, dict) and _user.get("account_type") == "business"
_is_shared = bool(ht.get("is_shared"))

vehicle_id    = ht["vehicle_id"]
vehicle_label = ht["vehicle_label"]
entry_type    = ht["entry_type"]
task_key      = ht["task_key"]
task_name     = ht["task_name"]

# ── Theme tokens ──────────────────────────────────────────────────────────────
_bg     = "#f0f4f8"  if _is_biz else "#070707"
_accent = "#0066b3"  if _is_biz else "#ffffff"
_fg     = "#1a2a3a"  if _is_biz else "#f0f0f0"
_fg2    = "#4a6a8a"  if _is_biz else "#555555"
_border = "#d0dce8"  if _is_biz else "#1e1e1e"
_card_g = "#ffffff"  if _is_biz else "#0c0c0c"
_row_bg = "#f8fafc"  if _is_biz else "#0e0e0e"
_top    = f"linear-gradient(90deg,transparent,{_accent},transparent)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {"radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%)" if not _is_biz else _bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.hist-header {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 14px; padding: 1.5rem 2rem 1.2rem; margin-bottom: 1.5rem; position: relative; overflow: hidden; }}
.hist-header::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {_top}; }}
.hist-vehicle {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.2rem; }}
.hist-title {{ font-size: 1.5rem; font-weight: 700; color: {_fg}; margin-bottom: 0.1rem; }}
.hist-type {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_accent}; letter-spacing: 0.18em; }}
.entry-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 10px; padding: 1.2rem 1.4rem 1rem; margin-bottom: 0.8rem; position: relative; }}
.entry-date {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.15em; margin-bottom: 0.4rem; }}
.entry-mileage {{ font-family: 'Share Tech Mono', monospace; font-size: 1.1rem; font-weight: 700; color: {_fg}; margin-bottom: 0.4rem; }}
.entry-info {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; margin-bottom: 0.2rem; }}
.entry-meta {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; margin-bottom: 0.15rem; }}
.entry-cost {{ font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: {"#059669" if _is_biz else "#4ade80"}; margin-bottom: 0.2rem; }}
.entry-notes {{ font-size: 0.82rem; color: {_fg2}; font-style: italic; margin-top: 0.3rem; border-top: 1px solid {_border}; padding-top: 0.4rem; }}
.empty-state {{ background: {_row_bg}; border: {"1px dashed #c0d0e0" if _is_biz else "1px dashed #222222"}; border-radius: 10px; padding: 3rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; }}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _col_title = st.columns([1, 5])
with _col_back:
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/VehicleDetail.py")
with _col_title:
    st.markdown(
        f'<div class="section-label" style="margin-top:0.5rem">SERVICE HISTORY</div>',
        unsafe_allow_html=True,
    )

# ── Header card ───────────────────────────────────────────────────────────────
_type_label = "SCHEDULED MAINTENANCE" if entry_type == "maintenance" else "COMPONENT REPLACEMENT"
st.markdown(f"""
<div class="hist-header">
  <div class="hist-vehicle">{vehicle_label}</div>
  <div class="hist-title">{task_name}</div>
  <div class="hist-type">{_type_label}</div>
</div>
""", unsafe_allow_html=True)

# ── Load and filter log ───────────────────────────────────────────────────────
_all_log = session.fetch_vehicle_service_log(vehicle_id, _token) or []
_entries = [e for e in _all_log if e["entry_type"] == entry_type and e["task_key"] == task_key]

if not _entries:
    st.markdown('<div class="empty-state">NO SERVICE HISTORY FOR THIS ITEM</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(f'<div class="section-label">{len(_entries)} RECORD{"S" if len(_entries) != 1 else ""}</div>', unsafe_allow_html=True)

# ── Confirm-delete state ──────────────────────────────────────────────────────
if "confirm_delete_log" not in st.session_state:
    st.session_state["confirm_delete_log"] = None

for entry in _entries:
    eid = entry["id"]
    logged_at = entry.get("logged_at", "")
    if logged_at:
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(logged_at.replace("Z", "+00:00"))
            logged_at = dt.strftime("%b %d, %Y  %H:%M")
        except Exception:
            pass

    shop      = entry.get("shop_name") or ""
    tech      = entry.get("technician_name") or ""
    rep_info  = entry.get("replacement_info") or ""
    cost      = entry.get("cost")
    notes     = entry.get("notes") or ""

    who_parts = []
    if shop:
        who_parts.append(f"SHOP: {shop}")
    if tech:
        who_parts.append(f"TECH: {tech}")
    who_line = "  ·  ".join(who_parts) if who_parts else ""

    with st.container():
        st.markdown(f"""
<div class="entry-card">
  <div class="entry-date">{logged_at}</div>
  <div class="entry-mileage">{entry['service_mileage']:,} mi</div>
  {f'<div class="entry-info">{rep_info}</div>' if rep_info else ""}
  {f'<div class="entry-meta">{who_line}</div>' if who_line else ""}
  {f'<div class="entry-cost">$ {cost:,.2f}</div>' if cost is not None else ""}
  {f'<div class="entry-notes">{notes}</div>' if notes else ""}
</div>
""", unsafe_allow_html=True)

        # Delete button — only for vehicle owner (not when viewing as linked business)
        if not _is_shared:
            if st.session_state["confirm_delete_log"] == eid:
                _c1, _c2, _c3 = st.columns([2, 1, 1])
                with _c1:
                    st.markdown(
                        f'<span style="font-family:\'Share Tech Mono\',monospace;font-size:0.72rem;color:#ef4444;">Delete this entry? This cannot be undone.</span>',
                        unsafe_allow_html=True,
                    )
                with _c2:
                    if st.button("CONFIRM DELETE", key=f"confirm_{eid}", use_container_width=True):
                        try:
                            r = session.delete(f"/vehicles/{vehicle_id}/service-log/{eid}", token=_token)
                            if r.status_code == 204:
                                session.fetch_vehicle_service_log.clear()
                                st.session_state["confirm_delete_log"] = None
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {r.text}")
                        except Exception as exc:
                            st.error(f"Connection error: {exc}")
                with _c3:
                    if st.button("CANCEL", key=f"cancel_{eid}", use_container_width=True):
                        st.session_state["confirm_delete_log"] = None
                        st.rerun()
            else:
                if st.button("DELETE ENTRY", key=f"del_{eid}"):
                    st.session_state["confirm_delete_log"] = eid
                    st.rerun()
