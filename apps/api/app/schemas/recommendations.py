from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categorization import Category


class RecommendationType(StrEnum):
    CATEGORY_REDUCTION = "CATEGORY_REDUCTION"
    MICRO_SPEND_CONSOLIDATION = "MICRO_SPEND_CONSOLIDATION"
    SUBSCRIPTION_AUDIT = "SUBSCRIPTION_AUDIT"
    MERCHANT_OPTIMIZATION = "MERCHANT_OPTIMIZATION"
    UTILIZATION_MANAGEMENT = "UTILIZATION_MANAGEMENT"
    BURN_RATE_CONTROL = "BURN_RATE_CONTROL"
    WEEKEND_PACING = "WEEKEND_PACING"
    IMPULSE_CONTROL = "IMPULSE_CONTROL"
    PURCHASE_REVIEW = "PURCHASE_REVIEW"
    FREQUENCY_MANAGEMENT = "FREQUENCY_MANAGEMENT"
    POSITIVE_REINFORCEMENT = "POSITIVE_REINFORCEMENT"


class RecommendationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ACCEPTED = "ACCEPTED"
    DISMISSED = "DISMISSED"
    COMPLETED = "COMPLETED"


class RecommendationEvidence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_spend: Decimal | None = None
    historical_avg: Decimal | None = None
    transaction_count: int | None = None
    top_merchants: list[str] = Field(default_factory=list)
    excess_amount: Decimal | None = None
    savings_calculation_basis: str | None = None
    context_data: dict[str, Any] = Field(default_factory=dict)


class Recommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    finding_id: str | None = None
    type: RecommendationType
    title: str
    reason: str
    evidence: RecommendationEvidence
    estimated_monthly_savings: Decimal = Field(
        Decimal("0.00"), ge=Decimal("0.00"), description="Conservative monthly savings estimate in INR"
    )
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    action: str
    priority: int = Field(1, ge=1, le=10, description="Priority ranking (1 is highest)")
    target_category: Category | None = None
    status: RecommendationStatus = RecommendationStatus.ACTIVE


class RecommendationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendations: list[Recommendation] = Field(default_factory=list)
    total_potential_monthly_savings: Decimal = Field(
        Decimal("0.00"), ge=Decimal("0.00"), description="Deduplicated conservative monthly savings in INR"
    )
    recommendations_count: int = 0
    high_impact_count: int = 0


class ActionStep(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    step_number: int = Field(..., ge=1)
    title: str
    description: str
    estimated_impact: str | None = None


class FindingHighlight(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    finding_title: str
    observation: str
    urgency: str = Field(
        "This Month", description="'Immediate Action', 'This Month', or 'Good Habit'"
    )


class LLMExplanationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    executive_summary: str
    what_stands_out: list[FindingHighlight] = Field(default_factory=list)
    action_steps: list[ActionStep] = Field(default_factory=list)
    coaching_tone_note: str
    generated_by: str = Field("gemini-1.5-flash", description="Model name or 'deterministic_template'")
    is_fallback: bool = False
