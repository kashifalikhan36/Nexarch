from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from pydantic import BaseModel
from typing import List, Dict, Any
from models.workflow import Workflow
from models.workflow_graph import WorkflowArchitectureGraphResponse
from services.workflow_generator import WorkflowGenerator
from services.workflow_graph_service import WorkflowGraphService
from services.issue_detector import IssueDetector
from datetime import datetime
from core.logging import get_logger
from core.auth import get_tenant_id
from core.cache import cache_manager

class WorkflowsResponse(BaseModel):
    workflows: List[Workflow]
    generated_at: str

class WorkflowComparison(BaseModel):
    workflows: List[Workflow]
    recommendation: str
    comparison_matrix: Dict[str, Any]

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])
logger = get_logger(__name__)


@router.get("/generated", response_model=WorkflowsResponse)
async def get_generated_workflows(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get generated workflows with tenant isolation and caching"""
    # Check cache
    cached = cache_manager.get(tenant_id, "workflows")
    if cached:
        logger.info(f"Returning cached workflows for tenant {tenant_id}")
        return WorkflowsResponse(**cached)
    
    # Generate workflows
    issues = IssueDetector.detect_issues(db, tenant_id)
    generator = WorkflowGenerator()
    workflows = generator.generate_workflows(db, issues, tenant_id)
    
    response_data = {
        "workflows": workflows,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # Cache result
    cache_manager.set(tenant_id, "workflows", response_data)
    
    return WorkflowsResponse(**response_data)


@router.get("/comparison", response_model=WorkflowComparison)
async def get_workflow_comparison(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Compare workflows with tenant isolation"""
    issues = IssueDetector.detect_issues(db, tenant_id)
    generator = WorkflowGenerator()
    workflows = generator.generate_workflows(db, issues, tenant_id)
    
    # Build comparison matrix
    comparison = {
        "complexity": {w.name: w.complexity_score for w in workflows},
        "risk": {w.name: w.risk_score for w in workflows},
        "changes": {w.name: len(w.proposed_changes) for w in workflows}
    }
    
    # Simple recommendation
    if workflows:
        recommendation = min(workflows, key=lambda w: w.complexity_score + w.risk_score).name
        rec_message = f"{recommendation} is recommended for balanced risk/complexity"
    else:
        rec_message = "No workflows available"
    
    return WorkflowComparison(
        workflows=workflows,
        recommendation=rec_message,
        comparison_matrix=comparison
    )


@router.get("/architecture/graph", response_model=WorkflowArchitectureGraphResponse)
async def get_workflow_architecture_graph(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get visual workflow graph representing the current architecture
    and generated workflow variants.
    
    Returns pure structured JSON consumable by React Flow or other
    graph visualization libraries.
    
    The response includes:
    - current_architecture: The discovered runtime architecture graph
    - generated_workflows: 2-3 workflow variants based on observed patterns
      (most common path, optimized path, high-reliability path)
    
    This endpoint is READ-ONLY:
    - Does NOT trigger any new instrumentation
    - Does NOT affect performance
    - Does NOT modify any existing data
    """
    # Check cache
    cached = cache_manager.get(tenant_id, "workflow_graph")
    if cached:
        logger.info(f"Returning cached workflow graph for tenant {tenant_id}")
        return WorkflowArchitectureGraphResponse(**cached)
    
    # Build current architecture graph
    current = WorkflowGraphService.build_current_architecture_graph(db, tenant_id)
    
    # Generate workflow variants
    variants = await WorkflowGraphService.generate_workflow_variants(db, tenant_id)
    
    response = WorkflowArchitectureGraphResponse(
        current_architecture=current,
        generated_workflows=variants
    )
    
    # Cache result
    cache_manager.set(tenant_id, "workflow_graph", response.model_dump())
    
    logger.info(f"Generated workflow architecture graph for tenant {tenant_id}: {len(current.nodes)} nodes, {len(variants)} variants")
    return response

