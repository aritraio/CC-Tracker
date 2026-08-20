from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.statement import TransactionType


class Category(StrEnum):
    FOOD_AND_DINING = "Food & Dining"
    SHOPPING = "Shopping"
    GROCERIES_AND_QUICK_COMMERCE = "Groceries & Quick-Commerce"
    TRANSPORT_AND_FUEL = "Transport & Fuel"
    TRAVEL_AND_LODGING = "Travel & Lodging"
    BILLS_AND_UTILITIES = "Bills & Utilities"
    ENTERTAINMENT_AND_OTT = "Entertainment & OTT"
    SUBSCRIPTIONS = "Subscriptions"
    HEALTHCARE_AND_FITNESS = "Healthcare & Fitness"
    EDUCATION = "Education"
    RENT_AND_HOUSING = "Rent & Housing"
    FEES_AND_CHARGES = "Fees & Charges"
    CASH_WITHDRAWAL = "Cash Withdrawal"
    OTHER_UNCATEGORIZED = "Other / Uncategorized"


class CategorizedTransaction(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    transaction_date: date
    post_date: date | None = None
    merchant_raw: str = Field(..., min_length=1, description="Raw transaction description")
    merchant_normalized: str = Field(
        ..., min_length=1, description="Normalized merchant/brand name"
    )
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Transaction amount")
    transaction_type: TransactionType = Field(default=TransactionType.PURCHASE)
    category: Category = Field(
        default=Category.OTHER_UNCATEGORIZED, description="Primary spend category"
    )
    subcategory: str | None = Field(None, description="Optional granular subcategory")
    tier: int = Field(1, ge=1, le=3, description="Categorization tier: 1=Dict, 2=Regex, 3=LLM")
    is_recurring: bool = Field(
        False, description="Flag indicating potential recurring subscription"
    )
    currency: str = "INR"
    source_page: int = Field(1, ge=1)
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)


class CategorizationStats(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    total_transactions: int = 0
    tier1_matches: int = 0
    tier2_matches: int = 0
    tier3_matches: int = 0
    cached_matches: int = 0
    hit_rate: float = 1.0
