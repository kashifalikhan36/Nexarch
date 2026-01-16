from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.base import get_db
from models.span import Span as SpanIngest
from pydantic import BaseModel
from services.ingest_service import IngestService
from core.logging import get_logger
from core.auth import get_tenant_id
from core.cache import get_cache_manager
from typing import List, Dict, Any
from datetime import datetime

class IngestResponse(BaseModel):
    status: str = "accepted"
    span_id: str

class BatchIngestResponse(BaseModel):
    status: str = "accepted"
    count: int
    failed: int = 0

class ArchitectureDiscoveryData(BaseModel):
    service_name: str
    service_type: str
    endpoints: List[Dict[str, Any]]
    databases: List[Dict[str, Any]]
    external_services: List[str] = []
    dependencies: Dict[str, List[str]] = {}
    architecture_patterns: Dict[str, Any] = {}
    discovered_at: str

router = APIRouter(prefix="/api/v1", tags=["ingest"])
logger = get_logger(__name__)
cache_manager = get_cache_manager()


@router.post("/ingest", status_code=202, response_model=IngestResponse)
async def ingest_span(
    span: SpanIngest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Accept telemetry span with tenant isolation"""
    try:
        stored_span = IngestService.store_span(db, span, tenant_id)
        
        # Invalidate dashboard cache when new data arrives
        cache_manager.invalidate(tenant_id, "dashboard_overview")
        cache_manager.invalidate(tenant_id, "architecture_map")
        
        return IngestResponse(span_id=stored_span.span_id)
    except Exception as e:
        logger.error(f"Ingest failed for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest span")


@router.post("/ingest/spans", status_code=202, response_model=IngestResponse)
async def ingest_span_alias(
    span: SpanIngest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Alias endpoint for /ingest/spans (SDK compatibility)"""
    return await ingest_span(span, tenant_id, db)


@router.post("/ingest/batch", status_code=202, response_model=BatchIngestResponse)
async def ingest_batch(
    spans: List[SpanIngest],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Accept batch of telemetry spans"""
    failed = 0
    for span in spans:
        try:
            IngestService.store_span(db, span, tenant_id)
        except Exception as e:
            logger.error(f"Failed to ingest span {span.span_id}: {e}")
            failed += 1
    
    return BatchIngestResponse(
        count=len(spans) - failed,
        failed=failed
    )


@router.post("/ingest/architecture-discovery", status_code=202)
async def ingest_architecture_discovery(
    discovery: ArchitectureDiscoveryData,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Accept architecture discovery data from SDK
    This is auto-sent when SDK initializes with enable_auto_discovery=True
    """
    try:
        logger.info(f"Received architecture discovery for tenant {tenant_id}, service: {discovery.service_name}")
        logger.info(f"Discovered {len(discovery.endpoints)} endpoints, {len(discovery.databases)} databases")
        
        # Import here to avoid circular dependency
        from db.models import ArchitectureDiscovery
        import json
        
        # Check if discovery already exists for this service
        existing = db.query(ArchitectureDiscovery).filter(
            ArchitectureDiscovery.tenant_id == tenant_id,
            ArchitectureDiscovery.service_name == discovery.service_name
        ).first()
        
        if existing:
            # Update existing discovery
            existing.service_type = discovery.service_type
            existing.version = discovery.version
            existing.endpoints = json.dumps([e.model_dump() for e in discovery.endpoints])
            existing.databases = json.dumps([d.model_dump() for d in discovery.databases])
            existing.external_services = json.dumps([s.model_dump() for s in discovery.external_services])
            existing.middleware = json.dumps(discovery.middleware)
            existing.architecture_patterns = json.dumps(discovery.architecture_patterns)
            existing.updated_at = datetime.utcnow()
            logger.info(f"Updated existing discovery for service {discovery.service_name}")
        else:
            # Create new discovery entry
            new_discovery = ArchitectureDiscovery(
                tenant_id=tenant_id,
                service_name=discovery.service_name,
                service_type=discovery.service_type,
                version=discovery.version,
                endpoints=json.dumps([e.model_dump() for e in discovery.endpoints]),
                databases=json.dumps([d.model_dump() for d in discovery.databases]),
                external_services=json.dumps([s.model_dump() for s in discovery.external_services]),
                middleware=json.dumps(discovery.middleware),
                architecture_patterns=json.dumps(discovery.architecture_patterns)
            )
            db.add(new_discovery)
            logger.info(f"Created new discovery for service {discovery.service_name}")
        
        db.commit()
        
        return {
            "status": "accepted",
            "service": discovery.service_name,
            "endpoints_discovered": len(discovery.endpoints),
            "databases_discovered": len(discovery.databases),
            "external_services_discovered": len(discovery.external_services),
            "message": "Architecture discovery data saved successfully"
        }
    except Exception as e:
        logger.error(f"Architecture discovery failed for tenant {tenant_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/stats")
async def get_ingest_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get ingestion statistics for tenant"""
    from db.models import Span
    from sqlalchemy import func
    
    stats = {
        "total_spans": db.query(func.count(Span.id)).filter(Span.tenant_id == tenant_id).scalar(),
        "unique_services": db.query(func.count(func.distinct(Span.service_name))).filter(Span.tenant_id == tenant_id).scalar(),
        "unique_traces": db.query(func.count(func.distinct(Span.trace_id))).filter(Span.tenant_id == tenant_id).scalar()
    }
    
    return stats
