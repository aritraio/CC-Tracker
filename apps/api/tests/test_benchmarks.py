import time
from datetime import date
from decimal import Decimal
import pytest

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.categorization.engine import get_default_categorization_engine
from app.recommendations.engine import get_default_recommendation_engine
from app.schemas.statement import ExtractedTransaction, StatementHeader, TransactionType
from app.services.reconciliation import reconcile_statement
from app.services.validator import validate_transactions


def generate_large_statement_corpus(count: int = 150) -> tuple[StatementHeader, list[ExtractedTransaction]]:
    """Generate a heavy synthetic statement with 150+ transactions across various merchants."""
    sample_merchants = [
        ("SWIGGY BANGALORE", Decimal("420.00"), TransactionType.PURCHASE),
        ("ZOMATO GURGAON", Decimal("850.00"), TransactionType.PURCHASE),
        ("AMAZON SELLER SERVICES", Decimal("2100.00"), TransactionType.PURCHASE),
        ("FLIPKART INTERNET", Decimal("1450.00"), TransactionType.PURCHASE),
        ("BLINKIT COMMERCE", Decimal("380.00"), TransactionType.PURCHASE),
        ("ZEPTO DELIVERY", Decimal("290.00"), TransactionType.PURCHASE),
        ("UBER INDIA SYSTEMS", Decimal("340.00"), TransactionType.PURCHASE),
        ("SHELL PETROL PUMP", Decimal("2500.00"), TransactionType.PURCHASE),
        ("NETFLIX ENTERTAINMENT", Decimal("649.00"), TransactionType.PURCHASE),
        ("SPOTIFY INDIA", Decimal("119.00"), TransactionType.PURCHASE),
        ("MAKEMYTRIP INDIA", Decimal("6500.00"), TransactionType.PURCHASE),
        ("APOLLO PHARMACY", Decimal("720.00"), TransactionType.PURCHASE),
        ("AIRTEL PREPAID RECHARGE", Decimal("399.00"), TransactionType.PURCHASE),
        ("SWIGGY REFUND", Decimal("150.00"), TransactionType.REFUND),
        ("ANNUAL CARD MEMBERSHIP FEE", Decimal("1000.00"), TransactionType.FEE),
    ]

    transactions: list[ExtractedTransaction] = []
    total_debits = Decimal("0.00")
    total_credits = Decimal("0.00")

    for i in range(count):
        m_name, m_amount, m_type = sample_merchants[i % len(sample_merchants)]
        day = (i % 28) + 1
        txn = ExtractedTransaction(
            transaction_date=date(2026, 7, day),
            merchant_raw=f"{m_name} #{i}",
            amount=m_amount,
            transaction_type=m_type,
            source_page=(i // 25) + 1,
        )
        transactions.append(txn)
        if m_type == TransactionType.REFUND:
            total_credits += m_amount
        else:
            total_debits += m_amount

    header = StatementHeader(
        issuer="HDFC Bank",
        card_last_4="8888",
        statement_period_start=date(2026, 7, 1),
        statement_period_end=date(2026, 7, 31),
        total_debits=total_debits,
        total_credits=total_credits,
        total_amount_due=total_debits - total_credits,
        credit_limit=Decimal("300000.00"),
    )

    return header, transactions


def test_benchmark_full_processing_pipeline() -> None:
    """
    Benchmark the complete pipeline:
    Reconciliation -> Validation -> 3-Tier Categorization -> Analytics -> 10 Anomaly Detectors -> Recommendations
    Requirement: SLA < 2.0 seconds for 150+ transactions.
    """
    header, raw_txns = generate_large_statement_corpus(count=150)

    start_time = time.perf_counter()

    # 1. Reconciliation
    reconciliation = reconcile_statement(header=header, transactions=raw_txns)
    assert reconciliation.status == "VALIDATED"

    # 2. Validation
    validation = validate_transactions(header=header, transactions=raw_txns)
    assert validation.is_valid is True

    # 3. Categorization (150 transactions)
    cat_engine = get_default_categorization_engine()
    categorized, cat_stats = cat_engine.categorize_batch(raw_txns)
    assert len(categorized) == 150

    # 4. Deterministic Analytics Engine
    analytics_engine = get_default_analytics_engine()
    analytics = analytics_engine.compute_analytics(categorized, header)

    # 5. 10 Anomaly Detectors
    anomalies = run_anomaly_detection(categorized, analytics, header)

    # 6. Recommendation Engine
    rec_engine = get_default_recommendation_engine()
    recommendations = rec_engine.generate_recommendations(anomalies, analytics, categorized, header)

    elapsed_time = time.perf_counter() - start_time

    # Assert SLA
    assert elapsed_time < 2.0, f"Full pipeline took {elapsed_time:.3f}s (exceeded 2.0s SLA limit)"
    assert cat_stats.hit_rate >= 0.90, f"Categorization hit rate was {cat_stats.hit_rate}"
    assert recommendations.recommendations_count > 0
