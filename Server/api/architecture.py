from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from db.base import get_db
from pydantic import BaseModel
from typing import List, Dict, Any
from models.node import Node
from models.edge import Edge
from models.issue import Issue
from services.graph_service import GraphService
from services.metrics_service import MetricsService
from services.issue_detector import IssueDetector
from core.logging import get_logger
from dependencies.auth import get_tenant_id_from_jwt_or_api_key as get_tenant_id
from core.cache import get_cache_manager

class ArchitectureResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    metrics_summary: Dict[str, Any]

class IssuesResponse(BaseModel):
    issues: List[Issue]
    total_count: int

router = APIRouter(prefix="/api/v1/architecture", tags=["architecture"])
logger = get_logger(__name__)


@router.get("/current", response_model=ArchitectureResponse)
async def get_current_architecture(
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get current architecture graph with tenant isolation and caching"""
    cache = get_cache_manager()
    # Check cache
    cached = cache.get(tenant_id, "architecture")
    if cached:
        logger.info(f"Returning cached architecture for tenant {tenant_id}")
        return ArchitectureResponse(**cached)

    # Build graph (single DB pass — nodes/metrics computed together)
    nodes, edges = GraphService.build_graph(db, tenant_id)
    metrics_summary = MetricsService.compute_global_metrics(db, tenant_id)

    response_data = {
        "nodes": nodes,
        "edges": edges,
        "metrics_summary": metrics_summary
    }

    # Cache in background so response is not held up
    background_tasks.add_task(cache.set, tenant_id, "architecture", response_data)

    return ArchitectureResponse(**response_data)


@router.get("/issues", response_model=IssuesResponse)
async def get_detected_issues(
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get detected issues with tenant isolation and caching"""
    cache = get_cache_manager()
    # Check cache
    cached = cache.get(tenant_id, "issues")
    if cached:
        logger.info(f"Returning cached issues for tenant {tenant_id}")
        return IssuesResponse(**cached)

    # Detect issues (single graph build inside)
    issues = await IssueDetector.detect_issues(db, tenant_id)

    response_data = {
        "issues": issues,
        "total_count": len(issues)
    }

    # Cache in background
    background_tasks.add_task(cache.set, tenant_id, "issues", response_data)

    return IssuesResponse(**response_data)
