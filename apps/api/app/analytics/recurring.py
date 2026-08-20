from collections import defaultdict
from datetime import date
from decimal import Decimal

from app.schemas.analytics import RecurringAnalysis, RecurringItem
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.statement import TransactionType

CREDIT_TRANSACTION_TYPES = {
    TransactionType.PAYMENT,
    TransactionType.REFUND,
    TransactionType.REVERSAL,
    TransactionType.REWARD,
}

KNOWN_SUBSCRIPTION_MERCHANTS = {
    "netflix",
    "spotify",
    "disney+ hotstar",
    "hotstar",
    "amazon prime",
    "youtube premium",
    "apple services",
    "apple.com/bill",
    "google one",
    "google storage",
    "chatgpt / openai",
    "openai",
    "microsoft 365",
    "icloud",
    "audible",
    "linkedin premium",
    "adobe",
    "dropbox",
    "strava",
    "times prime",
    "the hindu subscription",
    "canva pro",
    "playstation network",
    "xbox game pass",
    "cult.fit",
}


def detect_recurring_subscriptions(
    transactions: list[CategorizedTransaction],
    total_debits: Decimal,
) -> RecurringAnalysis:
    """
    Detect recurring subscriptions, memberships, and periodic digital services.
    Calculates monthly burden and annualized projections.
    """
    if not transactions:
        return RecurringAnalysis()

    # Group candidates by merchant_normalized
    merchant_txns: dict[str, list[CategorizedTransaction]] = defaultdict(list)

    for txn in transactions:
        if txn.transaction_type in CREDIT_TRANSACTION_TYPES:
            continue

        is_sub_cat = txn.category == Category.SUBSCRIPTIONS
        is_known_brand = txn.merchant_normalized.lower() in KNOWN_SUBSCRIPTION_MERCHANTS
        is_flagged = txn.is_recurring

        if is_sub_cat or is_known_brand or is_flagged:
            merchant_txns[txn.merchant_normalized].append(txn)

    recurring_items: list[RecurringItem] = []
    total_monthly = Decimal("0.00")
    total_annual = Decimal("0.00")

    for merchant_name, txns in merchant_txns.items():
        # Representative amount (most frequent or latest)
        amounts = [t.amount for t in txns]
        dates: list[date] = sorted([t.transaction_date for t in txns])
        rep_amount = max(set(amounts), key=amounts.count)
        cat = txns[0].category

        # Determine frequency heuristic (Annual if > ₹1200 for single instance OTT / Software, else Monthly)
        if len(txns) == 1 and rep_amount >= Decimal("1200.00"):
            frequency = "Annual"
            monthly_equiv = round(rep_amount / Decimal("12.00"), 2)
            annual_cost = rep_amount
        else:
            frequency = "Monthly"
            monthly_equiv = rep_amount
            annual_cost = rep_amount * Decimal("12.00")

        total_monthly += monthly_equiv
        total_annual += annual_cost

        recurring_items.append(
            RecurringItem(
                merchant_name=merchant_name,
                category=cat,
                amount=rep_amount,
                frequency=frequency,
                occurrences=len(txns),
                annualized_cost=annual_cost,
                transaction_dates=dates,
            )
        )

    # Sort descending by annualized cost
    recurring_items.sort(key=lambda r: r.annualized_cost, reverse=True)

    pct_of_spend = (
        float(round((total_monthly / total_debits) * Decimal("100.00"), 2))
        if total_debits > Decimal("0.00")
        else 0.0
    )

    return RecurringAnalysis(
        items=recurring_items,
        total_monthly_recurring=total_monthly,
        total_annual_recurring=total_annual,
        recurring_percentage_of_spend=pct_of_spend,
    )
