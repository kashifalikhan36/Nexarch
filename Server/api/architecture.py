from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from schemas.architecture import ArchitectureResponse, IssuesResponse
from services.graph_service import GraphService
from services.metrics_service import MetricsService
from services.issue_detector import IssueDetector
from core.logging import get_logger

router = APIRouter(prefix="/api/v1/architecture", tags=["architecture"])
logger = get_logger(__name__)


@router.get("/current", response_model=ArchitectureResponse)
async def get_current_architecture(db: Session = Depends(get_db)):
    """Get current architecture graph"""
    nodes, edges = GraphService.build_graph(db)
    metrics_summary = MetricsService.compute_global_metrics(db)
    
    return ArchitectureResponse(
        nodes=nodes,
        edges=edges,
        metrics_summary=metrics_summary
    )


@router.get("/issues", response_model=IssuesResponse)
async def get_issues(db: Session = Depends(get_db)):
    """Get detected issues"""
    issues = IssueDetector.detect_issues(db)
    
    return IssuesResponse(
        issues=issues,
        total_count=len(issues)
    )
