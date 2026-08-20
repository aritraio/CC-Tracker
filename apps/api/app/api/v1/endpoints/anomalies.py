from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.schemas.anomalies import AnomalyDetectionResult, HistoricalProfile
from app.schemas.categorization import CategorizedTransaction
from app.schemas.statement import StatementHeader

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


class AnomalyDetectionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    header: StatementHeader | None = None
    transactions: list[CategorizedTransaction]
    historical_profile: HistoricalProfile | None = None


@router.post(
    "/detect",
    response_model=AnomalyDetectionResult,
    status_code=status.HTTP_200_OK,
    summary="Run 10 pattern and anomaly detectors on credit card spend",
    description="Detects category spikes, spending accelerations, micro-spending leaks, high utilization, and behavioral patterns.",
)
async def detect_anomalies_endpoint(
    payload: AnomalyDetectionRequest,
) -> AnomalyDetectionResult:
    engine = get_default_analytics_engine()
    analytics = engine.compute_analytics(payload.transactions, payload.header)
    return run_anomaly_detection(
        transactions=payload.transactions,
        analytics=analytics,
        header=payload.header,
        historical_profile=payload.historical_profile,
    )
