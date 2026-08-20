import io
import logging
import re
from typing import TYPE_CHECKING

import pymupdf

from app.core.exceptions import UnsupportedStatementError
from app.parsers.base import BaseStatementParser

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Bank signatures with prioritized patterns
BANK_SIGNATURES: dict[str, list[re.Pattern[str]]] = {
    "HDFC": [
        re.compile(r"HDFC\s*BANK", re.IGNORECASE),
        re.compile(r"hdfcbank\.com", re.IGNORECASE),
        re.compile(r"HDFC\s*Bank\s*Credit\s*Card", re.IGNORECASE),
    ],
    "ICICI": [
        re.compile(r"ICICI\s*BANK", re.IGNORECASE),
        re.compile(r"icicibank\.com", re.IGNORECASE),
        re.compile(r"ICICI\s*Bank\s*Credit\s*Card", re.IGNORECASE),
        re.compile(r"Statement\s+of\s+Card\s+Account.*ICICI", re.IGNORECASE | re.DOTALL),
    ],
    "SBI": [
        re.compile(r"SBI\s*Cards?\s*(?:and\s*Payment\s*Services)?", re.IGNORECASE),
        re.compile(r"sbicard\.com", re.IGNORECASE),
        re.compile(r"State\s*Bank\s*of\s*India\s*Card", re.IGNORECASE),
        re.compile(r"SBI\s*Card\s*Statement", re.IGNORECASE),
    ],
    "AXIS": [
        re.compile(r"AXIS\s*BANK", re.IGNORECASE),
        re.compile(r"axisbank\.com", re.IGNORECASE),
        re.compile(r"Axis\s*Bank\s*Credit\s*Card", re.IGNORECASE),
        re.compile(r"EDGE\s*REWARDS.*AXIS", re.IGNORECASE | re.DOTALL),
    ],
    "AMEX": [
        re.compile(r"American\s*Express", re.IGNORECASE),
        re.compile(r"americanexpress\.com", re.IGNORECASE),
        re.compile(r"Membership\s*Rewards", re.IGNORECASE),
        re.compile(r"AMEX", re.IGNORECASE),
    ],
}


def detect_bank(first_page_text: str) -> str | None:
    """
    Detect the issuing bank identifier from the first page text of the credit card statement.
    Returns issuer code ('HDFC', 'ICICI', 'SBI', 'AXIS', 'AMEX') or None if unrecognized.
    """
    if not first_page_text:
        return None

    # Check each bank's regex signature patterns
    for bank_code, patterns in BANK_SIGNATURES.items():
        for pattern in patterns:
            if pattern.search(first_page_text):
                return bank_code

    return None


def get_first_page_text(pdf_stream: io.BytesIO) -> str:
    """Extract raw text from the first page of an in-memory PDF stream."""
    pdf_stream.seek(0)
    try:
        doc = pymupdf.open(stream=pdf_stream.getvalue(), filetype="pdf")
        if len(doc) > 0:
            first_page = doc[0]
            text = str(first_page.get_text("text") or "")
            doc.close()
            return text
        doc.close()
    except Exception as e:
        logger.warning("Failed to extract first page text with PyMuPDF: %s", e)

    return ""


def get_parser_for_statement(pdf_stream: io.BytesIO) -> BaseStatementParser:
    """
    Inspect the PDF stream, detect the issuing bank, and return an initialized parser instance.
    Raises UnsupportedStatementError if bank cannot be determined or parser is unavailable.
    """
    # Import parsers here to avoid circular dependencies
    from app.parsers.amex import AmexStatementParser
    from app.parsers.axis import AxisStatementParser
    from app.parsers.hdfc import HdfcStatementParser
    from app.parsers.icici import IciciStatementParser
    from app.parsers.sbi import SbiStatementParser

    parser_map: dict[str, type[BaseStatementParser]] = {
        "HDFC": HdfcStatementParser,
        "ICICI": IciciStatementParser,
        "SBI": SbiStatementParser,
        "AXIS": AxisStatementParser,
        "AMEX": AmexStatementParser,
    }

    first_page_text = get_first_page_text(pdf_stream)
    bank_code = detect_bank(first_page_text)

    if not bank_code:
        raise UnsupportedStatementError(
            message="Unable to detect a supported issuing bank from the statement.",
            details={"preview_length": len(first_page_text)},
        )

    parser_cls = parser_map.get(bank_code)
    if not parser_cls:
        raise UnsupportedStatementError(
            message=f"Parser for issuing bank '{bank_code}' is not implemented.",
            details={"bank": bank_code},
        )

    return parser_cls()
