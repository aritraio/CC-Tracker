import math
import re
from decimal import Decimal

from app.schemas.analytics import (
    CategoryBreakdown,
    MerchantConcentration,
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
    FindingEvidence,
    FindingSeverity,
    HistoricalProfile,
)
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.statement import StatementHeader, TransactionType

CREDIT_TRANSACTION_TYPES = {
    TransactionType.PAYMENT,
    TransactionType.REFUND,
    TransactionType.REVERSAL,
    TransactionType.REWARD,
}

SEVERITY_ORDER = {
    FindingSeverity.CRITICAL: 0,
    FindingSeverity.HIGH: 1,
    FindingSeverity.MEDIUM: 2,
    FindingSeverity.LOW: 3,
    FindingSeverity.INFO: 4,
}


# 1. Category Spike Detector
def detect_category_spike(
    category_breakdown: list[CategoryBreakdown],
    historical_profile: HistoricalProfile | None = None,
) -> list[Finding]:
    """Flag categories where current spend > 1.30x historical baseline."""
    findings: list[Finding] = []
    if not historical_profile or not historical_profile.category_baselines:
        return findings

    for cat_item in category_breakdown:
        cat_name = cat_item.category.value
        baseline = historical_profile.category_baselines.get(cat_name)
        if not baseline or baseline <= Decimal("0.00"):
            continue

        ratio = cat_item.total_amount / baseline
        excess = cat_item.total_amount - baseline

        if ratio > Decimal("1.30") and excess >= Decimal("1000.00"):
            pct_increase = float(round((ratio - Decimal("1.00")) * Decimal("100.00"), 2))
            severity = FindingSeverity.HIGH if ratio > Decimal("1.60") else FindingSeverity.MEDIUM

            findings.append(
                Finding(
                    id=f"finding_cat_spike_{cat_item.category.name.lower()}",
                    detector_type=DetectorType.CATEGORY_SPIKE,
                    severity=severity,
                    title=f"Category Spend Spike in {cat_name} (+{pct_increase:.1f}%)",
                    description=(
                        f"Spend in {cat_name} reached ₹{cat_item.total_amount:,.2f}, which is "
                        f"{pct_increase:.1f}% above your baseline of ₹{baseline:,.2f}."
                    ),
                    evidence=FindingEvidence(
                        current_value=cat_item.total_amount,
                        threshold_or_baseline=baseline,
                        delta_percentage=pct_increase,
                        related_category=cat_item.category,
                        related_merchants=cat_item.top_merchants,
                        transaction_count=cat_item.transaction_count,
                    ),
                    impact_amount=excess,
                    actionable=True,
                )
            )

    return findings


# 2. Spending Acceleration Detector
def detect_spending_acceleration(
    spend_metrics: SpendMetrics,
    historical_profile: HistoricalProfile | None = None,
) -> Finding | None:
    """Flag total cycle spend acceleration > 1.25x previous cycle."""
    if not historical_profile or not historical_profile.previous_cycle_spend:
        return None

    prev_spend = historical_profile.previous_cycle_spend
    if prev_spend <= Decimal("0.00"):
        return None

    ratio = spend_metrics.total_debits / prev_spend
    excess = spend_metrics.total_debits - prev_spend

    if ratio > Decimal("1.25") and excess >= Decimal("2000.00"):
        pct_increase = float(round((ratio - Decimal("1.00")) * Decimal("100.00"), 2))
        severity = FindingSeverity.HIGH if ratio > Decimal("1.50") else FindingSeverity.MEDIUM

        return Finding(
            id="finding_spending_acceleration",
            detector_type=DetectorType.SPENDING_ACCELERATION,
            severity=severity,
            title=f"Total Spending Accelerated by {pct_increase:.1f}%",
            description=(
                f"Total cycle spend grew to ₹{spend_metrics.total_debits:,.2f} compared to "
                f"₹{prev_spend:,.2f} last billing cycle."
            ),
            evidence=FindingEvidence(
                current_value=spend_metrics.total_debits,
                threshold_or_baseline=prev_spend,
                delta_percentage=pct_increase,
                transaction_count=spend_metrics.debit_transaction_count,
            ),
            impact_amount=excess,
            actionable=True,
        )

    return None


# 3. Frequent Small Spend Leak Detector
def detect_frequent_small_spend(
    micro_spend: MicroSpendMetrics,
    total_debits: Decimal,
    total_debit_count: int,
) -> Finding | None:
    """Flag micro-spend leak (purchases <= ₹250 accounting for > 25% count & > 15% spend)."""
    if total_debit_count == 0 or total_debits <= Decimal("0.00"):
        return None

    is_high_volume = (
        micro_spend.percentage_of_transactions >= 25.0 and micro_spend.percentage_of_spend >= 15.0
    )
    is_excess_micro = (
        micro_spend.percentage_of_transactions >= 35.0 and micro_spend.percentage_of_spend >= 10.0
    )

    if is_high_volume or is_excess_micro:
        # Estimated potential savings by consolidating 40% of micro orders
        estimated_savings = round(micro_spend.total_amount * Decimal("0.40"), 2)

        return Finding(
            id="finding_micro_spend_leak",
            detector_type=DetectorType.FREQUENT_SMALL_SPEND,
            severity=FindingSeverity.MEDIUM,
            title="Frequent Micro-Spending Leak",
            description=(
                f"{micro_spend.count} small transactions (<= ₹{micro_spend.threshold:,.2f}) totaled "
                f"₹{micro_spend.total_amount:,.2f}, accounting for {micro_spend.percentage_of_transactions:.1f}% of orders."
            ),
            evidence=FindingEvidence(
                current_value=micro_spend.total_amount,
                delta_percentage=micro_spend.percentage_of_spend,
                related_merchants=micro_spend.top_micro_merchants,
                transaction_count=micro_spend.count,
                context_data={
                    "percentage_of_transactions": micro_spend.percentage_of_transactions,
                    "threshold": str(micro_spend.threshold),
                },
            ),
            impact_amount=estimated_savings,
            actionable=True,
        )

    return None


# 4. Merchant Concentration Detector
def detect_merchant_concentration(
    merchant_concentration: list[MerchantConcentration],
) -> list[Finding]:
    """Flag single merchant accounting for > 35% of total cycle spend."""
    findings: list[Finding] = []

    for item in merchant_concentration:
        if item.percentage >= 35.0:
            severity = FindingSeverity.HIGH if item.percentage >= 50.0 else FindingSeverity.MEDIUM
            findings.append(
                Finding(
                    id=f"finding_merchant_conc_{re.sub(r'[^a-zA-Z0-9]', '_', item.merchant_name).lower()}",
                    detector_type=DetectorType.MERCHANT_CONCENTRATION,
                    severity=severity,
                    title=f"High Spend Concentration at {item.merchant_name} ({item.percentage:.1f}%)",
                    description=(
                        f"Purchases at {item.merchant_name} totaled ₹{item.total_amount:,.2f}, "
                        f"representing {item.percentage:.1f}% of your total statement spend."
                    ),
                    evidence=FindingEvidence(
                        current_value=item.total_amount,
                        delta_percentage=item.percentage,
                        related_category=item.category,
                        related_merchants=[item.merchant_name],
                        transaction_count=item.transaction_count,
                    ),
                    impact_amount=item.total_amount,
                    actionable=True,
                )
            )

    return findings


# 5. Unusual Purchase / Statistical Outlier Detector
def detect_unusual_purchase(
    transactions: list[CategorizedTransaction],
) -> list[Finding]:
    """Flag individual transactions with Z-score > 2.5 against personal distribution."""
    findings: list[Finding] = []
    debit_txns = [t for t in transactions if t.transaction_type not in CREDIT_TRANSACTION_TYPES]

    if len(debit_txns) < 4:
        return findings

    amounts = [float(t.amount) for t in debit_txns]
    n = len(amounts)
    mean = sum(amounts) / n
    variance = sum((x - mean) ** 2 for x in amounts) / (n - 1)
    std_dev = math.sqrt(variance)

    if std_dev <= 0:
        return findings

    sorted_amounts = sorted(amounts)
    mid = n // 2
    median = (
        sorted_amounts[mid] if n % 2 == 1 else (sorted_amounts[mid - 1] + sorted_amounts[mid]) / 2.0
    )

    for txn in debit_txns:
        amt = float(txn.amount)
        z_score = (amt - mean) / std_dev if std_dev > 0 else 0.0

        # Check Z-score > 2.5 (for N >= 8) or robust outlier when N < 8 (amt >= 3x median and z_score > 1.5)
        is_z_outlier = z_score > 2.5
        is_sample_outlier = n < 8 and amt >= 3.0 * median and z_score > 1.5

        if is_z_outlier or is_sample_outlier:
            severity = (
                FindingSeverity.HIGH
                if (z_score > 3.0 or amt >= 5.0 * median)
                else FindingSeverity.MEDIUM
            )
            excess = txn.amount - Decimal(f"{mean:.2f}")

            findings.append(
                Finding(
                    id=f"finding_outlier_{txn.transaction_date.strftime('%Y%m%d')}_{int(txn.amount)}",
                    detector_type=DetectorType.UNUSUAL_PURCHASE,
                    severity=severity,
                    title=f"Unusual Large Transaction: ₹{txn.amount:,.2f} at {txn.merchant_normalized}",
                    description=(
                        f"Purchase of ₹{txn.amount:,.2f} on {txn.transaction_date.isoformat()} is a "
                        f"statistical outlier (Z-Score: {z_score:.2f}, Average: ₹{mean:,.2f})."
                    ),
                    evidence=FindingEvidence(
                        current_value=txn.amount,
                        threshold_or_baseline=Decimal(f"{mean + 2.0 * std_dev:.2f}"),
                        delta_percentage=round((amt / mean - 1.0) * 100, 2),
                        related_category=txn.category,
                        related_merchants=[txn.merchant_normalized],
                        transaction_count=1,
                        context_data={"z_score": round(z_score, 2), "mean": round(mean, 2)},
                    ),
                    impact_amount=excess,
                    actionable=False,
                )
            )

    return findings


# 6. Subscription Burden Detector
def detect_subscription_burden(
    recurring_analysis: RecurringAnalysis,
) -> Finding | None:
    """Flag total recurring subscriptions > 10% of total spend."""
    if (
        recurring_analysis.recurring_percentage_of_spend >= 10.0
        and recurring_analysis.total_monthly_recurring >= Decimal("1000.00")
    ):
        severity = (
            FindingSeverity.HIGH
            if recurring_analysis.recurring_percentage_of_spend >= 20.0
            else FindingSeverity.MEDIUM
        )
        merchants = [item.merchant_name for item in recurring_analysis.items]

        return Finding(
            id="finding_subscription_burden",
            detector_type=DetectorType.SUBSCRIPTION_BURDEN,
            severity=severity,
            title=f"Heavy Subscription Burden ({recurring_analysis.recurring_percentage_of_spend:.1f}% of spend)",
            description=(
                f"You have {len(recurring_analysis.items)} recurring subscriptions totaling "
                f"₹{recurring_analysis.total_monthly_recurring:,.2f}/month (₹{recurring_analysis.total_annual_recurring:,.2f}/year)."
            ),
            evidence=FindingEvidence(
                current_value=recurring_analysis.total_monthly_recurring,
                delta_percentage=recurring_analysis.recurring_percentage_of_spend,
                related_category=Category.SUBSCRIPTIONS,
                related_merchants=merchants,
                transaction_count=len(recurring_analysis.items),
                context_data={"annual_cost": str(recurring_analysis.total_annual_recurring)},
            ),
            impact_amount=recurring_analysis.total_annual_recurring,
            actionable=True,
        )

    return None


# 7. Weekend Spending Spike Detector
def detect_weekend_spike(
    temporal_metrics: TemporalMetrics,
) -> Finding | None:
    """Flag weekend spend (Sat + Sun) > 55% of total cycle spend."""
    if temporal_metrics.weekend_percentage >= 55.0 and temporal_metrics.weekend_spend >= Decimal(
        "3000.00"
    ):
        return Finding(
            id="finding_weekend_spike",
            detector_type=DetectorType.WEEKEND_SPIKE,
            severity=FindingSeverity.MEDIUM,
            title=f"Weekend Spending Spike ({temporal_metrics.weekend_percentage:.1f}% on Weekends)",
            description=(
                f"Weekend purchases totaled ₹{temporal_metrics.weekend_spend:,.2f}, representing "
                f"{temporal_metrics.weekend_percentage:.1f}% of all billed debits."
            ),
            evidence=FindingEvidence(
                current_value=temporal_metrics.weekend_spend,
                delta_percentage=temporal_metrics.weekend_percentage,
                context_data={"weekday_spend": str(temporal_metrics.weekday_spend)},
            ),
            impact_amount=temporal_metrics.weekend_spend - temporal_metrics.weekday_spend,
            actionable=True,
        )

    return None


# 8. Late-Night Spending Spurt Detector
def detect_late_night_spurt(
    transactions: list[CategorizedTransaction],
) -> Finding | None:
    """Detect cluster of late-night orders between 11 PM and 4 AM or late-night keywords."""
    late_night_keywords = re.compile(
        r"\b(?:23:|0[0-3]:|MIDNIGHT|LATE\s*NIGHT|24X7)\b", re.IGNORECASE
    )
    late_txns: list[CategorizedTransaction] = []

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            continue
        if late_night_keywords.search(txn.merchant_raw):
            late_txns.append(txn)

    if len(late_txns) >= 3 or (
        len(late_txns) >= 2
        and sum((t.amount for t in late_txns), Decimal("0.00")) >= Decimal("2000.00")
    ):
        total_late = sum((t.amount for t in late_txns), Decimal("0.00"))
        merchants = list(dict.fromkeys(t.merchant_normalized for t in late_txns))

        return Finding(
            id="finding_late_night_spurt",
            detector_type=DetectorType.LATE_NIGHT_SPURT,
            severity=FindingSeverity.LOW,
            title="Late-Night Spending Cluster",
            description=(
                f"Identified {len(late_txns)} late-night transactions totaling ₹{total_late:,.2f} "
                f"placed between 11:00 PM and 4:00 AM."
            ),
            evidence=FindingEvidence(
                current_value=total_late,
                related_merchants=merchants,
                transaction_count=len(late_txns),
            ),
            impact_amount=total_late,
            actionable=True,
        )

    return None


# 9. Frequency Inflation Detector
def detect_frequency_inflation(
    spend_metrics: SpendMetrics,
    historical_profile: HistoricalProfile | None = None,
) -> Finding | None:
    """Flag transaction frequency growing > 30% while average ticket size stayed constant (+-10%)."""
    if (
        not historical_profile
        or not historical_profile.previous_cycle_count
        or not historical_profile.avg_ticket_size
    ):
        return None

    prev_count = historical_profile.previous_cycle_count
    prev_ticket = historical_profile.avg_ticket_size

    if prev_count <= 0 or prev_ticket <= Decimal("0.00"):
        return None

    count_ratio = spend_metrics.debit_transaction_count / prev_count
    ticket_ratio = spend_metrics.average_transaction_amount / prev_ticket

    if count_ratio > 1.30 and Decimal("0.90") <= ticket_ratio <= Decimal("1.10"):
        pct_increase = float(round((count_ratio - 1.0) * 100.0, 2))

        return Finding(
            id="finding_frequency_inflation",
            detector_type=DetectorType.FREQUENCY_INFLATION,
            severity=FindingSeverity.MEDIUM,
            title=f"Transaction Frequency Creep (+{pct_increase:.1f}% Orders)",
            description=(
                f"Transaction count increased from {prev_count} to {spend_metrics.debit_transaction_count} "
                f"(+{pct_increase:.1f}%) while your average ticket size stayed flat at ₹{spend_metrics.average_transaction_amount:,.2f}."
            ),
            evidence=FindingEvidence(
                current_value=spend_metrics.debit_transaction_count,
                threshold_or_baseline=prev_count,
                delta_percentage=pct_increase,
                transaction_count=spend_metrics.debit_transaction_count,
                context_data={"avg_ticket_size": str(spend_metrics.average_transaction_amount)},
            ),
            actionable=True,
        )

    return None


# 10. High Credit Utilization Detector
def detect_high_utilization(
    header: StatementHeader | None,
    spend_metrics: SpendMetrics,
) -> Finding | None:
    """Flag statement balance / total due exceeding 30% of total card credit limit."""
    if not header or not header.credit_limit or header.credit_limit <= Decimal("0.00"):
        return None

    balance = header.total_amount_due or spend_metrics.total_debits
    limit = header.credit_limit
    utilization_pct = float(round((balance / limit) * Decimal("100.00"), 2))

    if utilization_pct >= 30.0:
        severity = FindingSeverity.CRITICAL if utilization_pct >= 50.0 else FindingSeverity.HIGH

        return Finding(
            id="finding_high_utilization",
            detector_type=DetectorType.HIGH_CREDIT_UTILIZATION,
            severity=severity,
            title=f"High Credit Utilization Alert ({utilization_pct:.1f}%)",
            description=(
                f"Your card utilization is {utilization_pct:.1f}% (₹{balance:,.2f} of ₹{limit:,.2f} limit). "
                f"Credit bureaus recommend keeping utilization below 30% to protect your credit score."
            ),
            evidence=FindingEvidence(
                current_value=balance,
                threshold_or_baseline=round(limit * Decimal("0.30"), 2),
                delta_percentage=utilization_pct,
                context_data={
                    "credit_limit": str(limit),
                    "utilization_percentage": utilization_pct,
                },
            ),
            actionable=True,
        )

    return None


# Orchestrator
def run_anomaly_detection(
    transactions: list[CategorizedTransaction],
    analytics: StatementAnalytics,
    header: StatementHeader | None = None,
    historical_profile: HistoricalProfile | None = None,
) -> AnomalyDetectionResult:
    """Execute all 10 deterministic pattern and anomaly detectors and return prioritized findings."""
    findings: list[Finding] = []

    # 1. Category Spike
    findings.extend(detect_category_spike(analytics.category_breakdown, historical_profile))

    # 2. Spending Acceleration
    f2 = detect_spending_acceleration(analytics.spend_metrics, historical_profile)
    if f2:
        findings.append(f2)

    # 3. Frequent Small Spend
    f3 = detect_frequent_small_spend(
        analytics.micro_spend_metrics,
        analytics.spend_metrics.total_debits,
        analytics.spend_metrics.debit_transaction_count,
    )
    if f3:
        findings.append(f3)

    # 4. Merchant Concentration
    findings.extend(detect_merchant_concentration(analytics.merchant_concentration))

    # 5. Unusual Purchase (Z-score outlier)
    findings.extend(detect_unusual_purchase(transactions))

    # 6. Subscription Burden
    f6 = detect_subscription_burden(analytics.recurring_analysis)
    if f6:
        findings.append(f6)

    # 7. Weekend Spike
    f7 = detect_weekend_spike(analytics.temporal_metrics)
    if f7:
        findings.append(f7)

    # 8. Late Night Spurt
    f8 = detect_late_night_spurt(transactions)
    if f8:
        findings.append(f8)

    # 9. Frequency Inflation
    f9 = detect_frequency_inflation(analytics.spend_metrics, historical_profile)
    if f9:
        findings.append(f9)

    # 10. High Credit Utilization
    f10 = detect_high_utilization(header, analytics.spend_metrics)
    if f10:
        findings.append(f10)

    # Sort findings by severity priority
    findings.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    critical_c = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
    high_c = sum(1 for f in findings if f.severity == FindingSeverity.HIGH)
    med_c = sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM)
    low_c = sum(1 for f in findings if f.severity == FindingSeverity.LOW)

    return AnomalyDetectionResult(
        findings=findings,
        total_findings_count=len(findings),
        critical_count=critical_c,
        high_count=high_c,
        medium_count=med_c,
        low_count=low_c,
    )
