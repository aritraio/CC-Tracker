import json
import re
from pathlib import Path
from typing import Any

from app.schemas.categorization import Category

# Payment gateway prefixes to strip
GATEWAY_PREFIX_REGEX = re.compile(
    r"^(?:PYTM\*|PAYTM\*|RAZORPAY\*|RZPX\*|BILLDESK\*|CCAVENUE\*|PAYU\*|CASHFREE\*|INSTAMOJO\*|AIRPAY\*|EBS\*|PINELABS\*|POS\s+|ECOM\s+|UPI/|IN/|WWW\.)\s*",
    re.IGNORECASE,
)

# Trailing location, ISO country code, or digits
TRAILING_NOISE_REGEX = re.compile(
    r"\s+(?:BANGALORE|BENGALURU|MUMBAI|NEW DELHI|DELHI|GURGAON|GURUGRAM|NOIDA|HYDERABAD|SECUNDERABAD|CHENNAI|PUNE|KOLKATA|AHMEDABAD|JAIPUR|IND|IN|MH|KA|DL|TN|TS|UP|WB)\b.*$",
    re.IGNORECASE,
)


def clean_raw_merchant(raw_text: str) -> str:
    """Normalize raw transaction text by stripping gateway wrappers and location codes."""
    if not raw_text:
        return ""

    cleaned = raw_text.strip()
    # Strip leading payment gateway identifiers
    cleaned = GATEWAY_PREFIX_REGEX.sub("", cleaned)
    # Strip trailing location and country codes
    cleaned = TRAILING_NOISE_REGEX.sub("", cleaned)
    # Strip excessive punctuation
    cleaned = re.sub(r"[\*#_]+", " ", cleaned)
    # Normalize whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


class MerchantDictionary:
    """Tier 1: High-Speed Exact & Pattern Matcher backed by dictionary.json."""

    def __init__(self, dictionary_path: Path | None = None) -> None:
        if dictionary_path is None:
            dictionary_path = Path(__file__).parent / "dictionary.json"

        self._entries: list[dict[str, Any]] = []
        # Pattern map: pattern (upper) -> (canonical_name, category, subcategory)
        self._exact_map: dict[str, tuple[str, Category, str | None]] = {}
        self._regex_rules: list[tuple[re.Pattern[str], str, Category, str | None]] = []

        self._load_dictionary(dictionary_path)

    def _load_dictionary(self, path: Path) -> None:
        if not path.exists():
            return

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        self._entries = data
        for entry in data:
            canonical = entry["canonical_name"]
            cat = Category(entry["category"])
            subcat = entry.get("subcategory")

            for pattern in entry.get("patterns", []):
                pattern_upper = pattern.upper().strip()
                self._exact_map[pattern_upper] = (canonical, cat, subcat)

                # Also compile word boundary regex for substring matching
                escaped = re.escape(pattern_upper)
                regex = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
                self._regex_rules.append((regex, canonical, cat, subcat))

    def match(self, raw_text: str) -> tuple[str, Category, str | None] | None:
        """
        Attempt to match a raw merchant string against the Tier 1 dictionary.
        Returns (canonical_name, Category, subcategory) if matched, else None.
        """
        if not raw_text:
            return None

        cleaned = clean_raw_merchant(raw_text).upper()
        raw_upper = raw_text.upper()

        # 1. Direct exact match on cleaned string
        if cleaned in self._exact_map:
            return self._exact_map[cleaned]

        # 2. Direct exact match on raw uppercase string
        if raw_upper in self._exact_map:
            return self._exact_map[raw_upper]

        # 3. Substring word-boundary match against patterns
        for regex, canonical, cat, subcat in self._regex_rules:
            if regex.search(raw_upper) or regex.search(cleaned):
                return canonical, cat, subcat

        return None


# Global singleton instance
_default_dictionary: MerchantDictionary | None = None


def get_default_dictionary() -> MerchantDictionary:
    global _default_dictionary
    if _default_dictionary is None:
        _default_dictionary = MerchantDictionary()
    return _default_dictionary
