import hashlib
import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.schemas.statements_api import (
    ParseStatementResponse,
    StatementHistoryItem,
    StatementHistoryResponse,
    StatementSaveRequest,
    StatementSaveResponse,
)

logger = logging.getLogger(__name__)


class StorageService:
    """
    Persistence service managing credit card statements, cards, transactions,
    findings, and recommendations in local memory with seamless Postgres/Supabase readiness.
    """

    def __init__(self) -> None:
        self._statements: dict[str, dict[str, Any]] = {}
        self._cards: dict[str, dict[str, Any]] = {}

    def _generate_file_hash(self, statement: ParseStatementResponse) -> str:
        """Compute SHA-256 fingerprint for deduplication."""
        fingerprint = (
            f"{statement.header.issuer}_"
            f"{statement.header.card_last_4}_"
            f"{statement.header.statement_period_start}_"
            f"{statement.header.statement_period_end}_"
            f"{statement.header.total_amount_due}"
        )
        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    def save_statement_session(self, request: StatementSaveRequest) -> StatementSaveResponse:
        """
        Persist a complete parsed statement session.
        """
        statement_data = request.statement_data
        header = statement_data.header
        user_id = request.user_id or "anonymous_user"
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Manage or create card record
        card_id = f"card_{header.issuer.lower().replace(' ', '_')}_{header.card_last_4 or 'default'}"
        if card_id not in self._cards:
            self._cards[card_id] = {
                "id": card_id,
                "user_id": user_id,
                "issuer": header.issuer,
                "card_name": request.card_name or f"{header.issuer} Card",
                "card_last_4": header.card_last_4,
                "credit_limit": header.credit_limit,
                "created_at": now_iso,
            }

        # 2. Compute statement ID and file hash
        file_hash = self._generate_file_hash(statement_data)
        statement_id = f"stmt_{uuid.uuid4().hex[:12]}"

        # 3. Store full statement session
        saved_txns_count = len(statement_data.transactions) if request.save_transactions else 0
        saved_findings_count = len(statement_data.anomalies.findings) if request.save_findings else 0
        saved_recs_count = len(statement_data.recommendations.recommendations) if request.save_recommendations else 0

        self._statements[statement_id] = {
            "id": statement_id,
            "user_id": user_id,
            "card_id": card_id,
            "file_hash": file_hash,
            "data": statement_data,
            "saved_transactions": request.save_transactions,
            "saved_findings": request.save_findings,
            "saved_recommendations": request.save_recommendations,
            "created_at": now_iso,
        }

        logger.info(
            "Saved statement %s for user %s (%d txns, %d findings, %d recs)",
            statement_id,
            user_id,
            saved_txns_count,
            saved_findings_count,
            saved_recs_count,
        )

        return StatementSaveResponse(
            success=True,
            statement_id=statement_id,
            card_id=card_id,
            saved_transactions_count=saved_txns_count,
            saved_findings_count=saved_findings_count,
            saved_recommendations_count=saved_recs_count,
            saved_at=now_iso,
            message=f"Statement for {header.issuer} saved successfully.",
        )

    def get_statement_history(
        self, user_id: str | None = None, limit: int = 50
    ) -> StatementHistoryResponse:
        """
        Retrieve list of saved statement summaries.
        """
        history_items: list[StatementHistoryItem] = []

        for stmt_id, record in self._statements.items():
            if user_id and record["user_id"] != user_id and record["user_id"] != "anonymous_user":
                continue

            data: ParseStatementResponse = record["data"]
            header = data.header
            card_info = self._cards.get(record["card_id"], {})

            total_due = Decimal(str(header.total_amount_due or data.analytics.spend_metrics.total_debits))
            total_debits = Decimal(str(data.analytics.spend_metrics.total_debits))

            history_items.append(
                StatementHistoryItem(
                    id=stmt_id,
                    issuer=header.issuer,
                    card_last_4=header.card_last_4,
                    card_name=card_info.get("card_name"),
                    period_start=str(header.statement_period_start) if header.statement_period_start else None,
                    period_end=str(header.statement_period_end) if header.statement_period_end else None,
                    due_date=str(header.payment_due_date) if header.payment_due_date else None,
                    total_amount_due=total_due,
                    total_debits=total_debits,
                    reconciliation_status=data.reconciliation_status,
                    transaction_count=len(data.transactions),
                    findings_count=len(data.anomalies.findings),
                    recommendations_count=len(data.recommendations.recommendations),
                    created_at=record["created_at"],
                )
            )

        # Sort newest first
        history_items.sort(key=lambda x: x.created_at, reverse=True)

        return StatementHistoryResponse(
            statements=history_items[:limit],
            total_count=len(history_items),
        )

    def get_statement_by_id(
        self, statement_id: str, user_id: str | None = None
    ) -> ParseStatementResponse | None:
        """
        Retrieve complete parsed statement payload by ID.
        """
        record = self._statements.get(statement_id)
        if not record:
            return None

        if user_id and record["user_id"] != user_id and record["user_id"] != "anonymous_user":
            return None

        return record["data"]

    def delete_statement(self, statement_id: str, user_id: str | None = None) -> bool:
        """
        Delete a statement record.
        """
        record = self._statements.get(statement_id)
        if not record:
            return False

        if user_id and record["user_id"] != user_id and record["user_id"] != "anonymous_user":
            return False

        del self._statements[statement_id]
        return True

    def clear_storage(self) -> None:
        """Reset in-memory storage (for testing)."""
        self._statements.clear()
        self._cards.clear()


_default_storage_service: StorageService | None = None


def get_default_storage_service() -> StorageService:
    """Retrieve singleton StorageService instance."""
    global _default_storage_service
    if _default_storage_service is None:
        _default_storage_service = StorageService()
    return _default_storage_service
