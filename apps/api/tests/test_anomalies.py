from datetime import date
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from app.analytics.anomalies import (
    detect_category_spike,
    detect_frequency_inflation,
    detect_frequent_small_spend,
    detect_high_utilization,
    detect_late_night_spurt,
    detect_merchant_concentration,
    detect_spending_acceleration,
    detect_subscription_burden,
    detect_unusual_purchase,
    detect_weekend_spike,
    run_anomaly_detection,
)
from app.analytics.engine import get_default_analytics_engine
from app.main import app
from app.schemas.analytics import (
    CategoryBreakdown,
    MerchantConcentration,
    MicroSpendMetrics,
    RecurringAnalysis,
    RecurringItem,
    SpendMetrics,
    TemporalMetrics,
)
from app.schemas.anomalies import DetectorType, FindingSeverity, HistoricalProfile
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.statement import StatementHeader, TransactionType


def test_detect_category_spike() -> None:
    category_breakdown = [
        CategoryBreakdown(
            category=Category.FOOD_AND_DINING,
            total_amount=Decimal("8000.00"),  # Baseline 4000 -> 2.0x spike
            percentage=40.0,
            transaction_count=15,
            average_amount=Decimal("533.33"),
            top_merchants=["Swiggy", "Zomato"],
        ),
        CategoryBreakdown(
            category=Category.SHOPPING,
            total_amount=Decimal("5000.00"),  # Baseline 4800 -> 1.04x (no spike)
            percentage=25.0,
            transaction_count=3,
            average_amount=Decimal("1666.67"),
            top_merchants=["Amazon"],
        ),
    ]

    profile = HistoricalProfile(
        category_baselines={
            "Food & Dining": Decimal("4000.00"),
            "Shopping": Decimal("4800.00"),
        }
    )

    findings = detect_category_spike(category_breakdown, profile)

    assert len(findings) == 1
    assert findings[0].detector_type == DetectorType.CATEGORY_SPIKE
    assert findings[0].severity == FindingSeverity.HIGH
    assert findings[0].evidence.related_category == Category.FOOD_AND_DINING
    assert findings[0].impact_amount == Decimal("4000.00")


def test_detect_spending_acceleration() -> None:
    spend_metrics = SpendMetrics(
        total_debits=Decimal("45000.00"),
        debit_transaction_count=20,
    )
    profile = HistoricalProfile(
        previous_cycle_spend=Decimal("30000.00")  # 45k / 30k = 1.5x
    )

    finding = detect_spending_acceleration(spend_metrics, profile)

    assert finding is not None
    assert finding.detector_type == DetectorType.SPENDING_ACCELERATION
    assert finding.severity == FindingSeverity.MEDIUM
    assert finding.evidence.delta_percentage == 50.0
    assert finding.impact_amount == Decimal("15000.00")

    # Non-trigger when within 10%
    normal_profile = HistoricalProfile(previous_cycle_spend=Decimal("43000.00"))
    assert detect_spending_acceleration(spend_metrics, normal_profile) is None


def test_detect_frequent_small_spend() -> None:
    micro = MicroSpendMetrics(
        threshold=Decimal("250.00"),
        count=15,
        total_amount=Decimal("2800.00"),
        percentage_of_transactions=30.0,  # > 25%
        percentage_of_spend=16.0,  # > 15%
        top_micro_merchants=["Blinkit", "Zepto"],
    )

    finding = detect_frequent_small_spend(
        micro_spend=micro,
        total_debits=Decimal("17500.00"),
        total_debit_count=50,
    )

    assert finding is not None
    assert finding.detector_type == DetectorType.FREQUENT_SMALL_SPEND
    assert finding.severity == FindingSeverity.MEDIUM
    assert finding.impact_amount == Decimal("1120.00")  # 40% of 2800


def test_detect_merchant_concentration() -> None:
    merchants = [
        MerchantConcentration(
            merchant_name="Apple Store",
            category=Category.SHOPPING,
            total_amount=Decimal("80000.00"),
            percentage=55.0,  # > 50% -> HIGH
            transaction_count=1,
        ),
        MerchantConcentration(
            merchant_name="Swiggy",
            category=Category.FOOD_AND_DINING,
            total_amount=Decimal("15000.00"),
            percentage=10.0,
            transaction_count=12,
        ),
    ]

    findings = detect_merchant_concentration(merchants)

    assert len(findings) == 1
    assert findings[0].detector_type == DetectorType.MERCHANT_CONCENTRATION
    assert findings[0].severity == FindingSeverity.HIGH
    assert findings[0].evidence.related_merchants == ["Apple Store"]


def test_detect_unusual_purchase_z_score() -> None:
    # 5 transactions around 500-1000, 1 outlier at 25000
    txns = [
        CategorizedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="SWIGGY",
            merchant_normalized="Swiggy",
            amount=Decimal("500.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="ZEPTO",
            merchant_normalized="Zepto",
            amount=Decimal("600.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 3),
            merchant_raw="BLINKIT",
            merchant_normalized="Blinkit",
            amount=Decimal("700.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 4),
            merchant_raw="UBER",
            merchant_normalized="Uber",
            amount=Decimal("550.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 5),
            merchant_raw="JEWELLERY STORE",
            merchant_normalized="Jewellery Store",
            amount=Decimal("35000.00"),  # Statistical outlier
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    findings = detect_unusual_purchase(txns)

    assert len(findings) == 1
    assert findings[0].detector_type == DetectorType.UNUSUAL_PURCHASE
    assert findings[0].evidence.current_value == Decimal("35000.00")
    assert findings[0].evidence.related_merchants == ["Jewellery Store"]


def test_detect_subscription_burden() -> None:
    recurring = RecurringAnalysis(
        items=[
            RecurringItem(
                merchant_name="Netflix",
                category=Category.SUBSCRIPTIONS,
                amount=Decimal("649.00"),
                frequency="Monthly",
                annualized_cost=Decimal("7788.00"),
            ),
            RecurringItem(
                merchant_name="Cult.fit",
                category=Category.HEALTHCARE_AND_FITNESS,
                amount=Decimal("1500.00"),
                frequency="Monthly",
                annualized_cost=Decimal("18000.00"),
            ),
        ],
        total_monthly_recurring=Decimal("2149.00"),
        total_annual_recurring=Decimal("25788.00"),
        recurring_percentage_of_spend=18.5,  # > 10%
    )

    finding = detect_subscription_burden(recurring)

    assert finding is not None
    assert finding.detector_type == DetectorType.SUBSCRIPTION_BURDEN
    assert finding.severity == FindingSeverity.MEDIUM
    assert finding.evidence.delta_percentage == 18.5
    assert len(finding.evidence.related_merchants) == 2


def test_detect_weekend_spike() -> None:
    temporal = TemporalMetrics(
        weekend_spend=Decimal("15000.00"),
        weekday_spend=Decimal("8000.00"),
        weekend_percentage=65.22,  # > 55%
        weekday_percentage=34.78,
    )

    finding = detect_weekend_spike(temporal)

    assert finding is not None
    assert finding.detector_type == DetectorType.WEEKEND_SPIKE
    assert finding.severity == FindingSeverity.MEDIUM
    assert finding.evidence.current_value == Decimal("15000.00")


def test_detect_late_night_spurt() -> None:
    txns = [
        CategorizedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="23:45 SWIGGY LATE NIGHT",
            merchant_normalized="Swiggy",
            amount=Decimal("800.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 5),
            merchant_raw="01:15 ZOMATO MIDNIGHT SNACKS",
            merchant_normalized="Zomato",
            amount=Decimal("650.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 8),
            merchant_raw="02:30 24X7 STORE",
            merchant_normalized="24X7 Store",
            amount=Decimal("700.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    finding = detect_late_night_spurt(txns)

    assert finding is not None
    assert finding.detector_type == DetectorType.LATE_NIGHT_SPURT
    assert finding.evidence.transaction_count == 3
    assert finding.evidence.current_value == Decimal("2150.00")


def test_detect_frequency_inflation() -> None:
    spend_metrics = SpendMetrics(
        debit_transaction_count=45,  # 30 -> 45 (+50%)
        average_transaction_amount=Decimal("510.00"),  # 500 -> 510 (+2%)
    )
    profile = HistoricalProfile(
        previous_cycle_count=30,
        avg_ticket_size=Decimal("500.00"),
    )

    finding = detect_frequency_inflation(spend_metrics, profile)

    assert finding is not None
    assert finding.detector_type == DetectorType.FREQUENCY_INFLATION
    assert finding.severity == FindingSeverity.MEDIUM
    assert finding.evidence.delta_percentage == 50.0


def test_detect_high_utilization() -> None:
    header = StatementHeader(
        issuer="HDFC Bank",
        credit_limit=Decimal("100000.00"),
        total_amount_due=Decimal("65000.00"),  # 65% utilization -> CRITICAL
    )
    spend_metrics = SpendMetrics(total_debits=Decimal("65000.00"))

    finding = detect_high_utilization(header, spend_metrics)

    assert finding is not None
    assert finding.detector_type == DetectorType.HIGH_CREDIT_UTILIZATION
    assert finding.severity == FindingSeverity.CRITICAL
    assert finding.evidence.delta_percentage == 65.0


def test_run_anomaly_detection_orchestration() -> None:
    engine = get_default_analytics_engine()
    header = StatementHeader(
        issuer="HDFC Bank",
        credit_limit=Decimal("100000.00"),
        total_amount_due=Decimal("40000.00"),  # 40% -> HIGH utilization
        statement_period_start=date(2024, 4, 1),
        statement_period_end=date(2024, 4, 10),
    )
    transactions = [
        CategorizedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="PYTM*SWIGGY BANGALORE",
            merchant_normalized="Swiggy",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.FOOD_AND_DINING,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="AMAZON INDIA",
            merchant_normalized="Amazon",
            amount=Decimal("35000.00"),  # Single merchant > 35%
            transaction_type=TransactionType.PURCHASE,
            category=Category.SHOPPING,
        ),
        CategorizedTransaction(
            transaction_date=date(2024, 4, 6),  # Weekend
            merchant_raw="HOTEL TAJ",
            merchant_normalized="Taj Hotels",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.TRAVEL_AND_LODGING,
        ),
    ]

    analytics = engine.compute_analytics(transactions, header)
    result = run_anomaly_detection(transactions, analytics, header)

    assert result.total_findings_count >= 2
    # Verify sorted by severity (HIGH findings first)
    severities = [f.severity for f in result.findings]
    assert FindingSeverity.HIGH in severities


@pytest.mark.asyncio
async def test_anomalies_detect_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "header": {
                "issuer": "HDFC Bank",
                "credit_limit": "100000.00",
                "total_amount_due": "55000.00",
            },
            "transactions": [
                {
                    "transaction_date": "2024-04-01",
                    "merchant_raw": "SWIGGY BANGALORE",
                    "merchant_normalized": "Swiggy",
                    "amount": "500.00",
                    "transaction_type": "PURCHASE",
                    "category": "Food & Dining",
                    "currency": "INR",
                    "source_page": 1,
                    "confidence_score": 1.0,
                },
                {
                    "transaction_date": "2024-04-02",
                    "merchant_raw": "AMAZON INDIA",
                    "merchant_normalized": "Amazon",
                    "amount": "54500.00",
                    "transaction_type": "PURCHASE",
                    "category": "Shopping",
                    "currency": "INR",
                    "source_page": 1,
                    "confidence_score": 1.0,
                },
            ],
        }
        response = await ac.post("/api/v1/anomalies/detect", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "findings" in data
    assert data["total_findings_count"] >= 1
    assert data["critical_count"] >= 1  # 55% utilization
