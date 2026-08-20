from datetime import date
from decimal import Decimal

from app.parsers.utils import (
    classify_transaction_type,
    parse_amount,
    parse_indian_date,
    sanitize_merchant_text,
)
from app.schemas.statement import TransactionType


def test_parse_indian_date_formats() -> None:
    assert parse_indian_date("15/04/2024") == date(2024, 4, 15)
    assert parse_indian_date("15-04-2024") == date(2024, 4, 15)
    assert parse_indian_date("15/04/24") == date(2024, 4, 15)
    assert parse_indian_date("15-04-24") == date(2024, 4, 15)
    assert parse_indian_date("15 Apr 2024") == date(2024, 4, 15)
    assert parse_indian_date("15-Apr-2024") == date(2024, 4, 15)
    assert parse_indian_date("15 Apr 24") == date(2024, 4, 15)
    assert parse_indian_date("15-Apr-24") == date(2024, 4, 15)
    assert parse_indian_date("15 April 2024") == date(2024, 4, 15)
    assert parse_indian_date("15-April-2024") == date(2024, 4, 15)
    assert parse_indian_date("Apr 15, 2024") == date(2024, 4, 15)
    assert parse_indian_date("2024-04-15") == date(2024, 4, 15)
    assert parse_indian_date("15/04/2024 14:30:00") == date(2024, 4, 15)
    assert parse_indian_date("15/04/2024 14:30") == date(2024, 4, 15)
    assert parse_indian_date("Date is 15/04/2024 on transaction") == date(2024, 4, 15)
    assert parse_indian_date("invalid-date") is None
    assert parse_indian_date("") is None


def test_parse_amount_variations() -> None:
    amt, is_cr = parse_amount("1,23,456.78")
    assert amt == Decimal("123456.78")
    assert is_cr is False

    amt, is_cr = parse_amount("₹ 4,500.00 Cr")
    assert amt == Decimal("4500.00")
    assert is_cr is True

    amt, is_cr = parse_amount("500.00 (Cr)")
    assert amt == Decimal("500.00")
    assert is_cr is True

    amt, is_cr = parse_amount("-1,200.50")
    assert amt == Decimal("1200.50")
    assert is_cr is True

    amt, is_cr = parse_amount("(850.00)")
    assert amt == Decimal("850.00")
    assert is_cr is True

    amt, is_cr = parse_amount("999.00 DR")
    assert amt == Decimal("999.00")
    assert is_cr is False

    amt, is_cr = parse_amount("12.34.56")
    assert amt == Decimal("1234.56")

    amt, is_cr = parse_amount("")
    assert amt == Decimal("0.00")
    assert is_cr is False

    amt, is_cr = parse_amount("invalid")
    assert amt == Decimal("0.00")


def test_classify_transaction_type_credits() -> None:
    # Payments
    assert (
        classify_transaction_type("AUTOPAY PAYMENT RECEIVED", True, Decimal("5000"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("UPI/PAYMENT VIA CRED", True, Decimal("1000"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("NEFT PAYMENT HDFC", True, Decimal("2000"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("IMPS PAYMENT ICICI", True, Decimal("3000"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("BILLDESK PAYMENT", True, Decimal("4000"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("NETBANKING TRANSFER", True, Decimal("500"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("IBILL DESK PAYMENT", True, Decimal("600"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("THANK YOU FOR YOUR PAYMENT", True, Decimal("700"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("BIL/ONL PAYMENT", True, Decimal("800"))
        == TransactionType.PAYMENT
    )
    assert (
        classify_transaction_type("DIRECT DEBIT", True, Decimal("900")) == TransactionType.PAYMENT
    )

    # Rewards / Reversals / Refunds
    assert (
        classify_transaction_type("CASHBACK REWARD FOR APRIL", True, Decimal("250"))
        == TransactionType.REWARD
    )
    assert (
        classify_transaction_type("POINTS REDEEM CREDIT", True, Decimal("500"))
        == TransactionType.REWARD
    )
    assert (
        classify_transaction_type("FAILED TXN REVERSAL", True, Decimal("1200"))
        == TransactionType.REVERSAL
    )
    assert (
        classify_transaction_type("CHARGEBACK RESOLUTION", True, Decimal("3400"))
        == TransactionType.REVERSAL
    )
    assert (
        classify_transaction_type("AMAZON REFUND RECEIVED", True, Decimal("899"))
        == TransactionType.REFUND
    )


def test_classify_transaction_type_debits() -> None:
    # Tax / GST
    assert classify_transaction_type("IGST-DB@18%", False, Decimal("180")) == TransactionType.GST
    assert classify_transaction_type("CGST CHARGE", False, Decimal("90")) == TransactionType.GST
    assert classify_transaction_type("SGST CHARGE", False, Decimal("90")) == TransactionType.GST

    # Interest / Finance charges
    assert (
        classify_transaction_type("FINANCE CHARGE ON REVOLVING", False, Decimal("450"))
        == TransactionType.INTEREST
    )
    assert (
        classify_transaction_type("INTEREST CHARGE", False, Decimal("300"))
        == TransactionType.INTEREST
    )

    # Fees
    assert (
        classify_transaction_type("ANNUAL MEMBERSHIP FEE", False, Decimal("1500"))
        == TransactionType.FEE
    )
    assert (
        classify_transaction_type("LATE PAYMENT FEE", False, Decimal("750")) == TransactionType.FEE
    )
    assert classify_transaction_type("FUEL SURCHARGE", False, Decimal("50")) == TransactionType.FEE
    assert (
        classify_transaction_type("FOREX MARKUP FEE", False, Decimal("200")) == TransactionType.FEE
    )

    # EMI
    assert (
        classify_transaction_type("EASYEMI INSTALLMENT 1 OF 6", False, Decimal("2500"))
        == TransactionType.EMI
    )
    assert (
        classify_transaction_type("SMARTEMI PRINCIPAL", False, Decimal("1500"))
        == TransactionType.EMI
    )
    assert (
        classify_transaction_type("FLEXIPAY LOAN REPAYMENT", False, Decimal("3000"))
        == TransactionType.EMI
    )

    # Cash Advance
    assert (
        classify_transaction_type("ATM CASH WITHDRAWAL MUMBAI", False, Decimal("5000"))
        == TransactionType.CASH_WITHDRAWAL
    )

    # Adjustments
    assert (
        classify_transaction_type("MANUAL ADJUSTMENT DEBIT", False, Decimal("100"))
        == TransactionType.ADJUSTMENT
    )

    # Standard Purchases
    assert (
        classify_transaction_type("SWIGGY BANGALORE", False, Decimal("450"))
        == TransactionType.PURCHASE
    )
    assert (
        classify_transaction_type("AMAZON INDIA", False, Decimal("1299"))
        == TransactionType.PURCHASE
    )


def test_sanitize_merchant_text() -> None:
    assert sanitize_merchant_text("  * * SWIGGY   BANGALORE - - ") == "SWIGGY BANGALORE"
    assert sanitize_merchant_text(": AMAZON INDIA /") == "AMAZON INDIA"
    assert sanitize_merchant_text("") == ""
