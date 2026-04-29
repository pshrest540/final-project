import streamlit as st
import session

st.set_page_config(
    page_title="Connect — VEHIDOC",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

_user   = st.session_state.get("user", {})
_is_biz = isinstance(_user, dict) and _user.get("account_type") == "business"
if _is_biz:
    st.switch_page("pages/Home.py")

_token = st.session_state["token"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #070707; color: #f0f0f0; }
.stApp { background: radial-gradient(ellipse 120% 50% at 50% 0%, #131313 0%, #070707 60%); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 520px; }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #ffffff; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.8rem; }
.code-card { background: #111111; border: 1px solid #2a2a2a; border-radius: 18px; padding: 2.5rem 2rem 2rem; margin: 1rem 0 1.5rem; position: relative; overflow: hidden; text-align: center; }
.code-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #ffffff, transparent); }
.code-label { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: #888888; letter-spacing: 0.3em; margin-bottom: 1.2rem; }
.code-value { font-family: 'Share Tech Mono', monospace; font-size: 4rem; font-weight: 700; color: #ffffff; letter-spacing: 0.55em; margin-right: -0.55em; line-height: 1; margin-bottom: 1rem; }
.code-timer { font-family: 'Share Tech Mono', monospace; font-size: 1.1rem; color: #888888; letter-spacing: 0.2em; margin-bottom: 0.4rem; }
.code-hint { font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: #666666; letter-spacing: 0.15em; margin-top: 0.8rem; }
.info-card { background: #111111; border: 1px dashed #383838; border-radius: 12px; padding: 1.2rem 1.4rem; margin-top: 1.2rem; }
.info-step { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #888888; letter-spacing: 0.1em; margin-bottom: 0.5rem; line-height: 1.6; }
.stButton > button { background: #f5f5f5 !important; color: #080808 !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1rem !important; text-transform: uppercase !important; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
_col_back, _col_title = st.columns([1, 4])
with _col_back:
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/Home.py")
with _col_title:
    st.markdown('<div class="section-label" style="margin-top:0.5rem">CONNECT WITH A BUSINESS</div>', unsafe_allow_html=True)

# ── Fetch code (auto-generates if expired or missing) ─────────────────────────
_data = None
_error = None
try:
    r = session.get("/pairing/me", token=_token)
    if r.status_code == 200:
        _data = r.json()
    else:
        _error = r.json().get("detail", "Could not load connection code.")
except Exception as e:
    _error = str(e)

if _error:
    st.error(f"Could not load connection code: {_error}")
    st.stop()

_code      = _data["code"]
_expires   = _data["expires_at"]  # ISO string from API

# ── Code display card with live JS countdown ──────────────────────────────────
st.markdown(f"""
<div class="code-card">
  <div class="code-label">YOUR CONNECTION CODE</div>
  <div class="code-value">{_code}</div>
  <div class="code-timer" id="code-countdown">--:--</div>
  <div class="code-hint">SHOW THIS TO YOUR SERVICE PROVIDER · SINGLE USE · EXPIRES IN 5 MIN</div>
</div>

<script>
(function() {{
    var expiresAt = new Date("{_expires}");
    function tick() {{
        var now = new Date();
        var remaining = Math.max(0, Math.floor((expiresAt - now) / 1000));
        var mins = Math.floor(remaining / 60);
        var secs = remaining % 60;
        var el = document.getElementById('code-countdown');
        if (!el) return;
        if (remaining === 0) {{
            el.textContent = 'EXPIRED — CLICK REFRESH BELOW';
            el.style.color = '#ef4444';
        }} else {{
            el.textContent = mins + ':' + String(secs).padStart(2, '0');
            el.style.color = '#888888';
        }}
    }}
    tick();
    setInterval(tick, 1000);
}})();
</script>
""", unsafe_allow_html=True)

# ── Refresh button ────────────────────────────────────────────────────────────
if st.button("↺  REFRESH CODE", use_container_width=True):
    try:
        r = session.post("/pairing/generate", token=_token)
        if r.status_code == 200:
            st.rerun()
        else:
            st.error(r.json().get("detail", "Could not refresh code."))
    except Exception as e:
        st.error(str(e))

# ── Instructions ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="info-card">
  <div class="info-step">1 · Give the 5-character code above to your service provider in person or over the phone.</div>
  <div class="info-step">2 · They enter it on their dashboard under ADD CUSTOMER.</div>
  <div class="info-step">3 · The code is valid for 5 minutes and can only be used once.</div>
  <div class="info-step">4 · Once connected, use the sharing toggle on each vehicle to control what they can see.</div>
</div>
""", unsafe_allow_html=True)
