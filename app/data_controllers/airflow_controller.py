from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config.config import Config
from app.constants.constants import AirflowStateMap

logger = logging.getLogger(__name__)


class AirflowController:
    """Thin async client for Airflow REST API (v2)."""

    def __init__(self) -> None:
        self._root = Config.AIRFLOW_API_URL.rstrip("/")
        self._api_v2 = f"{self._root}/api/v2"
        self._username = Config.AIRFLOW_USERNAME
        self._password = Config.AIRFLOW_PASSWORD

    @staticmethod
    def _headers(token: str | None = None) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _request_with_auth(
        self,
        method: str,
        url: str,
        *,
        timeout: int,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Send request using bearer token first, then fallback to basic auth."""
        token_error: Exception | None = None

        try:
            token = await self._get_token()
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method,
                    url,
                    headers=self._headers(token),
                    params=params,
                    json=json,
                )
                response.raise_for_status()
                return response
        except Exception as exc:
            token_error = exc
            logger.info("Bearer token auth failed for %s %s: %s", method, url, exc)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method,
                    url,
                    headers=self._headers(),
                    auth=(self._username, self._password),
                    params=params,
                    json=json,
                )
                response.raise_for_status()
                return response
        except Exception as basic_exc:
            logger.warning(
                "Basic auth failed for %s %s: %s (token error: %s)",
                method,
                url,
                basic_exc,
                token_error,
            )
            raise RuntimeError(
                "Failed Airflow API auth via token and basic auth"
            ) from basic_exc

    async def _get_token(self) -> str:
        """Fetch access token from Airflow auth endpoint using common payload styles."""
        attempts: list[dict[str, Any]] = [
            {
                "json": {"username": self._username, "password": self._password},
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            },
            {
                "data": {"username": self._username, "password": self._password},
                "headers": {"Accept": "application/json"},
            },
            {
                "data": {
                    "grant_type": "password",
                    "username": self._username,
                    "password": self._password,
                },
                "headers": {"Accept": "application/json"},
            },
            {
                "auth": (self._username, self._password),
                "headers": {"Accept": "application/json"},
            },
        ]

        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=10) as client:
            for payload in attempts:
                try:
                    response = await client.post(f"{self._root}/auth/token", **payload)
                    if response.status_code >= 400:
                        last_error = httpx.HTTPStatusError(
                            f"Token request failed with {response.status_code}: {response.text}",
                            request=response.request,
                            response=response,
                        )
                        continue

                    data = response.json()
                    token = data.get("access_token") or data.get("token")
                    if token:
                        return token
                    last_error = ValueError(
                        "Airflow token response did not include access token"
                    )
                except Exception as exc:
                    last_error = exc

        raise RuntimeError("Failed to obtain Airflow auth token") from last_error

    async def trigger_dag(self, dag_id: str, conf: dict[str, Any]) -> dict[str, Any]:
        """Trigger DAG run in Airflow and return response JSON."""
        payload = {
            "logical_date": datetime.now(timezone.utc).isoformat(),
            "conf": conf,
        }

        response = await self._request_with_auth(
            "POST",
            f"{self._api_v2}/dags/{dag_id}/dagRuns",
            timeout=30,
            json=payload,
        )
        return response.json()

    async def get_dag_run(self, dag_id: str, dag_run_id: str) -> dict[str, Any]:
        """Get a specific DAG run by dag_run_id."""
        response = await self._request_with_auth(
            "GET",
            f"{self._api_v2}/dags/{dag_id}/dagRuns/{dag_run_id}",
            timeout=30,
        )
        return response.json()

    async def list_dag_runs(
        self,
        dag_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List recent DAG runs for a DAG."""
        response = await self._request_with_auth(
            "GET",
            f"{self._api_v2}/dags/{dag_id}/dagRuns",
            timeout=30,
            params={
                "limit": limit,
                "offset": offset,
                "order_by": "-start_date",
            },
        )
        return response.json()

    async def health_check(self) -> bool:
        """Return True if Airflow monitor endpoint is healthy."""
        try:
            # First verify server is reachable regardless of auth mode.
            async with httpx.AsyncClient(timeout=10) as client:
                version_resp = await client.get(f"{self._api_v2}/version")
                if version_resp.status_code >= 500:
                    return False

            response = await self._request_with_auth(
                "GET",
                f"{self._api_v2}/monitor/health",
                timeout=10,
            )
            return response.status_code == 200
        except Exception as exc:
            logger.warning("Airflow health check failed: %s", exc)
            return False

    @staticmethod
    def map_state(airflow_state: str | None) -> str:
        return AirflowStateMap.MAP.get((airflow_state or "").lower(), "pending")
