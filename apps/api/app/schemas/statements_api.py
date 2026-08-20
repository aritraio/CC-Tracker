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


class StatementSaveRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    statement_data: ParseStatementResponse
    user_id: str | None = Field(None, description="Authenticated user UUID or anonymous session ID")
    card_name: str | None = Field(None, description="Optional nickname for the card, e.g. 'Amazon Pay ICICI'")
    save_transactions: bool = True
    save_findings: bool = True
    save_recommendations: bool = True


class StatementSaveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    statement_id: str
    card_id: str | None = None
    saved_transactions_count: int = 0
    saved_findings_count: int = 0
    saved_recommendations_count: int = 0
    saved_at: str
    message: str


class StatementHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issuer: str
    card_last_4: str | None = None
    card_name: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    due_date: str | None = None
    total_amount_due: Decimal = Decimal("0.00")
    total_debits: Decimal = Decimal("0.00")
    reconciliation_status: str = "VALIDATED"
    transaction_count: int = 0
    findings_count: int = 0
    recommendations_count: int = 0
    created_at: str


class StatementHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    statements: list[StatementHistoryItem] = Field(default_factory=list)
    total_count: int = 0

