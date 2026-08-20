from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(StrEnum):
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"
    REVERSAL = "REVERSAL"
    PAYMENT = "PAYMENT"
    FEE = "FEE"
    INTEREST = "INTEREST"
    GST = "GST"
    EMI = "EMI"
    CASH_WITHDRAWAL = "CASH_WITHDRAWAL"
    REWARD = "REWARD"
    ADJUSTMENT = "ADJUSTMENT"
    UNKNOWN = "UNKNOWN"


class ExtractedTransaction(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    transaction_date: date
    post_date: date | None = None
    merchant_raw: str = Field(..., min_length=1, description="Raw transaction description")
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Positive transaction amount")
    transaction_type: TransactionType = Field(
        default=TransactionType.PURCHASE, description="Type of credit card transaction"
    )
    currency: str = Field("INR", description="Currency code (e.g. INR, USD)")
    source_page: int = Field(1, ge=1, description="1-indexed source PDF page")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence")


class StatementHeader(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    issuer: str = Field(..., description="Issuing bank name (e.g. HDFC, ICICI, SBI)")
    card_last_4: str | None = Field(
        None, min_length=4, max_length=4, description="Last 4 digits of card"
    )
    statement_period_start: date | None = Field(None, description="Billing cycle start date")
    statement_period_end: date | None = Field(
        None, description="Billing cycle end / statement date"
    )
    total_amount_due: Decimal | None = Field(None, description="Total statement outstanding dues")
    minimum_amount_due: Decimal | None = Field(None, description="Minimum due amount")
    payment_due_date: date | None = Field(None, description="Payment due date")
    credit_limit: Decimal | None = Field(None, description="Total credit limit")
    available_credit: Decimal | None = Field(None, description="Available credit limit")
    opening_balance: Decimal | None = Field(None, description="Previous cycle balance")
    total_debits: Decimal | None = Field(None, description="Total debits billed in cycle")
    total_credits: Decimal | None = Field(None, description="Total payments & credits in cycle")


class ParsedStatement(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    header: StatementHeader
    transactions: list[ExtractedTransaction]
    raw_text_length: int = Field(..., ge=0, description="Character count of extracted raw text")
    reconciliation_status: str = Field("VALIDATED", description="'VALIDATED' or 'REVIEW_REQUIRED'")
    reconciliation_discrepancy: Decimal = Field(
        Decimal("0.00"), description="Calculated reconciliation delta"
    )
    unparsed_lines: list[str] = Field(
        default_factory=list, description="Lines that could not be parsed"
    )
