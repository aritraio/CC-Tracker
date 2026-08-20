import io
import re
from datetime import date

from app.parsers.base import BaseStatementParser
from app.parsers.utils import (
    classify_transaction_type,
    parse_amount,
    parse_indian_date,
    sanitize_merchant_text,
)
from app.schemas.statement import (
    ExtractedTransaction,
    ParsedStatement,
    StatementHeader,
)
from app.services.reconciliation import reconcile_statement


class IciciStatementParser(BaseStatementParser):
    """Deterministic parser for ICICI Bank Credit Card statements."""

    issuer_name: str = "ICICI Bank"

    def identify(self, first_page_text: str) -> bool:
        if not first_page_text:
            return False
        return bool(
            re.search(r"ICICI\s*BANK", first_page_text, re.IGNORECASE)
            or re.search(r"icicibank\.com", first_page_text, re.IGNORECASE)
            or re.search(
                r"Statement\s+of\s+Card\s+Account.*ICICI",
                first_page_text,
                re.IGNORECASE | re.DOTALL,
            )
        )

    def parse(self, pdf_stream: io.BytesIO) -> ParsedStatement:
        pages = self.extract_text_pages(pdf_stream)
        full_text = "\n".join(pages)
        raw_text_length = len(full_text)

        header = self._extract_header(pages)
        transactions, unparsed = self._extract_transactions(pages)

        # Mathematical reconciliation check
        reconciliation = reconcile_statement(header, transactions, unparsed)

        return ParsedStatement(
            header=header,
            transactions=transactions,
            raw_text_length=raw_text_length,
            reconciliation_status=reconciliation.status,
            reconciliation_discrepancy=reconciliation.discrepancy,
            unparsed_lines=unparsed,
        )

    def _extract_header(self, pages: list[str]) -> StatementHeader:
        header_text = "\n".join(pages[:2]) if pages else ""

        # Last 4 digits
        card_last_4 = None
        card_match = re.search(
            r"(?:Card\s*(?:No|Number)?|Account\s*No)?[:\s]*[X\*\d\s\-]{8,24}(\d{4})",
            header_text,
            re.IGNORECASE,
        )
        if card_match:
            card_last_4 = card_match.group(1)

        # Statement / Billing Period & Dates
        stmt_start: date | None = None
        stmt_end: date | None = None
        period_match = re.search(
            r"(?:Statement\s*Period|Billing\s*Period)[:\s]*(?:From)?\s*(\d{2}[/\-\s\w]+?)\s*(?:to|-)\s*(\d{2}[/\-\s\w]+)",
            header_text,
            re.IGNORECASE,
        )
        if period_match:
            stmt_start = parse_indian_date(period_match.group(1))
            stmt_end = parse_indian_date(period_match.group(2))
        else:
            stmt_date_match = re.search(
                r"(?:Statement\s*Date)[:\s]*(\d{2}[/\-][\w]+[/\-]\d{2,4})",
                header_text,
                re.IGNORECASE,
            )
            if stmt_date_match:
                stmt_end = parse_indian_date(stmt_date_match.group(1))

        # Payment Due Date
        payment_due_date = None
        due_date_match = re.search(
            r"(?:Payment\s*Due\s*Date|Due\s*Date)[:\s]*(\d{2}[/\-][\w]+[/\-]\d{2,4})",
            header_text,
            re.IGNORECASE,
        )
        if due_date_match:
            payment_due_date = parse_indian_date(due_date_match.group(1))

        # Total Amount Due / Total Dues
        total_amount_due = None
        total_due_match = re.search(
            r"(?:Total\s*Amount\s*Due|Total\s*Dues|Total\s*Amt\s*Due)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if total_due_match:
            total_amount_due, _ = parse_amount(total_due_match.group(1))

        # Minimum Amount Due
        minimum_amount_due = None
        min_due_match = re.search(
            r"(?:Minimum\s*Amount\s*Due|Min\s*Amount\s*Due|Minimum\s*Dues)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if min_due_match:
            minimum_amount_due, _ = parse_amount(min_due_match.group(1))

        # Credit Limit
        credit_limit = None
        limit_match = re.search(
            r"(?:Credit\s*Limit|Total\s*Credit\s*Limit)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if limit_match:
            credit_limit, _ = parse_amount(limit_match.group(1))

        # Available Credit Limit
        available_credit = None
        avail_match = re.search(
            r"(?:Available\s*Credit\s*(?:Limit)?|Available\s*Limit)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if avail_match:
            available_credit, _ = parse_amount(avail_match.group(1))

        # Opening Balance
        opening_balance = None
        open_match = re.search(
            r"(?:Opening\s*Balance|Previous\s*Balance|Past\s*Dues)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if open_match:
            opening_balance, _ = parse_amount(open_match.group(1))

        # Total Debits
        total_debits = None
        debits_match = re.search(
            r"(?:Total\s*Debits|Debits|Total\s*Purchases)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if debits_match:
            total_debits, _ = parse_amount(debits_match.group(1))

        # Total Credits
        total_credits = None
        credits_match = re.search(
            r"(?:Total\s*Credits|Credits|Total\s*Payments)[:\s\D]*?([\d,]+\.\d{2}|[\d,]+)",
            header_text,
            re.IGNORECASE,
        )
        if credits_match:
            total_credits, _ = parse_amount(credits_match.group(1))

        return StatementHeader(
            issuer="ICICI Bank",
            card_last_4=card_last_4,
            statement_period_start=stmt_start,
            statement_period_end=stmt_end,
            total_amount_due=total_amount_due,
            minimum_amount_due=minimum_amount_due,
            payment_due_date=payment_due_date,
            credit_limit=credit_limit,
            available_credit=available_credit,
            opening_balance=opening_balance,
            total_debits=total_debits,
            total_credits=total_credits,
        )

    def _extract_transactions(
        self, pages: list[str]
    ) -> tuple[list[ExtractedTransaction], list[str]]:
        transactions: list[ExtractedTransaction] = []
        unparsed_lines: list[str] = []

        txn_line_pattern = re.compile(
            r"^(\d{2}/\d{2}/\d{2,4})\s+(?:(?:[A-Z0-9]{8,}|\d{1,4})\s+)?(.+?)\s+([\d,]+\.\d{2})\s*(CR|DR|Cr|Dr)?$",
            re.IGNORECASE,
        )

        in_reward_table = False

        for page_idx, page_text in enumerate(pages, start=1):
            lines = page_text.splitlines()

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                if re.search(
                    r"Reward\s*Points?\s*Summary|Opening\s*Points|Points\s*Earned",
                    stripped,
                    re.IGNORECASE,
                ):
                    in_reward_table = True
                    continue
                if in_reward_table and re.search(
                    r"Transaction\s*Details|Statement\s*Details", stripped, re.IGNORECASE
                ):
                    in_reward_table = False

                if in_reward_table:
                    continue

                if re.search(
                    r"(?:Transaction\s+Details|Date\s+Sr\.No|Statement\s+Period|Card\s+No|Page\s+\d+|Total\s+Dues|Payment\s+Due|Terms\s+and\s+Conditions|GSTIN|CIN\s*No)",
                    stripped,
                    re.IGNORECASE,
                ):
                    continue

                match = txn_line_pattern.match(stripped)
                if match:
                    date_str, desc, amount_str, cr_dr = match.groups()
                    parsed_date = parse_indian_date(date_str)
                    if not parsed_date:
                        unparsed_lines.append(stripped)
                        continue

                    full_amount_str = f"{amount_str} {cr_dr or ''}".strip()
                    amount, is_credit = parse_amount(full_amount_str)
                    if amount <= 0:
                        continue

                    cleaned_desc = sanitize_merchant_text(desc)
                    txn_type = classify_transaction_type(cleaned_desc, is_credit, amount)

                    transactions.append(
                        ExtractedTransaction(
                            transaction_date=parsed_date,
                            merchant_raw=cleaned_desc,
                            amount=amount,
                            transaction_type=txn_type,
                            currency="INR",
                            source_page=page_idx,
                            confidence_score=1.0,
                        )
                    )
                else:
                    if (
                        transactions
                        and len(stripped) < 80
                        and not re.search(
                            r"(?:Total|Dues|Page|Limit|Balance|Bank|Card|Date|Rs\.|INR|₹)",
                            stripped,
                            re.IGNORECASE,
                        )
                    ):
                        prev = transactions[-1]
                        updated_desc = sanitize_merchant_text(f"{prev.merchant_raw} {stripped}")
                        transactions[-1] = ExtractedTransaction(
                            transaction_date=prev.transaction_date,
                            post_date=prev.post_date,
                            merchant_raw=updated_desc,
                            amount=prev.amount,
                            transaction_type=prev.transaction_type,
                            currency=prev.currency,
                            source_page=prev.source_page,
                            confidence_score=prev.confidence_score,
                        )

        return transactions, unparsed_lines
