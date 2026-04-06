"""
Predictive Vehicle Maintenance - Results Page
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Vehicle Health Results",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "results" not in st.session_state:
    st.switch_page("Vehicle_Input.py")

results = st.session_state["results"]
label   = st.session_state.get("vehicle_label", "Your Vehicle")

dt = results["drivetrain"]
el = results["electrical"]
en = results["engine"]
overall = results["overall_avg"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: #0a0e1a; color: #c8d8e8; }
.stApp { background: #0a0e1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.overall-card { background: linear-gradient(135deg, #0f1628 0%, #0d1f35 100%); border: 1px solid #1e3a5f; border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; position: relative; overflow: hidden; }
.overall-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.overall-vehicle { font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: #5a7a9a; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.3rem; }
.overall-title { font-size: 2rem; font-weight: 700; color: #c8d8e8; letter-spacing: 0.05em; }
.overall-score-wrap { text-align: right; }
.overall-score { font-family: 'Share Tech Mono', monospace; font-size: 4rem; font-weight: 700; line-height: 1; }
.overall-label { font-size: 0.75rem; letter-spacing: 0.2em; text-transform: uppercase; color: #5a7a9a; margin-top: 0.2rem; }
.sys-card { background: linear-gradient(135deg, #0f1628 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 1.5rem; margin-bottom: 0.5rem; position: relative; overflow: hidden; }
.sys-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.sys-card-engine::before { background: linear-gradient(90deg, transparent, #f59e0b, transparent); }
.sys-card-drive::before  { background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.sys-card-elec::before   { background: linear-gradient(90deg, transparent, #a78bfa, transparent); }
.sys-title { font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.3rem; }
.sys-avg { font-size: 2.2rem; font-weight: 700; font-family: 'Share Tech Mono', monospace; line-height: 1; margin-bottom: 1rem; }
.comp-row { margin-bottom: 0.8rem; }
.comp-header { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.3rem; color: #8aabcc; }
.comp-name { font-weight: 600; letter-spacing: 0.05em; }
.comp-score { font-family: 'Share Tech Mono', monospace; }
.comp-bar-bg { background: #0d1526; border-radius: 4px; height: 6px; overflow: hidden; border: 1px solid #1e3a5f; }
.comp-bar-fill { height: 100%; border-radius: 4px; }
.rec-card { background: #0f1628; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem; border-left: 3px solid; display: flex; align-items: flex-start; gap: 0.8rem; }
.rec-icon { font-size: 1.1rem; margin-top: 0.1rem; }
.rec-system { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.2rem; }
.rec-text { font-size: 0.9rem; color: #c8d8e8; line-height: 1.4; }
.section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #00d4ff; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 1rem; }
.stButton > button { background: transparent !important; border: 1px solid #1e3a5f !important; color: #5a7a9a !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.8rem !important; letter-spacing: 0.1em !important; border-radius: 8px !important; }
.stButton > button:hover { border-color: #00d4ff !important; color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def score_color(s):
    if s >= 65: return "#00ff88"
    elif s >= 40: return "#f59e0b"
    else: return "#ef4444"

def status_text(s):
    if s >= 65: return "GOOD"
    elif s >= 40: return "MONITOR"
    else: return "SERVICE SOON"

def bar_color(s):
    if s >= 65: return "#00ff88"
    elif s >= 40: return "#f59e0b"
    else: return "#ef4444"

def render_system_card(title, title_color, card_class, avg, avg_color, components):
    """Render system card header and component bars as one self-contained block."""
    bars_html = ""
    for name, score in components:
        color = bar_color(score)
        pct   = min(100, max(0, score))
        bars_html += f"""
        <div class="comp-row">
            <div class="comp-header">
                <span class="comp-name">{name}</span>
                <span class="comp-score" style="color:{color}">{score:.1f}</span>
            </div>
            <div class="comp-bar-bg">
                <div class="comp-bar-fill" style="width:{pct}%;background:{color}"></div>
            </div>
        </div>"""

    st.markdown(f"""
        <div class="sys-card {card_class}">
            <div class="sys-title" style="color:{title_color}">{title}</div>
            <div class="sys-avg" style="color:{avg_color}">{avg:.0f}<span style="font-size:1rem;color:#3a5a7a">/100</span></div>
            {bars_html}
        </div>
    """, unsafe_allow_html=True)

def gauge_fig(value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"font": {"size": 36, "color": color, "family": "Share Tech Mono"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#1e3a5f", "tickwidth": 1,
                     "tickfont": {"color": "#3a5a7a", "size": 10}},
            "bar":  {"color": color, "thickness": 0.25},
            "bgcolor": "#0d1526",
            "bordercolor": "#1e3a5f",
            "steps": [
                {"range": [0,  40], "color": "#1a0a0a"},
                {"range": [40, 65], "color": "#1a1500"},
                {"range": [65, 100], "color": "#0a1a0f"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.8, "value": value},
        },
    ))
    fig.update_layout(
        height=200, margin=dict(t=20, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#c8d8e8"},
    )
    return fig

def get_recommendations(dt, el, en):
    recs = []
    checks = [
        (dt["cv_wellness"],       "DRIVETRAIN", "CV Joints",      "CV joints are worn. Inspect for clicking sounds during turns.",       "#00d4ff"),
        (dt["wb_wellness"],       "DRIVETRAIN", "Wheel Bearings", "Wheel bearings degraded. Listen for humming at highway speed.",       "#00d4ff"),
        (dt["brk_wellness"],      "DRIVETRAIN", "Brakes",         "Brake system needs attention. Schedule inspection immediately.",      "#00d4ff"),
        (el["bat_wellness"],      "ELECTRICAL", "Battery",        "Battery health low. Consider replacement before cold season.",        "#a78bfa"),
        (el["alt_wellness"],      "ELECTRICAL", "Alternator",     "Alternator output low. Monitor charging voltage.",                    "#a78bfa"),
        (el["sta_wellness"],      "ELECTRICAL", "Starter",        "Starter motor worn. Watch for slow cranking on startup.",             "#a78bfa"),
        (en["coolant_wellness"],  "ENGINE",     "Coolant System", "Coolant system degraded. Schedule a flush and inspection.",           "#f59e0b"),
        (en["ignition_wellness"], "ENGINE",     "Ignition",       "Ignition system worn. Replace spark plugs and check coils.",          "#f59e0b"),
        (en["fuel_wellness"],     "ENGINE",     "Fuel System",    "Fuel system needs attention. Inspect injectors and fuel pump.",       "#f59e0b"),
    ]
    for score, system, component, msg, color in checks:
        if score < 40:
            recs.append(("🔴", system, component, msg, "#ef4444", color))
        elif score < 65:
            recs.append(("🟡", system, component, f"{component} showing wear. {msg}", "#f59e0b", color))
    if not recs:
        recs.append(("🟢", "ALL SYSTEMS", "Overall", "Vehicle health looks great. Keep up with regular maintenance intervals.", "#00ff88", "#00ff88"))
    return recs

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

if st.button("← NEW ANALYSIS"):
    st.switch_page("Vehicle_Input.py")

ov_color  = score_color(overall)
ov_status = status_text(overall)

st.markdown(f"""
<div class="overall-card">
    <div>
        <div class="overall-vehicle">// Diagnostic Report</div>
        <div class="overall-title">{label}</div>
        <div style="margin-top:0.5rem;font-size:0.85rem;color:{ov_color};font-family:'Share Tech Mono',monospace;letter-spacing:0.15em;">
            ● {ov_status}
        </div>
    </div>
    <div class="overall-score-wrap">
        <div class="overall-score" style="color:{ov_color}">{overall:.0f}</div>
        <div class="overall-label">Overall Health</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">// System Analysis</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    en_color = score_color(en["system_avg"])
    render_system_card("// Engine", "#f59e0b", "sys-card-engine", en["system_avg"], en_color, [
        ("Coolant System", en["coolant_wellness"]),
        ("Ignition",       en["ignition_wellness"]),
        ("Fuel System",    en["fuel_wellness"]),
    ])
    st.plotly_chart(gauge_fig(en["system_avg"], en_color), use_container_width=True)

with col2:
    dt_color = score_color(dt["system_avg"])
    render_system_card("// Drivetrain", "#00d4ff", "sys-card-drive", dt["system_avg"], dt_color, [
        ("CV Joints",      dt["cv_wellness"]),
        ("Wheel Bearings", dt["wb_wellness"]),
        ("Brakes",         dt["brk_wellness"]),
    ])
    st.plotly_chart(gauge_fig(dt["system_avg"], dt_color), use_container_width=True)

with col3:
    el_color = score_color(el["system_avg"])
    render_system_card("// Electrical", "#a78bfa", "sys-card-elec", el["system_avg"], el_color, [
        ("Battery",    el["bat_wellness"]),
        ("Alternator", el["alt_wellness"]),
        ("Starter",    el["sta_wellness"]),
    ])
    st.plotly_chart(gauge_fig(el["system_avg"], el_color), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">// Maintenance Recommendations</div>', unsafe_allow_html=True)

recs     = get_recommendations(dt, el, en)
rec_cols = st.columns(2, gap="medium")

for i, (icon, system, component, msg, alert_color, sys_color) in enumerate(recs):
    with rec_cols[i % 2]:
        st.markdown(f"""
        <div class="rec-card" style="border-color:{alert_color}">
            <div class="rec-icon">{icon}</div>
            <div>
                <div class="rec-system" style="color:{sys_color}">{system} — {component}</div>
                <div class="rec-text">{msg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)