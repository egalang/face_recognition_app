from __future__ import annotations

from typing import Any

import requests

from app.core.config import settings


class OdooClient:
    def __init__(self) -> None:
        self.base_url = settings.odoo_base_url.rstrip("/")
        self.timeout = settings.odoo_timeout_seconds
        self.token = settings.odoo_access_token

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def fetch_students(self, limit: int = 5000, offset: int = 0) -> dict[str, Any]:
        url = f"{self.base_url}{settings.odoo_student_sync_endpoint}"
        response = requests.get(
            url,
            params={"limit": limit, "offset": offset},
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def log_attendance(self, enrollment_id: int, action: str) -> dict[str, Any]:
        url = f"{self.base_url}{settings.odoo_attendance_log_endpoint}"
        response = requests.post(
            url,
            json={"enrollment_id": enrollment_id, "log_type": action},
            headers={**self._headers(), "Content-Type": "application/json"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
