import io

import streamlit as st
from PIL import Image

from src.api import APIClient, APIError
from src.auth import (
    ensure_session_state_keys,
    require_auth,
    set_session_user,
    logout_local,
)
from src.config import (
    API_BASE_URL,
    AUTH_ME_PATH,
    AUTH_LOGOUT_PATH,
    PREDICT_PATH,
    PREDICTION_FEEDBACK_PATH,
)

st.set_page_config(page_title="Image Prediction Model", layout="centered")


def fit_image_bytes(img_bytes: bytes, max_size: tuple[int, int] = (120, 120)) -> bytes:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    img.thumbnail(max_size)
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def _ensure_local_state() -> None:
    st.session_state.setdefault("uploaded_image_bytes", None)
    st.session_state.setdefault("uploaded_image_name", None)
    st.session_state.setdefault("marbling_class", None)
    st.session_state.setdefault("prediction_result", None)

    # Feedback
    st.session_state.setdefault("agree_with_ai", None)
    st.session_state.setdefault("confidence_level", 3)
    st.session_state.setdefault("ai_helpfulness", 3)

    st.session_state.setdefault("feedback_submitted", False)
    st.session_state.setdefault("feedback_submit_error", None)


def _on_upload_change() -> None:
    f = st.session_state.get("uploader_file")
    if not f:
        return
    st.session_state["uploaded_image_bytes"] = f.getvalue()
    st.session_state["uploaded_image_name"] = f.name
    st.session_state["prediction_result"] = None
    st.session_state["feedback_submitted"] = False
    st.session_state["feedback_submit_error"] = None


def _reset_workflow() -> None:
    for key in [
        "uploaded_image_bytes",
        "uploaded_image_name",
        "uploader_file",
        "marbling_class",
        "prediction_result",
        "agree_with_ai",
        "confidence_level",
        "ai_helpfulness",
        "feedback_submitted",
        "feedback_submit_error",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def _guess_content_type(filename: str) -> str:
    name = filename.lower()
    if name.endswith(".png"):
        return "image/png"
    if name.endswith(".jpg") or name.endswith(".jpeg"):
        return "image/jpeg"
    if name.endswith(".webp"):
        return "image/webp"
    return "application/octet-stream"


# Auth bootstrap
ensure_session_state_keys()
_ensure_local_state()

api = APIClient(API_BASE_URL)
token = st.session_state.get("token")

if token and not st.session_state.get("user"):
    try:
        me = api.get_json(AUTH_ME_PATH, token=token)
        set_session_user(me, token)
    except APIError:
        set_session_user(None, None)

require_auth()

user = st.session_state["user"]
display_name = (user.get("full_name") or user.get("email") or "User").strip()

# Header
header_left, header_right = st.columns([1.5, 0.25], vertical_alignment="center")
with header_left:
    st.markdown(f"Welcome, {display_name}")
    st.caption("### Image Prediction Model")
with header_right:
    if st.button("Sign out"):
        try:
            api.post_empty(AUTH_LOGOUT_PATH, token=token)
        except Exception:
            pass
        logout_local()

st.divider()

st.markdown("#### Upload an image to run a prediction")
st.write(
    "This page sends your image to the prediction API and displays the predicted label with confidence."
)

raw_bytes: bytes | None = st.session_state.get("uploaded_image_bytes")
filename: str | None = st.session_state.get("uploaded_image_name")
result: dict | None = st.session_state.get("prediction_result")

has_image = raw_bytes is not None
has_result = result is not None

# MAIN
with st.container(border=True):
    # Estado 1: no hay imagen todavía
    if not has_image:
        st.markdown("**Upload**")
        st.file_uploader(
            "Choose an image file",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            label_visibility="collapsed",
            key="uploader_file",
            on_change=_on_upload_change,
        )
        st.caption("Tip: keep images under a few MB for faster uploads.")

    # Estado 2: hay resultado -> ocultar todo lo anterior y mostrar solo resultado + start over
    elif has_result:
        st.markdown("#### Result")

        left, right = st.columns([1.1, 1.4], vertical_alignment="top")

        with left:
            image_url = result.get("image_url")
            if image_url:
                st.image(image_url, caption="Original image", width="stretch")
            else:
                st.image(raw_bytes, caption="Original image", width="stretch")

        with right:
            st.markdown("**Prediction**")
            st.write(f"Label: {result.get('predicted_label')}")
            conf = result.get("confidence")
            if isinstance(conf, (int, float)):
                st.write(f"Confidence: {conf:.2%}")
                st.progress(min(max(float(conf), 0.0), 1.0))
            else:
                st.write(f"Confidence: {conf}")

            st.caption(f"Record id: {result.get('id')}")
            st.caption(f"Created at: {result.get('created_at')}")

        with st.expander("View raw response"):
            st.json(result)

        st.markdown("#### Feedback")

        # Pregunta 1
        st.radio(
            "Do you agree with the AI prediction?",
            options=["Yes", "No"],
            index=None,
            key="agree_with_ai",
        )

        # Pregunta 2
        st.markdown("**How confident are you in your final answer?**")
        st.slider(
            "Confidence level",
            min_value=1,
            max_value=5,
            step=1,
            key="confidence_level",
            label_visibility="collapsed",
        )

        # Pregunta 3
        st.markdown("**How helpful was the AI for this image?**")
        st.slider(
            "AI helpfulness",
            min_value=1,
            max_value=5,
            step=1,
            key="ai_helpfulness",
            label_visibility="collapsed",
        )

        # --- Submit feedback ---
        prediction_id = result.get("id")

        agree = st.session_state.get("agree_with_ai")  # "Yes" | "No" | None
        student_confidence = int(st.session_state.get("confidence_level") or 3)
        helpfulness_rating = int(st.session_state.get("ai_helpfulness") or 3)

        can_submit_feedback = (
            bool(prediction_id)
            and agree in ("Yes", "No")
            and 1 <= student_confidence <= 5
            and 1 <= helpfulness_rating <= 5
            and not st.session_state.get("feedback_submitted", False)
        )

        if st.session_state.get("feedback_submit_error"):
            st.error(st.session_state["feedback_submit_error"])

        if st.button("Submit feedback", disabled=not can_submit_feedback):
            try:
                payload = {
                    # 1 = Yes, 0 = No
                    "agree_with_model": 1 if agree == "Yes" else 0,
                    "student_confidence": student_confidence,
                    "helpfulness_rating": helpfulness_rating,
                }

                path = PREDICTION_FEEDBACK_PATH.format(prediction_id=prediction_id)
                api.post_json(path, payload, token=token)

                st.session_state["feedback_submitted"] = True
                st.session_state["feedback_submit_error"] = None
                st.success("Feedback submitted.")
                st.rerun()

            except APIError as e:
                st.session_state["feedback_submit_error"] = (
                    f"Feedback failed ({e.status_code}): {e.detail}"
                )
                st.rerun()
            except Exception as e:
                st.session_state["feedback_submit_error"] = f"Unexpected error: {e}"
                st.rerun()

        if st.session_state.get("feedback_submitted"):
            st.success("Feedback recorded. Thank you!")

        st.divider()

        # Nuevo botón: reiniciar flujo
        if st.button("Start over"):
            _reset_workflow()

    # Estado 3: hay imagen pero aún no hay resultado -> muestra preview + marbling + botones
    else:
        filename = filename or "image"
        fitted_png = fit_image_bytes(raw_bytes, (120, 120))

        # Contenedor 1: imagen + texto
        with st.container(border=True):
            left, right = st.columns([0.6, 1.4], vertical_alignment="center")

            with left:
                st.markdown(
                    "<div style='display:flex; justify-content:center; align-items:center; width:100%;'>",
                    unsafe_allow_html=True,
                )
                st.image(fitted_png, width=120)
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                st.markdown(
                    "This image will be analysed using AI to calculate marbling score."
                )

        # Contenedor 2: pregunta + opciones
        with st.container(border=True):
            st.markdown("**What marbling class belongs to your image?**")

            options = [
                "High Prime",
                "Average Prime",
                "Low Prime",
                "High Choice",
                "Average Choice",
                "Low Choice",
                "High Select",
                "Low Select",
                "High Standard",
            ]

            st.radio(
                label="Marbling class",
                options=options,
                index=None,
                label_visibility="collapsed",
                key="marbling_class",
            )

        # Acciones
        cols = st.columns([1, 1, 2])

        with cols[0]:
            if st.button("Change image"):
                _reset_workflow()

        with cols[1]:
            can_predict = st.session_state.get("marbling_class") is not None
            if st.button("Run prediction", disabled=not can_predict):
                try:
                    content_type = _guess_content_type(filename)
                    res = api.post_file(
                        PREDICT_PATH,
                        file_field="file",
                        filename=filename,
                        content=raw_bytes,
                        content_type=content_type,
                        token=token,
                    )
                    st.session_state["prediction_result"] = res
                    st.success("Prediction completed.")
                    st.rerun()
                except APIError as e:
                    st.error(f"Prediction failed ({e.status_code}): {e.detail}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
