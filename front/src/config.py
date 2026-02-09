from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

AUTH_REGISTER_PATH = "/auth/register"
AUTH_LOGIN_PATH = "/auth/login"
AUTH_ME_PATH = "/auth/me"
AUTH_LOGOUT_PATH = "/auth/logout"

PREDICT_PATH = "/predict"
PREDICTION_FEEDBACK_PATH = "/predictions/{prediction_id}/feedback"
