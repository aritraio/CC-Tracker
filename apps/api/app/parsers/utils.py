import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.schemas.statement import TransactionType

# Common Indian Date Formats
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d/%m/%y",
    "%d-%m-%y",
    "%d %b %Y",
    "%d-%b-%Y",
    "%d %b %y",
    "%d-%b-%y",
    "%d %B %Y",
    "%d-%B-%Y",
    "%b %d, %Y",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
]

# Regex patterns for parsing dates embedded in text
DATE_REGEX_PATTERNS = [
    re.compile(r"(\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)"),
    re.compile(r"(\d{2}-\d{2}-\d{4})"),
    re.compile(r"(\d{2}/\d{2}/\d{2})"),
    re.compile(r"(\d{2}-\d{2}-\d{2})"),
    re.compile(
        r"(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})",
        re.IGNORECASE,
    ),
    re.compile(
        r"(\d{2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*-\d{2,4})", re.IGNORECASE
    ),
]


def parse_indian_date(date_str: str) -> date | None:
    """Parse date from various string formats common in Indian credit card statements."""
    if not date_str:
        return None

    cleaned = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    # Try regex matching for substrings
    for pattern in DATE_REGEX_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            sub = match.group(1).strip()
            for fmt in DATE_FORMATS:
                try:
                    return datetime.strptime(sub, fmt).date()
                except ValueError:
                    continue

    return None


def parse_amount(val_str: str) -> tuple[Decimal, bool]:
    """
    Parse an amount string into a strictly positive Decimal and a boolean indicating if it's a Credit.
    Handles currency symbols, Indian number grouping, CR/DR flags, and negative signs.
    """
    if not val_str:
        return Decimal("0.00"), False

    raw = val_str.strip()
    is_credit = False

    # Check for Credit indicators
    if re.search(r"(?i)\bcr\b|\(cr\)|credit|\bcr\.", raw):
        is_credit = True
    elif raw.startswith("-") or (raw.startswith("(") and raw.endswith(")")):
        is_credit = True

    # Strip non-numeric characters except digits, dot, and commas
    cleaned = re.sub(r"[^\d.,]", "", raw)
    if not cleaned:
        return Decimal("0.00"), is_credit

    # Handle Indian comma separation (e.g. 1,23,456.78 -> 123456.78)
    cleaned = cleaned.replace(",", "")

    # In case there are multiple dots due to OCR/extraction glitches
    if cleaned.count(".") > 1:
        parts = cleaned.split(".")
        cleaned = "".join(parts[:-1]) + "." + parts[-1]

    try:
        amount = Decimal(cleaned)
        if amount < Decimal("0.00"):
            amount = abs(amount)
            is_credit = True
        return amount.quantize(Decimal("0.01")), is_credit
    except InvalidOperation:
        return Decimal("0.00"), is_credit


def classify_transaction_type(
    merchant_raw: str, is_credit: bool, amount: Decimal
) -> TransactionType:
    """Deterministically classify transaction based on raw merchant text and credit/debit flag."""
    text = merchant_raw.upper().strip()

    # Payments toward credit card
    if is_credit:
        if any(
            kw in text
            for kw in [
                "PAYMENT RECEIVED",
                "AUTO DEBIT",
                "AUTOPAY",
                "NEFT PAYMENT",
                "IMPS PAYMENT",
                "UPI/PAYMENT",
                "NETBANKING",
                "CRED PAYMENT",
                "BILLDESK",
                "IBILL",
                "THANK YOU FOR YOUR PAYMENT",
                "BIL/ONL",
                "PAYMENT THROUGH",
                "MOBILE PAYMENT",
                "CHEQUE PAYMENT",
                "CASH PAYMENT",
                "DIRECT DEBIT",
                "RTGS PAYMENT",
            ]
        ):
            return TransactionType.PAYMENT

        # Rewards / Cashback
        if any(
            kw in text
            for kw in ["CASHBACK", "REWARD REDEMPTION", "POINTS REDEEM", "LOYALTY REWARD"]
        ):
            return TransactionType.REWARD

        # Reversals
        if any(
            kw in text
            for kw in ["REVERSAL", "CHARGEBACK", "DISPUTE RESOLVED", "FAILED TXN REVERSAL"]
        ):
            return TransactionType.REVERSAL

        # Other credits default to REFUND
        return TransactionType.REFUND

    # Debits / Charges
    # GST / Tax
    if any(
        kw in text
        for kw in [
            "GST",
            "IGST",
            "CGST",
            "SGST",
            "GOODS & SERVICE TAX",
            "INTEGRATED GST",
            "CENTRAL GST",
            "STATE GST",
        ]
    ):
        return TransactionType.GST

    # Interest / Finance Charges
    if any(
        kw in text
        for kw in [
            "FINANCE CHARGE",
            "FIN CHG",
            "INTEREST CHARGE",
            "INTEREST ON",
            "LATE PAYMENT INTEREST",
            "OVERDUE INTEREST",
            "MONTHLY INTEREST",
        ]
    ):
        return TransactionType.INTEREST

    # Fees
    if any(
        kw in text
        for kw in [
            "ANNUAL FEE",
            "RENEWAL FEE",
            "MEMBERSHIP FEE",
            "JOINING FEE",
            "LATE PAYMENT FEE",
            "LATE FEE",
            "OVERLIMIT FEE",
            "CASH ADVANCE FEE",
            "CARD REPLACEMENT FEE",
            "SURCHARGE",
            "FUEL SURCHARGE",
            "PROCESSING FEE",
            "FOREX MARKUP",
            "CROSS CURRENCY MARKUP",
        ]
    ):
        return TransactionType.FEE

    # EMI Line Items
    if any(
        kw in text
        for kw in [
            "EMI",
            "EASYEMI",
            "SMARTEMI",
            "FLEXIPAY",
            "LOAN REPAYMENT",
            "INSTALLMENT",
            "SPLITPAY",
        ]
    ):
        return TransactionType.EMI

    # Cash Advance / ATM Withdrawal
    if any(
        kw in text
        for kw in [
            "ATM CASH",
            "CASH WITHDRAWAL",
            "ATM WDL",
            "DOMESTIC ATM",
            "INTERNATIONAL ATM",
        ]
    ):
        return TransactionType.CASH_WITHDRAWAL

    # Adjustments
    if any(kw in text for kw in ["MANUAL ADJUSTMENT", "DEBIT ADJUSTMENT", "BANK ADJUSTMENT"]):
        return TransactionType.ADJUSTMENT

    return TransactionType.PURCHASE


def sanitize_merchant_text(text: str) -> str:
    """Clean excess noise and formatting glitches from extracted merchant strings."""
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"^[\s\*\-\:\.\,\;\/_|#@~`]+", "", cleaned)
    cleaned = re.sub(r"[\s\*\-\:\.\,\;\/_|#@~`]+$", "", cleaned)
    return cleaned.strip()
