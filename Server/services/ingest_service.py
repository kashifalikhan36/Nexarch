from sqlalchemy.orm import Session
from db.models import Span as DBSpan
from models.span import Span as SpanIngest
from core.logging import get_logger
from typing import List, Tuple

logger = get_logger(__name__)


class IngestService:
    
    @staticmethod
    def store_span(db: Session, span_data: SpanIngest, tenant_id: str) -> DBSpan:
        """Store span in DB with tenant isolation"""
        span = DBSpan(
            tenant_id=tenant_id,
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
        
        logger.info(f"Stored span: {span.span_id} for tenant: {tenant_id}")
        return span

    @staticmethod
    def store_spans_batch(
        db: Session, spans_data: List[SpanIngest], tenant_id: str
    ) -> Tuple[int, int]:
        """Store a list of spans in a SINGLE DB transaction.

        Returns ``(success_count, fail_count)``.  A single commit at the end is
        dramatically faster than N individual commits for large batches.
        """
        prepared: List[DBSpan] = []
        fail = 0

        for span_data in spans_data:
            try:
                span = DBSpan(
                    tenant_id=tenant_id,
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
                    downstream=span_data.downstream,
                )
                db.add(span)
                prepared.append(span)
            except Exception as e:
                logger.error(f"Failed to prepare span {span_data.span_id}: {e}")
                fail += 1

        if prepared:
            try:
                db.commit()
                logger.info(
                    f"Batch stored {len(prepared)} spans for tenant {tenant_id}"
                )
            except Exception as e:
                db.rollback()
                logger.error(f"Batch commit failed for tenant {tenant_id}: {e}")
                return 0, len(spans_data)

        return len(prepared), fail
