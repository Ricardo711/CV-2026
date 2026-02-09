from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"APIError {status_code}: {detail}")


class APIClient:
    def __init__(self, base_url: str, timeout_s: float = 15.0):
        self.base_url = base_url
        self.timeout_s = timeout_s

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def post_json(
        self, path: str, payload: Dict[str, Any], token: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout_s) as client:
            r = client.post(url, json=payload, headers=self._headers(token))
        if r.status_code >= 400:
            raise APIError(r.status_code, self._extract_detail(r))
        return r.json() if r.content else {}

    def post_empty(self, path: str, token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout_s) as client:
            r = client.post(url, headers=self._headers(token))
        if r.status_code >= 400:
            raise APIError(r.status_code, self._extract_detail(r))
        return r.json() if r.content else {}

    def get_json(self, path: str, token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout_s) as client:
            r = client.get(url, headers=self._headers(token))
        if r.status_code >= 400:
            raise APIError(r.status_code, self._extract_detail(r))
        return r.json() if r.content else {}

    @staticmethod
    def _extract_detail(resp: httpx.Response) -> str:
        try:
            data = resp.json()
            if isinstance(data, dict):
                return str(data.get("detail") or data.get("message") or data)
            return str(data)
        except Exception:
            return resp.text or "Unknown error"

    def post_file(
        self,
        path: str,
        file_field: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        files = {
            file_field: (filename, content, content_type),
        }
        with httpx.Client(timeout=self.timeout_s) as client:
            r = client.post(url, files=files, headers=self._headers(token))
        if r.status_code >= 400:
            raise APIError(r.status_code, self._extract_detail(r))
        return r.json() if r.content else {}
