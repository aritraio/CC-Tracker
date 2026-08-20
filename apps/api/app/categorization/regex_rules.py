import re

from app.schemas.categorization import Category

# High-precision keyword regex rules for Tier 2 heuristic matching
REGEX_RULES: list[tuple[re.Pattern[str], Category, str | None]] = [
    # 1. Transport & Fuel
    (
        re.compile(
            r"\b(?:PETROL|DIESEL|FUEL|AUTO\s*FUELS|GAS\s*STATION|PETROLEUM|FUEL\s*PUMP|CNG\s*STATION|AUTO\s*GAS)\b",
            re.IGNORECASE,
        ),
        Category.TRANSPORT_AND_FUEL,
        "Fuel",
    ),
    (
        re.compile(
            r"\b(?:CAB|TAXI|METRO\s*RAIL|TRANSIT|PARKING|TOLL\s*PLAZA|FASTAG|AUTO\s*RICKSHAW)\b",
            re.IGNORECASE,
        ),
        Category.TRANSPORT_AND_FUEL,
        "Local Transport",
    ),
    # 2. Food & Dining
    (
        re.compile(
            r"\b(?:RESTAURANT|CAFE|BAKERY|FOODS|BISTRO|DHABA|BAR\s*&\s*RESTAURANT|BREWERY|KITCHEN|DINER|SWEETS|PIZZA|BURGER|COFFEE\s*SHOP|TEA\s*STALL|TIFFIN|CANTEEN|EATERY|PIZZERIA|BIRYANI|DHABA)\b",
            re.IGNORECASE,
        ),
        Category.FOOD_AND_DINING,
        "Dining Out",
    ),
    # 3. Groceries & Quick-Commerce
    (
        re.compile(
            r"\b(?:SUPERMARKET|HYPERMARKET|GROCERY|PROVISION\s*STORE|MART|KIRANA|ORGANIC\s*STORE|BAZAAR|VEGETABLES|FRUITS|DAIRY|MILK\s*STORE)\b",
            re.IGNORECASE,
        ),
        Category.GROCERIES_AND_QUICK_COMMERCE,
        "Supermarket & Grocery",
    ),
    # 4. Healthcare & Fitness
    (
        re.compile(
            r"\b(?:PHARMACY|CHEMIST|DRUG\s*STORE|HOSPITAL|CLINIC|DIAGNOSTICS|PATHOLOGY\s*LAB|DENTAL\s*CLINIC|EYE\s*CARE|HEALTHCARE|MEDICARE|MEDICAL\s*STORE|GYM|FITNESS\s*CENTRE|NURSING\s*HOME)\b",
            re.IGNORECASE,
        ),
        Category.HEALTHCARE_AND_FITNESS,
        "Medical & Healthcare",
    ),
    # 5. Travel & Lodging
    (
        re.compile(
            r"\b(?:AIRLINES|AIRWAYS|TRAVELS|HOTEL\s*AND\s*SUITES|RESORT|LODGE|TOURS|FLIGHT|RAILWAYS|HOMESTAY|MOTEL|INN\s*&\s*SUITES)\b",
            re.IGNORECASE,
        ),
        Category.TRAVEL_AND_LODGING,
        "Travel & Hotels",
    ),
    # 6. Bills & Utilities
    (
        re.compile(
            r"\b(?:ELECTRICITY|WATER\s*BILL|GAS\s*BILL|BROADBAND|TELECOM|FIBERNET|DTH|DISCOM|POWER\s*DISTRIBUTION|POSTPAID\s*BILL|RECHARGE)\b",
            re.IGNORECASE,
        ),
        Category.BILLS_AND_UTILITIES,
        "Utility Bills",
    ),
    # 7. Subscriptions
    (
        re.compile(
            r"\b(?:SUBSCRIPTION|MEMBERSHIP\s*RENEWAL|RECURRING\s*CHARGE|STREAMING\s*SERVICE|SAAS\s*SOFTWARE|CLOUD\s*STORAGE)\b",
            re.IGNORECASE,
        ),
        Category.SUBSCRIPTIONS,
        "Digital Subscriptions",
    ),
    # 8. Education
    (
        re.compile(
            r"\b(?:UNIVERSITY|COLLEGE|SCHOOL|ACADEMY|INSTITUTE|EDUCATION|TUITION|LEARNING|COACHING|CAMPUS|FEES\s*COLLECTION)\b",
            re.IGNORECASE,
        ),
        Category.EDUCATION,
        "Education & Tuition",
    ),
    # 9. Rent & Housing
    (
        re.compile(
            r"\b(?:HOUSE\s*RENT|MAINTENANCE\s*CHARGES|SOCIETY\s*MAINTENANCE|HOUSING\s*SOCIETY|APARTMENT\s*ASSOC|ESTATE\s*MANAGEMENT)\b",
            re.IGNORECASE,
        ),
        Category.RENT_AND_HOUSING,
        "Rent & Maintenance",
    ),
    # 10. Entertainment & OTT
    (
        re.compile(
            r"\b(?:CINEMAS?|MOVIES|THEATRE|MULTIPLEX|AMUSEMENT\s*PARK|GAMING\s*ZONE|ENTERTAINMENT\s*CITY)\b",
            re.IGNORECASE,
        ),
        Category.ENTERTAINMENT_AND_OTT,
        "Movies & Events",
    ),
    # 11. Shopping & Retail
    (
        re.compile(
            r"\b(?:RETAIL|FASHION|APPAREL|CLOTHING|ELECTRONICS|MALL|JEWELLERS|OPTICALS|FOOTWEAR|SHOES|COSMETICS|BOUTIQUE|LIFESTYLE|DEPARTMENT\s*STORE)\b",
            re.IGNORECASE,
        ),
        Category.SHOPPING,
        "Retail Shopping",
    ),
    # 12. Fees & Charges
    (
        re.compile(
            r"\b(?:LATE\s*FEE|ANNUAL\s*FEE|FINANCE\s*CHARGE|INTEREST\s*CHARGE|IGST|CGST|SGST|GST|SURCHARGE|MARKUP\s*FEE|PENALTY)\b",
            re.IGNORECASE,
        ),
        Category.FEES_AND_CHARGES,
        "Bank Charges & Taxes",
    ),
    # 13. Cash Withdrawal
    (
        re.compile(
            r"\b(?:ATM\s*CASH|CASH\s*WDL|CASH\s*ADVANCE|ATM\s*WITHDRAWAL)\b",
            re.IGNORECASE,
        ),
        Category.CASH_WITHDRAWAL,
        "ATM Cash",
    ),
]


def match_regex_rules(raw_text: str) -> tuple[Category, str | None] | None:
    """
    Attempt to match a raw merchant text against Tier 2 heuristic rules.
    Returns (Category, subcategory) if matched, else None.
    """
    if not raw_text:
        return None

    for regex, cat, subcat in REGEX_RULES:
        if regex.search(raw_text):
            return cat, subcat

    return None
