import json
import logging
import re
from decimal import Decimal
from typing import Any

from app.core.config import settings
from app.schemas.analytics import StatementAnalytics
from app.schemas.anomalies import AnomalyDetectionResult, Finding, FindingSeverity
from app.schemas.recommendations import (
    ActionStep,
    FindingHighlight,
    LLMExplanationResult,
    RecommendationResult,
)
from app.schemas.statement import StatementHeader

logger = logging.getLogger(__name__)

EXPLAINER_SYSTEM_PROMPT = """You are CC Track's Financial Intelligence Explainer — a compassionate, sharp, and highly encouraging personal financial coach.
Your job is to translate complex credit card analytics, detected spending anomalies, and rule-based recommendations into an actionable, empathetic, and clear narrative.

STRICT INSTRUCTIONS:
1. NEVER hallucinate numbers or calculate new totals. Only use the numbers provided in the input payload.
2. Be empathetic, constructive, and direct. Avoid generic shaming (e.g., do not say "Stop buying coffee").
3. Emphasize high-leverage changes and realistic monthly savings.
4. Output STRICT JSON conforming to this exact schema:
{
  "executive_summary": "A 2-3 sentence high-level overview of the billing cycle spending and health.",
  "what_stands_out": [
    {
      "finding_title": "Short title of anomaly/pattern",
      "observation": "Clear 1-2 sentence explanation of what happened and why it matters.",
      "urgency": "Immediate Action" | "This Month" | "Good Habit"
    }
  ],
  "action_steps": [
    {
      "step_number": 1,
      "title": "Clear Action Title",
      "description": "Concrete behavioral or tactical change to implement.",
      "estimated_impact": "Save ~₹X/month" or "Credit Score Protection"
    }
  ],
  "coaching_tone_note": "A warm, encouraging closing piece of advice."
}

Return ONLY valid raw JSON without markdown backticks or commentary.
"""


class DeterministicExplainer:
    """
    Deterministic rule-based explanation formatter.
    Guarantees 100% reliable, zero-API-dependency structured explanations.
    """

    def generate_explanation(
        self,
        analytics: StatementAnalytics,
        findings: list[Finding] | AnomalyDetectionResult,
        recommendations: RecommendationResult,
        header: StatementHeader | None = None,
    ) -> LLMExplanationResult:
        finding_list = findings.findings if isinstance(findings, AnomalyDetectionResult) else findings
        spend = analytics.spend_metrics
        recs = recommendations.recommendations
        total_savings = recommendations.total_potential_monthly_savings

        # 1. Executive summary
        issuer_str = f"on your {header.issuer} card" if header and header.issuer else "this billing cycle"
        if spend.total_debits == Decimal("0.00"):
            exec_summary = (
                f"No debit spending was recorded {issuer_str}. Your account shows total credits of "
                f"₹{spend.total_credits:,.2f}."
            )
        elif len(finding_list) == 0 or (len(recs) == 1 and recs[0].type.value == "POSITIVE_REINFORCEMENT"):
            exec_summary = (
                f"You spent ₹{spend.total_debits:,.2f} across {spend.debit_transaction_count} transactions "
                f"{issuer_str}. Your spending patterns demonstrate excellent discipline with no significant "
                "budget leaks or category overruns."
            )
        else:
            top_cat = analytics.category_breakdown[0] if analytics.category_breakdown else None
            top_cat_str = f" led primarily by {top_cat.category.value} (₹{top_cat.total_amount:,.2f})" if top_cat else ""
            savings_str = f" We've identified up to ₹{total_savings:,.2f} in potential monthly savings." if total_savings > Decimal("0.00") else ""
            exec_summary = (
                f"Your total spending {issuer_str} reached ₹{spend.total_debits:,.2f} across "
                f"{spend.debit_transaction_count} transactions{top_cat_str}.{savings_str}"
            )

        # 2. What stands out
        highlights: list[FindingHighlight] = []
        for finding in finding_list[:4]:
            if finding.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH):
                urgency = "Immediate Action"
            elif finding.severity == FindingSeverity.MEDIUM:
                urgency = "This Month"
            else:
                urgency = "Good Habit"

            highlights.append(
                FindingHighlight(
                    finding_title=finding.title,
                    observation=finding.description,
                    urgency=urgency,
                )
            )

        if not highlights:
            highlights.append(
                FindingHighlight(
                    finding_title="Stable Category Distribution",
                    observation="Spending across all categories is consistent and within expected thresholds.",
                    urgency="Good Habit",
                )
            )

        # 3. Action steps
        action_steps: list[ActionStep] = []
        step_num = 1
        for rec in recs[:3]:
            impact = (
                f"Save ₹{rec.estimated_monthly_savings:,.2f}/mo"
                if rec.estimated_monthly_savings > Decimal("0.00")
                else "Financial Health & Credit Score"
            )
            action_steps.append(
                ActionStep(
                    step_number=step_num,
                    title=rec.title,
                    description=rec.action,
                    estimated_impact=impact,
                )
            )
            step_num += 1

        if not action_steps:
            action_steps.append(
                ActionStep(
                    step_number=1,
                    title="Maintain Current Spending Pacing",
                    description="Keep reviewing your monthly statement summaries and optimize card reward redemptions.",
                    estimated_impact="Sustained Financial Health",
                )
            )

        # 4. Coaching tone note
        if total_savings >= Decimal("3000.00"):
            tone_note = (
                f"Making small adjustments to your top discretionary categories can unlock ₹{total_savings:,.2f} "
                "every month without feeling restrictive. Start with Step 1 and track your progress next cycle."
            )
        elif total_savings > Decimal("0.00"):
            tone_note = (
                f"Consolidating small purchases and reviewing recurring charges can easily keep ₹{total_savings:,.2f} "
                "in your pocket every month. Small habit changes compound quickly."
            )
        else:
            tone_note = (
                "You're in great financial shape with your current card usage. Keep up the disciplined pacing!"
            )

        return LLMExplanationResult(
            executive_summary=exec_summary,
            what_stands_out=highlights,
            action_steps=action_steps,
            coaching_tone_note=tone_note,
            generated_by="deterministic_template",
            is_fallback=False,
        )


class LLMExplainer:
    """
    Structured AI Explanation Formatter using Google Gemini Flash API with automatic deterministic fallback.
    Ensures zero PII transmission and strict JSON output verification.
    """

    def __init__(self) -> None:
        self.deterministic_explainer = DeterministicExplainer()
        self._gemini_client: Any = None
        self._init_client()

    def _init_client(self) -> None:
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._gemini_client = genai.GenerativeModel(settings.GEMINI_MODEL)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini model for explainer: {e}")

    def explain(
        self,
        analytics: StatementAnalytics,
        findings: list[Finding] | AnomalyDetectionResult,
        recommendations: RecommendationResult,
        header: StatementHeader | None = None,
    ) -> LLMExplanationResult:
        """
        Generate structured, human-friendly financial insights.
        Uses Gemini Flash if configured, else falls back to DeterministicExplainer.
        """
        finding_list = findings.findings if isinstance(findings, AnomalyDetectionResult) else findings

        if not self._gemini_client:
            return self.deterministic_explainer.generate_explanation(
                analytics=analytics,
                findings=finding_list,
                recommendations=recommendations,
                header=header,
            )

        try:
            prompt_payload = self._build_sanitized_prompt_payload(
                analytics=analytics,
                findings=finding_list,
                recommendations=recommendations,
                header=header,
            )
            explanation = self._call_gemini_explainer(prompt_payload)
            return explanation
        except Exception as e:
            logger.warning(f"LLM explanation generation failed: {e}. Falling back to deterministic template.")
            fallback_res = self.deterministic_explainer.generate_explanation(
                analytics=analytics,
                findings=finding_list,
                recommendations=recommendations,
                header=header,
            )
            fallback_res.is_fallback = True
            return fallback_res

    def _build_sanitized_prompt_payload(
        self,
        analytics: StatementAnalytics,
        findings: list[Finding],
        recommendations: RecommendationResult,
        header: StatementHeader | None = None,
    ) -> dict[str, Any]:
        """Construct sanitized summary payload (zero PII, zero full PANs/passwords)."""
        spend = analytics.spend_metrics

        cat_summary = [
            {
                "category": cb.category.value,
                "amount": float(cb.total_amount),
                "percentage": cb.percentage,
                "transaction_count": cb.transaction_count,
                "top_merchants": cb.top_merchants,
            }
            for cb in analytics.category_breakdown[:5]
        ]

        findings_summary = [
            {
                "title": f.title,
                "severity": f.severity.value,
                "description": f.description,
            }
            for f in findings[:5]
        ]

        recs_summary = [
            {
                "title": r.title,
                "estimated_monthly_savings": float(r.estimated_monthly_savings),
                "action": r.action,
                "priority": r.priority,
            }
            for r in recommendations.recommendations[:4]
        ]

        return {
            "statement_summary": {
                "issuer": header.issuer if header else "Credit Card",
                "total_debits": float(spend.total_debits),
                "total_credits": float(spend.total_credits),
                "net_spend": float(spend.net_spend),
                "transaction_count": spend.debit_transaction_count,
                "average_transaction": float(spend.average_transaction_amount),
                "weekend_spend_percentage": analytics.temporal_metrics.weekend_percentage,
                "recurring_subscriptions_total": float(analytics.recurring_analysis.total_monthly_recurring),
                "total_potential_monthly_savings": float(recommendations.total_potential_monthly_savings),
            },
            "top_categories": cat_summary,
            "detected_findings": findings_summary,
            "actionable_recommendations": recs_summary,
        }

    def _call_gemini_explainer(self, payload: dict[str, Any]) -> LLMExplanationResult:
        user_prompt = f"Analyze this structured credit card spending profile and provide actionable explanation JSON:\n{json.dumps(payload, indent=2)}"
        response = self._gemini_client.generate_content(
            f"{EXPLAINER_SYSTEM_PROMPT}\n\n{user_prompt}"
        )

        text = response.text.strip()
        # Clean JSON markdown formatting if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        parsed = json.loads(text)

        what_stands_out = [
            FindingHighlight(
                finding_title=item.get("finding_title", "Observation"),
                observation=item.get("observation", ""),
                urgency=item.get("urgency", "This Month"),
            )
            for item in parsed.get("what_stands_out", [])
        ]

        action_steps = [
            ActionStep(
                step_number=int(item.get("step_number", idx + 1)),
                title=item.get("title", f"Action Step {idx + 1}"),
                description=item.get("description", ""),
                estimated_impact=item.get("estimated_impact"),
            )
            for idx, item in enumerate(parsed.get("action_steps", []))
        ]

        return LLMExplanationResult(
            executive_summary=parsed.get("executive_summary", ""),
            what_stands_out=what_stands_out,
            action_steps=action_steps,
            coaching_tone_note=parsed.get("coaching_tone_note", ""),
            generated_by=settings.GEMINI_MODEL,
            is_fallback=False,
        )


# Global singletons
_default_deterministic_explainer: DeterministicExplainer | None = None
_default_llm_explainer: LLMExplainer | None = None


def get_default_deterministic_explainer() -> DeterministicExplainer:
    global _default_deterministic_explainer
    if _default_deterministic_explainer is None:
        _default_deterministic_explainer = DeterministicExplainer()
    return _default_deterministic_explainer


def get_default_llm_explainer() -> LLMExplainer:
    global _default_llm_explainer
    if _default_llm_explainer is None:
        _default_llm_explainer = LLMExplainer()
    return _default_llm_explainer
