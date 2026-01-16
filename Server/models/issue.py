from pydantic import BaseModel
from typing import List


class Issue(BaseModel):
    id: str
    severity: str  # low, medium, high, critical
    type: str
    description: str
    affected_nodes: List[str]
    metric_value: float
    evidence: dict
