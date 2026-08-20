import io
from decimal import Decimal

from app.core.exceptions import StatementReconciliationError
from app.parsers.amex import AmexStatementParser
from app.parsers.axis import AxisStatementParser
from app.parsers.base import BaseStatementParser
from app.parsers.hdfc import HdfcStatementParser
from app.parsers.icici import IciciStatementParser
from app.parsers.sbi import SbiStatementParser
from app.schemas.statement import ParsedStatement, StatementHeader
from tests.fixtures.helpers import create_pdf_from_text


class DummyParser(BaseStatementParser):
    issuer_name = "Dummy Bank"

    def identify(self, first_page_text: str) -> bool:
        return "Dummy" in first_page_text

    def parse(self, pdf_stream: io.BytesIO) -> ParsedStatement:
        pages = self.extract_text_pages(pdf_stream)
        tables = self.extract_tables_by_page(pdf_stream)
        assert isinstance(tables, list)
        return ParsedStatement(
            header=StatementHeader(issuer=self.issuer_name),
            transactions=[],
            raw_text_length=len("\n".join(pages)),
            reconciliation_status="VALIDATED",
            reconciliation_discrepancy=Decimal("0.00"),
        )


def test_base_parser_methods() -> None:
    pdf_stream = create_pdf_from_text("Dummy Bank Statement\nPage 1 Content")
    parser = DummyParser()
    assert parser.identify("Dummy Bank Statement") is True
    parsed = parser.parse(pdf_stream)
    assert parsed.header.issuer == "Dummy Bank"
    assert parsed.raw_text_length > 0


def test_base_parser_empty_or_corrupted_stream() -> None:
    parser = DummyParser()
    empty_stream = io.BytesIO(b"not a valid pdf buffer")
    pages = parser.extract_text_pages(empty_stream)
    assert pages == []

    tables = parser.extract_tables_by_page(empty_stream)
    assert tables == []


def test_multiline_transaction_stitching() -> None:
    multiline_text = """HDFC BANK
Credit Card Statement
Card No: 4524 XXXX XXXX 1234
Statement Date : 15/04/2024
Payment Due Date : 05/05/2024
Total Amount Due : 1,000.00
Total Debits : 1,000.00

Date Transaction Description Amount (in Rs.)
16/03/2024 SWIGGY FOOD ORDER 1,000.00
ORDER ID 987654321
BANGALORE IN
"""
    pdf_stream = create_pdf_from_text(multiline_text)
    parser = HdfcStatementParser()
    result = parser.parse(pdf_stream)

    assert len(result.transactions) == 1
    txn = result.transactions[0]
    assert "ORDER ID 987654321" in txn.merchant_raw
    assert "BANGALORE IN" in txn.merchant_raw


def test_reconciliation_review_required_on_discrepancy() -> None:
    discrepant_text = """HDFC BANK
Card No: 4524 XXXX XXXX 1234
Statement Date : 15/04/2024
Total Amount Due : 50,000.00
Total Debits : 50,000.00

Date Transaction Description Amount (in Rs.)
16/03/2024 SWIGGY BANGALORE IN 10,000.00
"""
    pdf_stream = create_pdf_from_text(discrepant_text)
    parser = HdfcStatementParser()
    result = parser.parse(pdf_stream)

    assert result.reconciliation_status == "REVIEW_REQUIRED"
    assert result.reconciliation_discrepancy == Decimal("40000.00")


def test_reconciliation_calculation_without_total_debits() -> None:
    text = """HDFC BANK
Card No: 4524 XXXX XXXX 1234
Statement Date : 15/04/2024
Opening Balance : 1,000.00
Total Amount Due : 5,000.00

Date Transaction Description Amount (in Rs.)
16/03/2024 SWIGGY BANGALORE IN 4,000.00
"""
    pdf_stream = create_pdf_from_text(text)
    parser = HdfcStatementParser()
    result = parser.parse(pdf_stream)

    assert result.reconciliation_status == "VALIDATED"
    assert result.reconciliation_discrepancy == Decimal("0.00")


def test_parsers_single_date_fallback() -> None:
    hdfc_text = "HDFC BANK\nStatement Date : 15/04/2024\nCard No: 4524 XXXX XXXX 1234\nTotal Amount Due : 0.00"
    assert (
        HdfcStatementParser().parse(create_pdf_from_text(hdfc_text)).header.statement_period_end
        is not None
    )

    icici_text = "ICICI BANK\nStatement Date : 20/04/2024\nCard No: 4375 12XX XXXX 4321\nTotal Amount Due : 0.00"
    assert (
        IciciStatementParser().parse(create_pdf_from_text(icici_text)).header.statement_period_end
        is not None
    )

    sbi_text = "SBI Card\nStatement Date : 12 Apr 2024\nCard No: 4129 XXXX XXXX 9876\nTotal Amount Due : 0.00"
    assert (
        SbiStatementParser().parse(create_pdf_from_text(sbi_text)).header.statement_period_end
        is not None
    )

    axis_text = "AXIS BANK\nStatement Date : 17/04/2024\nCard No: 5241 XXXX XXXX 7890\nTotal Amount Due : 0.00"
    assert (
        AxisStatementParser().parse(create_pdf_from_text(axis_text)).header.statement_period_end
        is not None
    )

    amex_text = "American Express\nStatement Date : 30/04/2024\nCard No: 3759 XXXXXX 1234\nTotal Amount Due : 0.00"
    assert (
        AmexStatementParser().parse(create_pdf_from_text(amex_text)).header.statement_period_end
        is not None
    )


def test_reconciliation_error_class() -> None:
    err = StatementReconciliationError("Reconciliation mismatch", {"discrepancy": 100})
    assert err.error_code == "STATEMENT_RECONCILIATION_FAILED"
    assert err.status_code == 422
