from datetime import date, timedelta
from decimal import Decimal

from app.schemas.reconciliation import (
    ValidationIssue,
    ValidationIssueType,
    ValidationResult,
)
from app.schemas.statement import ExtractedTransaction, StatementHeader


def validate_transactions(
    header: StatementHeader,
    transactions: list[ExtractedTransaction],
    reference_date: date | None = None,
) -> ValidationResult:
    """
    Execute transaction sanity, date range verification, duplicate detection,
    and credit limit checks on extracted line items.
    """
    today = reference_date or date.today()
    issues: list[ValidationIssue] = []
    seen_transactions: dict[tuple[date, str, Decimal, str], int] = {}
    duplicate_indices: set[int] = set()

    for idx, txn in enumerate(transactions):
        # 1. Check for Missing / Empty Merchant Description
        if not txn.merchant_raw or not txn.merchant_raw.strip():
            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.MISSING_MANDATORY_FIELD,
                    severity="ERROR",
                    message="Transaction description is empty or missing.",
                    transaction_index=idx,
                    details={"index": idx},
                )
            )

        # 2. Check for Non-Positive / Invalid Amount
        if txn.amount <= Decimal("0.00"):
            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.INVALID_AMOUNT,
                    severity="ERROR",
                    message=f"Transaction amount must be strictly positive (got ₹{txn.amount}).",
                    transaction_index=idx,
                    details={"index": idx, "amount": str(txn.amount)},
                )
            )

        # 3. Check for Future Dates
        if txn.transaction_date > today:
            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.FUTURE_DATE,
                    severity="ERROR",
                    message=(
                        f"Transaction date {txn.transaction_date.isoformat()} is in the future "
                        f"(reference date: {today.isoformat()})."
                    ),
                    transaction_index=idx,
                    details={"date": txn.transaction_date.isoformat(), "index": idx},
                )
            )

        # 4. Check for Out-of-Billing-Cycle Dates
        if header.statement_period_start and header.statement_period_end:
            early_bound = header.statement_period_start - timedelta(days=14)
            late_bound = header.statement_period_end + timedelta(days=7)
            if txn.transaction_date < early_bound or txn.transaction_date > late_bound:
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationIssueType.OUTSIDE_BILLING_CYCLE,
                        severity="WARNING",
                        message=(
                            f"Transaction date {txn.transaction_date.isoformat()} is outside the "
                            f"statement billing period ({header.statement_period_start.isoformat()} "
                            f"to {header.statement_period_end.isoformat()})."
                        ),
                        transaction_index=idx,
                        details={
                            "date": txn.transaction_date.isoformat(),
                            "period_start": header.statement_period_start.isoformat(),
                            "period_end": header.statement_period_end.isoformat(),
                        },
                    )
                )

        # 5. Check for Excessive Amount Exceeding Credit Limit
        if header.credit_limit is not None and header.credit_limit > Decimal("0.00"):
            if txn.amount > (header.credit_limit * Decimal("2.0")):
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationIssueType.CREDIT_LIMIT_EXCEEDED,
                        severity="WARNING",
                        message=(
                            f"Transaction amount ₹{txn.amount:,.2f} exceeds 200% of "
                            f"card credit limit (₹{header.credit_limit:,.2f})."
                        ),
                        transaction_index=idx,
                        details={
                            "amount": str(txn.amount),
                            "credit_limit": str(header.credit_limit),
                        },
                    )
                )

        # 6. Exact Duplicate Detection
        key = (
            txn.transaction_date,
            txn.merchant_raw.upper().strip(),
            txn.amount,
            txn.transaction_type.value,
        )
        if key in seen_transactions:
            duplicate_indices.add(idx)
            first_idx = seen_transactions[key]
            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.DUPLICATE_TRANSACTION,
                    severity="WARNING",
                    message=(
                        f"Potential duplicate transaction: '{txn.merchant_raw}' for "
                        f"₹{txn.amount:,.2f} on {txn.transaction_date.isoformat()} "
                        f"(matches row #{first_idx + 1})."
                    ),
                    transaction_index=idx,
                    details={
                        "duplicate_of_index": first_idx,
                        "date": txn.transaction_date.isoformat(),
                        "amount": str(txn.amount),
                    },
                )
            )
        else:
            seen_transactions[key] = idx

    # If any error severity issue exists, mark valid as False
    has_errors = any(i.severity == "ERROR" for i in issues)

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues,
        duplicate_count=len(duplicate_indices),
        flagged_count=len(issues),
        sanitized_transactions=transactions,
    )
