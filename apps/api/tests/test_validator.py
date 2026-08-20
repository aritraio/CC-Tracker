from datetime import date
from decimal import Decimal

from app.schemas.reconciliation import ValidationIssueType
from app.schemas.statement import (
    ExtractedTransaction,
    StatementHeader,
    TransactionType,
)
from app.services.validator import validate_transactions


def test_validate_transactions_valid() -> None:
    header = StatementHeader(
        issuer="HDFC Bank",
        statement_period_start=date(2024, 3, 16),
        statement_period_end=date(2024, 4, 15),
        credit_limit=Decimal("100000.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 3, 20),
            merchant_raw="SWIGGY BANGALORE",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 10),
            merchant_raw="AMAZON INDIA",
            amount=Decimal("2500.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    result = validate_transactions(header, transactions, reference_date=date(2024, 4, 20))

    assert result.is_valid is True
    assert len(result.issues) == 0
    assert result.duplicate_count == 0
    assert result.flagged_count == 0


def test_validate_transactions_future_date() -> None:
    header = StatementHeader(issuer="HDFC Bank")
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 5, 1),
            merchant_raw="FUTURE ORDER",
            amount=Decimal("500.00"),
            transaction_type=TransactionType.PURCHASE,
        )
    ]

    result = validate_transactions(header, transactions, reference_date=date(2024, 4, 15))

    assert result.is_valid is False
    assert len(result.issues) == 1
    assert result.issues[0].issue_type == ValidationIssueType.FUTURE_DATE
    assert result.issues[0].severity == "ERROR"


def test_validate_transactions_out_of_billing_cycle() -> None:
    header = StatementHeader(
        issuer="ICICI Bank",
        statement_period_start=date(2024, 3, 1),
        statement_period_end=date(2024, 3, 31),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 1, 15),  # 45 days before cycle start
            merchant_raw="OLD CHARGE",
            amount=Decimal("1200.00"),
            transaction_type=TransactionType.PURCHASE,
        )
    ]

    result = validate_transactions(header, transactions, reference_date=date(2024, 4, 15))

    assert result.is_valid is True
    assert len(result.issues) == 1
    assert result.issues[0].issue_type == ValidationIssueType.OUTSIDE_BILLING_CYCLE
    assert result.issues[0].severity == "WARNING"


def test_validate_transactions_duplicate_detection() -> None:
    header = StatementHeader(issuer="SBI Card")
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 5),
            merchant_raw="BLINKIT COMMERCE",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 5),
            merchant_raw="BLINKIT COMMERCE",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    result = validate_transactions(header, transactions, reference_date=date(2024, 4, 15))

    assert result.is_valid is True
    assert result.duplicate_count == 1
    assert len(result.issues) == 1
    assert result.issues[0].issue_type == ValidationIssueType.DUPLICATE_TRANSACTION


def test_validate_transactions_credit_limit_exceeded() -> None:
    header = StatementHeader(
        issuer="Axis Bank",
        credit_limit=Decimal("50000.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 5),
            merchant_raw="JEWELLERY PURCHASE",
            amount=Decimal("150000.00"),  # > 200% of 50k
            transaction_type=TransactionType.PURCHASE,
        )
    ]

    result = validate_transactions(header, transactions, reference_date=date(2024, 4, 15))

    assert result.is_valid is True
    assert len(result.issues) == 1
    assert result.issues[0].issue_type == ValidationIssueType.CREDIT_LIMIT_EXCEEDED
    assert result.issues[0].severity == "WARNING"


def test_validate_transactions_empty_merchant_or_invalid_amount() -> None:
    header = StatementHeader(issuer="HDFC Bank")
    # Using model_construct to bypass pydantic model validation and test validator defense layer
    t1 = ExtractedTransaction.model_construct(
        transaction_date=date(2024, 4, 1),
        merchant_raw="",
        amount=Decimal("100.00"),
        transaction_type=TransactionType.PURCHASE,
        currency="INR",
        source_page=1,
        confidence_score=1.0,
    )
    t2 = ExtractedTransaction.model_construct(
        transaction_date=date(2024, 4, 2),
        merchant_raw="TEST",
        amount=Decimal("0.00"),
        transaction_type=TransactionType.PURCHASE,
        currency="INR",
        source_page=1,
        confidence_score=1.0,
    )

    result = validate_transactions(header, [t1, t2], reference_date=date(2024, 4, 15))

    assert result.is_valid is False
    assert len(result.issues) == 2
    issue_types = {i.issue_type for i in result.issues}
    assert ValidationIssueType.MISSING_MANDATORY_FIELD in issue_types
    assert ValidationIssueType.INVALID_AMOUNT in issue_types
