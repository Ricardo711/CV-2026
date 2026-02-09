from __future__ import annotations

import streamlit as st


def ensure_session_state_keys() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("user", None)


def set_session_user(user: dict | None, token: str | None) -> None:
    st.session_state["user"] = user
    st.session_state["token"] = token


def is_authenticated() -> bool:
    return bool(st.session_state.get("token")) and bool(st.session_state.get("user"))


def require_auth(redirect_page: str = "pages/1_Login.py") -> None:
    ensure_session_state_keys()
    if not is_authenticated():
        st.switch_page(redirect_page)


def logout_local(redirect_page: str = "pages/1_Login.py") -> None:
    """
    Logout real para Streamlit: limpia el estado local.
    """
    ensure_session_state_keys()
    st.session_state["token"] = None
    st.session_state["user"] = None
    st.switch_page(redirect_page)
    st.stop()
