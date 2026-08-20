from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import HDFC_SAMPLE_TEXT


@pytest.mark.asyncio
async def test_parse_statement_endpoint_success() -> None:
    pdf_stream = create_pdf_from_text(HDFC_SAMPLE_TEXT)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("statement.pdf", pdf_bytes, "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["header"]["issuer"] == "HDFC Bank"
        assert data["header"]["card_last_4"] == "1234"
        assert data["reconciliation_status"] == "VALIDATED"
        assert len(data["transactions"]) == 10
        assert data["transactions"][0]["merchant_raw"] == "SWIGGY BANGALORE IN"


@pytest.mark.asyncio
async def test_parse_statement_invalid_extension() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("statement.txt", b"plain text", "text/plain")}
        response = await client.post("/api/v1/statements/parse", files=files)
        assert response.status_code == 400
        assert "Only PDF statements are supported" in response.json()["detail"]


@pytest.mark.asyncio
async def test_parse_statement_empty_file() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("statement.pdf", b"", "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)
        assert response.status_code == 400
        assert "Empty file uploaded" in response.json()["detail"]


@pytest.mark.asyncio
async def test_parse_statement_unsupported_bank() -> None:
    pdf_stream = create_pdf_from_text("Monthly Gas Utility Invoice - Not a Credit Card")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("statement.pdf", pdf_stream.getvalue(), "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "UNSUPPORTED_STATEMENT_FORMAT"


@pytest.mark.asyncio
async def test_parse_statement_unexpected_exception() -> None:
    pdf_stream = create_pdf_from_text(HDFC_SAMPLE_TEXT)
    transport = ASGITransport(app=app)
    with patch(
        "app.api.v1.endpoints.statements.get_parser_for_statement",
        side_effect=RuntimeError("Unexpected parsing failure"),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("statement.pdf", pdf_stream.getvalue(), "application/pdf")}
            response = await client.post("/api/v1/statements/parse", files=files)
            assert response.status_code == 422
            data = response.json()
            assert data["error_code"] == "STATEMENT_PARSING_FAILED"
            assert "Unexpected parsing failure" in data["message"]
