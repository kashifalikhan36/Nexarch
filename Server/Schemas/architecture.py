from pydantic import BaseModel
from typing import List, Dict, Any


class NodeMetrics(BaseModel):
    avg_latency_ms: float
    error_rate: float
    call_count: int


class Node(BaseModel):
    id: str
    type: str  # service, database, external
    metrics: NodeMetrics


class Edge(BaseModel):
    source: str
    target: str
    call_count: int
    avg_latency_ms: float
    error_rate: float


class ArchitectureResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    metrics_summary: Dict[str, Any]


class Issue(BaseModel):
    severity: str  # critical, high, medium, low
    type: str
    description: str
    affected_nodes: List[str]
    metric_value: float


class IssuesResponse(BaseModel):
    issues: List[Issue]
    total_count: int
