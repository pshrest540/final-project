import html
import streamlit as st
import session

st.set_page_config(
    page_title="Account — MIA",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_fresh = session.fetch_current_user(st.session_state["token"])
if _fresh:
    st.session_state["user"] = _fresh

_token  = st.session_state["token"]
_user   = st.session_state.get("user", {})
_is_biz = isinstance(_user, dict) and _user.get("account_type") == "business"

# ── Theme tokens ──────────────────────────────────────────────────────────────
_bg     = "#f0f4f8"  if _is_biz else "#070707"
_accent = "#0066b3"  if _is_biz else "#ffffff"
_fg     = "#1a2a3a"  if _is_biz else "#f0f0f0"
_fg2    = "#4a6a8a"  if _is_biz else "#555555"
_border = "#d0dce8"  if _is_biz else "#1e1e1e"
_card_g = "#ffffff"  if _is_biz else "#0c0c0c"
_inp_bg = "#f8fafc"  if _is_biz else "#111111"
_btn_g  = "linear-gradient(135deg,#0066b3 0%,#004d8c 100%)" if _is_biz else "#f5f5f5"
_btn_c  = "#ffffff"  if _is_biz else "#080808"
_shadow = "rgba(0,102,179,0.25)" if _is_biz else "rgba(255,255,255,0.07)"
_top    = f"linear-gradient(90deg,transparent,{_accent},transparent)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Rajdhani', sans-serif; background-color: {_bg}; color: {_fg}; }}
.stApp {{ background: {"radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%)" if not _is_biz else _bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 640px; }}
.section-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_accent}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.6rem; }}
.acct-card {{ background: {_card_g}; border: 1px solid {_border}; border-radius: 14px; padding: 1.8rem 2rem 1.5rem; margin: 0.5rem 0 1.2rem; position: relative; overflow: hidden; }}
.acct-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: {_top}; }}
.acct-email {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: {_fg2}; letter-spacing: 0.12em; margin-bottom: 0.2rem; }}
.acct-name {{ font-size: 1.6rem; font-weight: 700; color: {_fg}; margin-bottom: 0.2rem; }}
.acct-type {{ font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: {_accent}; letter-spacing: 0.2em; }}
.danger-card {{ background: {"rgba(239,68,68,0.04)" if _is_biz else "rgba(239,68,68,0.06)"}; border: 1px solid {"#fca5a5" if _is_biz else "#3a0f0f"}; border-radius: 14px; padding: 1.5rem 2rem; margin-top: 1.5rem; }}
.danger-title {{ font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #ef4444; letter-spacing: 0.2em; margin-bottom: 0.6rem; }}
.divider {{ height: 1px; background: linear-gradient(90deg,{_accent} 0%,transparent 60%); margin: 0.3rem 0 1.2rem; opacity: 0.2; }}
.stButton > button {{ background: {_btn_g} !important; color: {_btn_c} !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; box-shadow: 0 0 15px {_shadow} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _col_title = st.columns([1, 5])
with _col_back:
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/Home.py")
with _col_title:
    st.markdown('<div class="section-label" style="margin-top:0.5rem">ACCOUNT SETTINGS</div>', unsafe_allow_html=True)

# ── Identity card ──────────────────────────────────────────────────────────────
_display_name = html.escape(
    (_user.get("business_name") or _user.get("full_name") or _user.get("email", ""))
    if isinstance(_user, dict) else ""
)
_acct_type_label = _user.get("account_type", "personal").upper() if isinstance(_user, dict) else "PERSONAL"
_email_display = html.escape(_user.get("email", "") if isinstance(_user, dict) else "")

st.markdown(f"""
<div class="acct-card">
  <div class="acct-email">{_email_display}</div>
  <div class="acct-name">{_display_name}</div>
  <div class="acct-type">{_acct_type_label} ACCOUNT</div>
</div>
""", unsafe_allow_html=True)

# ── Update name ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">UPDATE NAME</div>', unsafe_allow_html=True)
with st.form("update_name_form", clear_on_submit=False):
    if _is_biz:
        new_biz_name = st.text_input(
            "Business name",
            value=_user.get("business_name") or "",
            max_chars=255,
        )
        name_submitted = st.form_submit_button("SAVE NAME", use_container_width=True, type="primary")
        if name_submitted:
            payload = {"business_name": new_biz_name.strip()}
            r = session.patch("/auth/me", token=_token, json=payload)
            if r.status_code == 200:
                updated = r.json()
                st.session_state["user"] = updated
                session.fetch_current_user.clear()
                st.success("Business name updated.")
                st.rerun()
            else:
                st.error(r.json().get("detail", r.text))
    else:
        new_full_name = st.text_input(
            "Full name",
            value=_user.get("full_name") or "",
            max_chars=255,
        )
        name_submitted = st.form_submit_button("SAVE NAME", use_container_width=True, type="primary")
        if name_submitted:
            payload = {"full_name": new_full_name.strip()}
            r = session.patch("/auth/me", token=_token, json=payload)
            if r.status_code == 200:
                updated = r.json()
                st.session_state["user"] = updated
                session.fetch_current_user.clear()
                st.success("Name updated.")
                st.rerun()
            else:
                st.error(r.json().get("detail", r.text))

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Change email ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">CHANGE EMAIL</div>', unsafe_allow_html=True)
with st.form("change_email_form", clear_on_submit=True):
    new_email        = st.text_input("New email address", placeholder="new@example.com")
    cur_pw_email     = st.text_input("Current password", type="password", key="cur_pw_email")
    email_submitted  = st.form_submit_button("UPDATE EMAIL", use_container_width=True, type="primary")
    if email_submitted:
        if not new_email.strip() or not cur_pw_email:
            st.error("Both fields are required.")
        else:
            payload = {"email": new_email.strip(), "current_password": cur_pw_email}
            r = session.patch("/auth/me", token=_token, json=payload)
            if r.status_code == 200:
                updated = r.json()
                st.session_state["user"] = updated
                session.fetch_current_user.clear()
                st.success("Email updated.")
                st.rerun()
            else:
                st.error(r.json().get("detail", r.text))

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Change password ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">CHANGE PASSWORD</div>', unsafe_allow_html=True)
with st.form("change_pw_form", clear_on_submit=True):
    cur_pw       = st.text_input("Current password", type="password", key="cur_pw_change")
    new_pw       = st.text_input("New password (8+ characters)", type="password", key="new_pw")
    confirm_pw   = st.text_input("Confirm new password", type="password", key="confirm_pw")
    pw_submitted = st.form_submit_button("UPDATE PASSWORD", use_container_width=True, type="primary")
    if pw_submitted:
        if not cur_pw or not new_pw or not confirm_pw:
            st.error("All fields are required.")
        elif new_pw != confirm_pw:
            st.error("New passwords do not match.")
        elif len(new_pw) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            payload = {"current_password": cur_pw, "new_password": new_pw}
            r = session.patch("/auth/me", token=_token, json=payload)
            if r.status_code == 200:
                st.success("Password updated.")
            else:
                st.error(r.json().get("detail", r.text))

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Logout ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">SESSION</div>', unsafe_allow_html=True)
if st.button("LOGOUT", use_container_width=True):
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)
    st.session_state.pop("selected_vehicle", None)
    st.switch_page("pages/Login.py")

# ── Danger zone ────────────────────────────────────────────────────────────────
st.markdown('<div class="danger-card">', unsafe_allow_html=True)
st.markdown('<div class="danger-title">DANGER ZONE</div>', unsafe_allow_html=True)
st.markdown(
    f'<p style="font-size:0.82rem;color:{_fg2};margin-bottom:1rem">Deleting your account is permanent. '
    f'All your vehicles, predictions, and service history will be erased.</p>',
    unsafe_allow_html=True,
)

if "confirm_delete_acct" not in st.session_state:
    st.session_state["confirm_delete_acct"] = False

if not st.session_state["confirm_delete_acct"]:
    if st.button("DELETE MY ACCOUNT", use_container_width=True):
        st.session_state["confirm_delete_acct"] = True
        st.rerun()
else:
    st.warning("This will permanently delete your account and all associated data.")
    with st.form("delete_acct_form", clear_on_submit=True):
        del_pw      = st.text_input("Enter your password to confirm", type="password", key="del_pw")
        del_confirm = st.form_submit_button("CONFIRM DELETE ACCOUNT", use_container_width=True)
        cancel_del  = st.form_submit_button("CANCEL")
        if cancel_del:
            st.session_state["confirm_delete_acct"] = False
            st.rerun()
        if del_confirm:
            if not del_pw:
                st.error("Password is required.")
            else:
                r = session.delete("/auth/me", token=_token, json={"current_password": del_pw})
                if r.status_code == 204:
                    st.session_state.clear()
                    st.switch_page("pages/Login.py")
                else:
                    st.error(r.json().get("detail", r.text))

st.markdown('</div>', unsafe_allow_html=True)
