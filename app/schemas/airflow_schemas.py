from typing import Any, Literal

from pydantic import BaseModel, Field


class ScrapingDagTriggerRequest(BaseModel):
    source: Literal["AMAZON", "FLIPKART"] = Field(
        default="AMAZON",
        description="Marketplace source to run in the scraper DAG.",
    )
    dag_id: str | None = Field(
        default=None,
        description="Optional DAG override. Defaults to configured scraper DAG ID.",
    )
    conf: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Airflow dag_run conf to merge into trigger payload.",
    )


class EmbeddingDagTriggerRequest(BaseModel):
    dag_id: str | None = Field(
        default=None,
        description="Optional DAG override. Defaults to configured embedding DAG ID.",
    )
    conf: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Airflow dag_run conf to merge into trigger payload.",
    )
