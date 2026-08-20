from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict

from app.analytics.engine import get_default_analytics_engine
from app.schemas.analytics import StatementAnalytics
from app.schemas.categorization import CategorizedTransaction
from app.schemas.statement import StatementHeader

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class AnalyticsComputeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    header: StatementHeader | None = None
    transactions: list[CategorizedTransaction]


@router.post(
    "/compute",
    response_model=StatementAnalytics,
    status_code=status.HTTP_200_OK,
    summary="Compute deterministic statement analytics",
    description="Calculates spend metrics, category breakdowns, merchant concentrations, temporal burn curves, and recurring subscription burdens.",
)
async def compute_statement_analytics(
    payload: AnalyticsComputeRequest,
) -> StatementAnalytics:
    engine = get_default_analytics_engine()
    return engine.compute_analytics(payload.transactions, payload.header)
