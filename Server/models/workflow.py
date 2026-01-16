from pydantic import BaseModel
from typing import List


class WorkflowChange(BaseModel):
    type: str
    target: str
    description: str
    impact: str


class Workflow(BaseModel):
    id: str
    name: str
    description: str
    proposed_changes: List[WorkflowChange]
    pros: List[str]
    cons: List[str]
    complexity_score: int  # 1-10
    risk_score: int  # 1-10
    expected_impact: dict
