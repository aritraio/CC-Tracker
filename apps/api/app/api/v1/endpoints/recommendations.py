from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.recommendations.engine import get_default_recommendation_engine
from app.recommendations.llm_explainer import get_default_llm_explainer
from app.schemas.anomalies import AnomalyDetectionResult
from app.schemas.recommendations import LLMExplanationResult, RecommendationResult
from app.schemas.statements_api import RecommendationsGenerateRequest

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class RecommendationsGenerateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    anomalies: AnomalyDetectionResult
    recommendations: RecommendationResult
    explanation: LLMExplanationResult | None = None


@router.post(
    "/generate",
    response_model=RecommendationsGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate evidence-based recommendations and explanation from categorized transactions",
    description="Computes spend patterns, detects anomalies, calculates conservative savings recommendations, and generates human explanation.",
)
async def generate_recommendations_endpoint(
    payload: RecommendationsGenerateRequest,
) -> RecommendationsGenerateResponse:
    analytics_engine = get_default_analytics_engine()
    analytics = analytics_engine.compute_analytics(payload.transactions, payload.header)

    anomalies = run_anomaly_detection(
        transactions=payload.transactions,
        analytics=analytics,
        header=payload.header,
        historical_profile=payload.historical_profile,
    )

    rec_engine = get_default_recommendation_engine()
    recommendations = rec_engine.generate_recommendations(
        findings=anomalies,
        analytics=analytics,
        transactions=payload.transactions,
        header=payload.header,
        historical_profile=payload.historical_profile,
    )

    explanation: LLMExplanationResult | None = None
    if payload.generate_explanation:
        explainer = get_default_llm_explainer()
        explanation = explainer.explain(
            analytics=analytics,
            findings=anomalies,
            recommendations=recommendations,
            header=payload.header,
        )

    return RecommendationsGenerateResponse(
        anomalies=anomalies,
        recommendations=recommendations,
        explanation=explanation,
    )
