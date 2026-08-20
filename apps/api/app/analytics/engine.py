from app.analytics.calculator import (
    calculate_category_breakdown,
    calculate_merchant_concentration,
    calculate_micro_spend_metrics,
    calculate_spend_metrics,
    calculate_temporal_metrics,
)
from app.analytics.recurring import detect_recurring_subscriptions
from app.schemas.analytics import StatementAnalytics
from app.schemas.categorization import CategorizedTransaction
from app.schemas.statement import StatementHeader


class AnalyticsEngine:
    """
    Deterministic Financial Analytics Orchestration Engine.
    Executes vectorized aggregations, temporal burn analysis, and recurring detectors.
    """

    def compute_analytics(
        self,
        transactions: list[CategorizedTransaction],
        header: StatementHeader | None = None,
    ) -> StatementAnalytics:
        """Compute full analytical profile from categorized transactions and optional statement header."""
        spend_metrics = calculate_spend_metrics(transactions)
        total_debits = spend_metrics.total_debits

        category_breakdown = calculate_category_breakdown(transactions, total_debits)
        merchant_concentration = calculate_merchant_concentration(transactions, total_debits)

        start_date = header.statement_period_start if header else None
        end_date = header.statement_period_end if header else None
        temporal_metrics = calculate_temporal_metrics(transactions, start_date, end_date)

        micro_spend_metrics = calculate_micro_spend_metrics(transactions, total_debits)
        recurring_analysis = detect_recurring_subscriptions(transactions, total_debits)

        return StatementAnalytics(
            spend_metrics=spend_metrics,
            category_breakdown=category_breakdown,
            merchant_concentration=merchant_concentration,
            temporal_metrics=temporal_metrics,
            micro_spend_metrics=micro_spend_metrics,
            recurring_analysis=recurring_analysis,
        )


# Global singleton
_default_analytics_engine: AnalyticsEngine | None = None


def get_default_analytics_engine() -> AnalyticsEngine:
    global _default_analytics_engine
    if _default_analytics_engine is None:
        _default_analytics_engine = AnalyticsEngine()
    return _default_analytics_engine
