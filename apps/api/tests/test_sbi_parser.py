from datetime import date
from decimal import Decimal

from app.parsers.sbi import SbiStatementParser
from app.schemas.statement import TransactionType
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import SBI_SAMPLE_TEXT


def test_sbi_parser_identify() -> None:
    parser = SbiStatementParser()
    assert parser.identify(SBI_SAMPLE_TEXT) is True
    assert parser.identify("ICICI Bank Credit Card") is False


def test_sbi_parser_parse() -> None:
    parser = SbiStatementParser()
    pdf_stream = create_pdf_from_text(SBI_SAMPLE_TEXT)
    result = parser.parse(pdf_stream)

    assert result.header.issuer == "SBI Card"
    assert result.header.card_last_4 == "9876"
    assert result.header.statement_period_start == date(2024, 3, 13)
    assert result.header.statement_period_end == date(2024, 4, 12)
    assert result.header.payment_due_date == date(2024, 5, 2)
    assert result.header.total_amount_due == Decimal("28950.00")
    assert result.header.minimum_amount_due == Decimal("1450.00")
    assert result.header.credit_limit == Decimal("200000.00")
    assert result.header.available_credit == Decimal("171050.00")
    assert result.header.total_debits == Decimal("28950.00")

    # Verify transactions extracted
    assert len(result.transactions) == 5
    first_txn = result.transactions[0]
    assert first_txn.transaction_date == date(2024, 3, 15)
    assert "ZOMATO ORDER ONLINE" in first_txn.merchant_raw
    assert first_txn.amount == Decimal("890.00")
    assert first_txn.transaction_type == TransactionType.PURCHASE

    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")
