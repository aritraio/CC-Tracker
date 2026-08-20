import io
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.analytics.anomalies import run_anomaly_detection
from app.analytics.engine import get_default_analytics_engine
from app.categorization.engine import get_default_categorization_engine
from app.core.exceptions import CCTrackError, UnsupportedStatementError
from app.parsers.detector import get_parser_for_statement
from app.recommendations.engine import get_default_recommendation_engine
from app.recommendations.llm_explainer import get_default_llm_explainer
from app.schemas.statements_api import (
    ParseStatementResponse,
    StatementHistoryResponse,
    StatementSaveRequest,
    StatementSaveResponse,
    StatementValidateRequest,
    StatementValidateResponse,
)
from app.services.reconciliation import reconcile_statement
from app.services.storage_service import get_default_storage_service
from app.services.validator import validate_transactions


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statements", tags=["Statements"])


@router.post(
    "/parse",
    response_model=ParseStatementResponse,
    status_code=status.HTTP_200_OK,
    summary="Statelessly parse and deeply analyze an uploaded credit card PDF statement",
    description=(
        "Ingests an in-memory PDF statement, detects the issuing bank, extracts structured line items and headers, "
        "runs financial reconciliation, performs 3-tier merchant categorization, calculates deterministic analytics, "
        "identifies 10 behavioral spending anomalies, computes evidence-backed recommendations with conservative savings, "
        "and formats a human-friendly coaching narrative via LLM/deterministic fallback."
    ),
)
async def parse_statement(
    file: UploadFile = File(..., description="Decrypted credit card PDF statement file"),
) -> ParseStatementResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF statements are supported.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded.",
        )

    try:
        # 1. Parse PDF in RAM stream
        pdf_stream = io.BytesIO(content)
        parser = get_parser_for_statement(pdf_stream)
        parsed_statement = parser.parse(pdf_stream)

        header = parsed_statement.header
        raw_transactions = parsed_statement.transactions
        unparsed_lines = parsed_statement.unparsed_lines

        # 2. Financial Reconciliation Check
        reconciliation_summary = reconcile_statement(
            header=header,
            transactions=raw_transactions,
            unparsed_lines=unparsed_lines,
        )

        # 3. Transaction Sanity Validation Check
        validation_result = validate_transactions(
            header=header,
            transactions=raw_transactions,
        )

        # 4. 3-Tier Categorization & Merchant Normalization
        cat_engine = get_default_categorization_engine()
        categorized_transactions, cat_stats = cat_engine.categorize_batch(raw_transactions)

        # 5. Deterministic Analytics Engine
        analytics_engine = get_default_analytics_engine()
        analytics = analytics_engine.compute_analytics(
            transactions=categorized_transactions,
            header=header,
        )

        # 6. Pattern & Anomaly Detectors (10 Detectors)
        anomalies_result = run_anomaly_detection(
            transactions=categorized_transactions,
            analytics=analytics,
            header=header,
        )

        # 7. Evidence-Based Recommendation Engine
        rec_engine = get_default_recommendation_engine()
        recommendations_result = rec_engine.generate_recommendations(
            findings=anomalies_result,
            analytics=analytics,
            transactions=categorized_transactions,
            header=header,
        )

        # 8. Human-Friendly AI Coaching Explanation (Gemini Flash + Deterministic Fallback)
        explainer = get_default_llm_explainer()
        explanation_result = explainer.explain(
            analytics=analytics,
            findings=anomalies_result,
            recommendations=recommendations_result,
            header=header,
        )

        return ParseStatementResponse(
            header=header,
            transactions=categorized_transactions,
            raw_text_length=parsed_statement.raw_text_length,
            reconciliation_status=reconciliation_summary.status,
            reconciliation_discrepancy=reconciliation_summary.discrepancy,
            reconciliation=reconciliation_summary,
            validation=validation_result,
            categorization_stats=cat_stats,
            analytics=analytics,
            anomalies=anomalies_result,
            recommendations=recommendations_result,
            explanation=explanation_result,
            unparsed_lines=unparsed_lines,
        )

    except (UnsupportedStatementError, CCTrackError, HTTPException):
        raise
    except Exception as e:
        logger.error("Failed to parse statement: %s", e, exc_info=True)
        raise CCTrackError(
            error_code="STATEMENT_PARSING_FAILED",
            message=f"Failed to parse credit card statement: {str(e)}",
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        )


@router.post(
    "/validate",
    response_model=StatementValidateResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate and reconcile extracted statement transactions",
    description="Runs mathematical balance reconciliation and sanity integrity checks on statement line items.",
)
async def validate_statement_endpoint(
    payload: StatementValidateRequest,
) -> StatementValidateResponse:
    reconciliation_summary = reconcile_statement(
        header=payload.header,
        transactions=payload.transactions,
        unparsed_lines=payload.unparsed_lines,
    )
    validation_result = validate_transactions(
        header=payload.header,
        transactions=payload.transactions,
    )
    return StatementValidateResponse(
        reconciliation=reconciliation_summary,
        validation=validation_result,
    )


@router.post(
    "/save",
    response_model=StatementSaveResponse,
    status_code=status.HTTP_200_OK,
    summary="Persist parsed statement session to storage vault",
    description="Saves statement header, transactions, findings, and recommendations for long-term tracking and historical baseline profiling.",
)
async def save_statement_endpoint(
    payload: StatementSaveRequest,
) -> StatementSaveResponse:
    storage = get_default_storage_service()
    return storage.save_statement_session(payload)


@router.get(
    "/history",
    response_model=StatementHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve statement history summaries",
    description="Lists past saved statement periods, spend totals, reconciliation statuses, and card identifiers.",
)
async def get_statement_history_endpoint(
    user_id: str | None = None,
    limit: int = 50,
) -> StatementHistoryResponse:
    storage = get_default_storage_service()
    return storage.get_statement_history(user_id=user_id, limit=limit)


@router.get(
    "/{statement_id}",
    response_model=ParseStatementResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve complete parsed statement details by ID",
    description="Loads the complete parsed statement dataset including full transactions, analytics, and findings.",
)
async def get_statement_by_id_endpoint(
    statement_id: str,
    user_id: str | None = None,
) -> ParseStatementResponse:
    storage = get_default_storage_service()
    statement = storage.get_statement_by_id(statement_id=statement_id, user_id=user_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Statement with ID '{statement_id}' not found.",
        )
    return statement

