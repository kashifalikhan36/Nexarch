from sqlalchemy.orm import Session
from db.models import Span
from schemas.ingest import SpanIngest
from core.logging import get_logger

logger = get_logger(__name__)


class IngestService:
    
    @staticmethod
    def store_span(db: Session, span_data: SpanIngest) -> Span:
        """Store span in DB"""
        span = Span(
            trace_id=span_data.trace_id,
            span_id=span_data.span_id,
            parent_span_id=span_data.parent_span_id,
            service_name=span_data.service_name,
            operation=span_data.operation,
            kind=span_data.kind,
            start_time=span_data.start_time,
            end_time=span_data.end_time,
            latency_ms=span_data.latency_ms,
            status_code=span_data.status_code,
            error=span_data.error,
            downstream=span_data.downstream
        )
        
        db.add(span)
        db.commit()
        db.refresh(span)
        
        logger.info(f"Stored span: {span.span_id}")
        return span
