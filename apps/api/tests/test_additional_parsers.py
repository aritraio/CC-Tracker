from datetime import date
from decimal import Decimal

from app.parsers.amex import AmexStatementParser
from app.parsers.axis import AxisStatementParser
from app.schemas.statement import TransactionType
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import AMEX_SAMPLE_TEXT, AXIS_SAMPLE_TEXT


def test_axis_parser() -> None:
    parser = AxisStatementParser()
    assert parser.identify(AXIS_SAMPLE_TEXT) is True
    assert parser.identify("Random bank") is False

    pdf_stream = create_pdf_from_text(AXIS_SAMPLE_TEXT)
    result = parser.parse(pdf_stream)

    assert result.header.issuer == "Axis Bank"
    assert result.header.card_last_4 == "7890"
    assert result.header.statement_period_start == date(2024, 3, 18)
    assert result.header.statement_period_end == date(2024, 4, 17)
    assert result.header.payment_due_date == date(2024, 5, 7)
    assert result.header.total_amount_due == Decimal("24150.00")
    assert result.header.minimum_amount_due == Decimal("1210.00")
    assert result.header.credit_limit == Decimal("350000.00")
    assert result.header.available_credit == Decimal("325850.00")
    assert result.header.total_debits == Decimal("24150.00")

    assert len(result.transactions) == 5
    assert result.transactions[0].merchant_raw == "MYNTRA DESIGNS BANGALORE"
    assert result.transactions[0].amount == Decimal("4200.00")
    assert result.transactions[0].transaction_type == TransactionType.PURCHASE

    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")


def test_amex_parser() -> None:
    parser = AmexStatementParser()
    assert parser.identify(AMEX_SAMPLE_TEXT) is True
    assert parser.identify("Random bank") is False

    pdf_stream = create_pdf_from_text(AMEX_SAMPLE_TEXT)
    result = parser.parse(pdf_stream)

    assert result.header.issuer == "American Express"
    assert result.header.card_last_4 == "1234"
    assert result.header.statement_period_start == date(2024, 4, 1)
    assert result.header.statement_period_end == date(2024, 4, 30)
    assert result.header.payment_due_date == date(2024, 5, 18)
    assert result.header.total_amount_due == Decimal("64800.00")
    assert result.header.minimum_amount_due == Decimal("3240.00")
    assert result.header.credit_limit == Decimal("500000.00")
    assert result.header.available_credit == Decimal("435200.00")
    assert result.header.total_debits == Decimal("64800.00")

    assert len(result.transactions) == 4
    assert result.transactions[0].merchant_raw == "TAJ HOTELS RESORTS MUMBAI"
    assert result.transactions[0].amount == Decimal("42000.00")
    assert result.transactions[0].transaction_type == TransactionType.PURCHASE

    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")
