from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analytics import StatementAnalytics
from app.schemas.anomalies import AnomalyDetectionResult, HistoricalProfile
from app.schemas.categorization import CategorizationStats, CategorizedTransaction
from app.schemas.recommendations import LLMExplanationResult, RecommendationResult
from app.schemas.reconciliation import ReconciliationSummary, ValidationResult
from app.schemas.statement import ExtractedTransaction, StatementHeader


class ParseStatementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    header: StatementHeader
    transactions: list[CategorizedTransaction]
    raw_text_length: int = Field(..., ge=0)
    reconciliation_status: str = Field("VALIDATED", description="'VALIDATED' or 'REVIEW_REQUIRED'")
    reconciliation_discrepancy: Decimal = Field(Decimal("0.00"))
    reconciliation: ReconciliationSummary
    validation: ValidationResult
    categorization_stats: CategorizationStats
    analytics: StatementAnalytics
    anomalies: AnomalyDetectionResult
    recommendations: RecommendationResult
    explanation: LLMExplanationResult
    unparsed_lines: list[str] = Field(default_factory=list)


class StatementValidateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    header: StatementHeader
    transactions: list[ExtractedTransaction]
    unparsed_lines: list[str] = Field(default_factory=list)


class StatementValidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reconciliation: ReconciliationSummary
    validation: ValidationResult


class RecommendationsGenerateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    header: StatementHeader | None = None
    transactions: list[CategorizedTransaction]
    historical_profile: HistoricalProfile | None = None
    generate_explanation: bool = True
