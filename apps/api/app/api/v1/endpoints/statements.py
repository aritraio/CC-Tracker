import io
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.exceptions import CCTrackError, UnsupportedStatementError
from app.parsers.detector import get_parser_for_statement
from app.schemas.statement import ParsedStatement

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statements", tags=["Statements"])


@router.post(
    "/parse",
    response_model=ParsedStatement,
    summary="Parse an uploaded credit card PDF statement",
    description="Statelessly parses an in-memory PDF statement, detects the bank, and returns structured line items and headers.",
)
async def parse_statement(
    file: UploadFile = File(..., description="Decrypted credit card PDF statement file"),
) -> ParsedStatement:
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
        pdf_stream = io.BytesIO(content)
        parser = get_parser_for_statement(pdf_stream)
        parsed_statement = parser.parse(pdf_stream)
        return parsed_statement

    except (UnsupportedStatementError, CCTrackError, HTTPException):
        raise
    except Exception as e:
        logger.error("Failed to parse statement: %s", e, exc_info=True)
        raise CCTrackError(
            error_code="STATEMENT_PARSING_FAILED",
            message=f"Failed to parse credit card statement: {str(e)}",
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        )
