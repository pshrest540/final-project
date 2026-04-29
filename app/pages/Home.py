import html
import streamlit as st
import session

st.set_page_config(
    page_title="Dashboard — VEHIDOC",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_fresh_user = session.fetch_current_user(st.session_state["token"])
if _fresh_user:
    st.session_state["user"] = _fresh_user

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
_inp_bg       = "#ddeaf5"            if _is_biz else "#111111"
_inp_border   = "#85aac7"            if _is_biz else "#2a2a2a"
_empty_bg     = "#f8fafc"            if _is_biz else "#0e0e0e"
_empty_border = "1px dashed #c0d0e0" if _is_biz else "1px dashed #222222"
_vin_color    = "#7a9abc"            if _is_biz else "#3a3a3a"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {"radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%)" if not _is_biz else _bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.page-title {{ font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: {_accent}; letter-spacing: 0.1em; text-shadow: 0 0 20px {_shadow}; margin-bottom: 0; }}
.welcome-block {{ padding: 1.5rem 0 2rem; }}
.welcome-text {{ font-family: 'Share Tech Mono', monospace; font-size: 1rem; color: {_fg2}; letter-spacing: 0.15em; }}
.welcome-name {{ color: {_accent}; }}
.divider {{ height: 1px; background: linear-gradient(90deg,{_accent} 0%,transparent 60%); margin: 0.5rem 0 1.5rem; opacity: 0.3; }}
.v-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 12px; padding: 1.2rem 1.4rem 0.8rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }}
.v-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {_top}; }}
.v-year {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.2em; margin-bottom: 0.2rem; }}
.v-name {{ font-size: 1.25rem; font-weight: 700; color: {_fg}; letter-spacing: 0.03em; margin-bottom: 0.2rem; }}
.v-mileage {{ font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: {_accent}; margin-bottom: 0.3rem; }}
.v-customer {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.08em; margin-bottom: 0.3rem; }}
.v-vin {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_vin_color}; letter-spacing: 0.1em; }}
.share-panel {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 1.5rem; }}
.share-code {{ font-family: 'Share Tech Mono', monospace; font-size: 1.45rem; color: {_accent}; letter-spacing: 0.25em; }}
.share-muted {{ font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: {_fg2}; letter-spacing: 0.12em; text-transform: uppercase; }}
.share-badge {{ display:inline-block; font-family:'Share Tech Mono',monospace; font-size:0.58rem; letter-spacing:0.12em; color:{_accent}; border:1px solid {_border}; border-radius:999px; padding:0.2rem 0.5rem; margin-bottom:0.4rem; }}
.empty-state {{ background: {_empty_bg}; border: {_empty_border}; border-radius: 10px; padding: 2rem; text-align: center; color: {_fg2}; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; letter-spacing: 0.1em; margin: 1rem 0; }}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {_inp_bg} !important;
    border: 1px solid {_inp_border} !important;
    border-radius: 6px !important;
    color: {_fg} !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {_accent} !important;
    box-shadow: 0 0 0 3px {"rgba(0,102,179,0.12)" if _is_biz else "rgba(255,255,255,0.06)"} !important;
    outline: none !important;
}}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px {_shadow} !important; }}
.stButton > button:hover {{ box-shadow: 0 0 28px {_shadow_h} !important; }}
[data-testid="InputInstructions"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)


# ── Top bar ───────────────────────────────────────────────────────────────────
_tl, _tr = st.columns([4, 2])
with _tl:
    _title = "// FLEET DASHBOARD" if _is_biz else "// DASHBOARD"
    st.markdown(f'<div class="page-title">{_title}</div>', unsafe_allow_html=True)
with _tr:
    _email = html.escape(_user.get("email", "") if isinstance(_user, dict) else "")
    st.markdown(
        f'<p style="text-align:right;font-family:\'Share Tech Mono\',monospace;'
        f'font-size:0.7rem;color:{_fg2};margin:0;padding-top:0.35rem">{_email}</p>',
        unsafe_allow_html=True,
    )
    _btn_acct, _btn_lo = st.columns(2)
    with _btn_acct:
        if st.button("ACCOUNT", key="account", use_container_width=True):
            st.switch_page("pages/Account.py")
    with _btn_lo:
        if st.button("LOGOUT", key="logout", use_container_width=True):
            st.session_state.pop("token", None)
            st.session_state.pop("user", None)
            st.session_state.pop("selected_vehicle", None)
            st.switch_page("pages/Login.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────────────────────────
_name  = html.escape((_user.get("business_name") or _user.get("full_name") or _user.get("email", "")) if isinstance(_user, dict) else "")
_greet = "FLEET MANAGER" if _is_biz else "WELCOME BACK"
st.markdown(
    f'<div class="welcome-block"><div class="welcome-text">{_greet}, '
    f'<span class="welcome-name">{_name.upper()}</span></div></div>',
    unsafe_allow_html=True,
)

# ── Vehicles section ──────────────────────────────────────────────────────────
if _is_biz:
    st.markdown('<div class="share-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">// ADD CUSTOMER</div>', unsafe_allow_html=True)
    with st.form("link_customer_form", clear_on_submit=True):
        c_code, c_btn = st.columns([3, 1])
        with c_code:
            pairing_code = st.text_input(
                "Customer connection code",
                max_chars=5,
                placeholder="AB3X7",
                key="customer_pairing_code",
                help="Ask the customer to open the Connect page and share their 5-character code with you.",
            )
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted_link = st.form_submit_button("ADD")
        if submitted_link:
            clean = pairing_code.strip().upper()
            if len(clean) != 5:
                st.error("Enter the customer's 5-character connection code.")
            else:
                try:
                    r = session.post(
                        "/sharing/customers",
                        token=st.session_state["token"],
                        json={"pairing_code": clean},
                    )
                    if r.status_code in (200, 201):
                        session.fetch_linked_customers.clear()
                        session.fetch_vehicles.clear()
                        st.success("Customer linked.")
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "Could not link customer."))
                except Exception as e:
                    st.error(f"Could not link customer: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("CUSTOMER LOOKUP", key="go_customers", use_container_width=True):
        st.switch_page("pages/Customers.py")

else:
    share_code = (_user.get("share_code") if isinstance(_user, dict) else "") or "------"
    st.markdown(
        f'<div class="share-panel">'
        f'<div class="share-muted">YOUR ID</div>'
        f'<div class="share-code">{html.escape(share_code)}</div>'
        f'<div style="font-size:0.75rem;color:{_fg2};margin-top:0.3rem;font-family:\'Share Tech Mono\',monospace;letter-spacing:0.08em">'
        f'Give this to a service provider so they can find your vehicles.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    _conn_col, _conn_btn = st.columns([3, 1])
    with _conn_col:
        st.markdown(
            f'<div class="share-panel" style="margin-bottom:0">'
            f'<div class="share-muted">LINK A SERVICE PROVIDER</div>'
            f'<div style="font-size:0.82rem;color:{_fg2};margin-top:0.3rem">Generate a one-time connection code to share with your mechanic or dealer.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with _conn_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CONNECT", key="connect_biz", use_container_width=True):
            st.switch_page("pages/Connect.py")

    # ── Connected businesses ────────────────────────────────────────────────
    linked_businesses = session.fetch_linked_businesses(st.session_state["token"]) or []
    if linked_businesses:
        st.markdown('<div class="share-panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">// CONNECTED BUSINESSES</div>', unsafe_allow_html=True)
        for biz in linked_businesses:
            biz_label = html.escape(biz.get("business_name") or biz.get("email") or biz["user_id"])
            b_label, b_remove = st.columns([4, 1])
            with b_label:
                st.markdown(
                    f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:1.1rem;font-weight:700;color:{_fg};margin-bottom:0.3rem">{biz_label}</div>',
                    unsafe_allow_html=True,
                )
            with b_remove:
                if st.button("REMOVE", key=f"unbiz_{biz['user_id']}"):
                    st.session_state[f"confirm_unbiz_{biz['user_id']}"] = True
                    st.rerun()
            if st.session_state.get(f"confirm_unbiz_{biz['user_id']}"):
                st.warning(f"Remove **{biz_label}**? They will lose access to all your shared vehicles and all pending proposals will be cancelled.")
                _cc1, _cc2 = st.columns(2)
                with _cc1:
                    if st.button("CONFIRM REMOVE", key=f"unbiz_confirm_{biz['user_id']}", use_container_width=True):
                        try:
                            r = session.delete(f"/sharing/businesses/{biz['user_id']}", token=st.session_state["token"])
                            r.raise_for_status()
                            session.fetch_linked_businesses.clear()
                            session.fetch_incoming_proposals.clear()
                            st.session_state.pop(f"confirm_unbiz_{biz['user_id']}", None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not remove business: {e}")
                with _cc2:
                    if st.button("CANCEL", key=f"unbiz_cancel_{biz['user_id']}", use_container_width=True):
                        st.session_state.pop(f"confirm_unbiz_{biz['user_id']}", None)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Pending proposal notification ──────────────────────────────────────
    incoming = session.fetch_incoming_proposals(st.session_state["token"]) or []
    pending_count = sum(1 for p in incoming if p["status"] == "pending")
    if pending_count > 0:
        st.markdown(
            f'<div class="share-panel" style="border-color:{"#f59e0b"};background:{"rgba(245,158,11,0.06)" if _is_biz else "rgba(245,158,11,0.08)"}">'
            f'<div class="share-muted" style="color:#f59e0b">PENDING SERVICE PROPOSALS</div>'
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:1.1rem;color:#f59e0b;margin-top:0.3rem">'
            f'{pending_count} PROPOSAL{"S" if pending_count != 1 else ""} AWAITING YOUR REVIEW</div>'
            f'<div style="font-size:0.78rem;color:{_fg2};margin-top:0.4rem">'
            f'Open a vehicle\'s details page to accept or deny each proposal.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

_vh, _vadd = st.columns([3, 1])
with _vh:
    _sec = "// FLEET VEHICLES" if _is_biz else "// YOUR VEHICLES"
    st.markdown(f'<div class="section-label">{_sec}</div>', unsafe_allow_html=True)
with _vadd:
    if not _is_biz:
        if st.button("+ ADD VEHICLE", key="add_vehicle"):
            st.switch_page("pages/AddVehicle.py")

vehicles = session.fetch_vehicles(st.session_state["token"])

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
            _shared = bool(v.get("is_shared"))
            _vin  = f'<div class="v-vin">VIN: {html.escape(v["vin"])}</div>' if v.get("vin") else ""
            _cust_name = v.get("customer_name")
            if _shared:
                _cust_name = _cust_name or v.get("owner_name") or v.get("owner_email")
            _cust = f'<div class="v-customer">CUSTOMER: {html.escape(_cust_name)}</div>' if (_is_biz and _cust_name) else ""
            _shared_badge = '<div class="share-badge">SHARED</div>' if _shared else ""
            st.markdown(
                f'<div class="v-card">'
                f'{_shared_badge}'
                f'<div class="v-year">// {v["year"]}</div>'
                f'<div class="v-name">{html.escape(v["brand"])} {html.escape(v["model"])}</div>'
                f'{_cust}'
                f'<div class="v-mileage">{v["current_mileage"]:,} miles</div>'
                f'{_vin}'
                f'</div>',
                unsafe_allow_html=True,
            )
            if not _is_biz:
                share_value = bool(v.get("share_enabled"))
                new_share_value = st.toggle(
                    "SHARE WITH DEALER",
                    value=share_value,
                    key=f"share_toggle_{v['vehicle_id']}",
                )
                if new_share_value != share_value:
                    try:
                        r = session.patch(
                            f"/vehicles/{v['vehicle_id']}/sharing",
                            token=st.session_state["token"],
                            json={"share_enabled": new_share_value},
                        )
                        r.raise_for_status()
                        session.fetch_vehicles.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not update sharing: {e}")
            if st.button("DETAILS", key=f"detail_{v['vehicle_id']}", use_container_width=True):
                st.session_state["selected_vehicle"] = v
                st.switch_page("pages/VehicleDetail.py")
