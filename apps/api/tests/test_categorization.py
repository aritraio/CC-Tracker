from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from app.categorization.engine import (
    CategorizationEngine,
    get_default_categorization_engine,
)
from app.categorization.llm_fallback import (
    InMemoryLruCache,
    LlmCategorizer,
    get_default_llm_categorizer,
)
from app.categorization.normalizer import (
    clean_raw_merchant,
    get_default_dictionary,
)
from app.categorization.regex_rules import match_regex_rules
from app.schemas.categorization import Category
from app.schemas.statement import ExtractedTransaction, TransactionType


def test_clean_raw_merchant_gateway_stripping() -> None:
    assert clean_raw_merchant("PYTM*SWIGGY BANGALORE IN") == "SWIGGY"
    assert clean_raw_merchant("RAZORPAY*ZEPTONOW MUMBAI MH") == "ZEPTONOW"
    assert clean_raw_merchant("BILLDESK*AIRTEL POSTPAID DL") == "AIRTEL POSTPAID"
    assert clean_raw_merchant("POS SHELL PETROL PUMP BANGALORE") == "SHELL PETROL PUMP"
    assert clean_raw_merchant("CCAVENUE*MAKEMYTRIP GURGAON") == "MAKEMYTRIP"
    assert clean_raw_merchant("WWW.NETFLIX.COM IND") == "NETFLIX.COM"
    assert clean_raw_merchant("") == ""


def test_tier1_merchant_dictionary_matches() -> None:
    dictionary = get_default_dictionary()

    # Empty text
    assert dictionary.match("") is None

    # Food & Dining
    match = dictionary.match("SWIGGY BANGALORE")
    assert match is not None
    assert match[0] == "Swiggy"
    assert match[1] == Category.FOOD_AND_DINING

    match = dictionary.match("ZOMATO MEDIA PVT LTD")
    assert match is not None
    assert match[0] == "Zomato"
    assert match[1] == Category.FOOD_AND_DINING

    match = dictionary.match("TATA STARBUCKS MUMBAI")
    assert match is not None
    assert match[0] == "Starbucks"

    # Quick Commerce & Groceries
    match = dictionary.match("BLINK COMMERCE PRIVATE LIMITED")
    assert match is not None
    assert match[0] == "Blinkit"
    assert match[1] == Category.GROCERIES_AND_QUICK_COMMERCE

    match = dictionary.match("ZEPTO KIRANAKART")
    assert match is not None
    assert match[0] == "Zepto"

    # Shopping
    match = dictionary.match("AMZN MKTP IND PVT LTD")
    assert match is not None
    assert match[0] == "Amazon"
    assert match[1] == Category.SHOPPING

    match = dictionary.match("MYNTRA DESIGNS BLR")
    assert match is not None
    assert match[0] == "Myntra"

    # Transport & Fuel
    match = dictionary.match("UBER INDIA SYSTEMS")
    assert match is not None
    assert match[0] == "Uber"
    assert match[1] == Category.TRANSPORT_AND_FUEL

    match = dictionary.match("HINDUSTAN PETROLEUM HPCL")
    assert match is not None
    assert match[0] == "HPCL Petrol"

    # Travel & Lodging
    match = dictionary.match("INTERGLOBE AVIATION INDIGO")
    assert match is not None
    assert match[0] == "IndiGo Airlines"
    assert match[1] == Category.TRAVEL_AND_LODGING

    match = dictionary.match("IRCTC TICKETING SERVICES")
    assert match is not None
    assert match[0] == "IRCTC"

    # Subscriptions
    match = dictionary.match("NETFLIX ENTERTAINMENT")
    assert match is not None
    assert match[0] == "Netflix"
    assert match[1] == Category.SUBSCRIPTIONS

    match = dictionary.match("SPOTIFY INDIA")
    assert match is not None
    assert match[0] == "Spotify"

    # Healthcare
    match = dictionary.match("APOLLO PHARMACY 247")
    assert match is not None
    assert match[0] == "Apollo Pharmacy"
    assert match[1] == Category.HEALTHCARE_AND_FITNESS

    match = dictionary.match("CULT FIT HEALTHCARE")
    assert match is not None
    assert match[0] == "Cult.fit"


def test_tier2_regex_heuristic_rules() -> None:
    assert match_regex_rules("") is None

    # Fuel keyword
    match = match_regex_rules("LOCAL PETROL PUMP WHITEFIELD")
    assert match is not None
    assert match[0] == Category.TRANSPORT_AND_FUEL

    # Dining keyword
    match = match_regex_rules("ROYAL PUNJAB DHABA AND RESTAURANT")
    assert match is not None
    assert match[0] == Category.FOOD_AND_DINING

    # Groceries keyword
    match = match_regex_rules("SRI LAKSHMI PROVISION STORE")
    assert match is not None
    assert match[0] == Category.GROCERIES_AND_QUICK_COMMERCE

    # Medical keyword
    match = match_regex_rules("SHREE GANESH PHARMACY AND CLINIC")
    assert match is not None
    assert match[0] == Category.HEALTHCARE_AND_FITNESS

    # Education keyword
    match = match_regex_rules("DELHI PUBLIC SCHOOL TUITION FEES")
    assert match is not None
    assert match[0] == Category.EDUCATION

    # Utilities keyword
    match = match_regex_rules("BESCOM ELECTRICITY BILL PAYMENT")
    assert match is not None
    assert match[0] == Category.BILLS_AND_UTILITIES

    # Rent keyword
    match = match_regex_rules("PALM MEADOWS SOCIETY MAINTENANCE")
    assert match is not None
    assert match[0] == Category.RENT_AND_HOUSING

    # Non-matching string
    assert match_regex_rules("RANDOM XYZ CORP 12345") is None


def test_in_memory_lru_cache() -> None:
    cache = InMemoryLruCache(maxsize=3)
    cache.set("A", ("Brand A", Category.SHOPPING, None))
    cache.set("B", ("Brand B", Category.FOOD_AND_DINING, None))
    cache.set("C", ("Brand C", Category.TRANSPORT_AND_FUEL, None))

    assert len(cache) == 3
    assert cache.get("A") == ("Brand A", Category.SHOPPING, None)

    # Adding a 4th element evicts oldest ("B" because "A" was accessed)
    cache.set("D", ("Brand D", Category.SUBSCRIPTIONS, None))
    assert len(cache) == 3
    assert cache.get("B") is None
    assert cache.get("A") is not None
    assert cache.get("D") is not None


def test_tier3_llm_fallback_mocked() -> None:
    categorizer = LlmCategorizer()
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = """
    [
      {
        "raw": "MYSTERIOUS CAFE BLR",
        "canonical_name": "Mysterious Cafe",
        "category": "Food & Dining",
        "subcategory": "Cafe"
      }
    ]
    """
    mock_gemini.generate_content.return_value = mock_response
    categorizer._gemini_client = mock_gemini

    results = categorizer.categorize_batch(["MYSTERIOUS CAFE BLR"])

    assert "MYSTERIOUS CAFE BLR" in results
    canonical, cat, subcat = results["MYSTERIOUS CAFE BLR"]
    assert canonical == "Mysterious Cafe"
    assert cat == Category.FOOD_AND_DINING
    assert subcat == "Cafe"

    # Second call should hit the in-memory cache without calling Gemini
    mock_gemini.generate_content.reset_mock()
    results_second = categorizer.categorize_batch(["MYSTERIOUS CAFE BLR"])
    assert results_second["MYSTERIOUS CAFE BLR"] == (canonical, cat, subcat)
    mock_gemini.generate_content.assert_not_called()


def test_categorization_engine_orchestration_batch() -> None:
    engine = CategorizationEngine()

    # Empty batch
    empty_res, empty_stats = engine.categorize_batch([])
    assert len(empty_res) == 0
    assert empty_stats.total_transactions == 0

    transactions = [
        ExtractedTransaction(
            transaction_date=date(2024, 4, 1),
            merchant_raw="PYTM*SWIGGY BANGALORE",
            amount=Decimal("350.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 2),
            merchant_raw="AMZN MKTP IND",
            amount=Decimal("1200.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 3),
            merchant_raw="CITY PETROL PUMP",  # Tier 2 regex
            amount=Decimal("2000.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 4),
            merchant_raw="AUTOPAY PAYMENT",  # Payment
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.PAYMENT,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 5),
            merchant_raw="NETFLIX ENTERTAINMENT",
            amount=Decimal("649.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
        ExtractedTransaction(
            transaction_date=date(2024, 4, 6),
            merchant_raw="UNKNOWN UNRESOLVED HARDWARE 999",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.PURCHASE,
        ),
    ]

    categorized, stats = engine.categorize_batch(transactions)

    assert len(categorized) == 6
    assert stats.total_transactions == 6
    assert stats.tier1_matches >= 3  # Swiggy, Amazon, Payment, Netflix
    assert stats.tier2_matches >= 1  # City Petrol Pump
    assert stats.tier3_matches >= 1  # Unresolved Hardware

    # Verify Swiggy
    assert categorized[0].merchant_normalized == "Swiggy"
    assert categorized[0].category == Category.FOOD_AND_DINING
    assert categorized[0].tier == 1

    # Verify Amazon
    assert categorized[1].merchant_normalized == "Amazon"
    assert categorized[1].category == Category.SHOPPING
    assert categorized[1].tier == 1

    # Verify Petrol Pump
    assert categorized[2].category == Category.TRANSPORT_AND_FUEL
    assert categorized[2].tier == 2

    # Verify Netflix recurring flag
    assert categorized[4].merchant_normalized == "Netflix"
    assert categorized[4].category == Category.SUBSCRIPTIONS
    assert categorized[4].is_recurring is True

    # Single transaction categorization
    single = engine.categorize_transaction(transactions[0])
    assert single.merchant_normalized == "Swiggy"

    # Singletons
    assert get_default_categorization_engine() is not None
    assert get_default_llm_categorizer() is not None
