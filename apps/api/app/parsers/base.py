import io
import logging
from abc import ABC, abstractmethod

import pdfplumber
import pymupdf

from app.schemas.statement import ParsedStatement

logger = logging.getLogger(__name__)


class BaseStatementParser(ABC):
    """Abstract base class for all bank-specific credit card statement parsers."""

    issuer_name: str = "UNKNOWN"

    @abstractmethod
    def identify(self, first_page_text: str) -> bool:
        """
        Check whether this parser is responsible for the given statement based on first page text.
        """
        pass

    @abstractmethod
    def parse(self, pdf_stream: io.BytesIO) -> ParsedStatement:
        """
        Extract header metadata and structured line items from an in-memory PDF stream.
        """
        pass

    def extract_text_pages(self, pdf_stream: io.BytesIO) -> list[str]:
        """
        Extract text from each page of the in-memory PDF without saving to disk.
        Tries PyMuPDF first for speed, falls back to pdfplumber if needed.
        """
        pdf_stream.seek(0)
        pages: list[str] = []

        try:
            doc = pymupdf.open(stream=pdf_stream.getvalue(), filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = str(page.get_text("text") or "")
                pages.append(text)
            doc.close()
            if any(p.strip() for p in pages):
                return pages
        except Exception as e:
            logger.warning("PyMuPDF text extraction failed: %s. Falling back to pdfplumber.", e)

        # Fallback to pdfplumber
        pdf_stream.seek(0)
        try:
            with pdfplumber.open(pdf_stream) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
        except Exception as e:
            logger.error("pdfplumber text extraction failed: %s", e)

        return pages

    def extract_tables_by_page(self, pdf_stream: io.BytesIO) -> list[list[list[str | None]]]:
        """
        Extract tabular structures per page using pdfplumber.
        """
        pdf_stream.seek(0)
        all_tables: list[list[list[str | None]]] = []
        try:
            with pdfplumber.open(pdf_stream) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables() or []
                    all_tables.extend(tables)
        except Exception as e:
            logger.warning("Table extraction error: %s", e)
        return all_tables
