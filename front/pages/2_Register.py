import streamlit as st

from src.api import APIClient, APIError
from src.config import API_BASE_URL, AUTH_REGISTER_PATH

st.set_page_config(page_title="Register", layout="centered")

api = APIClient(API_BASE_URL)

st.title("Register")

with st.form("register_form", clear_on_submit=False):
    full_name = st.text_input("Nombre", placeholder="Tu nombre")
    email = st.text_input("Email", placeholder="tu@email.com")
    password = st.text_input("Password", type="password")
    password2 = st.text_input("Confirmar password", type="password")
    submit = st.form_submit_button("Crear cuenta")

if submit:
    if not email or not password:
        st.error("Email y password son obligatorios.")
        st.stop()

    if password != password2:
        st.error("Los passwords no coinciden.")
        st.stop()

    payload = {"email": email, "password": password, "full_name": full_name}

    try:
        api.post_json(AUTH_REGISTER_PATH, payload)
        st.success("Usuario creado. Ahora inicia sesión.")
        st.switch_page("pages/1_Login.py")
    except APIError as e:
        if isinstance(e.detail, list):
            mensajes = []
            for err in e.detail:
                campo = err["loc"][-1]
                msg = err["msg"]
                mensajes.append(f"{campo}: {msg}")
            st.error("\n".join(mensajes))
        else:
            st.error(e.detail)

    except Exception as e:
        st.error(f"Error inesperado: {e}")
