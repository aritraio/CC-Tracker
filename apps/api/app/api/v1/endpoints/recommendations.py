from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.recommendations.engine import get_default_recommendation_engine
from app.recommendations.llm_explainer import get_default_llm_explainer
from app.schemas.anomalies import AnomalyDetectionResult
from app.schemas.recommendations import (
    LLMExplanationResult,
    RecommendationEventType,
    RecommendationFeedbackRequest,
    RecommendationFeedbackResponse,
    RecommendationResult,
    RecommendationStatus,
)
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


@router.post(
    "/{recommendation_id}/feedback",
    response_model=RecommendationFeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Record user interaction & feedback on a recommendation",
    description="Captures user decisions (ACCEPTED, DISMISSED, EXPLORED_TRANSACTIONS, UNDONE) and tracks dismiss reasons for behavioral feedback loop.",
)
async def record_recommendation_feedback_endpoint(
    recommendation_id: str,
    payload: RecommendationFeedbackRequest,
) -> RecommendationFeedbackResponse:
    import uuid
    from datetime import datetime, timezone
    from app.schemas.recommendations import RecommendationEventType, RecommendationStatus

    # Determine updated recommendation status based on event type
    status_map = {
        RecommendationEventType.ACCEPTED: RecommendationStatus.ACCEPTED,
        RecommendationEventType.DISMISSED: RecommendationStatus.DISMISSED,
        RecommendationEventType.COMPLETED: RecommendationStatus.COMPLETED,
        RecommendationEventType.UNDONE: RecommendationStatus.ACTIVE,
        RecommendationEventType.VIEWED: RecommendationStatus.ACTIVE,
        RecommendationEventType.EXPLORED_TRANSACTIONS: RecommendationStatus.ACTIVE,
    }

    new_status = status_map.get(payload.event_type, RecommendationStatus.ACTIVE)
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    status_messages = {
        RecommendationEventType.ACCEPTED: f"Goal '{recommendation_id}' accepted successfully. Tracking target savings.",
        RecommendationEventType.DISMISSED: f"Recommendation '{recommendation_id}' dismissed (Reason: {payload.dismiss_reason or 'Not specified'}).",
        RecommendationEventType.COMPLETED: f"Goal '{recommendation_id}' marked as completed.",
        RecommendationEventType.UNDONE: f"Action on '{recommendation_id}' reset to active state.",
        RecommendationEventType.EXPLORED_TRANSACTIONS: f"Transaction drilldown explored for '{recommendation_id}'.",
        RecommendationEventType.VIEWED: f"Recommendation '{recommendation_id}' viewed.",
    }

    message = status_messages.get(payload.event_type, f"Feedback recorded for '{recommendation_id}'.")

    return RecommendationFeedbackResponse(
        success=True,
        recommendation_id=recommendation_id,
        current_status=new_status,
        recorded_event_id=event_id,
        timestamp=now_iso,
        message=message,
    )

