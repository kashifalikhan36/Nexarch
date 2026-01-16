from sqlalchemy.orm import Session
from models.workflow import Workflow
from models.issue import Issue
from services.graph_service import GraphService
from reasoning.langgraph_pipeline import WorkflowReasoningPipeline
from core.logging import get_logger
from typing import List

logger = get_logger(__name__)


class WorkflowGenerator:
    
    def __init__(self):
        self.pipeline = WorkflowReasoningPipeline()
    
    def generate_workflows(self, db: Session, issues: List[Issue]) -> List[Workflow]:
        """Generate workflows using LangGraph"""
        G = GraphService.get_graph_from_db(db)
        workflows = self.pipeline.run(G)
        logger.info(f"Generated {len(workflows)} workflows via LangGraph")
        return workflows

