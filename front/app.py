# app.py
# Streamlit demo frontend (NO backend) for a 3-screen calibration/uncertainty CV tutor.
# You can upload ANY image and walk through:
#   Screen 1: Student answer
#   Screen 2: Model feedback (C1/C2/C3)
#   Screen 3: Reflection + local log
#
# Run:
#   streamlit run app.py

import json
import time
import random
from dataclasses import dataclass
from typing import Optional, Dict, Any

import streamlit as st


# -----------------------------
# Config
# -----------------------------
APP_TITLE = "Calibration & Uncertainty Visual Tutor (Frontend Demo)"
CLASS_LABELS_DEFAULT = ["Very Low", "Low", "Moderate", "High", "Very High"]
CONDITIONS = ["C1", "C2", "C3"]  # C1: no confidence, C2: raw conf, C3: calibrated + uncertainty


# -----------------------------
# Demo "model" simulator (replace later with backend)
# -----------------------------
def demo_predict(class_labels):
    """
    Returns a fake prediction, confidence, and uncertainty to simulate the UI.
    """
    pred_label = random.choice(class_labels)
    confidence = random.uniform(0.35, 0.98)      # in [0,1]
    uncertainty = random.uniform(0.02, 0.45)     # arbitrary scale
    return {
        "predicted_label": pred_label,
        "confidence": float(confidence),
        "uncertainty": float(uncertainty),
        "calibration": "temperature_scaling (demo)",
        "model_version": "demo_model_v0",
    }


def format_model_feedback(condition: str, pred_label: str, confidence: Optional[float], uncertainty: Optional[float]) -> str:
    if condition == "C1":
        return f"The AI predicts: **{pred_label}**."
    if condition == "C2":
        conf_txt = "N/A" if confidence is None else f"{confidence * 100:.1f}%"
        return f"The AI predicts: **{pred_label}** (**{conf_txt}** confidence)."
    # C3
    conf_txt = "N/A" if confidence is None else f"{confidence * 100:.1f}%"
    unc_txt = "N/A" if uncertainty is None else f"{uncertainty:.3f}"
    return (
        f"The AI predicts: **{pred_label}**\n\n"
        f"- Calibrated confidence: **{conf_txt}**\n"
        f"- Uncertainty score: **{unc_txt}**\n\n"
        f"Interpretation: if confidence is low or uncertainty is high, treat the prediction cautiously."
    )


def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = 1  # 1,2,3 screens
    if "condition" not in st.session_state:
        st.session_state.condition = "C1"
    if "class_labels" not in st.session_state:
        st.session_state.class_labels = CLASS_LABELS_DEFAULT.copy()
    if "trial_started_at" not in st.session_state:
        st.session_state.trial_started_at = None
    if "data" not in st.session_state:
        st.session_state.data = {}  # stores answers + demo prediction + reflection
    if "logs" not in st.session_state:
        st.session_state.logs = []  # local session logs


def reset_trial():
    st.session_state.phase = 1
    st.session_state.trial_started_at = None
    st.session_state.data = {}


# -----------------------------
# UI
# -----------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_state()

    st.title(APP_TITLE)
    st.caption("This is a backend-free UI prototype to preview your 3-screen student flow.")

    with st.sidebar:
        st.header("Demo controls")

        # Condition selector (lets you preview each experimental condition)
        st.session_state.condition = st.selectbox(
            "Condition (UI treatment)",
            CONDITIONS,
            index=CONDITIONS.index(st.session_state.condition),
            help="C1: label only | C2: label + raw confidence | C3: calibrated confidence + uncertainty"
        )

        # Optional: edit class labels
        with st.expander("Class labels", expanded=False):
            labels_txt = st.text_area("One label per line", value="\n".join(st.session_state.class_labels), height=140)
            if st.button("Update labels"):
                new_labels = [ln.strip() for ln in labels_txt.splitlines() if ln.strip()]
                if len(new_labels) >= 2:
                    st.session_state.class_labels = new_labels
                    st.success("Labels updated.")
                else:
                    st.error("Provide at least 2 labels.")

        if st.button("Reset trial"):
            reset_trial()
            st.experimental_rerun()

    st.divider()

    # Upload any image
    uploaded = st.file_uploader("Upload any image to simulate a marbling task", type=["jpg", "jpeg", "png", "webp"])
    if uploaded:
        st.image(uploaded, caption=f"Uploaded: {uploaded.name}", use_container_width=True)
        st.session_state.data["image_name"] = uploaded.name
    else:
        st.info("Upload an image to start the 3-screen flow.")
        st.stop()

    # Initialize timing
    if st.session_state.trial_started_at is None:
        st.session_state.trial_started_at = time.time()

    # --------------------------------------
    # SCREEN 1 — Student Answer
    # --------------------------------------
    if st.session_state.phase == 1:
        st.subheader("Screen 1/3 — Your answer (before seeing AI)")

        student_answer = st.radio(
            "Select the marbling grade:",
            st.session_state.class_labels,
            index=0
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Submit answer →"):
                st.session_state.data["student_initial_answer"] = student_answer

                # simulate a model prediction for the demo UI
                pred = demo_predict(st.session_state.class_labels)
                st.session_state.data["predict"] = pred

                st.session_state.phase = 2
                st.experimental_rerun()

        with col2:
            st.caption("In your real study, the model prediction comes from your inference backend.")

    # --------------------------------------
    # SCREEN 2 — AI Feedback (condition-based)
    # --------------------------------------
    elif st.session_state.phase == 2:
        st.subheader("Screen 2/3 — AI feedback")

        pred = st.session_state.data.get("predict", {})
        pred_label = pred.get("predicted_label", "N/A")
        conf = pred.get("confidence")
        unc = pred.get("uncertainty")

        st.markdown(format_model_feedback(st.session_state.condition, pred_label, conf, unc))

        st.divider()
        st.write("You may revise your answer (optional).")
        initial = st.session_state.data.get("student_initial_answer", st.session_state.class_labels[0])

        final_answer = st.radio(
            "Final answer:",
            st.session_state.class_labels,
            index=st.session_state.class_labels.index(initial) if initial in st.session_state.class_labels else 0
        )
        st.session_state.data["student_final_answer"] = final_answer
        st.session_state.data["changed_answer"] = int(final_answer != initial)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back"):
                st.session_state.phase = 1
                st.experimental_rerun()
        with col2:
            if st.button("Continue →"):
                st.session_state.phase = 3
                st.experimental_rerun()

    # --------------------------------------
    # SCREEN 3 — Reflection + local log
    # --------------------------------------
    elif st.session_state.phase == 3:
        st.subheader("Screen 3/3 — Reflection")

        agree = st.radio("Do you agree with the AI prediction?", ["Yes", "No"], index=0)
        self_conf = st.slider("How confident are you in your final answer?", 1, 5, 3)
        helpful = st.slider("How helpful was the AI for this image?", 1, 5, 3)
        comment = st.text_area("Optional comment", value="", height=90)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Back"):
                st.session_state.phase = 2
                st.experimental_rerun()

        with col2:
            if st.button("Submit (save locally)"):
                ended_at = time.time()
                time_on_task = float(ended_at - st.session_state.trial_started_at)

                pred = st.session_state.data.get("predict", {})
                log = {
                    "condition": st.session_state.condition,
                    "image_name": st.session_state.data.get("image_name"),

                    "student_initial_answer": st.session_state.data.get("student_initial_answer"),
                    "student_final_answer": st.session_state.data.get("student_final_answer"),
                    "changed_answer": int(st.session_state.data.get("changed_answer", 0)),

                    "model_prediction": pred.get("predicted_label"),
                    "model_confidence": pred.get("confidence"),
                    "model_uncertainty": pred.get("uncertainty"),
                    "calibration": pred.get("calibration"),
                    "model_version": pred.get("model_version"),

                    "agree_with_model": 1 if agree == "Yes" else 0,
                    "student_confidence": int(self_conf),
                    "helpfulness_rating": int(helpful),
                    "comment": comment,

                    "time_on_task_seconds": round(time_on_task, 3),
                    "client_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                }

                st.session_state.logs.append(log)
                st.success("Saved locally (no backend). See the log below.")

        with col3:
            if st.button("New trial"):
                reset_trial()
                st.experimental_rerun()

        st.divider()
        st.write("### Latest log entry")
        if st.session_state.logs:
            st.json(st.session_state.logs[-1])

        st.write("### Download all logs (JSON)")
        st.download_button(
            "Download logs",
            data=json.dumps(st.session_state.logs, indent=2),
            file_name="demo_logs.json",
            mime="application/json",
        )

    else:
        st.error("Invalid state. Reset the trial from the sidebar.")


if __name__ == "__main__":
    main()
