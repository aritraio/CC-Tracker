from collections import defaultdict
from datetime import date
from decimal import Decimal

from app.schemas.analytics import (
    CategoryBreakdown,
    DailySpend,
    MerchantConcentration,
    MicroSpendMetrics,
    SpendMetrics,
    TemporalMetrics,
)
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.statement import TransactionType

CREDIT_TRANSACTION_TYPES = {
    TransactionType.PAYMENT,
    TransactionType.REFUND,
    TransactionType.REVERSAL,
    TransactionType.REWARD,
}

DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def calculate_spend_metrics(
    transactions: list[CategorizedTransaction],
) -> SpendMetrics:
    """Calculate core spend metrics: totals, net spend, average, median, min, max."""
    if not transactions:
        return SpendMetrics()

    debits: list[Decimal] = []
    credits: list[Decimal] = []

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            credits.append(txn.amount)
        else:
            debits.append(txn.amount)

    total_debits = sum(debits, start=Decimal("0.00"))
    total_credits = sum(credits, start=Decimal("0.00"))
    net_spend = total_debits - total_credits

    debit_count = len(debits)
    credit_count = len(credits)
    total_count = len(transactions)

    if debit_count > 0:
        avg_amount = round(total_debits / Decimal(debit_count), 2)
        sorted_debits = sorted(debits)
        mid = debit_count // 2
        if debit_count % 2 == 1:
            median_amount = sorted_debits[mid]
        else:
            median_amount = round(
                (sorted_debits[mid - 1] + sorted_debits[mid]) / Decimal("2.00"), 2
            )
        max_amount = sorted_debits[-1]
        min_amount = sorted_debits[0]
    else:
        avg_amount = Decimal("0.00")
        median_amount = Decimal("0.00")
        max_amount = Decimal("0.00")
        min_amount = Decimal("0.00")

    return SpendMetrics(
        total_debits=total_debits,
        total_credits=total_credits,
        net_spend=net_spend,
        total_transaction_count=total_count,
        debit_transaction_count=debit_count,
        credit_transaction_count=credit_count,
        average_transaction_amount=avg_amount,
        median_transaction_amount=median_amount,
        max_transaction_amount=max_amount,
        min_transaction_amount=min_amount,
    )


def calculate_category_breakdown(
    transactions: list[CategorizedTransaction],
    total_debits: Decimal,
) -> list[CategoryBreakdown]:
    """Aggregate spending across all 14 standard categories with top merchants per bucket."""
    if not transactions or total_debits <= Decimal("0.00"):
        return []

    cat_amounts: dict[Category, Decimal] = defaultdict(lambda: Decimal("0.00"))
    cat_counts: dict[Category, int] = defaultdict(int)
    cat_merchants: dict[Category, dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: Decimal("0.00"))
    )

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            continue
        cat = txn.category
        cat_amounts[cat] += txn.amount
        cat_counts[cat] += 1
        cat_merchants[cat][txn.merchant_normalized] += txn.amount

    breakdown: list[CategoryBreakdown] = []
    for cat, amount in cat_amounts.items():
        pct = float(round((amount / total_debits) * Decimal("100.00"), 2))
        count = cat_counts[cat]
        avg = round(amount / Decimal(count), 2) if count > 0 else Decimal("0.00")

        # Top 3 merchants by spend in this category
        sorted_merchants = sorted(
            cat_merchants[cat].items(), key=lambda item: item[1], reverse=True
        )
        top_3 = [m[0] for m in sorted_merchants[:3]]

        breakdown.append(
            CategoryBreakdown(
                category=cat,
                total_amount=amount,
                percentage=pct,
                transaction_count=count,
                average_amount=avg,
                top_merchants=top_3,
            )
        )

    # Sort descending by total spend
    breakdown.sort(key=lambda b: b.total_amount, reverse=True)
    return breakdown


def calculate_merchant_concentration(
    transactions: list[CategorizedTransaction],
    total_debits: Decimal,
    top_n: int = 10,
) -> list[MerchantConcentration]:
    """Calculate merchant spend concentration and percentage share."""
    if not transactions or total_debits <= Decimal("0.00"):
        return []

    merchant_totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    merchant_categories: dict[str, Category] = {}
    merchant_counts: dict[str, int] = defaultdict(int)

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            continue
        name = txn.merchant_normalized
        merchant_totals[name] += txn.amount
        merchant_categories[name] = txn.category
        merchant_counts[name] += 1

    sorted_merchants = sorted(merchant_totals.items(), key=lambda item: item[1], reverse=True)

    concentration: list[MerchantConcentration] = []
    for name, amount in sorted_merchants[:top_n]:
        pct = float(round((amount / total_debits) * Decimal("100.00"), 2))
        concentration.append(
            MerchantConcentration(
                merchant_name=name,
                category=merchant_categories[name],
                total_amount=amount,
                percentage=pct,
                transaction_count=merchant_counts[name],
            )
        )

    return concentration


def calculate_temporal_metrics(
    transactions: list[CategorizedTransaction],
    period_start: date | None = None,
    period_end: date | None = None,
) -> TemporalMetrics:
    """Calculate daily spend trajectory, weekday vs. weekend ratios, and day of week patterns."""
    if not transactions:
        return TemporalMetrics()

    daily_totals: dict[date, Decimal] = defaultdict(lambda: Decimal("0.00"))
    daily_counts: dict[date, int] = defaultdict(int)
    day_of_week_totals: dict[str, Decimal] = {day: Decimal("0.00") for day in DAYS_OF_WEEK}

    weekday_spend = Decimal("0.00")
    weekend_spend = Decimal("0.00")
    total_debits = Decimal("0.00")

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            continue

        d = txn.transaction_date
        daily_totals[d] += txn.amount
        daily_counts[d] += 1
        total_debits += txn.amount

        # Weekday: 0 (Mon) - 4 (Fri), Weekend: 5 (Sat) - 6 (Sun)
        day_idx = d.weekday()
        day_name = DAYS_OF_WEEK[day_idx]
        day_of_week_totals[day_name] += txn.amount

        if day_idx in (5, 6):
            weekend_spend += txn.amount
        else:
            weekday_spend += txn.amount

    # Build sorted cumulative daily spending curve
    sorted_dates = sorted(daily_totals.keys())
    daily_spending: list[DailySpend] = []
    running_total = Decimal("0.00")

    for d in sorted_dates:
        amt = daily_totals[d]
        running_total += amt
        daily_spending.append(
            DailySpend(
                date=d,
                amount=amt,
                transaction_count=daily_counts[d],
                cumulative_amount=running_total,
            )
        )

    # Weekday vs Weekend percentages
    if total_debits > Decimal("0.00"):
        weekday_pct = float(round((weekday_spend / total_debits) * Decimal("100.00"), 2))
        weekend_pct = float(round((weekend_spend / total_debits) * Decimal("100.00"), 2))
    else:
        weekday_pct = 0.0
        weekend_pct = 0.0

    # Calculate average daily burn rate
    if period_start and period_end and period_end >= period_start:
        days_in_cycle = max(1, (period_end - period_start).days + 1)
    else:
        days_in_cycle = max(1, len(sorted_dates))

    avg_daily_burn = round(total_debits / Decimal(days_in_cycle), 2)

    return TemporalMetrics(
        daily_spending=daily_spending,
        weekday_spend=weekday_spend,
        weekend_spend=weekend_spend,
        weekday_percentage=weekday_pct,
        weekend_percentage=weekend_pct,
        avg_daily_burn_rate=avg_daily_burn,
        day_of_week_breakdown=day_of_week_totals,
    )


def calculate_micro_spend_metrics(
    transactions: list[CategorizedTransaction],
    total_debits: Decimal,
    threshold: Decimal = Decimal("250.00"),
) -> MicroSpendMetrics:
    """Calculate frequent micro-spending leak metrics for purchases <= threshold."""
    if not transactions:
        return MicroSpendMetrics(threshold=threshold)

    micro_txns: list[CategorizedTransaction] = []
    total_debit_txns = 0
    merchant_counts: dict[str, int] = defaultdict(int)

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            continue
        total_debit_txns += 1
        if txn.amount <= threshold:
            micro_txns.append(txn)
            merchant_counts[txn.merchant_normalized] += 1

    micro_count = len(micro_txns)
    micro_total = sum((t.amount for t in micro_txns), start=Decimal("0.00"))

    pct_txns = (
        float(round((Decimal(micro_count) / Decimal(total_debit_txns)) * Decimal("100.00"), 2))
        if total_debit_txns > 0
        else 0.0
    )
    pct_spend = (
        float(round((micro_total / total_debits) * Decimal("100.00"), 2))
        if total_debits > Decimal("0.00")
        else 0.0
    )

    top_merchants = [
        m[0] for m in sorted(merchant_counts.items(), key=lambda item: item[1], reverse=True)[:3]
    ]

    return MicroSpendMetrics(
        threshold=threshold,
        count=micro_count,
        total_amount=micro_total,
        percentage_of_transactions=pct_txns,
        percentage_of_spend=pct_spend,
        top_micro_merchants=top_merchants,
    )
