from datetime import date
from decimal import Decimal

from app.parsers.hdfc import HdfcStatementParser
from app.schemas.statement import TransactionType
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import HDFC_SAMPLE_TEXT, HDFC_SAMPLE_WITH_PAYMENTS


def test_hdfc_parser_identify() -> None:
    parser = HdfcStatementParser()
    assert parser.identify(HDFC_SAMPLE_TEXT) is True
    assert parser.identify("Random invoice statement") is False


def test_hdfc_parser_parse_standard() -> None:
    parser = HdfcStatementParser()
    pdf_stream = create_pdf_from_text(HDFC_SAMPLE_TEXT)
    result = parser.parse(pdf_stream)

    # Check Header Metadata
    assert result.header.issuer == "HDFC Bank"
    assert result.header.card_last_4 == "1234"
    assert result.header.statement_period_start == date(2024, 3, 16)
    assert result.header.statement_period_end == date(2024, 4, 15)
    assert result.header.payment_due_date == date(2024, 5, 5)
    assert result.header.total_amount_due == Decimal("45230.50")
    assert result.header.minimum_amount_due == Decimal("2300.00")
    assert result.header.credit_limit == Decimal("300000.00")
    assert result.header.available_credit == Decimal("254769.50")
    assert result.header.total_debits == Decimal("45230.50")

    # Check Transactions
    assert len(result.transactions) == 10
    first_txn = result.transactions[0]
    assert first_txn.transaction_date == date(2024, 3, 16)
    assert first_txn.merchant_raw == "SWIGGY BANGALORE IN"
    assert first_txn.amount == Decimal("549.00")
    assert first_txn.transaction_type == TransactionType.PURCHASE

    # Check Fee and GST classification
    fee_txn = next(t for t in result.transactions if "MEMBERSHIP FEE" in t.merchant_raw)
    assert fee_txn.transaction_type == TransactionType.FEE
    assert fee_txn.amount == Decimal("1500.00")

    gst_txn = next(t for t in result.transactions if "IGST" in t.merchant_raw)
    assert gst_txn.transaction_type == TransactionType.GST
    assert gst_txn.amount == Decimal("270.00")

    # Check Reconciliation
    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")


def test_hdfc_parser_parse_with_credits_and_autopay() -> None:
    parser = HdfcStatementParser()
    pdf_stream = create_pdf_from_text(HDFC_SAMPLE_WITH_PAYMENTS)
    result = parser.parse(pdf_stream)

    assert result.header.issuer == "HDFC Bank"
    assert result.header.card_last_4 == "5678"
    assert result.header.statement_period_end == date(2024, 4, 15)
    assert result.header.total_amount_due == Decimal("8450.00")
    assert result.header.opening_balance == Decimal("12500.00")

    # Verify Autopay payment parsed and typed correctly
    assert len(result.transactions) == 4
    autopay_txn = result.transactions[0]
    assert autopay_txn.transaction_date == date(2024, 3, 17)
    assert "AUTOPAY PAYMENT" in autopay_txn.merchant_raw
    assert autopay_txn.amount == Decimal("12500.00")
    assert autopay_txn.transaction_type == TransactionType.PAYMENT

    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")
