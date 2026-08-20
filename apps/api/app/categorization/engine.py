from app.categorization.llm_fallback import (
    LlmCategorizer,
    get_default_llm_categorizer,
)
from app.categorization.normalizer import (
    MerchantDictionary,
    clean_raw_merchant,
    get_default_dictionary,
)
from app.categorization.regex_rules import match_regex_rules
from app.schemas.categorization import (
    CategorizationStats,
    CategorizedTransaction,
    Category,
)
from app.schemas.statement import ExtractedTransaction, TransactionType


class CategorizationEngine:
    """
    3-Tier Categorization Orchestrator:
    - Tier 1: Exact / Substring Merchant Dictionary (250+ Indian Merchants)
    - Tier 2: Heuristic & Keyword Regex Rules (14 Standard Buckets)
    - Tier 3: Privacy-Preserving LLM Fallback (Gemini Flash) with RAM Cache
    """

    def __init__(
        self,
        dictionary: MerchantDictionary | None = None,
        llm_categorizer: LlmCategorizer | None = None,
    ) -> None:
        self.dictionary = dictionary or get_default_dictionary()
        self.llm_categorizer = llm_categorizer or get_default_llm_categorizer()

    def categorize_transaction(self, txn: ExtractedTransaction) -> CategorizedTransaction:
        """Categorize a single transaction through the 3-tier cascade."""
        results, _ = self.categorize_batch([txn])
        return results[0]

    def categorize_batch(
        self, transactions: list[ExtractedTransaction]
    ) -> tuple[list[CategorizedTransaction], CategorizationStats]:
        """
        Categorize a batch of transactions with high-speed Tier 1/2 evaluation
        and single-roundtrip Tier 3 batching.
        """
        if not transactions:
            return [], CategorizationStats()

        categorized: list[CategorizedTransaction | None] = [None] * len(transactions)
        tier1_count = 0
        tier2_count = 0
        tier3_count = 0
        cached_count = 0

        unresolved_indices: list[int] = []
        unresolved_strings: list[str] = []

        # Tier 1 & Tier 2 Evaluation
        for idx, txn in enumerate(transactions):
            # Special case: Payments/Refunds/Reversals
            if txn.transaction_type == TransactionType.PAYMENT:
                categorized[idx] = CategorizedTransaction(
                    transaction_date=txn.transaction_date,
                    post_date=txn.post_date,
                    merchant_raw=txn.merchant_raw,
                    merchant_normalized=clean_raw_merchant(txn.merchant_raw).title() or "Payment",
                    amount=txn.amount,
                    transaction_type=txn.transaction_type,
                    category=Category.OTHER_UNCATEGORIZED,
                    subcategory="Payment",
                    tier=1,
                    is_recurring=False,
                    currency=txn.currency,
                    source_page=txn.source_page,
                    confidence_score=txn.confidence_score,
                )
                tier1_count += 1
                continue

            # 1. Tier 1: Dictionary match
            dict_match = self.dictionary.match(txn.merchant_raw)
            if dict_match:
                canonical, cat, subcat = dict_match
                is_sub = cat == Category.SUBSCRIPTIONS or subcat in {
                    "OTT Streaming",
                    "Music Streaming",
                    "Digital Subscriptions",
                }
                categorized[idx] = CategorizedTransaction(
                    transaction_date=txn.transaction_date,
                    post_date=txn.post_date,
                    merchant_raw=txn.merchant_raw,
                    merchant_normalized=canonical,
                    amount=txn.amount,
                    transaction_type=txn.transaction_type,
                    category=cat,
                    subcategory=subcat,
                    tier=1,
                    is_recurring=is_sub,
                    currency=txn.currency,
                    source_page=txn.source_page,
                    confidence_score=txn.confidence_score,
                )
                tier1_count += 1
                continue

            # 2. Tier 2: Regex Rule match
            regex_match = match_regex_rules(txn.merchant_raw)
            if regex_match:
                cat, subcat = regex_match
                cleaned_name = clean_raw_merchant(txn.merchant_raw).title() or txn.merchant_raw
                is_sub = cat == Category.SUBSCRIPTIONS
                categorized[idx] = CategorizedTransaction(
                    transaction_date=txn.transaction_date,
                    post_date=txn.post_date,
                    merchant_raw=txn.merchant_raw,
                    merchant_normalized=cleaned_name,
                    amount=txn.amount,
                    transaction_type=txn.transaction_type,
                    category=cat,
                    subcategory=subcat,
                    tier=2,
                    is_recurring=is_sub,
                    currency=txn.currency,
                    source_page=txn.source_page,
                    confidence_score=0.9,
                )
                tier2_count += 1
                continue

            # Check cache before adding to Tier 3 batch
            cached = self.llm_categorizer.cache.get(txn.merchant_raw)
            if cached:
                canonical, cat, subcat = cached
                is_sub = cat == Category.SUBSCRIPTIONS
                categorized[idx] = CategorizedTransaction(
                    transaction_date=txn.transaction_date,
                    post_date=txn.post_date,
                    merchant_raw=txn.merchant_raw,
                    merchant_normalized=canonical,
                    amount=txn.amount,
                    transaction_type=txn.transaction_type,
                    category=cat,
                    subcategory=subcat,
                    tier=3,
                    is_recurring=is_sub,
                    currency=txn.currency,
                    source_page=txn.source_page,
                    confidence_score=0.85,
                )
                cached_count += 1
                continue

            unresolved_indices.append(idx)
            unresolved_strings.append(txn.merchant_raw)

        # 3. Tier 3: Batch LLM for remaining unresolved items
        if unresolved_strings:
            llm_results = self.llm_categorizer.categorize_batch(unresolved_strings)
            for idx in unresolved_indices:
                txn = transactions[idx]
                canonical, cat, subcat = llm_results.get(
                    txn.merchant_raw,
                    (
                        clean_raw_merchant(txn.merchant_raw).title() or txn.merchant_raw,
                        Category.OTHER_UNCATEGORIZED,
                        None,
                    ),
                )
                is_sub = cat == Category.SUBSCRIPTIONS
                categorized[idx] = CategorizedTransaction(
                    transaction_date=txn.transaction_date,
                    post_date=txn.post_date,
                    merchant_raw=txn.merchant_raw,
                    merchant_normalized=canonical,
                    amount=txn.amount,
                    transaction_type=txn.transaction_type,
                    category=cat,
                    subcategory=subcat,
                    tier=3,
                    is_recurring=is_sub,
                    currency=txn.currency,
                    source_page=txn.source_page,
                    confidence_score=0.8,
                )
                tier3_count += 1

        final_results = [t for t in categorized if t is not None]
        total = len(transactions)
        resolved_count = tier1_count + tier2_count + cached_count + tier3_count
        hit_rate = (resolved_count / total) if total > 0 else 1.0

        stats = CategorizationStats(
            total_transactions=total,
            tier1_matches=tier1_count,
            tier2_matches=tier2_count,
            tier3_matches=tier3_count,
            cached_matches=cached_count,
            hit_rate=round(hit_rate, 4),
        )

        return final_results, stats


# Global singleton instance
_default_engine: CategorizationEngine | None = None


def get_default_categorization_engine() -> CategorizationEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = CategorizationEngine()
    return _default_engine
