from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.recommendations.engine import (
    RecommendationEngine,
    get_default_recommendation_engine,
)
from app.recommendations.llm_explainer import (
    DeterministicExplainer,
    LLMExplainer,
    get_default_deterministic_explainer,
)
from app.schemas.analytics import (
    CategoryBreakdown,
    MerchantConcentration,
    MicroSpendMetrics,
    RecurringAnalysis,
    RecurringItem,
    SpendMetrics,
    StatementAnalytics,
    TemporalMetrics,
)
from app.schemas.anomalies import (
    DetectorType,
    Finding,
    FindingEvidence,
    FindingSeverity,
    HistoricalProfile,
)
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.recommendations import (
    LLMExplanationResult,
    RecommendationType,
)
from app.schemas.statement import StatementHeader, TransactionType


@pytest.fixture
def sample_spend_metrics() -> SpendMetrics:
    return SpendMetrics(
        total_debits=Decimal("45000.00"),
        total_credits=Decimal("5000.00"),
        net_spend=Decimal("40000.00"),
        total_transaction_count=35,
        debit_transaction_count=33,
        credit_transaction_count=2,
        average_transaction_amount=Decimal("1363.64"),
        median_transaction_amount=Decimal("650.00"),
        max_transaction_amount=Decimal("12000.00"),
        min_transaction_amount=Decimal("40.00"),
    )


@pytest.fixture
def sample_analytics(sample_spend_metrics: SpendMetrics) -> StatementAnalytics:
    return StatementAnalytics(
        spend_metrics=sample_spend_metrics,
        category_breakdown=[
            CategoryBreakdown(
                category=Category.FOOD_AND_DINING,
                total_amount=Decimal("15000.00"),
                percentage=33.33,
                transaction_count=20,
                average_amount=Decimal("750.00"),
                top_merchants=["Swiggy", "Zomato"],
            ),
            CategoryBreakdown(
                category=Category.SHOPPING,
                total_amount=Decimal("12000.00"),
                percentage=26.67,
                transaction_count=4,
                average_amount=Decimal("3000.00"),
                top_merchants=["Amazon", "Flipkart"],
            ),
            CategoryBreakdown(
                category=Category.SUBSCRIPTIONS,
                total_amount=Decimal("2500.00"),
                percentage=5.56,
                transaction_count=4,
                average_amount=Decimal("625.00"),
                top_merchants=["Netflix", "Spotify", "Hotstar"],
            ),
        ],
        merchant_concentration=[
            MerchantConcentration(
                merchant_name="Swiggy",
                category=Category.FOOD_AND_DINING,
                total_amount=Decimal("9000.00"),
                percentage=20.0,
                transaction_count=12,
            )
        ],
        temporal_metrics=TemporalMetrics(
            daily_spending=[],
            weekday_spend=Decimal("20000.00"),
            weekend_spend=Decimal("25000.00"),
            weekday_percentage=44.44,
            weekend_percentage=55.56,
            avg_daily_burn_rate=Decimal("1500.00"),
            day_of_week_breakdown={},
        ),
        micro_spend_metrics=MicroSpendMetrics(
            threshold=Decimal("250.00"),
            count=15,
            total_amount=Decimal("2250.00"),
            percentage_of_transactions=45.45,
            percentage_of_spend=5.0,
            top_micro_merchants=["Chai Point", "Blinkit", "Zepto"],
        ),
        recurring_analysis=RecurringAnalysis(
            items=[
                RecurringItem(
                    merchant_name="Netflix",
                    category=Category.SUBSCRIPTIONS,
                    amount=Decimal("649.00"),
                    frequency="Monthly",
                    occurrences=1,
                    annualized_cost=Decimal("7788.00"),
                    transaction_dates=[date(2026, 8, 5)],
                ),
                RecurringItem(
                    merchant_name="Spotify",
                    category=Category.SUBSCRIPTIONS,
                    amount=Decimal("119.00"),
                    frequency="Monthly",
                    occurrences=1,
                    annualized_cost=Decimal("1428.00"),
                    transaction_dates=[date(2026, 8, 12)],
                ),
            ],
            total_monthly_recurring=Decimal("768.00"),
            total_annual_recurring=Decimal("9216.00"),
            recurring_percentage_of_spend=1.71,
        ),
    )


def test_recommend_category_spike_food(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_cat_spike_food",
        detector_type=DetectorType.CATEGORY_SPIKE,
        severity=FindingSeverity.HIGH,
        title="Category Spend Spike in Food & Dining (+87.5%)",
        description="Spend in Food & Dining reached ₹15,000.00, which is 87.5% above baseline of ₹8,000.00.",
        evidence=FindingEvidence(
            current_value=Decimal("15000.00"),
            threshold_or_baseline=Decimal("8000.00"),
            delta_percentage=87.5,
            related_category=Category.FOOD_AND_DINING,
            related_merchants=["Swiggy", "Zomato"],
            transaction_count=20,
        ),
        impact_amount=Decimal("7000.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    assert result.recommendations_count == 1
    rec = result.recommendations[0]
    assert rec.type == RecommendationType.CATEGORY_REDUCTION
    assert rec.target_category == Category.FOOD_AND_DINING
    assert rec.priority == 1
    assert "Trim Food & Dining" in rec.title
    assert rec.estimated_monthly_savings > Decimal("0.00")
    assert rec.estimated_monthly_savings <= Decimal("7000.00")  # Less than excess
    assert rec.confidence_score == 0.90
    assert "Trim food delivery frequency" in rec.action


def test_recommend_category_spike_quick_commerce(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_cat_spike_grocery",
        detector_type=DetectorType.CATEGORY_SPIKE,
        severity=FindingSeverity.MEDIUM,
        title="Category Spend Spike in Groceries & Quick-Commerce (+45.0%)",
        description="Quick commerce grocery spend reached ₹6,000.00.",
        evidence=FindingEvidence(
            current_value=Decimal("6000.00"),
            threshold_or_baseline=Decimal("4000.00"),
            delta_percentage=45.0,
            related_category=Category.GROCERIES_AND_QUICK_COMMERCE,
            related_merchants=["Blinkit", "Zepto"],
            transaction_count=18,
        ),
        impact_amount=Decimal("2000.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.CATEGORY_REDUCTION
    assert rec.target_category == Category.GROCERIES_AND_QUICK_COMMERCE
    assert "Consolidate Quick-Commerce" in rec.title
    assert rec.estimated_monthly_savings > Decimal("0.00")


def test_recommend_micro_spend_consolidation(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_frequent_small_spend",
        detector_type=DetectorType.FREQUENT_SMALL_SPEND,
        severity=FindingSeverity.MEDIUM,
        title="Frequent Micro-Spend Leak (< ₹250)",
        description="15 small transactions totaled ₹2,250.00.",
        evidence=FindingEvidence(
            current_value=Decimal("2250.00"),
            delta_percentage=45.45,
            related_merchants=["Chai Point", "Blinkit", "Zepto"],
            transaction_count=15,
        ),
        impact_amount=Decimal("2250.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.MICRO_SPEND_CONSOLIDATION
    assert "Plug Micro-Spending" in rec.title
    # 35% of 2250 = 787.50
    assert rec.estimated_monthly_savings == Decimal("787.50")
    assert rec.confidence_score == 0.88


def test_recommend_subscription_audit(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_subscription_burden",
        detector_type=DetectorType.SUBSCRIPTION_BURDEN,
        severity=FindingSeverity.MEDIUM,
        title="Elevated Subscription Burden (12.5%)",
        description="Recurring payments total ₹4,500.00/month.",
        evidence=FindingEvidence(
            current_value=Decimal("4500.00"),
            delta_percentage=12.5,
            related_category=Category.SUBSCRIPTIONS,
            transaction_count=5,
        ),
        impact_amount=Decimal("4500.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.SUBSCRIPTION_AUDIT
    assert "Audit Recurring Subscriptions" in rec.title
    assert rec.estimated_monthly_savings > Decimal("0.00")
    assert rec.confidence_score == 0.92


def test_recommend_merchant_optimization(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_merchant_concentration_amazon",
        detector_type=DetectorType.MERCHANT_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Merchant Spend Concentration at Amazon (38.0%)",
        description="Amazon captured ₹17,100.00 of total spend.",
        evidence=FindingEvidence(
            current_value=Decimal("17100.00"),
            delta_percentage=38.0,
            related_category=Category.SHOPPING,
            related_merchants=["Amazon"],
        ),
        impact_amount=Decimal("17100.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.MERCHANT_OPTIMIZATION
    assert "Optimize Spend at Amazon" in rec.title
    # 5% of 17100 = 855.00
    assert rec.estimated_monthly_savings == Decimal("855.00")
    assert "cashback" in rec.action.lower()


def test_recommend_spending_acceleration(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_spending_acceleration",
        detector_type=DetectorType.SPENDING_ACCELERATION,
        severity=FindingSeverity.HIGH,
        title="Spending Velocity Acceleration (+50.0%)",
        description="Spend accelerated from ₹30,000 to ₹45,000.",
        evidence=FindingEvidence(
            current_value=Decimal("45000.00"),
            threshold_or_baseline=Decimal("30000.00"),
            delta_percentage=50.0,
            transaction_count=35,
        ),
        impact_amount=Decimal("15000.00"),
        actionable=True,
    )

    profile = HistoricalProfile(previous_cycle_spend=Decimal("30000.00"))

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
        historical_profile=profile,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.BURN_RATE_CONTROL
    assert "Weekly Burn-Rate" in rec.title
    assert rec.estimated_monthly_savings > Decimal("0.00")
    assert "weekly spending cap" in rec.action.lower()


def test_recommend_weekend_spike(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_weekend_spike",
        detector_type=DetectorType.WEEKEND_SPIKE,
        severity=FindingSeverity.MEDIUM,
        title="Disproportionate Weekend Spend (55.6%)",
        description="Weekend spend reached ₹25,000.00.",
        evidence=FindingEvidence(
            current_value=Decimal("25000.00"),
            delta_percentage=55.56,
        ),
        impact_amount=Decimal("25000.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.WEEKEND_PACING
    assert "Weekend Leisure" in rec.title
    # 20% of 25000 = 5000.00
    assert rec.estimated_monthly_savings == Decimal("5000.00")


def test_recommend_late_night_spurt(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_late_night_spurt",
        detector_type=DetectorType.LATE_NIGHT_SPURT,
        severity=FindingSeverity.MEDIUM,
        title="Late-Night Spending Cluster (11 PM - 4 AM)",
        description="4 orders placed late night totaled ₹3,200.00.",
        evidence=FindingEvidence(
            current_value=Decimal("3200.00"),
            related_category=Category.FOOD_AND_DINING,
            related_merchants=["Swiggy", "Zomato"],
            transaction_count=4,
        ),
        impact_amount=Decimal("3200.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.IMPULSE_CONTROL
    assert "Late-Night Impulse" in rec.title
    # 50% of 3200 = 1600.00
    assert rec.estimated_monthly_savings == Decimal("1600.00")


def test_recommend_credit_utilization(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_high_utilization",
        detector_type=DetectorType.HIGH_CREDIT_UTILIZATION,
        severity=FindingSeverity.CRITICAL,
        title="High Credit Utilization (75.0%)",
        description="Credit utilization stands at 75.0% (₹75,000 / ₹100,000).",
        evidence=FindingEvidence(
            current_value=Decimal("75000.00"),
            threshold_or_baseline=Decimal("100000.00"),
            delta_percentage=75.0,
        ),
        impact_amount=Decimal("75000.00"),
        actionable=True,
    )

    header = StatementHeader(
        issuer="HDFC Bank",
        credit_limit=Decimal("100000.00"),
        total_amount_due=Decimal("75000.00"),
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
        header=header,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.UTILIZATION_MANAGEMENT
    assert "Mid-Cycle Payment" in rec.title
    assert rec.priority == 1
    assert rec.confidence_score == 0.96
    assert "mid-cycle partial payment" in rec.action.lower()


def test_recommend_unusual_purchase(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_unusual_purchase_apple",
        detector_type=DetectorType.UNUSUAL_PURCHASE,
        severity=FindingSeverity.MEDIUM,
        title="Statistical Spending Outlier: ₹85,000.00 at Apple Store",
        description="A single purchase of ₹85,000.00 was detected.",
        evidence=FindingEvidence(
            current_value=Decimal("85000.00"),
            related_merchants=["Apple Store"],
        ),
        impact_amount=Decimal("85000.00"),
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.PURCHASE_REVIEW
    assert "Review High-Value Outlier" in rec.title
    assert rec.estimated_monthly_savings == Decimal("0.00")
    assert "warranty" in rec.action.lower()


def test_recommend_frequency_inflation(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    finding = Finding(
        id="finding_frequency_inflation",
        detector_type=DetectorType.FREQUENCY_INFLATION,
        severity=FindingSeverity.MEDIUM,
        title="Transaction Frequency Inflation (+45.0%)",
        description="Transaction count rose by 45.0% while ticket size remained steady.",
        evidence=FindingEvidence(
            current_value=35,
            delta_percentage=45.0,
            transaction_count=35,
        ),
        impact_amount=None,
        actionable=True,
    )

    result = engine.generate_recommendations(
        findings=[finding],
        analytics=sample_analytics,
    )

    rec = result.recommendations[0]
    assert rec.type == RecommendationType.FREQUENCY_MANAGEMENT
    assert "Batch Frequent Transactions" in rec.title
    assert rec.estimated_monthly_savings > Decimal("0.00")


def test_clean_statement_positive_reinforcement(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    result = engine.generate_recommendations(
        findings=[],
        analytics=sample_analytics,
    )

    assert result.recommendations_count == 1
    rec = result.recommendations[0]
    assert rec.type == RecommendationType.POSITIVE_REINFORCEMENT
    assert rec.title == "Excellent Spending Discipline"
    assert rec.estimated_monthly_savings == Decimal("0.00")
    assert result.total_potential_monthly_savings == Decimal("0.00")


def test_conservative_savings_deduplication(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    # Multiple findings
    f1 = Finding(
        id="f1",
        detector_type=DetectorType.CATEGORY_SPIKE,
        severity=FindingSeverity.HIGH,
        title="Spike in Food",
        description="Spike",
        evidence=FindingEvidence(
            current_value=Decimal("15000.00"),
            threshold_or_baseline=Decimal("8000.00"),
            related_category=Category.FOOD_AND_DINING,
            transaction_count=20,
        ),
    )
    f2 = Finding(
        id="f2",
        detector_type=DetectorType.FREQUENT_SMALL_SPEND,
        severity=FindingSeverity.MEDIUM,
        title="Micro spend",
        description="Micro spend",
        evidence=FindingEvidence(current_value=Decimal("2000.00")),
    )
    f3 = Finding(
        id="f3",
        detector_type=DetectorType.MERCHANT_CONCENTRATION,
        severity=FindingSeverity.MEDIUM,
        title="Amazon spend",
        description="Amazon spend",
        evidence=FindingEvidence(
            current_value=Decimal("10000.00"),
            related_merchants=["Amazon"],
        ),
    )

    result = engine.generate_recommendations(
        findings=[f1, f2, f3],
        analytics=sample_analytics,
    )

    assert result.recommendations_count == 3
    # Ensure total savings does not exceed 50% of total debits (45000 * 0.5 = 22500)
    assert result.total_potential_monthly_savings <= Decimal("22500.00")
    assert result.total_potential_monthly_savings > Decimal("0.00")


def test_deterministic_explainer(sample_analytics: StatementAnalytics) -> None:
    explainer = DeterministicExplainer()
    engine = RecommendationEngine()

    finding = Finding(
        id="f1",
        detector_type=DetectorType.CATEGORY_SPIKE,
        severity=FindingSeverity.HIGH,
        title="Category Spend Spike in Food & Dining (+87.5%)",
        description="Food & Dining spend reached ₹15,000.00.",
        evidence=FindingEvidence(
            current_value=Decimal("15000.00"),
            threshold_or_baseline=Decimal("8000.00"),
            related_category=Category.FOOD_AND_DINING,
            transaction_count=20,
        ),
    )
    recs = engine.generate_recommendations([finding], sample_analytics)

    header = StatementHeader(issuer="HDFC Bank", total_amount_due=Decimal("45000.00"))
    result = explainer.generate_explanation(
        analytics=sample_analytics,
        findings=[finding],
        recommendations=recs,
        header=header,
    )

    assert isinstance(result, LLMExplanationResult)
    assert "HDFC Bank" in result.executive_summary
    assert "₹45,000.00" in result.executive_summary
    assert len(result.what_stands_out) > 0
    assert len(result.action_steps) > 0
    assert result.generated_by == "deterministic_template"
    assert result.is_fallback is False


def test_llm_explainer_fallback_when_no_api_key(sample_analytics: StatementAnalytics) -> None:
    with patch("app.recommendations.llm_explainer.settings.GEMINI_API_KEY", None):
        explainer = LLMExplainer()
        engine = RecommendationEngine()
        recs = engine.generate_recommendations([], sample_analytics)

        result = explainer.explain(
            analytics=sample_analytics,
            findings=[],
            recommendations=recs,
        )

        assert isinstance(result, LLMExplanationResult)
        assert result.generated_by == "deterministic_template"


def test_llm_explainer_with_mocked_gemini(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    recs = engine.generate_recommendations([], sample_analytics)

    mock_json_response = """
    {
      "executive_summary": "Your monthly spend of ₹45,000 across 33 transactions is well managed.",
      "what_stands_out": [
        {
          "finding_title": "Food & Dining Spend",
          "observation": "Food delivery made up 33% of your total monthly spend.",
          "urgency": "This Month"
        }
      ],
      "action_steps": [
        {
          "step_number": 1,
          "title": "Batch Meal Prep",
          "description": "Reduce delivery frequency by 2 orders per week.",
          "estimated_impact": "Save ~₹2,500/month"
        }
      ],
      "coaching_tone_note": "Great discipline on other categories — small adjustments will yield high savings!"
    }
    """

    mock_gemini_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_json_response
    mock_gemini_model.generate_content.return_value = mock_response

    with patch("app.recommendations.llm_explainer.settings.GEMINI_API_KEY", "fake-key"):
        explainer = LLMExplainer()
        explainer._gemini_client = mock_gemini_model

        result = explainer.explain(
            analytics=sample_analytics,
            findings=[],
            recommendations=recs,
        )

        assert result.executive_summary == "Your monthly spend of ₹45,000 across 33 transactions is well managed."
        assert len(result.what_stands_out) == 1
        assert result.what_stands_out[0].finding_title == "Food & Dining Spend"
        assert len(result.action_steps) == 1
        assert result.action_steps[0].title == "Batch Meal Prep"
        assert result.is_fallback is False


def test_llm_explainer_error_fallback(sample_analytics: StatementAnalytics) -> None:
    engine = RecommendationEngine()
    recs = engine.generate_recommendations([], sample_analytics)

    mock_gemini_model = MagicMock()
    # Simulate API failure / malformed text
    mock_gemini_model.generate_content.side_effect = Exception("API Connection Timeout")

    with patch("app.recommendations.llm_explainer.settings.GEMINI_API_KEY", "fake-key"):
        explainer = LLMExplainer()
        explainer._gemini_client = mock_gemini_model

        result = explainer.explain(
            analytics=sample_analytics,
            findings=[],
            recommendations=recs,
        )

        # Should fall back cleanly
        assert isinstance(result, LLMExplanationResult)
        assert result.generated_by == "deterministic_template"
        assert result.is_fallback is True


def test_full_pipeline_from_analytics_to_recommendations() -> None:
    # Build a list of transactions
    txns = [
        CategorizedTransaction(
            transaction_date=date(2026, 8, 2),
            merchant_raw="SWIGGY BANGALORE",
            merchant_normalized="Swiggy",
            amount=Decimal("1200.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.FOOD_AND_DINING,
        ),
        CategorizedTransaction(
            transaction_date=date(2026, 8, 3),
            merchant_raw="SWIGGY BANGALORE",
            merchant_normalized="Swiggy",
            amount=Decimal("850.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.FOOD_AND_DINING,
        ),
        CategorizedTransaction(
            transaction_date=date(2026, 8, 4),
            merchant_raw="NETFLIX.COM",
            merchant_normalized="Netflix",
            amount=Decimal("649.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.SUBSCRIPTIONS,
            is_recurring=True,
        ),
        CategorizedTransaction(
            transaction_date=date(2026, 8, 5),
            merchant_raw="CHAI POINT",
            merchant_normalized="Chai Point",
            amount=Decimal("120.00"),
            transaction_type=TransactionType.PURCHASE,
            category=Category.FOOD_AND_DINING,
        ),
    ]

    header = StatementHeader(
        issuer="HDFC Bank",
        credit_limit=Decimal("50000.00"),
        total_amount_due=Decimal("2819.00"),
    )

    analytics_engine = get_default_analytics_engine()
    analytics = analytics_engine.compute_analytics(txns, header)

    profile = HistoricalProfile(
        category_baselines={"Food & Dining": Decimal("500.00")},
        previous_cycle_spend=Decimal("1500.00"),
    )

    findings_res = run_anomaly_detection(
        analytics=analytics,
        transactions=txns,
        header=header,
        historical_profile=profile,
    )

    rec_engine = get_default_recommendation_engine()
    recs = rec_engine.generate_recommendations(
        findings=findings_res,
        analytics=analytics,
        transactions=txns,
        header=header,
        historical_profile=profile,
    )

    assert recs.recommendations_count > 0

    explainer = get_default_deterministic_explainer()
    explanation = explainer.generate_explanation(
        analytics=analytics,
        findings=findings_res,
        recommendations=recs,
        header=header,
    )

    assert len(explanation.action_steps) > 0
    assert len(explanation.what_stands_out) > 0
    assert "HDFC Bank" in explanation.executive_summary
