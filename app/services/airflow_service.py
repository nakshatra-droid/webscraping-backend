from __future__ import annotations

import logging

import httpx
from fastapi import HTTPException, status

from app.config.config import Config
from app.constants.constants import AirflowConstants, ListingSources
from app.data_controllers.airflow_controller import AirflowController

logger = logging.getLogger(__name__)


class AirflowService:
    """Application service for Airflow DAG trigger operations."""

    def __init__(self) -> None:
        self.controller = AirflowController()

    async def _ensure_airflow_health(self) -> None:
        is_healthy = await self.controller.health_check()
        if not is_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Airflow is not reachable or authentication failed. "
                    "Verify AIRFLOW_API_URL, AIRFLOW_USERNAME, AIRFLOW_PASSWORD, "
                    "and ensure the Airflow API server is running."
                ),
            )

    async def trigger_scraping_run(
        self,
        source: str = ListingSources.AMAZON,
        dag_id: str | None = None,
        extra_conf: dict | None = None,
    ) -> dict:
        selected_source = (source or ListingSources.AMAZON).upper()
        if selected_source not in (ListingSources.AMAZON, ListingSources.FLIPKART):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="source must be either AMAZON or FLIPKART",
            )

        run_dag_id = (
            dag_id or Config.AIRFLOW_SCRAPER_DAG_ID or AirflowConstants.SCRAPER_DAG_ID
        )
        conf = {"source": selected_source, **(extra_conf or {})}

        await self._ensure_airflow_health()

        try:
            response = await self.controller.trigger_dag(run_dag_id, conf)
            airflow_state = response.get("state")
            return {
                "dag_id": run_dag_id,
                "dag_run_id": response.get("dag_run_id"),
                "logical_date": response.get("logical_date"),
                "source": selected_source,
                "airflow_state": airflow_state,
                "status": self.controller.map_state(airflow_state),
            }
        except httpx.HTTPStatusError as exc:
            logger.error("Airflow rejected scraping DAG trigger: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Airflow rejected scraper DAG trigger: {exc.response.text}",
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected error triggering scraping DAG")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to trigger scraper DAG: {str(exc)}",
            ) from exc

    async def trigger_embedding_run(
        self,
        dag_id: str | None = None,
        extra_conf: dict | None = None,
    ) -> dict:
        run_dag_id = (
            dag_id
            or Config.AIRFLOW_EMBEDDING_DAG_ID
            or AirflowConstants.EMBEDDING_DAG_ID
        )
        conf = extra_conf or {}

        await self._ensure_airflow_health()

        try:
            response = await self.controller.trigger_dag(run_dag_id, conf)
            airflow_state = response.get("state")
            return {
                "dag_id": run_dag_id,
                "dag_run_id": response.get("dag_run_id"),
                "logical_date": response.get("logical_date"),
                "airflow_state": airflow_state,
                "status": self.controller.map_state(airflow_state),
            }
        except httpx.HTTPStatusError as exc:
            logger.error("Airflow rejected embedding DAG trigger: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Airflow rejected embedding DAG trigger: {exc.response.text}",
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected error triggering embedding DAG")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to trigger embedding DAG: {str(exc)}",
            ) from exc
