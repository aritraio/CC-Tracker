from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.statement import ExtractedTransaction


class ValidationIssueType(StrEnum):
    FUTURE_DATE = "FUTURE_DATE"
    OUTSIDE_BILLING_CYCLE = "OUTSIDE_BILLING_CYCLE"
    DUPLICATE_TRANSACTION = "DUPLICATE_TRANSACTION"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    CREDIT_LIMIT_EXCEEDED = "CREDIT_LIMIT_EXCEEDED"
    MISSING_MANDATORY_FIELD = "MISSING_MANDATORY_FIELD"


class ValidationIssue(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    issue_type: ValidationIssueType
    severity: str = Field("WARNING", description="'WARNING' or 'ERROR'")
    message: str
    transaction_index: int | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    is_valid: bool = Field(True, description="True if no blocking ERROR issues exist")
    issues: list[ValidationIssue] = Field(default_factory=list)
    duplicate_count: int = Field(0, ge=0)
    flagged_count: int = Field(0, ge=0)
    sanitized_transactions: list[ExtractedTransaction] = Field(default_factory=list)


class ReconciliationSummary(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    status: str = Field("VALIDATED", description="'VALIDATED' or 'REVIEW_REQUIRED'")
    discrepancy: Decimal = Field(Decimal("0.00"), description="Calculated reconciliation delta")
    extracted_debits: Decimal = Field(
        Decimal("0.00"), description="Sum of purchases and debit charges"
    )
    extracted_credits: Decimal = Field(
        Decimal("0.00"), description="Sum of payments, refunds, rewards"
    )
    statement_total_debits: Decimal | None = None
    statement_total_credits: Decimal | None = None
    statement_total_amount_due: Decimal | None = None
    expected_total_due: Decimal | None = None
    is_balanced: bool = Field(True, description="True if discrepancy <= 1.00")
    unparsed_lines_count: int = Field(0, ge=0)
    warnings: list[str] = Field(default_factory=list)
