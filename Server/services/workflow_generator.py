import json
from sqlalchemy.orm import Session
from schemas.workflow import Workflow, WorkflowChange
from schemas.architecture import Issue
from services.graph_service import GraphService
from utils.ai_client import AzureOpenAIChatClient
from core.config import get_settings
from core.logging import get_logger
from typing import List
from datetime import datetime

logger = get_logger(__name__)
settings = get_settings()


class WorkflowGenerator:
    
    def __init__(self):
        self.ai_client = AzureOpenAIChatClient(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
    
    def generate_workflows(self, db: Session, issues: List[Issue]) -> List[Workflow]:
        """Generate 3 workflow alternatives"""
        
        # Get current architecture
        nodes, edges = GraphService.build_graph(db)
        
        arch_context = {
            "nodes": [{"id": n.id, "type": n.type} for n in nodes],
            "edges": [{"source": e.source, "target": e.target, "latency": e.avg_latency_ms} for e in edges],
            "issues": [{"type": i.type, "severity": i.severity, "nodes": i.affected_nodes} for i in issues]
        }
        
        # Generate workflows
        workflows = []
        workflows.append(self._generate_minimal_workflow(arch_context, issues))
        workflows.append(self._generate_performance_workflow(arch_context, issues))
        workflows.append(self._generate_cost_workflow(arch_context, issues))
        
        logger.info(f"Generated {len(workflows)} workflows")
        return workflows
    
    def _generate_minimal_workflow(self, arch_context: dict, issues: List[Issue]) -> Workflow:
        """Minimal change workflow"""
        changes = []
        
        for issue in issues[:3]:  # Top 3
            if issue.type == "high_latency_edge":
                changes.append(WorkflowChange(
                    type="optimization",
                    target=issue.affected_nodes[0],
                    description=f"Add caching layer between {issue.affected_nodes[0]} and {issue.affected_nodes[1]}"
                ))
            elif issue.type == "high_error_rate":
                changes.append(WorkflowChange(
                    type="resilience",
                    target=issue.affected_nodes[0],
                    description=f"Add circuit breaker to {issue.affected_nodes[0]}"
                ))
        
        return Workflow(
            name="Minimal Change",
            description="Quick fixes with minimal infrastructure changes",
            proposed_changes=changes if changes else [
                WorkflowChange(type="monitoring", target="all", description="Enhance observability")
            ],
            pros=["Low risk", "Fast implementation", "Minimal downtime"],
            cons=["Limited impact", "May not solve root causes"],
            complexity_score=2,
            risk_score=1
        )
    
    def _generate_performance_workflow(self, arch_context: dict, issues: List[Issue]) -> Workflow:
        """Performance optimized workflow"""
        changes = []
        
        # High latency issues
        high_latency = [i for i in issues if i.type == "high_latency_edge"]
        for issue in high_latency[:2]:
            changes.append(WorkflowChange(
                type="caching",
                target=issue.affected_nodes[0],
                description=f"Implement Redis cache for {issue.affected_nodes[0]}"
            ))
        
        # Deep chains
        deep_chains = [i for i in issues if i.type == "deep_sync_chain"]
        for issue in deep_chains[:1]:
            changes.append(WorkflowChange(
                type="async_pattern",
                target=issue.affected_nodes[0],
                description=f"Convert {issue.affected_nodes[0]} to async pattern with message queue"
            ))
        
        if not changes:
            changes.append(WorkflowChange(
                type="optimization",
                target="architecture",
                description="Add distributed caching layer"
            ))
        
        return Workflow(
            name="Performance Optimized",
            description="Maximize throughput and reduce latency",
            proposed_changes=changes,
            pros=["Significant latency reduction", "Better scalability", "Improved user experience"],
            cons=["Higher infrastructure cost", "More complex", "Longer implementation"],
            complexity_score=6,
            risk_score=4
        )
    
    def _generate_cost_workflow(self, arch_context: dict, issues: List[Issue]) -> Workflow:
        """Cost optimized workflow"""
        changes = []
        
        # Fan-out issues
        fan_out = [i for i in issues if i.type == "fan_out_overload"]
        for issue in fan_out[:1]:
            changes.append(WorkflowChange(
                type="consolidation",
                target=issue.affected_nodes[0],
                description=f"Consolidate downstream calls from {issue.affected_nodes[0]}"
            ))
        
        # Error rate
        errors = [i for i in issues if i.type == "high_error_rate"]
        for issue in errors[:1]:
            changes.append(WorkflowChange(
                type="optimization",
                target=issue.affected_nodes[0],
                description=f"Optimize retry logic in {issue.affected_nodes[0]} to reduce wasted calls"
            ))
        
        if not changes:
            changes.append(WorkflowChange(
                type="right_sizing",
                target="infrastructure",
                description="Right-size service instances based on actual load"
            ))
        
        return Workflow(
            name="Cost Optimized",
            description="Reduce operational costs while maintaining reliability",
            proposed_changes=changes,
            pros=["Lower operational cost", "Better resource utilization", "Reduced waste"],
            cons=["May impact peak performance", "Requires careful monitoring"],
            complexity_score=4,
            risk_score=3
        )
