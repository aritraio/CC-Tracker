import time

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.fixtures.helpers import create_pdf_from_text
from tests.fixtures.sample_texts import (
    AMEX_SAMPLE_TEXT,
    AXIS_SAMPLE_TEXT,
    HDFC_SAMPLE_TEXT,
    ICICI_SAMPLE_TEXT,
    SBI_SAMPLE_TEXT,
)


@pytest.mark.asyncio
async def test_full_pipeline_hdfc_statement() -> None:
    pdf_stream = create_pdf_from_text(HDFC_SAMPLE_TEXT)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("hdfc_statement.pdf", pdf_bytes, "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)

        assert response.status_code == 200
        data = response.json()

        # 1. Header verification
        assert data["header"]["issuer"] == "HDFC Bank"
        assert data["header"]["card_last_4"] == "1234"
        assert data["header"]["total_amount_due"] == "45230.50"

        # 2. Transactions & Categorization
        assert len(data["transactions"]) == 10
        first_txn = data["transactions"][0]
        assert first_txn["merchant_normalized"] == "Swiggy"
        assert first_txn["category"] == "Food & Dining"
        assert first_txn["amount"] == "549.00"

        # 3. Reconciliation
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert data["reconciliation"]["is_balanced"] is True
        assert data["reconciliation"]["discrepancy"] == "0.00"

        # 4. Validation
        assert data["validation"]["is_valid"] is True

        # 5. Analytics
        assert data["analytics"]["spend_metrics"]["total_debits"] == "45230.50"
        assert len(data["analytics"]["category_breakdown"]) > 0

        # 6. Recommendations & Explanation
        assert "recommendations" in data
        assert len(data["recommendations"]["recommendations"]) > 0
        assert "explanation" in data
        assert len(data["explanation"]["action_steps"]) > 0
        assert "HDFC Bank" in data["explanation"]["executive_summary"]


@pytest.mark.asyncio
async def test_full_pipeline_icici_statement() -> None:
    pdf_stream = create_pdf_from_text(ICICI_SAMPLE_TEXT)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("icici_statement.pdf", pdf_bytes, "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["header"]["issuer"] == "ICICI Bank"
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert len(data["transactions"]) == 6
        assert data["analytics"]["spend_metrics"]["total_debits"] == "32450.00"


@pytest.mark.asyncio
async def test_full_pipeline_sbi_statement() -> None:
    pdf_stream = create_pdf_from_text(SBI_SAMPLE_TEXT)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("sbi_statement.pdf", pdf_bytes, "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["header"]["issuer"] == "SBI Card"
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert len(data["transactions"]) == 5
        assert data["analytics"]["spend_metrics"]["total_debits"] == "28950.00"


@pytest.mark.asyncio
async def test_full_pipeline_axis_statement() -> None:
    pdf_stream = create_pdf_from_text(AXIS_SAMPLE_TEXT)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("axis_statement.pdf", pdf_bytes, "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["header"]["issuer"] == "Axis Bank"
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert len(data["transactions"]) == 5


@pytest.mark.asyncio
async def test_full_pipeline_amex_statement() -> None:
    pdf_stream = create_pdf_from_text(AMEX_SAMPLE_TEXT)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("amex_statement.pdf", pdf_bytes, "application/pdf")}
        response = await client.post("/api/v1/statements/parse", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["header"]["issuer"] == "American Express"
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert len(data["transactions"]) == 4


@pytest.mark.asyncio
async def test_statement_validate_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "header": {
                "issuer": "HDFC Bank",
                "total_debits": "5000.00",
                "total_credits": "0.00",
            },
            "transactions": [
                {
                    "transaction_date": "2026-08-01",
                    "merchant_raw": "SWIGGY",
                    "amount": "2000.00",
                    "transaction_type": "PURCHASE",
                    "currency": "INR",
                    "source_page": 1,
                    "confidence_score": 1.0,
                },
                {
                    "transaction_date": "2026-08-02",
                    "merchant_raw": "AMAZON",
                    "amount": "3000.00",
                    "transaction_type": "PURCHASE",
                    "currency": "INR",
                    "source_page": 1,
                    "confidence_score": 1.0,
                },
            ],
            "unparsed_lines": [],
        }

        response = await client.post("/api/v1/statements/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert data["reconciliation"]["discrepancy"] == "0.00"
        assert data["validation"]["is_valid"] is True


@pytest.mark.asyncio
async def test_recommendations_generate_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "header": {
                "issuer": "HDFC Bank",
                "credit_limit": "100000.00",
                "total_amount_due": "45000.00",
            },
            "transactions": [
                {
                    "transaction_date": "2026-08-01",
                    "merchant_raw": "SWIGGY BANGALORE",
                    "merchant_normalized": "Swiggy",
                    "amount": "1500.00",
                    "transaction_type": "PURCHASE",
                    "category": "Food & Dining",
                    "tier": 1,
                    "confidence_score": 1.0,
                },
                {
                    "transaction_date": "2026-08-02",
                    "merchant_raw": "SWIGGY BANGALORE",
                    "merchant_normalized": "Swiggy",
                    "amount": "1200.00",
                    "transaction_type": "PURCHASE",
                    "category": "Food & Dining",
                    "tier": 1,
                    "confidence_score": 1.0,
                },
                {
                    "transaction_date": "2026-08-03",
                    "merchant_raw": "NETFLIX",
                    "merchant_normalized": "Netflix",
                    "amount": "649.00",
                    "transaction_type": "PURCHASE",
                    "category": "Subscriptions",
                    "tier": 1,
                    "confidence_score": 1.0,
                    "is_recurring": True,
                },
            ],
            "generate_explanation": True,
        }

        response = await client.post("/api/v1/recommendations/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "anomalies" in data
        assert "explanation" in data
        assert data["explanation"] is not None
        assert len(data["explanation"]["action_steps"]) > 0


@pytest.mark.asyncio
async def test_performance_benchmark_multipage_statement() -> None:
    """
    Performance Benchmark: 5-page PDF statement containing 50+ transactions
    must parse, reconcile, categorize, analyze, and generate recommendations in < 2.0 seconds.
    """
    # 1. Construct 5-page synthetic statement
    page_1_header = """HDFC BANK
Credit Card Statement
Card No: 4524 XXXX XXXX 9999
Statement Period : 01/03/2024 to 31/03/2024
Statement Date : 31/03/2024
Payment Due Date : 20/04/2024
Total Amount Due : 55,000.00
Minimum Amount Due : 2,750.00
Credit Limit : 4,00,000.00
Available Credit Limit : 3,45,000.00
Opening Balance : 0.00
Total Debits : 55,000.00
Total Credits : 0.00

Date Transaction Description Amount (in Rs.)
"""

    pages = []
    # 50 transactions distributed across 5 pages (10 transactions per page)
    # Total debits = 50 * 1,100 = 55,000.00
    for page_idx in range(5):
        page_lines = [page_1_header] if page_idx == 0 else ["Date Transaction Description Amount (in Rs.)\n"]
        for row_idx in range(10):
            day = (page_idx * 5 + row_idx) % 28 + 1
            date_str = f"{day:02d}/03/2024"
            if row_idx % 4 == 0:
                desc = "SWIGGY BANGALORE IN"
            elif row_idx % 4 == 1:
                desc = "AMAZON RETAIL MUMBAI"
            elif row_idx % 4 == 2:
                desc = "BLINKIT COMMERCE"
            else:
                desc = "UBER INDIA RIDES"
            page_lines.append(f"{date_str} {desc} 1,100.00\n")
        pages.append("".join(page_lines))

    pdf_stream = create_pdf_from_text(pages)
    pdf_bytes = pdf_stream.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("large_statement.pdf", pdf_bytes, "application/pdf")}

        start_time = time.perf_counter()
        response = await client.post("/api/v1/statements/parse", files=files)
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        data = response.json()

        # Verification of extraction correctness
        assert data["header"]["issuer"] == "HDFC Bank"
        assert len(data["transactions"]) == 50
        assert data["reconciliation"]["status"] == "VALIDATED"
        assert data["reconciliation"]["discrepancy"] == "0.00"
        assert data["analytics"]["spend_metrics"]["total_debits"] == "55000.00"
        assert len(data["recommendations"]["recommendations"]) > 0

        # Strict Performance Benchmark: under 2.0 seconds
        assert elapsed_time < 2.0, f"Parsing took {elapsed_time:.2f}s, exceeding 2.0s benchmark limit."
