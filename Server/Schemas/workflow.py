from pydantic import BaseModel
from typing import List, Dict, Any


class WorkflowChange(BaseModel):
    type: str
    target: str
    description: str


class Workflow(BaseModel):
    name: str
    description: str
    proposed_changes: List[WorkflowChange]
    pros: List[str]
    cons: List[str]
    complexity_score: int  # 1-10
    risk_score: int  # 1-10


class WorkflowsResponse(BaseModel):
    workflows: List[Workflow]
    generated_at: str


class WorkflowComparison(BaseModel):
    workflows: List[Workflow]
    recommendation: str
    comparison_matrix: Dict[str, Any]
