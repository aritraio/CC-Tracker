from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categorization import Category


class SpendMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_debits: Decimal = Field(
        Decimal("0.00"), description="Sum of all purchases & debit charges"
    )
    total_credits: Decimal = Field(Decimal("0.00"), description="Sum of all payments & refunds")
    net_spend: Decimal = Field(Decimal("0.00"), description="Total debits minus refunds/credits")
    total_transaction_count: int = Field(0, ge=0)
    debit_transaction_count: int = Field(0, ge=0)
    credit_transaction_count: int = Field(0, ge=0)
    average_transaction_amount: Decimal = Field(
        Decimal("0.00"), description="Average debit purchase amount"
    )
    median_transaction_amount: Decimal = Field(
        Decimal("0.00"), description="Median debit purchase amount"
    )
    max_transaction_amount: Decimal = Field(
        Decimal("0.00"), description="Single largest debit purchase"
    )
    min_transaction_amount: Decimal = Field(
        Decimal("0.00"), description="Single smallest debit purchase"
    )


class CategoryBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: Category
    total_amount: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    percentage: float = Field(0.0, ge=0.0, le=100.0, description="Percentage of total debits")
    transaction_count: int = Field(0, ge=0)
    average_amount: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    top_merchants: list[str] = Field(
        default_factory=list, description="Top 3 merchant names in this category"
    )


class MerchantConcentration(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_name: str
    category: Category
    total_amount: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    percentage: float = Field(0.0, ge=0.0, le=100.0, description="Percentage of total debits")
    transaction_count: int = Field(0, ge=0)


class DailySpend(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    amount: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    transaction_count: int = Field(0, ge=0)
    cumulative_amount: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))


class TemporalMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    daily_spending: list[DailySpend] = Field(default_factory=list)
    weekday_spend: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    weekend_spend: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    weekday_percentage: float = Field(0.0, ge=0.0, le=100.0)
    weekend_percentage: float = Field(0.0, ge=0.0, le=100.0)
    avg_daily_burn_rate: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    day_of_week_breakdown: dict[str, Decimal] = Field(default_factory=dict)


class MicroSpendMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    threshold: Decimal = Field(Decimal("250.00"), description="Micro-spend upper threshold in INR")
    count: int = Field(0, ge=0)
    total_amount: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    percentage_of_transactions: float = Field(0.0, ge=0.0, le=100.0)
    percentage_of_spend: float = Field(0.0, ge=0.0, le=100.0)
    top_micro_merchants: list[str] = Field(default_factory=list)


class RecurringItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_name: str
    category: Category
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    frequency: str = Field("Monthly", description="'Monthly', 'Annual', 'Quarterly'")
    occurrences: int = Field(1, ge=1)
    annualized_cost: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    transaction_dates: list[date] = Field(default_factory=list)


class RecurringAnalysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[RecurringItem] = Field(default_factory=list)
    total_monthly_recurring: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    total_annual_recurring: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    recurring_percentage_of_spend: float = Field(0.0, ge=0.0, le=100.0)


class StatementAnalytics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    spend_metrics: SpendMetrics
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)
    merchant_concentration: list[MerchantConcentration] = Field(default_factory=list)
    temporal_metrics: TemporalMetrics
    micro_spend_metrics: MicroSpendMetrics
    recurring_analysis: RecurringAnalysis
