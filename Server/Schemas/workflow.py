from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class WorkflowChange(BaseModel):
    type: str
    target: str
    description: str
    impact: str = ""


class Workflow(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    proposed_changes: List[WorkflowChange] = []
    steps: List[Dict[str, Any]] = []
    pros: List[str] = []
    cons: List[str] = []
    complexity_score: int = 5  # 1-10
    complexity: str = "medium"  # low, medium, high
    risk_score: int = 5  # 1-10
    expected_impact: Dict[str, Any] = {}
    estimated_impact: float = 0.5  # 0-1
    tenant_id: Optional[str] = None


class WorkflowsResponse(BaseModel):
    workflows: List[Workflow]
    generated_at: str


class WorkflowComparison(BaseModel):
    workflows: List[Workflow]
    recommendation: str
    comparison_matrix: Dict[str, Any]
