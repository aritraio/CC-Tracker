import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.categorization import Category
from app.schemas.recommendations import (
    DismissReason,
    RecommendationEventType,
    RecommendationFeedbackRequest,
    RecommendationFeedbackResponse,
    RecommendationStatus,
)

client = TestClient(app)


def test_recommendation_feedback_accept() -> None:
    """Test accepting a recommendation goal."""
    rec_id = "rec_food_reduction_01"
    payload = {
        "event_type": "ACCEPTED",
        "estimated_monthly_savings": "1400.00",
        "target_category": "Food & Dining",
        "metadata": {"client_version": "1.0"},
    }

    response = client.post(f"/api/v1/recommendations/{rec_id}/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommendation_id"] == rec_id
    assert data["current_status"] == "ACCEPTED"
    assert data["recorded_event_id"].startswith("evt_")
    assert "Tracking target savings" in data["message"]


def test_recommendation_feedback_dismiss_with_reason() -> None:
    """Test dismissing a recommendation with structured reason and notes."""
    rec_id = "rec_subscription_audit_02"
    payload = {
        "event_type": "DISMISSED",
        "dismiss_reason": "TOO_RESTRICTIVE",
        "feedback_notes": "I need these subscriptions for remote work.",
        "target_category": "Subscriptions",
    }

    response = client.post(f"/api/v1/recommendations/{rec_id}/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommendation_id"] == rec_id
    assert data["current_status"] == "DISMISSED"
    assert "TOO_RESTRICTIVE" in data["message"]


def test_recommendation_feedback_explore_transactions() -> None:
    """Test recording an explore transactions interaction."""
    rec_id = "rec_micro_spend_03"
    payload = {
        "event_type": "EXPLORED_TRANSACTIONS",
        "metadata": {"drilldown_source": "RecommendationCard"},
    }

    response = client.post(f"/api/v1/recommendations/{rec_id}/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommendation_id"] == rec_id
    assert data["current_status"] == "ACTIVE"


def test_recommendation_feedback_undo_action() -> None:
    """Test resetting an accepted or dismissed recommendation back to active."""
    rec_id = "rec_weekend_pacing_04"
    payload = {
        "event_type": "UNDONE",
        "metadata": {"previous_state": "DISMISSED"},
    }

    response = client.post(f"/api/v1/recommendations/{rec_id}/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommendation_id"] == rec_id
    assert data["current_status"] == "ACTIVE"
    assert "reset to active state" in data["message"]


def test_recommendation_feedback_schema_validation() -> None:
    """Test Pydantic model validation on feedback request."""
    req = RecommendationFeedbackRequest(
        event_type=RecommendationEventType.DISMISSED,
        dismiss_reason=DismissReason.ALREADY_PLANNED,
        feedback_notes="Already unsubscribed",
        estimated_monthly_savings=Decimal("499.00"),
        target_category=Category.SUBSCRIPTIONS,
    )
    assert req.event_type == RecommendationEventType.DISMISSED
    assert req.dismiss_reason == DismissReason.ALREADY_PLANNED
    assert req.estimated_monthly_savings == Decimal("499.00")
