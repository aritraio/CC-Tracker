from datetime import date
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.analytics import (
    CategoryBreakdown,
    MicroSpendMetrics,
    RecurringAnalysis,
    SpendMetrics,
    StatementAnalytics,
    TemporalMetrics,
)
from app.schemas.anomalies import AnomalyDetectionResult
from app.schemas.categorization import CategorizationStats, CategorizedTransaction, Category
from app.schemas.recommendations import LLMExplanationResult, RecommendationResult
from app.schemas.reconciliation import ReconciliationSummary, ValidationResult
from app.schemas.statement import StatementHeader, TransactionType
from app.schemas.statements_api import ParseStatementResponse
from app.services.storage_service import get_default_storage_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_storage():
    """Reset storage before each test."""
    storage = get_default_storage_service()
    storage.clear_storage()
    yield
    storage.clear_storage()


def create_sample_statement_response() -> ParseStatementResponse:
    """Helper to create a valid ParseStatementResponse fixture."""
    header = StatementHeader(
        issuer="HDFC Bank",
        card_last_4="4321",
        statement_period_start=date(2026, 7, 1),
        statement_period_end=date(2026, 7, 31),
        total_amount_due=Decimal("45000.00"),
        credit_limit=Decimal("200000.00"),
    )
    transactions = [
        CategorizedTransaction(
            transaction_date=date(2026, 7, 5),
            merchant_raw="SWIGGY BANGALORE",
            merchant_normalized="Swiggy",
            amount=Decimal("650.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.FOOD_AND_DINING,
            tier=1,
            is_recurring=False,
            currency="INR",
            source_page=1,
            confidence_score=1.0,
        ),
        CategorizedTransaction(
            transaction_date=date(2026, 7, 10),
            merchant_raw="AMAZON INDIA",
            merchant_normalized="Amazon",
            amount=Decimal("2499.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.SHOPPING,
            tier=1,
            is_recurring=False,
            currency="INR",
            source_page=1,
            confidence_score=1.0,
        ),
    ]
    reconciliation = ReconciliationSummary(
        status="VALIDATED",
        discrepancy=Decimal("0.00"),
        extracted_debits=Decimal("3149.00"),
        extracted_credits=Decimal("0.00"),
        is_balanced=True,
    )
    validation = ValidationResult(is_valid=True)
    cat_stats = CategorizationStats(total_transactions=2, tier1_matches=2, hit_rate=1.0)
    analytics = StatementAnalytics(
        spend_metrics=SpendMetrics(
            total_debits=Decimal("3149.00"),
            total_credits=Decimal("0.00"),
            net_spend=Decimal("3149.00"),
            total_transaction_count=2,
            debit_transaction_count=2,
            credit_transaction_count=0,
            average_transaction_amount=Decimal("1574.50"),
            median_transaction_amount=Decimal("1574.50"),
            max_transaction_amount=Decimal("2499.00"),
            min_transaction_amount=Decimal("650.00"),
        ),
        temporal_metrics=TemporalMetrics(
            weekday_spend=Decimal("3149.00"),
            weekend_spend=Decimal("0.00"),
            weekday_percentage=100.0,
            weekend_percentage=0.0,
            avg_daily_burn_rate=Decimal("101.58"),
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
    anomalies = AnomalyDetectionResult()
    recommendations = RecommendationResult()
    explanation = LLMExplanationResult(
        executive_summary="Sample statement parsed successfully.",
        coaching_tone_note="Keep up the good budgeting habits.",
    )

    return ParseStatementResponse(
        header=header,
        transactions=transactions,
        raw_text_length=1200,
        reconciliation_status="VALIDATED",
        reconciliation_discrepancy=Decimal("0.00"),
        reconciliation=reconciliation,
        validation=validation,
        categorization_stats=cat_stats,
        analytics=analytics,
        anomalies=anomalies,
        recommendations=recommendations,
        explanation=explanation,
    )


def test_save_statement_session() -> None:
    """Test saving parsed statement data via POST /api/v1/statements/save."""
    statement_data = create_sample_statement_response()
    payload = {
        "statement_data": statement_data.model_dump(mode="json"),
        "user_id": "test_user_123",
        "card_name": "HDFC Millennia",
        "save_transactions": True,
        "save_findings": True,
        "save_recommendations": True,
    }

    response = client.post("/api/v1/statements/save", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["statement_id"].startswith("stmt_")
    assert data["saved_transactions_count"] == 2
    assert "saved successfully" in data["message"]


def test_get_statement_history() -> None:
    """Test listing saved statements in history."""
    statement_data = create_sample_statement_response()
    save_payload = {
        "statement_data": statement_data.model_dump(mode="json"),
        "user_id": "user_abc",
        "card_name": "HDFC Regalia",
    }

    client.post("/api/v1/statements/save", json=save_payload)

    response = client.get("/api/v1/statements/history?user_id=user_abc")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    stmt = data["statements"][0]
    assert stmt["issuer"] == "HDFC Bank"
    assert stmt["card_last_4"] == "4321"
    assert stmt["transaction_count"] == 2
    assert float(stmt["total_amount_due"]) == 45000.00


def test_get_statement_by_id() -> None:
    """Test fetching a complete statement by statement ID."""
    statement_data = create_sample_statement_response()
    save_payload = {
        "statement_data": statement_data.model_dump(mode="json"),
        "user_id": "user_xyz",
    }

    save_res = client.post("/api/v1/statements/save", json=save_payload)
    statement_id = save_res.json()["statement_id"]

    # Fetch statement
    response = client.get(f"/api/v1/statements/{statement_id}")
    assert response.status_code == 200
    fetched_data = response.json()
    assert fetched_data["header"]["issuer"] == "HDFC Bank"
    assert len(fetched_data["transactions"]) == 2
    assert fetched_data["transactions"][0]["merchant_normalized"] == "Swiggy"


def test_get_statement_by_id_not_found() -> None:
    """Test 404 response for invalid statement ID."""
    response = client.get("/api/v1/statements/stmt_non_existent_999")
    assert response.status_code == 404
    data = response.json()
    # Problem details format
    error_msg = data.get("message") or data.get("detail", "")
    assert "not found" in error_msg.lower()
