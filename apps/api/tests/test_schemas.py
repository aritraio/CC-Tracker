from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.statement import (
    ExtractedTransaction,
    ParsedStatement,
    StatementHeader,
    TransactionType,
)


def test_transaction_type_enum() -> None:
    assert TransactionType.PURCHASE == "PURCHASE"
    assert TransactionType.REFUND == "REFUND"
    assert TransactionType.PAYMENT == "PAYMENT"
    assert TransactionType.FEE == "FEE"
    assert TransactionType.GST == "GST"
    assert TransactionType.INTEREST == "INTEREST"
    assert TransactionType.EMI == "EMI"
    assert TransactionType.CASH_WITHDRAWAL == "CASH_WITHDRAWAL"


def test_extracted_transaction_valid() -> None:
    txn = ExtractedTransaction(
        transaction_date=date(2024, 4, 15),
        merchant_raw="SWIGGY BANGALORE",
        amount=Decimal("450.50"),
        transaction_type=TransactionType.PURCHASE,
        currency="INR",
        source_page=1,
        confidence_score=1.0,
    )
    assert txn.transaction_date == date(2024, 4, 15)
    assert txn.amount == Decimal("450.50")
    assert txn.merchant_raw == "SWIGGY BANGALORE"
    assert txn.transaction_type == TransactionType.PURCHASE
    assert txn.source_page == 1


def test_extracted_transaction_validation_errors() -> None:
    # Zero / Negative amount should fail
    with pytest.raises(ValidationError):
        ExtractedTransaction(
            transaction_date=date(2024, 4, 15),
            merchant_raw="TEST",
            amount=Decimal("0.00"),
            transaction_type=TransactionType.PURCHASE,
        )

    # Empty merchant_raw should fail
    with pytest.raises(ValidationError):
        ExtractedTransaction(
            transaction_date=date(2024, 4, 15),
            merchant_raw="",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.PURCHASE,
        )

    # Invalid source_page (< 1)
    with pytest.raises(ValidationError):
        ExtractedTransaction(
            transaction_date=date(2024, 4, 15),
            merchant_raw="TEST",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.PURCHASE,
            source_page=0,
        )


def test_statement_header_and_parsed_statement() -> None:
    header = StatementHeader(
        issuer="HDFC Bank",
        card_last_4="1234",
        statement_period_start=date(2024, 3, 16),
        statement_period_end=date(2024, 4, 15),
        total_amount_due=Decimal("45230.50"),
        minimum_amount_due=Decimal("2300.00"),
        payment_due_date=date(2024, 5, 5),
        credit_limit=Decimal("300000.00"),
        available_credit=Decimal("254769.50"),
        opening_balance=Decimal("0.00"),
        total_debits=Decimal("45230.50"),
        total_credits=Decimal("0.00"),
    )
    assert header.issuer == "HDFC Bank"
    assert header.card_last_4 == "1234"

    txn = ExtractedTransaction(
        transaction_date=date(2024, 4, 15),
        merchant_raw="SWIGGY",
        amount=Decimal("45230.50"),
        transaction_type=TransactionType.PURCHASE,
        source_page=1,
    )

    parsed = ParsedStatement(
        header=header,
        transactions=[txn],
        raw_text_length=1500,
        reconciliation_status="VALIDATED",
        reconciliation_discrepancy=Decimal("0.00"),
    )
    assert parsed.reconciliation_status == "VALIDATED"
    assert len(parsed.transactions) == 1
    assert parsed.raw_text_length == 1500
