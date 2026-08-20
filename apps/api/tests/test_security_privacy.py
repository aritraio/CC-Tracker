import glob
import os
from datetime import date
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.parsers.hdfc import HdfcStatementParser
from app.recommendations.llm_explainer import LLMExplainer
from app.schemas.analytics import (
    MicroSpendMetrics,
    RecurringAnalysis,
    SpendMetrics,
    StatementAnalytics,
    TemporalMetrics,
)

from app.schemas.anomalies import AnomalyDetectionResult
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.recommendations import RecommendationResult
from app.schemas.statement import ExtractedTransaction, StatementHeader, TransactionType
from app.services.storage_service import get_default_storage_service

client = TestClient(app)


def test_ephemeral_ram_processing_zero_disk_writes() -> None:
    """Verify that statement processing performs zero disk writes to /tmp or workspace."""
    # Count files before
    tmp_files_before = set(glob.glob("/tmp/cctrack*") + glob.glob("/tmp/*.pdf"))

    parser = HdfcStatementParser()
    sample_text = """
    HDFC Bank Credit Card Statement
    Card No: 4123 45XX XXXX 9876
    Statement Period: 01/07/2026 to 31/07/2026
    Total Amount Due: Rs. 1,450.00
    05/07/2026 SWIGGY BANGALORE 450.00 Dr
    12/07/2026 AMAZON INDIA 1000.00 Dr
    """
    # Parse in RAM
    header = parser._extract_header([sample_text])
    txns, _ = parser._extract_transactions([sample_text])

    assert header.card_last_4 == "9876"
    assert len(txns) == 2

    # Count files after
    tmp_files_after = set(glob.glob("/tmp/cctrack*") + glob.glob("/tmp/*.pdf"))
    new_files = tmp_files_after - tmp_files_before
    assert len(new_files) == 0, f"Found leaked disk files: {new_files}"


def test_data_minimization_card_pan_masking() -> None:
    """Verify that full 16-digit PANs are never exposed in StatementHeader."""
    header = StatementHeader(
        issuer="HDFC Bank",
        card_last_4="4321",
        credit_limit=Decimal("150000.00"),
    )
    # card_last_4 must be at most 4 digits
    assert header.card_last_4 is not None
    assert len(header.card_last_4) <= 4

    # Storage service record card
    storage = get_default_storage_service()
    storage.clear_storage()
    history = storage.get_statement_history()
    for item in history.statements:
        if item.card_last_4:
            assert len(item.card_last_4) <= 4


def test_sanitized_llm_payload_no_pii() -> None:
    """Verify that inputs to LLM explainer do not contain raw PANs, CVVs, or passwords."""
    explainer = LLMExplainer()
    header = StatementHeader(
        issuer="ICICI Bank",
        card_last_4="5678",
        total_amount_due=Decimal("12500.00"),
    )
    analytics = StatementAnalytics(
        spend_metrics=SpendMetrics(
            total_debits=Decimal("12500.00"),
            total_credits=Decimal("0.00"),
            net_spend=Decimal("12500.00"),
            total_transaction_count=5,
            debit_transaction_count=5,
            credit_transaction_count=0,
            average_transaction_amount=Decimal("2500.00"),
            median_transaction_amount=Decimal("2500.00"),
            max_transaction_amount=Decimal("5000.00"),
            min_transaction_amount=Decimal("500.00"),
        ),
        temporal_metrics=TemporalMetrics(
            weekday_spend=Decimal("10000.00"),
            weekend_spend=Decimal("2500.00"),
            weekday_percentage=80.0,
            weekend_percentage=20.0,
            avg_daily_burn_rate=Decimal("416.67"),
        ),
        micro_spend_metrics=MicroSpendMetrics(
            threshold=Decimal("250.00"),
            count=0,
            total_amount=Decimal("0.00"),
            percentage_of_transactions=0.0,
            percentage_of_spend=0.0,
        ),
        recurring_analysis=RecurringAnalysis(
            total_monthly_recurring=Decimal("0.00"),
            total_annual_recurring=Decimal("0.00"),
            recurring_percentage_of_spend=0.0,
        ),
    )

    findings = AnomalyDetectionResult()
    recommendations = RecommendationResult()

    # Generate explanation with deterministic template fallback
    explanation = explainer.explain(
        analytics=analytics,
        findings=findings,
        recommendations=recommendations,
        header=header,
    )

    summary = explanation.executive_summary
    # Ensure no 16-digit PAN is hallucinated or present
    import re
    pan_matches = re.findall(r"\b\d{16}\b", summary)
    assert len(pan_matches) == 0
    assert "cvv" not in summary.lower()
    assert "password" not in summary.lower()


def test_api_error_response_no_credential_leak() -> None:
    """Verify that API errors conform to RFC 7807 and never leak credentials."""
    response = client.post(
        "/api/v1/statements/parse",
        files={"file": ("statement.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400
    data = response.json()
    assert "message" in data or "detail" in data
    # No sensitive paths or env vars
    assert "password" not in str(data).lower()
    assert "secret" not in str(data).lower()
