from decimal import Decimal

from app.schemas.reconciliation import ReconciliationSummary
from app.schemas.statement import (
    ExtractedTransaction,
    StatementHeader,
    TransactionType,
)

CREDIT_TRANSACTION_TYPES = {
    TransactionType.PAYMENT,
    TransactionType.REFUND,
    TransactionType.REVERSAL,
    TransactionType.REWARD,
}

RECONCILIATION_TOLERANCE = Decimal("1.00")


def reconcile_statement(
    header: StatementHeader,
    transactions: list[ExtractedTransaction],
    unparsed_lines: list[str] | None = None,
) -> ReconciliationSummary:
    """
    Deterministically reconcile extracted credit card line items against statement summary headers.

    Rules:
    1. sum(Debits) and sum(Credits) calculated with exact Decimal precision.
    2. Compared against header.total_debits / header.total_credits if present.
    3. Compared against expected net change: opening_balance + sum(Debits) - sum(Credits) vs total_amount_due.
    4. Status is VALIDATED if abs(discrepancy) <= ₹1.00; otherwise REVIEW_REQUIRED.
    """
    unparsed = unparsed_lines or []
    warnings: list[str] = []

    # 1. Sum up Debits and Credits
    extracted_debits = sum(
        (t.amount for t in transactions if t.transaction_type not in CREDIT_TRANSACTION_TYPES),
        start=Decimal("0.00"),
    )
    extracted_credits = sum(
        (t.amount for t in transactions if t.transaction_type in CREDIT_TRANSACTION_TYPES),
        start=Decimal("0.00"),
    )

    discrepancy = Decimal("0.00")
    expected_total_due: Decimal | None = None

    # 2. Check total_debits if present
    if header.total_debits is not None:
        debit_delta = abs(header.total_debits - extracted_debits)
        discrepancy = max(discrepancy, debit_delta)
        if debit_delta > RECONCILIATION_TOLERANCE:
            warnings.append(
                f"Extracted debits (₹{extracted_debits:,.2f}) does not match statement total debits "
                f"(₹{header.total_debits:,.2f}). Discrepancy: ₹{debit_delta:,.2f}."
            )

    # 3. Check total_credits if present
    if header.total_credits is not None:
        credit_delta = abs(header.total_credits - extracted_credits)
        discrepancy = max(discrepancy, credit_delta)
        if credit_delta > RECONCILIATION_TOLERANCE:
            warnings.append(
                f"Extracted credits (₹{extracted_credits:,.2f}) does not match statement total credits "
                f"(₹{header.total_credits:,.2f}). Discrepancy: ₹{credit_delta:,.2f}."
            )

    # 4. Check total_amount_due (Net balance change)
    if header.total_amount_due is not None:
        opening = header.opening_balance or Decimal("0.00")
        expected_total_due = opening + extracted_debits - extracted_credits
        due_delta = abs(header.total_amount_due - expected_total_due)

        if header.total_debits is None:
            discrepancy = max(discrepancy, due_delta)
            if due_delta > RECONCILIATION_TOLERANCE:
                warnings.append(
                    f"Calculated outstanding dues (₹{expected_total_due:,.2f}) does not match "
                    f"statement total amount due (₹{header.total_amount_due:,.2f}). Discrepancy: ₹{due_delta:,.2f}."
                )

    # 5. Check unparsed lines
    if unparsed:
        warnings.append(f"{len(unparsed)} line(s) could not be parsed as structured transactions.")

    is_balanced = discrepancy <= RECONCILIATION_TOLERANCE
    status = "VALIDATED" if is_balanced else "REVIEW_REQUIRED"

    return ReconciliationSummary(
        status=status,
        discrepancy=discrepancy,
        extracted_debits=extracted_debits,
        extracted_credits=extracted_credits,
        statement_total_debits=header.total_debits,
        statement_total_credits=header.total_credits,
        statement_total_amount_due=header.total_amount_due,
        expected_total_due=expected_total_due,
        is_balanced=is_balanced,
        unparsed_lines_count=len(unparsed),
        warnings=warnings,
    )
