from fastapi import APIRouter, Depends
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
from core.auth import get_tenant_id
from core.cache import cache_manager

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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get current architecture graph with tenant isolation and caching"""
    # Check cache
    cached = cache_manager.get(tenant_id, "architecture")
    if cached:
        logger.info(f"Returning cached architecture for tenant {tenant_id}")
        return ArchitectureResponse(**cached)
    
    # Build graph
    nodes, edges = GraphService.build_graph(db, tenant_id)
    metrics_summary = MetricsService.compute_global_metrics(db, tenant_id)
    
    response_data = {
        "nodes": nodes,
        "edges": edges,
        "metrics_summary": metrics_summary
    }
    
    # Cache result
    cache_manager.set(tenant_id, "architecture", response_data)
    
    return ArchitectureResponse(**response_data)


@router.get("/issues", response_model=IssuesResponse)
async def get_detected_issues(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get detected issues with tenant isolation and caching"""
    # Check cache
    cached = cache_manager.get(tenant_id, "issues")
    if cached:
        logger.info(f"Returning cached issues for tenant {tenant_id}")
        return IssuesResponse(**cached)
    
    # Detect issues
    issues = IssueDetector.detect_issues(db, tenant_id)
    
    response_data = {
        "issues": issues,
        "total_count": len(issues)
    }
    
    # Cache result
    cache_manager.set(tenant_id, "issues", response_data)
    
    return IssuesResponse(**response_data)
async def get_issues(db: Session = Depends(get_db)):
    """Get detected issues"""
    issues = IssueDetector.detect_issues(db)
    
    return IssuesResponse(
        issues=issues,
        total_count=len(issues)
    )
