"""Dashboard – Trends sub-router: /trends, /traces/timeline"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.base import get_db
from db.models import Span
from dependencies.auth import get_tenant_id_from_jwt
from datetime import datetime, timedelta
from core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _compute_hourly_trends(spans, hours: int):
    """Shared bucketing logic used by both /trends and /traces/timeline."""
    if not spans:
        return {"latency": [], "error_rate": [], "volume": []}

    hourly: dict = {}
    for span in spans:
        bucket = span.start_time.replace(minute=0, second=0, microsecond=0)
        hourly.setdefault(bucket, []).append(span)

    latency_trends, error_trends, volume_trends = [], [], []
    for bucket_time in sorted(hourly):
        bucket_spans = hourly[bucket_time]
        ts = bucket_time.isoformat()

        avg_lat = sum(s.latency_ms for s in bucket_spans) / len(bucket_spans)
        latency_trends.append({"timestamp": ts, "value": round(avg_lat, 2)})

        errors = sum(1 for s in bucket_spans if s.error or (s.status_code and s.status_code >= 500))
        error_trends.append({"timestamp": ts, "value": round(errors / len(bucket_spans), 4)})

        volume_trends.append({"timestamp": ts, "value": len(bucket_spans)})

    return {
        "latency": latency_trends,
        "error_rate": error_trends,
        "volume": volume_trends,
        "period_hours": hours,
        "timeline": volume_trends,
    }


@router.get("/trends")
async def get_trends(
    tenant_id: str = Depends(get_tenant_id_from_jwt),
    db: Session = Depends(get_db),
    hours: int = Query(default=24, ge=1, le=168),
):
    """Time-series trends for latency, error rate, and volume."""
    end_time   = datetime.now()
    start_time = end_time - timedelta(hours=hours)

    spans = (
        db.query(Span)
        .filter(Span.tenant_id == tenant_id, Span.start_time >= start_time, Span.start_time <= end_time)
        .all()
    )
    return _compute_hourly_trends(spans, hours)


@router.get("/traces/timeline")
async def get_trace_timeline(
    tenant_id: str = Depends(get_tenant_id_from_jwt),
    db: Session = Depends(get_db),
    hours: int = Query(default=24, ge=1, le=168),
):
    """Trace volume timeline (alias for /trends)."""
    return await get_trends(tenant_id, db, hours)
