import pytest

from app.core.exceptions import UnsupportedStatementError
from app.parsers.amex import AmexStatementParser
from app.parsers.axis import AxisStatementParser
from app.parsers.detector import detect_bank, get_parser_for_statement
from app.parsers.hdfc import HdfcStatementParser
from app.parsers.icici import IciciStatementParser
from app.parsers.sbi import SbiStatementParser
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import (
    AMEX_SAMPLE_TEXT,
    AXIS_SAMPLE_TEXT,
    HDFC_SAMPLE_TEXT,
    ICICI_SAMPLE_TEXT,
    SBI_SAMPLE_TEXT,
)


def test_detect_bank_from_text() -> None:
    assert detect_bank(HDFC_SAMPLE_TEXT) == "HDFC"
    assert detect_bank(ICICI_SAMPLE_TEXT) == "ICICI"
    assert detect_bank(SBI_SAMPLE_TEXT) == "SBI"
    assert detect_bank(AXIS_SAMPLE_TEXT) == "AXIS"
    assert detect_bank(AMEX_SAMPLE_TEXT) == "AMEX"
    assert detect_bank("Random text without any bank keywords") is None
    assert detect_bank("") is None


def test_get_parser_for_statement_success() -> None:
    hdfc_pdf = create_pdf_from_text(HDFC_SAMPLE_TEXT)
    parser = get_parser_for_statement(hdfc_pdf)
    assert isinstance(parser, HdfcStatementParser)

    icici_pdf = create_pdf_from_text(ICICI_SAMPLE_TEXT)
    parser = get_parser_for_statement(icici_pdf)
    assert isinstance(parser, IciciStatementParser)

    sbi_pdf = create_pdf_from_text(SBI_SAMPLE_TEXT)
    parser = get_parser_for_statement(sbi_pdf)
    assert isinstance(parser, SbiStatementParser)

    axis_pdf = create_pdf_from_text(AXIS_SAMPLE_TEXT)
    parser = get_parser_for_statement(axis_pdf)
    assert isinstance(parser, AxisStatementParser)

    amex_pdf = create_pdf_from_text(AMEX_SAMPLE_TEXT)
    parser = get_parser_for_statement(amex_pdf)
    assert isinstance(parser, AmexStatementParser)


def test_get_parser_for_statement_unsupported() -> None:
    unknown_pdf = create_pdf_from_text("Monthly Invoice for Generic Software Subscription")
    with pytest.raises(UnsupportedStatementError) as exc_info:
        get_parser_for_statement(unknown_pdf)
    assert exc_info.value.error_code == "UNSUPPORTED_STATEMENT_FORMAT"
