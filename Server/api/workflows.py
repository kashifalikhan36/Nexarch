from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from pydantic import BaseModel
from typing import List, Dict, Any
from models.workflow import Workflow
from services.workflow_generator import WorkflowGenerator
from services.issue_detector import IssueDetector
from datetime import datetime
from core.logging import get_logger

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
async def get_generated_workflows(db: Session = Depends(get_db)):
    """Get generated workflows"""
    issues = IssueDetector.detect_issues(db)
    generator = WorkflowGenerator()
    workflows = generator.generate_workflows(db, issues)
    
    return WorkflowsResponse(
        workflows=workflows,
        generated_at=datetime.utcnow().isoformat()
    )


@router.get("/comparison", response_model=WorkflowComparison)
async def get_workflow_comparison(db: Session = Depends(get_db)):
    """Compare workflows"""
    issues = IssueDetector.detect_issues(db)
    generator = WorkflowGenerator()
    workflows = generator.generate_workflows(db, issues)
    
    # Build comparison matrix
    comparison = {
        "complexity": {w.name: w.complexity_score for w in workflows},
        "risk": {w.name: w.risk_score for w in workflows},
        "changes": {w.name: len(w.proposed_changes) for w in workflows}
    }
    
    # Simple recommendation
    recommendation = min(workflows, key=lambda w: w.complexity_score + w.risk_score).name
    
    return WorkflowComparison(
        workflows=workflows,
        recommendation=f"{recommendation} is recommended for balanced risk/complexity",
        comparison_matrix=comparison
    )
