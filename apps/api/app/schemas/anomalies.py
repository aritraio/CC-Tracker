from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categorization import Category


class DetectorType(StrEnum):
    CATEGORY_SPIKE = "CATEGORY_SPIKE"
    SPENDING_ACCELERATION = "SPENDING_ACCELERATION"
    FREQUENT_SMALL_SPEND = "FREQUENT_SMALL_SPEND"
    MERCHANT_CONCENTRATION = "MERCHANT_CONCENTRATION"
    UNUSUAL_PURCHASE = "UNUSUAL_PURCHASE"
    SUBSCRIPTION_BURDEN = "SUBSCRIPTION_BURDEN"
    WEEKEND_SPIKE = "WEEKEND_SPIKE"
    LATE_NIGHT_SPURT = "LATE_NIGHT_SPURT"
    FREQUENCY_INFLATION = "FREQUENCY_INFLATION"
    HIGH_CREDIT_UTILIZATION = "HIGH_CREDIT_UTILIZATION"


class FindingSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingEvidence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_value: Decimal | float | int
    threshold_or_baseline: Decimal | float | int | None = None
    delta_percentage: float | None = None
    related_category: Category | None = None
    related_merchants: list[str] = Field(default_factory=list)
    transaction_count: int | None = None
    context_data: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    detector_type: DetectorType
    severity: FindingSeverity
    title: str
    description: str
    evidence: FindingEvidence
    impact_amount: Decimal | None = None
    actionable: bool = True


class HistoricalProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    avg_monthly_spend: Decimal | None = None
    avg_transaction_count: int | None = None
    avg_ticket_size: Decimal | None = None
    category_baselines: dict[str, Decimal] = Field(
        default_factory=dict, description="Historical category spend averages"
    )
    previous_cycle_spend: Decimal | None = None
    previous_cycle_count: int | None = None


class AnomalyDetectionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    findings: list[Finding] = Field(default_factory=list)
    total_findings_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
