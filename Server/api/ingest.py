from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.base import get_db
from models.span import Span as SpanIngest
from pydantic import BaseModel
from services.ingest_service import IngestService
from core.logging import get_logger

class IngestResponse(BaseModel):
    status: str = "accepted"
    span_id: str

router = APIRouter(prefix="/api/v1", tags=["ingest"])
logger = get_logger(__name__)


@router.post("/ingest", status_code=202, response_model=IngestResponse)
async def ingest_span(span: SpanIngest, db: Session = Depends(get_db)):
    """Accept telemetry span"""
    try:
        stored_span = IngestService.store_span(db, span)
        return IngestResponse(span_id=stored_span.span_id)
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest span")
