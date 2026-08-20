from datetime import date
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from app.analytics.calculator import (
    calculate_category_breakdown,
    calculate_merchant_concentration,
    calculate_micro_spend_metrics,
    calculate_spend_metrics,
    calculate_temporal_metrics,
)
from app.analytics.engine import AnalyticsEngine, get_default_analytics_engine
from app.analytics.recurring import detect_recurring_subscriptions
from app.main import app
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.statement import StatementHeader, TransactionType


@pytest.fixture
def sample_transactions() -> list[CategorizedTransaction]:
    return [
        CategorizedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="PYTM*SWIGGY BANGALORE",
            merchant_normalized="Swiggy",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.FOOD_AND_DINING,
            subcategory="Food Delivery",
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="AMAZON INDIA",
            merchant_normalized="Amazon",
            amount=Decimal("2500.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.SHOPPING,
            subcategory="E-Commerce",
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 5),  # Friday
            merchant_raw="ZEPTO QUICK",
            merchant_normalized="Zepto",
            amount=Decimal("150.00"),  # Micro spend <= 250
            transaction_type=TransactionType.PURCHASE,
            category=Category.GROCERIES_AND_QUICK_COMMERCE,
            subcategory="Quick Commerce",
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 6),  # Saturday (Weekend)
            merchant_raw="HPCL PETROL PUMP",
            merchant_normalized="HPCL Petrol",
            amount=Decimal("2000.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.TRANSPORT_AND_FUEL,
            subcategory="Fuel",
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 7),  # Sunday (Weekend)
            merchant_raw="NETFLIX ENTERTAINMENT",
            merchant_normalized="Netflix",
            amount=Decimal("649.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.SUBSCRIPTIONS,
            subcategory="OTT Streaming",
            is_recurring=True,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 10),
            merchant_raw="AUTOPAY PAYMENT",
            merchant_normalized="Autopay Payment",
            amount=Decimal("3000.00"),
            transaction_type=TransactionType.PAYMENT,
            category=Category.OTHER_UNCATEGORIZED,
        ),
    ]


def test_calculate_spend_metrics_empty() -> None:
    metrics = calculate_spend_metrics([])
    assert metrics.total_debits == Decimal("0.00")
    assert metrics.total_credits == Decimal("0.00")
    assert metrics.net_spend == Decimal("0.00")
    assert metrics.total_transaction_count == 0


def test_calculate_spend_metrics(sample_transactions: list[CategorizedTransaction]) -> None:
    metrics = calculate_spend_metrics(sample_transactions)

    # Debits: 450 + 2500 + 150 + 2000 + 649 = 5749.00
    # Credits: 3000.00
    # Net: 5749 - 3000 = 2749.00
    assert metrics.total_debits == Decimal("5749.00")
    assert metrics.total_credits == Decimal("3000.00")
    assert metrics.net_spend == Decimal("2749.00")
    assert metrics.debit_transaction_count == 5
    assert metrics.credit_transaction_count == 1
    assert metrics.total_transaction_count == 6

    # Average: 5749 / 5 = 1149.80
    assert metrics.average_transaction_amount == Decimal("1149.80")
    # Sorted debits: [150, 450, 649, 2000, 2500] -> Median = 649.00
    assert metrics.median_transaction_amount == Decimal("649.00")
    assert metrics.max_transaction_amount == Decimal("2500.00")
    assert metrics.min_transaction_amount == Decimal("150.00")


def test_calculate_category_breakdown(sample_transactions: list[CategorizedTransaction]) -> None:
    total_debits = Decimal("5749.00")
    breakdown = calculate_category_breakdown(sample_transactions, total_debits)

    assert len(breakdown) == 5  # Shopping, Transport, Subscriptions, Food, Groceries
    categories = {b.category for b in breakdown}
    assert Category.SHOPPING in categories
    assert Category.TRANSPORT_AND_FUEL in categories
    assert Category.SUBSCRIPTIONS in categories
    assert Category.FOOD_AND_DINING in categories
    assert Category.GROCERIES_AND_QUICK_COMMERCE in categories

    # Verify percentages sum up to 100% (within 0.05% rounding)
    total_pct = sum(b.percentage for b in breakdown)
    assert 99.9 <= total_pct <= 100.1

    # Sorted descending by amount: Shopping (2500) > Transport (2000) > Subscriptions (649) ...
    assert breakdown[0].category == Category.SHOPPING
    assert breakdown[0].total_amount == Decimal("2500.00")
    assert breakdown[0].top_merchants == ["Amazon"]


def test_calculate_merchant_concentration(
    sample_transactions: list[CategorizedTransaction],
) -> None:
    total_debits = Decimal("5749.00")
    concentration = calculate_merchant_concentration(sample_transactions, total_debits, top_n=3)

    assert len(concentration) == 3
    assert concentration[0].merchant_name == "Amazon"
    assert concentration[0].total_amount == Decimal("2500.00")
    # Amazon percentage: (2500 / 5749) * 100 = 43.49%
    assert concentration[0].percentage == 43.49
    assert concentration[1].merchant_name == "HPCL Petrol"


def test_calculate_temporal_metrics(sample_transactions: list[CategorizedTransaction]) -> None:
    temporal = calculate_temporal_metrics(
        sample_transactions,
        period_start=date(2024, 4, 1),
        period_end=date(2024, 4, 10),
    )

    # Total debits = 5749.00
    # Weekend spend (April 6 Sat + April 7 Sun) = 2000 + 649 = 2649.00
    # Weekday spend (April 1 + 2 + 5) = 450 + 2500 + 150 = 3100.00
    assert temporal.weekend_spend == Decimal("2649.00")
    assert temporal.weekday_spend == Decimal("3100.00")
    assert temporal.weekday_percentage == 53.92
    assert temporal.weekend_percentage == 46.08

    # Daily spending series has 5 active dates
    assert len(temporal.daily_spending) == 5
    assert temporal.daily_spending[-1].cumulative_amount == Decimal("5749.00")

    # 10 days in cycle -> 5749.00 / 10 = 574.90 avg daily burn
    assert temporal.avg_daily_burn_rate == Decimal("574.90")
    assert "Saturday" in temporal.day_of_week_breakdown
    assert temporal.day_of_week_breakdown["Saturday"] == Decimal("2000.00")


def test_calculate_micro_spend_metrics(sample_transactions: list[CategorizedTransaction]) -> None:
    total_debits = Decimal("5749.00")
    micro = calculate_micro_spend_metrics(
        sample_transactions, total_debits, threshold=Decimal("250.00")
    )

    # Only Zepto (₹150.00) is <= 250
    assert micro.count == 1
    assert micro.total_amount == Decimal("150.00")
    assert micro.percentage_of_transactions == 20.0  # 1 out of 5 debit transactions
    assert micro.percentage_of_spend == 2.61  # (150 / 5749) * 100
    assert micro.top_micro_merchants == ["Zepto"]


def test_detect_recurring_subscriptions(sample_transactions: list[CategorizedTransaction]) -> None:
    total_debits = Decimal("5749.00")
    recurring = detect_recurring_subscriptions(sample_transactions, total_debits)

    # Netflix ₹649 monthly
    assert len(recurring.items) == 1
    item = recurring.items[0]
    assert item.merchant_name == "Netflix"
    assert item.frequency == "Monthly"
    assert item.amount == Decimal("649.00")
    assert item.annualized_cost == Decimal("7788.00")  # 649 * 12

    assert recurring.total_monthly_recurring == Decimal("649.00")
    assert recurring.total_annual_recurring == Decimal("7788.00")


def test_analytics_engine_orchestrator(sample_transactions: list[CategorizedTransaction]) -> None:
    engine = AnalyticsEngine()
    header = StatementHeader(
        issuer="HDFC Bank",
        statement_period_start=date(2024, 4, 1),
        statement_period_end=date(2024, 4, 10),
    )

    analytics = engine.compute_analytics(sample_transactions, header)

    assert analytics.spend_metrics.total_debits == Decimal("5749.00")
    assert len(analytics.category_breakdown) == 5
    assert len(analytics.merchant_concentration) == 5
    assert analytics.temporal_metrics.weekday_spend == Decimal("3100.00")
    assert analytics.micro_spend_metrics.count == 1
    assert len(analytics.recurring_analysis.items) == 1

    # Test singleton
    assert get_default_analytics_engine() is not None


@pytest.mark.asyncio
async def test_analytics_compute_endpoint(
    sample_transactions: list[CategorizedTransaction],
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "header": {
                "issuer": "HDFC Bank",
                "statement_period_start": "2024-04-01",
                "statement_period_end": "2024-04-10",
            },
            "transactions": [t.model_dump(mode="json") for t in sample_transactions],
        }
        response = await ac.post("/api/v1/analytics/compute", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "spend_metrics" in data
    assert data["spend_metrics"]["total_debits"] == "5749.00"
    assert data["spend_metrics"]["net_spend"] == "2749.00"
    assert len(data["category_breakdown"]) == 5
    assert len(data["merchant_concentration"]) == 5
