import json
import logging
import re
import threading
from collections import OrderedDict
from typing import Any

from app.core.config import settings
from app.schemas.categorization import Category

logger = logging.getLogger(__name__)

# Standard categories allowed for LLM output
VALID_CATEGORIES = {c.value: c for c in Category}

SYSTEM_PROMPT = """You are a specialized Indian credit card transaction categorizer.
Categorize each merchant string into exactly ONE of the following 14 categories:
1. "Food & Dining"
2. "Shopping"
3. "Groceries & Quick-Commerce"
4. "Transport & Fuel"
5. "Travel & Lodging"
6. "Bills & Utilities"
7. "Entertainment & OTT"
8. "Subscriptions"
9. "Healthcare & Fitness"
10. "Education"
11. "Rent & Housing"
12. "Fees & Charges"
13. "Cash Withdrawal"
14. "Other / Uncategorized"

For each item, return a JSON array of objects with:
- "raw": Exact original input string
- "canonical_name": Cleaned readable brand or business name (e.g. "Swiggy", "Local Kirana Store")
- "category": One of the exact 14 category names listed above
- "subcategory": Optional specific subcategory (e.g. "Bakery", "Electronics", "Apparel")

Return strictly valid JSON only without markdown code blocks.
"""


class InMemoryLruCache:
    """Thread-safe LRU Cache for categorized merchant strings."""

    def __init__(self, maxsize: int = 2000) -> None:
        self._maxsize = maxsize
        self._cache: OrderedDict[str, tuple[str, Category, str | None]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> tuple[str, Category, str | None] | None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return None

    def set(self, key: str, value: tuple[str, Category, str | None]) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)


class LlmCategorizer:
    """
    Tier 3: Batch LLM Fallback (Google Gemini Flash / OpenAI) with strict privacy preservation
    and in-memory LRU caching.
    """

    def __init__(self) -> None:
        self.cache = InMemoryLruCache(maxsize=5000)
        self._gemini_client: Any = None
        self._init_client()

    def _init_client(self) -> None:
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._gemini_client = genai.GenerativeModel(settings.GEMINI_MODEL)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

    def categorize_batch(
        self, raw_merchants: list[str]
    ) -> dict[str, tuple[str, Category, str | None]]:
        """
        Categorize a batch of raw merchant strings.
        Returns a dict mapping raw_merchant -> (canonical_name, Category, subcategory).
        """
        results: dict[str, tuple[str, Category, str | None]] = {}
        uncached: list[str] = []

        # 1. Check in-memory cache first
        for raw in raw_merchants:
            cached = self.cache.get(raw)
            if cached:
                results[raw] = cached
            else:
                uncached.append(raw)

        if not uncached:
            return results

        # Deduplicate uncached strings
        unique_uncached = list(dict.fromkeys(uncached))

        # 2. Call LLM for unknown merchants if client is configured
        llm_results: dict[str, tuple[str, Category, str | None]] = {}
        if self._gemini_client:
            try:
                llm_results = self._call_gemini(unique_uncached)
            except Exception as e:
                logger.warning(f"LLM fallback categorization failed: {e}")

        # 3. Process results and populate cache / fallback
        for raw in unique_uncached:
            if raw in llm_results:
                matched = llm_results[raw]
            else:
                # Fallback: cleaned merchant string with OTHER_UNCATEGORIZED
                clean_name = re.sub(r"[#\*_]+", " ", raw).strip().title() or raw
                matched = (clean_name, Category.OTHER_UNCATEGORIZED, None)

            self.cache.set(raw, matched)
            results[raw] = matched

        return results

    def _call_gemini(self, merchants: list[str]) -> dict[str, tuple[str, Category, str | None]]:
        user_prompt = (
            f"Categorize these Indian credit card merchant descriptions:\n"
            f"{json.dumps(merchants, indent=2)}"
        )

        response = self._gemini_client.generate_content(f"{SYSTEM_PROMPT}\n\n{user_prompt}")

        text = response.text.strip()
        # Strip markdown fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        parsed = json.loads(text)
        results: dict[str, tuple[str, Category, str | None]] = {}

        if isinstance(parsed, list):
            for item in parsed:
                raw = item.get("raw")
                canonical = item.get("canonical_name", raw)
                cat_str = item.get("category", "Other / Uncategorized")
                subcat = item.get("subcategory")

                cat = VALID_CATEGORIES.get(cat_str, Category.OTHER_UNCATEGORIZED)
                if raw:
                    results[raw] = (canonical, cat, subcat)

        return results


# Global singleton instance
_default_llm_categorizer: LlmCategorizer | None = None


def get_default_llm_categorizer() -> LlmCategorizer:
    global _default_llm_categorizer
    if _default_llm_categorizer is None:
        _default_llm_categorizer = LlmCategorizer()
    return _default_llm_categorizer
