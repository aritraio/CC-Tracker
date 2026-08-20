import logging
from decimal import Decimal

from app.schemas.analytics import (
    MicroSpendMetrics,
    RecurringAnalysis,
    SpendMetrics,
    StatementAnalytics,
    TemporalMetrics,
)
from app.schemas.anomalies import (
    AnomalyDetectionResult,
    DetectorType,
    Finding,
    FindingSeverity,
    HistoricalProfile,
)
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.recommendations import (
    Recommendation,
    RecommendationEvidence,
    RecommendationResult,
    RecommendationStatus,
    RecommendationType,
)
from app.schemas.statement import StatementHeader

logger = logging.getLogger(__name__)

# Known rewards/cashback rates for top Indian merchants
MERCHANT_REWARD_RATES: dict[str, float] = {
    "Amazon": 0.05,
    "Swiggy": 0.05,
    "Zomato": 0.05,
    "Flipkart": 0.05,
    "Blinkit": 0.04,
    "Zepto": 0.04,
    "Myntra": 0.05,
    "Tata Neu": 0.05,
    "Uber": 0.04,
    "Ola": 0.03,
}


class RecommendationEngine:
    """
    Deterministic, Evidence-Based Financial Recommendation Engine.
    Transforms detected anomalies and financial metrics into conservative, actionable advice.
    """

    def generate_recommendations(
        self,
        findings: list[Finding] | AnomalyDetectionResult,
        analytics: StatementAnalytics,
        transactions: list[CategorizedTransaction] | None = None,
        header: StatementHeader | None = None,
        historical_profile: HistoricalProfile | None = None,
    ) -> RecommendationResult:
        """
        Generate prioritized, evidence-backed recommendations based on deterministic findings.
        """
        finding_list = findings.findings if isinstance(findings, AnomalyDetectionResult) else findings
        recommendations: list[Recommendation] = []

        # Map each finding to one or more actionable recommendations
        for finding in finding_list:
            rec = self._map_finding_to_recommendation(
                finding=finding,
                analytics=analytics,
                header=header,
                historical_profile=historical_profile,
            )
            if rec:
                recommendations.append(rec)

        # If no findings triggered, generate a positive reinforcement recommendation
        if not recommendations:
            recommendations.append(self._create_positive_reinforcement_recommendation(analytics))

        # Sort recommendations by priority (1 is highest) and estimated savings
        recommendations.sort(
            key=lambda r: (r.priority, -float(r.estimated_monthly_savings), -r.confidence_score)
        )

        # Compute conservative, deduplicated total potential monthly savings
        total_savings = self._calculate_deduplicated_savings(recommendations, analytics.spend_metrics)
        high_impact = sum(
            1 for r in recommendations if r.estimated_monthly_savings >= Decimal("1000.00")
        )

        return RecommendationResult(
            recommendations=recommendations,
            total_potential_monthly_savings=total_savings,
            recommendations_count=len(recommendations),
            high_impact_count=high_impact,
        )

    def _map_finding_to_recommendation(
        self,
        finding: Finding,
        analytics: StatementAnalytics,
        header: StatementHeader | None = None,
        historical_profile: HistoricalProfile | None = None,
    ) -> Recommendation | None:
        """Route finding to specific recommendation generator."""
        detector = finding.detector_type

        if detector == DetectorType.CATEGORY_SPIKE:
            return self._recommend_category_reduction(finding, analytics)
        elif detector == DetectorType.FREQUENT_SMALL_SPEND:
            return self._recommend_micro_spend_consolidation(finding, analytics.micro_spend_metrics)
        elif detector == DetectorType.SUBSCRIPTION_BURDEN:
            return self._recommend_subscription_audit(finding, analytics.recurring_analysis)
        elif detector == DetectorType.MERCHANT_CONCENTRATION:
            return self._recommend_merchant_optimization(finding)
        elif detector == DetectorType.SPENDING_ACCELERATION:
            return self._recommend_burn_rate_control(finding, analytics.spend_metrics, historical_profile)
        elif detector == DetectorType.WEEKEND_SPIKE:
            return self._recommend_weekend_pacing(finding, analytics.temporal_metrics)
        elif detector == DetectorType.LATE_NIGHT_SPURT:
            return self._recommend_late_night_control(finding)
        elif detector == DetectorType.HIGH_CREDIT_UTILIZATION:
            return self._recommend_credit_utilization_management(finding, header)
        elif detector == DetectorType.UNUSUAL_PURCHASE:
            return self._recommend_unusual_purchase_review(finding)
        elif detector == DetectorType.FREQUENCY_INFLATION:
            return self._recommend_frequency_management(finding, analytics.spend_metrics)
        return None

    # 1. Category Spike -> Category Reduction
    def _recommend_category_reduction(
        self, finding: Finding, analytics: StatementAnalytics
    ) -> Recommendation:
        cat = finding.evidence.related_category or Category.OTHER_UNCATEGORIZED
        current_spend = Decimal(str(finding.evidence.current_value))
        baseline = (
            Decimal(str(finding.evidence.threshold_or_baseline))
            if finding.evidence.threshold_or_baseline
            else current_spend * Decimal("0.70")
        )
        excess = max(Decimal("0.00"), current_spend - baseline)
        count = finding.evidence.transaction_count or 1
        delta_pct = finding.evidence.delta_percentage or 0.0

        # Category specific calculations
        if cat == Category.FOOD_AND_DINING:
            avg_order = current_spend / Decimal(count) if count > 0 else Decimal("400.00")
            # Cutting 2 orders/week (~8.66 orders/month)
            order_reduction_savings = Decimal("8.66") * avg_order
            estimated_savings = min(excess, order_reduction_savings, current_spend * Decimal("0.30"))
            action = (
                f"Trim food delivery frequency by ~2 orders/week (avg order ₹{avg_order:,.0f}). "
                "Batch weekend restaurant visits to bring monthly dining spend back toward baseline."
            )
            title = "Trim Food & Dining Delivery Orders"
            basis = "Reduction of ~2 food delivery orders per week"
        elif cat == Category.GROCERIES_AND_QUICK_COMMERCE:
            avg_order = current_spend / Decimal(count) if count > 0 else Decimal("300.00")
            # Cutting 3 impulse quick-commerce runs/week + delivery fees
            estimated_savings = min(excess, Decimal("12.0") * avg_order, current_spend * Decimal("0.25"))
            action = (
                "Consolidate quick-commerce runs into scheduled weekly grocery orders to eliminate "
                "impulse cart items and repeated delivery surcharges."
            )
            title = "Consolidate Quick-Commerce Grocery Orders"
            basis = "Consolidation of ad-hoc deliveries into weekly scheduled orders"
        elif cat == Category.SHOPPING:
            estimated_savings = min(excess, current_spend * Decimal("0.25"))
            action = (
                "Apply a 48-hour cooling-off rule before checkout on non-essential online shopping "
                "items above ₹1,000."
            )
            title = "Pace Discretionary Online Shopping"
            basis = "48-hour purchase delay rule on non-essential goods"
        else:
            estimated_savings = min(excess, current_spend * Decimal("0.20"))
            action = (
                f"Set a strict sub-budget cap of ₹{baseline:,.2f} for {cat.value} in your "
                "banking app to arrest cycle overruns."
            )
            title = f"Moderate {cat.value} Outflow"
            basis = f"Capping monthly category budget to historical baseline ₹{baseline:,.2f}"

        estimated_savings = max(Decimal("0.00"), round(estimated_savings, 2))

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.CATEGORY_REDUCTION,
            title=title,
            reason=(
                f"{cat.value} spend increased by {delta_pct:.1f}% to ₹{current_spend:,.2f} "
                f"across {count} transactions (baseline: ₹{baseline:,.2f})."
            ),
            evidence=RecommendationEvidence(
                current_spend=current_spend,
                historical_avg=baseline,
                transaction_count=count,
                top_merchants=finding.evidence.related_merchants,
                excess_amount=excess,
                savings_calculation_basis=basis,
            ),
            estimated_monthly_savings=estimated_savings,
            confidence_score=0.90,
            action=action,
            priority=1 if finding.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH) else 2,
            target_category=cat,
            status=RecommendationStatus.ACTIVE,
        )

    # 2. Frequent Small Spend -> Micro-Spend Consolidation
    def _recommend_micro_spend_consolidation(
        self, finding: Finding, micro_spend: MicroSpendMetrics
    ) -> Recommendation:
        total_micro = micro_spend.total_amount
        count = micro_spend.count
        # Conservative 35% savings from cutting frivolous impulse micro-orders
        savings = round(total_micro * Decimal("0.35"), 2)

        top_merchants_str = ", ".join(micro_spend.top_micro_merchants[:3]) if micro_spend.top_micro_merchants else "convenience merchants"

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.MICRO_SPEND_CONSOLIDATION,
            title="Plug Micro-Spending Leaks (< ₹250)",
            reason=(
                f"{count} small transactions (< ₹250) quietly drained ₹{total_micro:,.2f} "
                f"({micro_spend.percentage_of_spend:.1f}% of total spend) primarily at {top_merchants_str}."
            ),
            evidence=RecommendationEvidence(
                current_spend=total_micro,
                transaction_count=count,
                top_merchants=micro_spend.top_micro_merchants,
                savings_calculation_basis="Consolidation of 35% of impulse micro-transactions",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.88,
            action=(
                "Set a weekly prepaid wallet allowance for micro-expenses (coffee, snacks, quick-cabs) "
                "or consolidate small purchases to eliminate incidental payment friction."
            ),
            priority=2,
            target_category=Category.OTHER_UNCATEGORIZED,
            status=RecommendationStatus.ACTIVE,
        )

    # 3. Subscription Burden -> Subscription Audit
    def _recommend_subscription_audit(
        self, finding: Finding, recurring: RecurringAnalysis
    ) -> Recommendation:
        total_recurring = recurring.total_monthly_recurring
        count = len(recurring.items) or (finding.evidence.transaction_count or 1)
        pct = recurring.recurring_percentage_of_spend or (finding.evidence.delta_percentage or 0.0)
        # Savings estimated as switching to annual (20% discount) or canceling 1 duplicate service
        savings = round(total_recurring * Decimal("0.20"), 2)
        merchant_names = [item.merchant_name for item in recurring.items] or finding.evidence.related_merchants

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.SUBSCRIPTION_AUDIT,
            title="Audit Recurring Subscriptions & Memberships",
            reason=(
                f"Active recurring subscriptions total ₹{total_recurring:,.2f}/month "
                f"({pct:.1f}% of monthly spend) across {count} services."
            ),
            evidence=RecommendationEvidence(
                current_spend=total_recurring,
                transaction_count=count,
                top_merchants=merchant_names,
                savings_calculation_basis="20% optimization via annual billing or canceling 1 unutilized service",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.92,
            action=(
                f"Review recurring charges ({', '.join(merchant_names[:4]) if merchant_names else 'recurring services'}). "
                "Cancel unutilized memberships and switch daily-driver entertainment platforms to discounted annual plans."
            ),
            priority=2,
            target_category=Category.SUBSCRIPTIONS,
            status=RecommendationStatus.ACTIVE,
        )

    # 4. Merchant Concentration -> Merchant Optimization
    def _recommend_merchant_optimization(self, finding: Finding) -> Recommendation:
        merchant_name = finding.evidence.related_merchants[0] if finding.evidence.related_merchants else "Primary Merchant"
        merchant_spend = Decimal(str(finding.evidence.current_value))
        cat = finding.evidence.related_category

        reward_rate = Decimal(str(MERCHANT_REWARD_RATES.get(merchant_name, 0.03)))
        savings = round(merchant_spend * reward_rate, 2)

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.MERCHANT_OPTIMIZATION,
            title=f"Optimize Spend at {merchant_name}",
            reason=(
                f"₹{merchant_spend:,.2f} ({finding.evidence.delta_percentage or 0.0:.1f}% of total spend) "
                f"was concentrated at {merchant_name}."
            ),
            evidence=RecommendationEvidence(
                current_spend=merchant_spend,
                top_merchants=[merchant_name],
                savings_calculation_basis=f"Unlocking {float(reward_rate)*100:.0f}% direct card cashback or milestone rewards",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.86,
            action=(
                f"Route purchases on {merchant_name} through high-cashback category cards (e.g. Amazon Pay ICICI, "
                "Swiggy HDFC, or Flipkart Axis) or leverage merchant gift vouchers at a 4-5% discount."
            ),
            priority=3,
            target_category=cat,
            status=RecommendationStatus.ACTIVE,
        )

    # 5. Spending Acceleration -> Burn Rate Control
    def _recommend_burn_rate_control(
        self,
        finding: Finding,
        spend_metrics: SpendMetrics,
        historical_profile: HistoricalProfile | None = None,
    ) -> Recommendation:
        current_spend = spend_metrics.total_debits
        prev_spend = (
            historical_profile.previous_cycle_spend
            if historical_profile and historical_profile.previous_cycle_spend
            else current_spend * Decimal("0.80")
        )
        excess = max(Decimal("0.00"), current_spend - prev_spend)
        pct_accel = finding.evidence.delta_percentage or 0.0

        savings = round(min(excess, current_spend * Decimal("0.15")), 2)
        weekly_cap = round(prev_spend / Decimal("4.0"), 2)

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.BURN_RATE_CONTROL,
            title="Enforce Weekly Burn-Rate Budget Pacing",
            reason=(
                f"Overall spend accelerated by {pct_accel:.1f}% this cycle "
                f"(₹{current_spend:,.2f} vs ₹{prev_spend:,.2f} previous cycle)."
            ),
            evidence=RecommendationEvidence(
                current_spend=current_spend,
                historical_avg=prev_spend,
                excess_amount=excess,
                savings_calculation_basis="Enforcing weekly spending target equal to historical cycle velocity",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.82,
            action=(
                f"Set a weekly spending cap of ₹{weekly_cap:,.2f} (₹{prev_spend:,.2f} / 4) in your "
                "mobile banking app to avoid end-of-cycle budget overruns."
            ),
            priority=1,
            target_category=Category.OTHER_UNCATEGORIZED,
            status=RecommendationStatus.ACTIVE,
        )

    # 6. Weekend Spike -> Weekend Pacing
    def _recommend_weekend_pacing(
        self, finding: Finding, temporal: TemporalMetrics
    ) -> Recommendation:
        weekend_spend = temporal.weekend_spend
        # Moderate weekend leisure outflow by 20%
        savings = round(weekend_spend * Decimal("0.20"), 2)

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.WEEKEND_PACING,
            title="Pace Weekend Leisure & Dining Outflows",
            reason=(
                f"Weekend purchases accounted for ₹{weekend_spend:,.2f} "
                f"({temporal.weekend_percentage:.1f}% of total spend), indicating high leisure concentration."
            ),
            evidence=RecommendationEvidence(
                current_spend=weekend_spend,
                savings_calculation_basis="20% moderation in weekend leisure and dining outflows",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.84,
            action=(
                "Establish a fixed weekend entertainment envelope (e.g. max ₹2,500/weekend) "
                "and designate one weekend day as a no-spend day."
            ),
            priority=3,
            target_category=Category.FOOD_AND_DINING,
            status=RecommendationStatus.ACTIVE,
        )

    # 7. Late Night Spurt -> Impulse Control
    def _recommend_late_night_control(self, finding: Finding) -> Recommendation:
        late_night_spend = Decimal(str(finding.evidence.current_value))
        count = finding.evidence.transaction_count or 1
        # Curbing 50% of late-night impulse orders
        savings = round(late_night_spend * Decimal("0.50"), 2)

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.IMPULSE_CONTROL,
            title="Curtail Late-Night Impulse Orders (11 PM - 4 AM)",
            reason=(
                f"{count} late-night purchases totaled ₹{late_night_spend:,.2f}, driven by "
                "impulsive delivery and quick-commerce orders."
            ),
            evidence=RecommendationEvidence(
                current_spend=late_night_spend,
                transaction_count=count,
                top_merchants=finding.evidence.related_merchants,
                savings_calculation_basis="50% reduction in late-night impulsive food/shopping orders",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.87,
            action=(
                "Set screen time app limits on food delivery apps after 10:30 PM or remove saved card "
                "details to add friction against late-night impulsive purchases."
            ),
            priority=2,
            target_category=finding.evidence.related_category or Category.FOOD_AND_DINING,
            status=RecommendationStatus.ACTIVE,
        )

    # 8. High Credit Utilization -> Utilization Management
    def _recommend_credit_utilization_management(
        self, finding: Finding, header: StatementHeader | None = None
    ) -> Recommendation:
        balance = Decimal(str(finding.evidence.current_value))
        limit = (
            header.credit_limit
            if header and header.credit_limit
            else Decimal(str(finding.evidence.threshold_or_baseline or balance * Decimal("2.0")))
        )
        util_pct = float(finding.evidence.delta_percentage or 40.0)

        # Target 25% utilization
        target_balance = limit * Decimal("0.25")
        mid_cycle_payment = max(Decimal("0.00"), balance - target_balance)

        # Estimated finance charge / credit protection impact (calculated at 3.5% monthly finance charge defense)
        excess_over_30 = max(Decimal("0.00"), balance - (limit * Decimal("0.30")))
        finance_charge_saved = round(max(Decimal("500.00"), excess_over_30 * Decimal("0.035")), 2)

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.UTILIZATION_MANAGEMENT,
            title="Make Mid-Cycle Payment to Protect Credit Score",
            reason=(
                f"Credit utilization stands at {util_pct:.1f}% (₹{balance:,.2f} on a ₹{limit:,.2f} limit), "
                "exceeding the recommended 30% credit bureau threshold."
            ),
            evidence=RecommendationEvidence(
                current_spend=balance,
                historical_avg=limit,
                excess_amount=mid_cycle_payment,
                savings_calculation_basis="Preventing finance charges and avoiding CIBIL score degradation",
            ),
            estimated_monthly_savings=finance_charge_saved,
            confidence_score=0.96,
            action=(
                f"Make a mid-cycle partial payment of ₹{mid_cycle_payment:,.2f} 3-4 days before your statement date "
                "to report < 25% utilization to CIBIL and Experian."
            ),
            priority=1,
            target_category=Category.FEES_AND_CHARGES,
            status=RecommendationStatus.ACTIVE,
        )

    # 9. Unusual Purchase -> Purchase Review
    def _recommend_unusual_purchase_review(self, finding: Finding) -> Recommendation:
        merchant = finding.evidence.related_merchants[0] if finding.evidence.related_merchants else "Unknown Merchant"
        amount = Decimal(str(finding.evidence.current_value))

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.PURCHASE_REVIEW,
            title=f"Review High-Value Outlier: ₹{amount:,.2f} at {merchant}",
            reason=finding.description,
            evidence=RecommendationEvidence(
                current_spend=amount,
                top_merchants=[merchant],
                savings_calculation_basis="Verification of billing accuracy, return policy, and warranty",
            ),
            estimated_monthly_savings=Decimal("0.00"),
            confidence_score=0.85,
            action=(
                f"Confirm transaction legitimacy at {merchant}, verify invoice warranty details, and "
                "check whether zero-cost EMI or merchant cashback terms were correctly applied."
            ),
            priority=3,
            target_category=Category.SHOPPING,
            status=RecommendationStatus.ACTIVE,
        )

    # 10. Frequency Inflation -> Frequency Management
    def _recommend_frequency_management(
        self, finding: Finding, spend_metrics: SpendMetrics
    ) -> Recommendation:
        count = spend_metrics.debit_transaction_count
        pct_growth = finding.evidence.delta_percentage or 30.0
        # Savings from cutting incidental fees/packaging charges (~₹30 per extra transaction)
        excess_count = max(5, int(count * (pct_growth / 100.0) / 2))
        savings = round(Decimal(excess_count) * Decimal("35.00"), 2)

        return Recommendation(
            id=f"rec_{finding.id}",
            finding_id=finding.id,
            type=RecommendationType.FREQUENCY_MANAGEMENT,
            title="Batch Frequent Transactions to Cut Incidental Fees",
            reason=(
                f"Transaction count grew by {pct_growth:.1f}% ({count} transactions) while average "
                f"spend per order stayed constant at ₹{spend_metrics.average_transaction_amount:,.2f}."
            ),
            evidence=RecommendationEvidence(
                current_spend=spend_metrics.total_debits,
                transaction_count=count,
                savings_calculation_basis="Saving incidental handling, packaging, and convenience charges by batching orders",
            ),
            estimated_monthly_savings=savings,
            confidence_score=0.80,
            action=(
                "Consolidate daily recurring small purchases into planned bi-weekly baskets to reduce "
                "processing friction and incidental platform fees."
            ),
            priority=4,
            target_category=Category.OTHER_UNCATEGORIZED,
            status=RecommendationStatus.ACTIVE,
        )

    # Clean Statement -> Positive Reinforcement
    def _create_positive_reinforcement_recommendation(
        self, analytics: StatementAnalytics
    ) -> Recommendation:
        total_spend = analytics.spend_metrics.total_debits
        return Recommendation(
            id="rec_positive_reinforcement",
            finding_id=None,
            type=RecommendationType.POSITIVE_REINFORCEMENT,
            title="Excellent Spending Discipline",
            reason=(
                f"Your spending of ₹{total_spend:,.2f} is well-distributed across categories with "
                "no abnormal spikes, micro-spend leaks, or elevated credit utilization."
            ),
            evidence=RecommendationEvidence(
                current_spend=total_spend,
                transaction_count=analytics.spend_metrics.debit_transaction_count,
                savings_calculation_basis="Optimal spending velocity and balanced category distribution",
            ),
            estimated_monthly_savings=Decimal("0.00"),
            confidence_score=0.95,
            action=(
                "Continue maintaining current budgeting habits and check card reward portals to ensure "
                "accumulated reward points are redeemed before expiry."
            ),
            priority=1,
            target_category=None,
            status=RecommendationStatus.ACTIVE,
        )

    def _calculate_deduplicated_savings(
        self, recommendations: list[Recommendation], spend_metrics: SpendMetrics
    ) -> Decimal:
        """
        Conservative deduplication to avoid double-counting overlapping savings.
        E.g. Category reduction and Burn rate control both target the same spend.
        """
        category_savings = Decimal("0.00")
        micro_savings = Decimal("0.00")
        sub_savings = Decimal("0.00")
        reward_savings = Decimal("0.00")
        other_savings = Decimal("0.00")

        for rec in recommendations:
            if rec.type == RecommendationType.CATEGORY_REDUCTION:
                category_savings += rec.estimated_monthly_savings
            elif rec.type == RecommendationType.MICRO_SPEND_CONSOLIDATION:
                micro_savings += rec.estimated_monthly_savings
            elif rec.type == RecommendationType.SUBSCRIPTION_AUDIT:
                sub_savings += rec.estimated_monthly_savings
            elif rec.type == RecommendationType.MERCHANT_OPTIMIZATION:
                reward_savings += rec.estimated_monthly_savings
            elif rec.type in (
                RecommendationType.IMPULSE_CONTROL,
                RecommendationType.FREQUENCY_MANAGEMENT,
            ):
                other_savings += rec.estimated_monthly_savings

        # Total conservative aggregate: category + micro + sub + rewards + others
        total = category_savings + micro_savings + sub_savings + reward_savings + other_savings

        # Total savings can never exceed 50% of total debits to stay credible
        max_allowed = spend_metrics.total_debits * Decimal("0.50")
        return min(round(total, 2), max_allowed)


# Global singleton
_default_recommendation_engine: RecommendationEngine | None = None


def get_default_recommendation_engine() -> RecommendationEngine:
    global _default_recommendation_engine
    if _default_recommendation_engine is None:
        _default_recommendation_engine = RecommendationEngine()
    return _default_recommendation_engine
