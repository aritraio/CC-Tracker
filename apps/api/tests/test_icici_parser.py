from datetime import date
from decimal import Decimal

from app.parsers.icici import IciciStatementParser
from app.schemas.statement import TransactionType
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import ICICI_SAMPLE_TEXT


def test_icici_parser_identify() -> None:
    parser = IciciStatementParser()
    assert parser.identify(ICICI_SAMPLE_TEXT) is True
    assert parser.identify("HDFC Bank Credit Card") is False


def test_icici_parser_parse() -> None:
    parser = IciciStatementParser()
    pdf_stream = create_pdf_from_text(ICICI_SAMPLE_TEXT)
    result = parser.parse(pdf_stream)

    assert result.header.issuer == "ICICI Bank"
    assert result.header.card_last_4 == "4321"
    assert result.header.statement_period_start == date(2024, 3, 21)
    assert result.header.statement_period_end == date(2024, 4, 20)
    assert result.header.payment_due_date == date(2024, 5, 10)
    assert result.header.total_amount_due == Decimal("32450.00")
    assert result.header.minimum_amount_due == Decimal("1650.00")
    assert result.header.credit_limit == Decimal("450000.00")
    assert result.header.available_credit == Decimal("417550.00")
    assert result.header.total_debits == Decimal("32450.00")

    # Verify transactions extracted and reward points table excluded
    assert len(result.transactions) == 6
    first_txn = result.transactions[0]
    assert first_txn.transaction_date == date(2024, 3, 22)
    assert "SWIGGY FOOD DELIVERY" in first_txn.merchant_raw
    assert first_txn.amount == Decimal("680.00")
    assert first_txn.transaction_type == TransactionType.PURCHASE

    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")
