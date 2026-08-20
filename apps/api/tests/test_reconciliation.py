from datetime import date
from decimal import Decimal

from app.schemas.statement import (
    ExtractedTransaction,
    StatementHeader,
    TransactionType,
)
from app.services.reconciliation import reconcile_statement


def test_reconcile_statement_perfect_match() -> None:
    header = StatementHeader(
        issuer="HDFC Bank",
        total_debits=Decimal("15000.00"),
        total_credits=Decimal("5000.00"),
        total_amount_due=Decimal("10000.00"),
        opening_balance=Decimal("0.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="AMAZON",
            amount=Decimal("10000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="FLIPKART",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 3),
            merchant_raw="AUTOPAY PAYMENT",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.PAYMENT,
        ),
    ]

    summary = reconcile_statement(header, transactions)

    assert summary.status == "VALIDATED"
    assert summary.is_balanced is True
    assert summary.discrepancy == Decimal("0.00")
    assert summary.extracted_debits == Decimal("15000.00")
    assert summary.extracted_credits == Decimal("5000.00")
    assert summary.expected_total_due == Decimal("10000.00")
    assert len(summary.warnings) == 0


def test_reconcile_statement_within_rounding_tolerance() -> None:
    # Discrepancy of ₹0.50 <= ₹1.00
    header = StatementHeader(
        issuer="ICICI Bank",
        total_debits=Decimal("1000.50"),
        total_credits=Decimal("0.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="SWIGGY",
            amount=Decimal("1000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    summary = reconcile_statement(header, transactions)

    assert summary.status == "VALIDATED"
    assert summary.is_balanced is True
    assert summary.discrepancy == Decimal("0.50")


def test_reconcile_statement_debit_discrepancy_review_required() -> None:
    # Discrepancy of ₹500.00 > ₹1.00
    header = StatementHeader(
        issuer="SBI Card",
        total_debits=Decimal("5500.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="SWIGGY",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    summary = reconcile_statement(
        header, transactions, unparsed_lines=["Unrecognized text row 123"]
    )

    assert summary.status == "REVIEW_REQUIRED"
    assert summary.is_balanced is False
    assert summary.discrepancy == Decimal("500.00")
    assert summary.unparsed_lines_count == 1
    assert any("Discrepancy: ₹500.00" in w for w in summary.warnings)
    assert any("1 line(s) could not be parsed" in w for w in summary.warnings)


def test_reconcile_statement_credits_discrepancy() -> None:
    header = StatementHeader(
        issuer="Axis Bank",
        total_debits=Decimal("10000.00"),
        total_credits=Decimal("8000.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="PURCHASE",
            amount=Decimal("10000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="PAYMENT",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.PAYMENT,
        ),
    ]

    summary = reconcile_statement(header, transactions)

    assert summary.status == "REVIEW_REQUIRED"
    assert summary.discrepancy == Decimal("3000.00")
    assert any("Extracted credits" in w for w in summary.warnings)


def test_reconcile_statement_net_dues_calculation() -> None:
    # When total_debits is not present, use opening + debits - credits vs total_amount_due
    header = StatementHeader(
        issuer="American Express",
        opening_balance=Decimal("2000.00"),
        total_amount_due=Decimal("7000.00"),
    )
    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="PURCHASE 1",
            amount=Decimal("6000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="PAYMENT 1",
            amount=Decimal("1000.00"),
            transaction_type=TransactionType.PAYMENT,
        ),
    ]

    summary = reconcile_statement(header, transactions)

    assert summary.status == "VALIDATED"
    assert summary.expected_total_due == Decimal("7000.00")
    assert summary.discrepancy == Decimal("0.00")
