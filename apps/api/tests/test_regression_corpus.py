from datetime import date
from decimal import Decimal
import io
import pytest
from fastapi.testclient import TestClient

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.categorization.engine import get_default_categorization_engine
from app.main import app
from app.parsers.detector import get_parser_for_statement
from app.parsers.hdfc import HdfcStatementParser
from app.parsers.icici import IciciStatementParser
from app.parsers.sbi import SbiStatementParser
from app.parsers.axis import AxisStatementParser
from app.parsers.amex import AmexStatementParser
from app.recommendations.engine import get_default_recommendation_engine
from app.schemas.categorization import CategorizedTransaction, Category
from app.schemas.statement import ExtractedTransaction, StatementHeader, TransactionType
from app.services.reconciliation import reconcile_statement
from app.services.validator import validate_transactions

client = TestClient(app)


def test_multi_page_statement_stitching() -> None:
    """Test extracting transactions that span across multiple statement pages."""
    txns = [
        ExtractedTransaction(
            transaction_date=date(2026, 6, 1),
            merchant_raw="SWIGGY BANGALORE IN",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.PURCHASE,
            source_page=1,
        ),
        ExtractedTransaction(
            transaction_date=date(2026, 6, 5),
            merchant_raw="AMAZON SELLER SERVICES MUMBAI",
            amount=Decimal("1899.00"),
            transaction_type=TransactionType.PURCHASE,
            source_page=2,
        ),
        ExtractedTransaction(
            transaction_date=date(2026, 6, 12),
            merchant_raw="UBER INDIA SYSTEMS HYDERABAD",
            amount=Decimal("380.00"),
            transaction_type=TransactionType.PURCHASE,
            source_page=3,
        ),
    ]

    header = StatementHeader(
        issuer="HDFC Bank",
        card_last_4="1234",
        statement_period_start=date(2026, 6, 1),
        statement_period_end=date(2026, 6, 30),
        total_debits=Decimal("2729.00"),
        total_amount_due=Decimal("2729.00"),
    )

    reconciliation = reconcile_statement(header=header, transactions=txns)
    assert reconciliation.status == "VALIDATED"
    assert reconciliation.is_balanced is True
    assert reconciliation.extracted_debits == Decimal("2729.00")
    assert len(txns) == 3


def test_statement_with_refunds_and_reversals() -> None:
    """Test statement containing purchase, refund credit, and reversal transactions."""
    txns = [
        ExtractedTransaction(
            transaction_date=date(2026, 6, 2),
            merchant_raw="ZOMATO RESTAURANT",
            amount=Decimal("1200.00"),
            transaction_type=TransactionType.PURCHASE,
            source_page=1,
        ),
        ExtractedTransaction(
            transaction_date=date(2026, 6, 4),
            merchant_raw="ZOMATO REFUND",
            amount=Decimal("400.00"),
            transaction_type=TransactionType.REFUND,
            source_page=1,
        ),
        ExtractedTransaction(
            transaction_date=date(2026, 6, 8),
            merchant_raw="AIRTEL PAYMENT REVERSAL",
            amount=Decimal("299.00"),
            transaction_type=TransactionType.REVERSAL,
            source_page=1,
        ),
    ]

    header = StatementHeader(
        issuer="ICICI Bank",
        card_last_4="5678",
        total_debits=Decimal("1200.00"),
        total_credits=Decimal("699.00"),
    )

    reconciliation = reconcile_statement(header=header, transactions=txns)
    assert reconciliation.status == "VALIDATED"
    assert reconciliation.extracted_debits == Decimal("1200.00")
    assert reconciliation.extracted_credits == Decimal("699.00")

    # Categorize and run analytics
    cat_engine = get_default_categorization_engine()
    categorized, _ = cat_engine.categorize_batch(txns)

    analytics_engine = get_default_analytics_engine()
    analytics = analytics_engine.compute_analytics(categorized, header)

    assert analytics.spend_metrics.total_debits == Decimal("1200.00")
    assert analytics.spend_metrics.total_credits == Decimal("699.00")
    assert analytics.spend_metrics.net_spend == Decimal("501.00")


def test_statement_with_emi_and_gst_items() -> None:
    """Test statement with EMI installment, interest charge, and GST tax lines."""
    txns = [
        ExtractedTransaction(
            transaction_date=date(2026, 6, 10),
            merchant_raw="APPLE STORE EMI PRINCIPAL 01/06",
            amount=Decimal("8500.00"),
            transaction_type=TransactionType.EMI,
            source_page=1,
        ),
        ExtractedTransaction(
            transaction_date=date(2026, 6, 10),
            merchant_raw="EMI INTEREST CHARGE",
            amount=Decimal("450.00"),
            transaction_type=TransactionType.INTEREST,
            source_page=1,
        ),
        ExtractedTransaction(
            transaction_date=date(2026, 6, 10),
            merchant_raw="IGST ON INTEREST 18%",
            amount=Decimal("81.00"),
            transaction_type=TransactionType.GST,
            source_page=1,
        ),
    ]

    header = StatementHeader(
        issuer="SBI Card",
        card_last_4="9999",
        total_debits=Decimal("9031.00"),
    )

    reconciliation = reconcile_statement(header=header, transactions=txns)
    assert reconciliation.status == "VALIDATED"
    assert reconciliation.extracted_debits == Decimal("9031.00")

    cat_engine = get_default_categorization_engine()
    categorized, _ = cat_engine.categorize_batch(txns)
    assert categorized[2].category == Category.FEES_AND_CHARGES


def test_reconciliation_boundary_tolerance() -> None:
    """Test exact ₹1.00 tolerance boundary for rounding reconciliation."""
    txns = [
        ExtractedTransaction(
            transaction_date=date(2026, 6, 15),
            merchant_raw="RELIANCE DIGITAL",
            amount=Decimal("15000.50"),
            transaction_type=TransactionType.PURCHASE,
            source_page=1,
        )
    ]

    # Delta of ₹0.50 <= ₹1.00 -> VALIDATED
    header_pass = StatementHeader(
        issuer="Axis Bank",
        total_debits=Decimal("15000.00"),
    )
    rec_pass = reconcile_statement(header=header_pass, transactions=txns)
    assert rec_pass.status == "VALIDATED"
    assert rec_pass.discrepancy == Decimal("0.50")

    # Delta of ₹1.50 > ₹1.00 -> REVIEW_REQUIRED
    header_fail = StatementHeader(
        issuer="Axis Bank",
        total_debits=Decimal("14999.00"),
    )
    rec_fail = reconcile_statement(header=header_fail, transactions=txns)
    assert rec_fail.status == "REVIEW_REQUIRED"
    assert rec_fail.discrepancy == Decimal("1.50")


def test_zero_transactions_statement() -> None:
    """Test handling of a statement with 0 transactions (dormant card cycle)."""
    header = StatementHeader(
        issuer="American Express",
        card_last_4="0001",
        statement_period_start=date(2026, 6, 1),
        statement_period_end=date(2026, 6, 30),
        total_amount_due=Decimal("0.00"),
        total_debits=Decimal("0.00"),
        total_credits=Decimal("0.00"),
    )

    reconciliation = reconcile_statement(header=header, transactions=[])
    assert reconciliation.status == "VALIDATED"
    assert reconciliation.is_balanced is True

    validation = validate_transactions(header=header, transactions=[])
    assert validation.is_valid is True

    analytics_engine = get_default_analytics_engine()
    analytics = analytics_engine.compute_analytics([], header)
    assert analytics.spend_metrics.total_debits == Decimal("0.00")
    assert analytics.spend_metrics.total_transaction_count == 0
