"""
Shared HTTP session for all Streamlit pages.

Why this exists:
  - requests.get() opens a new TCP+TLS socket on every call (~150-400 ms overhead on HTTPS).
  - st.cache_resource stores a single requests.Session per Streamlit server process,
    so TCP connections are reused across all reruns and page navigations.
  - st.cache_data on each fetch function stores the last API response in memory so that
    widget interactions (slider moves etc.) do not trigger redundant HTTP calls.
"""

import os
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
import streamlit as st

API_BASE    = os.environ.get("API_BASE",    "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "120"))


# ── Connection-pooled session (one per server process, shared across all users) ──
@st.cache_resource(show_spinner=False)
def _session() -> requests.Session:
    s = requests.Session()
    adapter = HTTPAdapter(pool_connections=4, pool_maxsize=16)
    s.mount("https://", adapter)
    s.mount("http://",  adapter)
    return s


def _auth(token: Optional[str]) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


# ── Low-level verbs ───────────────────────────────────────────────────────────

def get(path: str, token: Optional[str] = None, **kw) -> requests.Response:
    return _session().get(f"{API_BASE}{path}", headers=_auth(token), timeout=API_TIMEOUT, **kw)

def post(path: str, token: Optional[str] = None, **kw) -> requests.Response:
    return _session().post(f"{API_BASE}{path}", headers=_auth(token), timeout=API_TIMEOUT, **kw)

def delete(path: str, token: Optional[str] = None, **kw) -> requests.Response:
    return _session().delete(f"{API_BASE}{path}", headers=_auth(token), timeout=API_TIMEOUT, **kw)

def patch(path: str, token: Optional[str] = None, **kw) -> requests.Response:
    return _session().patch(f"{API_BASE}{path}", headers=_auth(token), timeout=API_TIMEOUT, **kw)


# ── Cached fetches ────────────────────────────────────────────────────────────
# No-argument functions are global caches (all users share one entry).
# Functions that take `token` are per-user caches (token is unique per session).

@st.cache_data(ttl=30, show_spinner=False)
def check_health() -> bool:
    """Cached API liveness check — runs at most once every 30 s across all users."""
    try:
        return get("/health").status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=30, show_spinner=False)
def check_db() -> bool:
    try:
        return get("/db/health").status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=300, show_spinner=False)
def fetch_brands() -> Optional[list]:
    """Brand/model list — changes only when data files change, cache for 5 min."""
    try:
        r = get("/brands")
        r.raise_for_status()
        return r.json()["brands"]
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_current_user(token: str) -> Optional[dict]:
    try:
        r = get("/auth/me", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_vehicles(token: str) -> Optional[list]:
    try:
        r = get("/vehicles", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_linked_customers(token: str) -> Optional[list]:
    try:
        r = get("/sharing/customers", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_predictions(vehicle_id: str, token: str) -> Optional[list]:
    try:
        r = get(f"/vehicles/{vehicle_id}/predictions", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=15, show_spinner=False)
def fetch_admin_stats(token: str) -> Optional[dict]:
    try:
        r = get("/admin/stats", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=15, show_spinner=False)
def fetch_admin_users(token: str) -> Optional[list]:
    try:
        r = get("/admin/users", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_maintenance(vehicle_id: str, token: str) -> Optional[list]:
    try:
        r = get(f"/vehicles/{vehicle_id}/maintenance", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_replacements(vehicle_id: str, token: str) -> Optional[list]:
    try:
        r = get(f"/vehicles/{vehicle_id}/replacements", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_vehicle_service_log(vehicle_id: str, token: str) -> Optional[list]:
    try:
        r = get(f"/vehicles/{vehicle_id}/service-log", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=15, show_spinner=False)
def fetch_incoming_proposals(token: str) -> Optional[list]:
    try:
        r = get("/sharing/proposals/incoming", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=15, show_spinner=False)
def fetch_outgoing_proposals(token: str) -> Optional[list]:
    try:
        r = get("/sharing/proposals/outgoing", token=token)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
