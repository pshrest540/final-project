import html
import streamlit as st
import session

st.set_page_config(
    page_title="Admin Console — MIA",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Auth + role gate ──────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_user = st.session_state.get("user", {})
if not isinstance(_user, dict) or _user.get("account_type") != "admin":
    st.switch_page("pages/Home.py")

_token = st.session_state["token"]

# ── Admin red theme ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0d0808; color: #f0d8d8; }
.stApp { background: #0d0808; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.page-title  { font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: #e53535; letter-spacing: 0.1em; text-shadow: 0 0 20px rgba(229,53,53,0.4); }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #e53535; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }
.divider { height: 1px; background: linear-gradient(90deg,#e53535 0%,transparent 60%); margin: 0.5rem 0 1.5rem; opacity: 0.3; }

/* stat cards */
.stat-card { background: linear-gradient(135deg,#1c0a0a 0%,#220d0d 100%); border: 1px solid #3a1515; border-radius: 12px; padding: 1.4rem 1.6rem; position: relative; overflow: hidden; text-align: center; }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg,transparent,#e53535,transparent); }
.stat-value { font-family: 'Share Tech Mono', monospace; font-size: 2.6rem; font-weight: 700; color: #e53535; line-height: 1; }
.stat-label { font-size: 0.72rem; color: #8a5555; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.3rem; }

/* user rows */
.user-row { background: linear-gradient(135deg,#1a0a0a 0%,#1f0c0c 100%); border: 1px solid #3a1515; border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }
.user-row::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg,transparent,#3a1515,transparent); }
.user-email { font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: #f0d8d8; }
.user-name  { font-size: 0.78rem; color: #8a5555; margin-top: 0.1rem; }
.badge { display: inline-block; font-family: 'Share Tech Mono', monospace; font-size: 0.6rem; letter-spacing: 0.15em; padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase; font-weight: 700; }
.badge-personal  { background: rgba(0,212,255,0.12); color: #00d4ff; border: 1px solid rgba(0,212,255,0.25); }
.badge-business  { background: rgba(0,102,179,0.15); color: #4499dd; border: 1px solid rgba(0,102,179,0.3); }
.badge-admin     { background: rgba(229,53,53,0.15);  color: #e53535; border: 1px solid rgba(229,53,53,0.3); }
.user-meta { font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; color: #6a3535; }

/* system card */
.sys-card { background: linear-gradient(135deg,#1a0a0a 0%,#1f0c0c 100%); border: 1px solid #3a1515; border-radius: 12px; padding: 1.6rem; position: relative; overflow: hidden; }
.sys-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg,transparent,#e53535,transparent); }

/* status pill */
.status-ok  { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #00c864; }
.status-err { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #e53535; }

/* buttons — all .stButton globally */
.stButton > button {
    background: linear-gradient(135deg,#cc2020 0%,#991010 100%) !important;
    color: #ffffff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important; font-weight: 700 !important;
    letter-spacing: 0.12em !important; border: none !important;
    border-radius: 8px !important; padding: 0.5rem 1rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 14px rgba(204,32,32,0.3) !important;
}
.stButton > button:hover { box-shadow: 0 0 26px rgba(204,32,32,0.55) !important; }

.stSelectbox > div > div { background: #1a0a0a !important; border: 1px solid #3a1515 !important; border-radius: 8px !important; color: #f0d8d8 !important; }
.stTextInput > div > div > input { background: #1a0a0a !important; border: 1px solid #3a1515 !important; border-radius: 8px !important; color: #f0d8d8 !important; }
</style>
""", unsafe_allow_html=True)


# ── Top bar ───────────────────────────────────────────────────────────────────
_tl, _tr = st.columns([4, 2])
with _tl:
    st.markdown('<div class="page-title">// ADMIN CONSOLE</div>', unsafe_allow_html=True)
with _tr:
    _email = html.escape(_user.get("email", ""))
    st.markdown(
        f'<p style="text-align:right;font-family:\'Share Tech Mono\',monospace;'
        f'font-size:0.7rem;color:#8a5555;margin:0;padding-top:0.35rem">{_email}</p>',
        unsafe_allow_html=True,
    )
    if st.button("LOGOUT", key="logout"):
        for k in ("token", "user", "selected_vehicle"):
            st.session_state.pop(k, None)
        st.switch_page("pages/Login.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
stats = session.fetch_admin_stats(_token)
if stats:
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["total_users"]}</div><div class="stat-label">Registered Users</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["total_vehicles"]}</div><div class="stat-label">Vehicles Tracked</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["total_predictions"]}</div><div class="stat-label">Analyses Run</div></div>', unsafe_allow_html=True)
else:
    st.error("Could not load stats.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Two-column layout: users left, system controls right ──────────────────────
col_users, col_sys = st.columns([3, 1], gap="large")

# ════════════════════════════════════════════════════════════════════════════
# LEFT — User Management
# ════════════════════════════════════════════════════════════════════════════
with col_users:
    st.markdown('<div class="section-label">// User Management</div>', unsafe_allow_html=True)

    search = st.text_input("", placeholder="Search by email or name…", key="user_search", label_visibility="collapsed")

    users = session.fetch_admin_users(_token)
    if users is None:
        st.error("Could not load users.")
    else:
        # Filter
        q = search.strip().lower()
        if q:
            users = [u for u in users if q in u["email"].lower()
                     or q in (u.get("full_name") or "").lower()
                     or q in (u.get("business_name") or "").lower()]

        st.markdown(f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.68rem;color:#6a3535;margin-bottom:0.8rem">{len(users)} USER(S) SHOWN</p>', unsafe_allow_html=True)

        for u in users:
            uid        = u["user_id"]
            is_self    = uid == _user.get("user_id")
            badge_cls  = f"badge-{u['account_type']}"  # Enum-constrained, safe
            display    = html.escape(u.get("business_name") or u.get("full_name") or "")
            joined     = (u.get("created_at") or "")[:10]
            confirm_key = f"confirm_del_{uid}"
            type_key    = f"type_sel_{uid}"

            # initialise the type selectbox state to current value
            if type_key not in st.session_state:
                st.session_state[type_key] = u["account_type"] if u["account_type"] != "admin" else "personal"

            st.markdown('<div class="user-row">', unsafe_allow_html=True)

            row_info, row_actions = st.columns([3, 2], gap="small")

            with row_info:
                st.markdown(
                    f'<div class="user-email">{html.escape(u["email"])}</div>'
                    f'{"<div class=\'user-name\'>" + display + "</div>" if display else ""}'
                    f'<div style="margin-top:0.35rem;display:flex;align-items:center;gap:0.5rem">'
                    f'<span class="badge {badge_cls}">{u["account_type"]}</span>'
                    f'<span class="user-meta">· {u["vehicle_count"]} vehicles · {u["prediction_count"]} analyses · joined {joined}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with row_actions:
                if not is_self and u["account_type"] != "admin":
                    # Account-type change
                    new_type = st.selectbox(
                        "Type",
                        options=["personal", "business"],
                        key=type_key,
                        label_visibility="collapsed",
                    )
                    if new_type != u["account_type"]:
                        if st.button("SAVE TYPE", key=f"save_type_{uid}"):
                            try:
                                r = session.patch(
                                    f"/admin/users/{uid}/account-type",
                                    token=_token,
                                    json={"account_type": new_type},
                                )
                                r.raise_for_status()
                                terr = None
                            except Exception as e:
                                terr = str(e)
                            if terr:
                                st.error(terr)
                            else:
                                session.fetch_admin_users.clear()
                                st.success("Account type updated.")
                                st.rerun()

                    # Delete flow
                    if confirm_key not in st.session_state:
                        if st.button("DELETE USER", key=f"del_{uid}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning(f"Delete **{u['email']}** and all their data?")
                        cy, cn = st.columns(2)
                        with cy:
                            if st.button("YES, DELETE", key=f"conf_{uid}"):
                                try:
                                    r = session.delete(f"/admin/users/{uid}", token=_token)
                                    ok = r.status_code == 204
                                    derr = None if ok else r.json().get("detail", "Error")
                                except Exception as e:
                                    ok = False
                                    derr = str(e)
                                st.session_state.pop(confirm_key, None)
                                if ok:
                                    session.fetch_admin_users.clear()
                                    session.fetch_admin_stats.clear()
                                    st.success("User deleted.")
                                    st.rerun()
                                else:
                                    st.error(derr)
                        with cn:
                            if st.button("CANCEL", key=f"canc_{uid}"):
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
                else:
                    if is_self:
                        st.markdown('<span class="user-meta" style="color:#e53535">← YOU</span>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# RIGHT — System Controls
# ════════════════════════════════════════════════════════════════════════════
with col_sys:
    # DB Health
    st.markdown('<div class="section-label">// System Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="sys-card">', unsafe_allow_html=True)
    if session.check_db():
        st.markdown('<p class="status-ok">● DATABASE ONLINE</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-err">● DATABASE OFFLINE</p>', unsafe_allow_html=True)

    if session.check_health():
        st.markdown('<p class="status-ok">● API ONLINE</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-err">● API OFFLINE</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Model retraining
    st.markdown('<div class="section-label">// ML Models</div>', unsafe_allow_html=True)
    st.markdown('<div class="sys-card">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:#8a5555;margin-bottom:1rem">'
        'Triggers a background retrain of all three RandomForest models '
        '(engine, drivetrain, electrical). Takes several minutes. '
        'The API continues serving existing models until retraining completes.'
        '</p>',
        unsafe_allow_html=True,
    )
    if st.button("⚡ RETRAIN MODELS", key="retrain"):
        with st.spinner("Submitting retrain job…"):
            try:
                r = session.post("/retrain", token=_token)
                r.raise_for_status()
                result = r.json()
                rerr = None
            except Exception as e:
                result = None
                rerr = str(e)
        if rerr:
            st.error(f"Retrain failed: {rerr}")
        else:
            st.success(result.get("message", "Retrain job accepted."))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick nav
    st.markdown('<div class="section-label">// Navigation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sys-card">', unsafe_allow_html=True)
    if st.button("← BACK TO MAIN APP", key="goto_home"):
        st.switch_page("pages/Home.py")
    st.markdown('</div>', unsafe_allow_html=True)
