import streamlit as st

from src.api import APIClient, APIError
from src.auth import ensure_session_state_keys, set_session_user
from src.config import API_BASE_URL, AUTH_LOGIN_PATH, AUTH_ME_PATH

st.set_page_config(page_title="Login", layout="centered")

ensure_session_state_keys()
api = APIClient(API_BASE_URL)

st.title("Login")

# Si ya hay sesión en memoria, manda a Dashboard
if st.session_state.get("token") and st.session_state.get("user"):
    st.info("Already logged in. Redirecting to Dashboard...")
    st.switch_page("pages/3_Dashboard.py")

with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit:
    if not email or not password:
        st.error("Email and password are required.")
        st.stop()

    try:
        login_res = api.post_json(
            AUTH_LOGIN_PATH, {"email": email, "password": password}
        )

        token = login_res.get("access_token")
        if not token:
            st.error("Login response missing access_token. Check the backend.")
            st.stop()

        # Load user with Bearer
        me = api.get_json(AUTH_ME_PATH, token=token)

        set_session_user(me, token)

        st.success("Logged in successfully.")
        st.switch_page("pages/3_Dashboard.py")

    except APIError as e:
        st.error(f"Login failed ({e.status_code}): {e.detail}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
