from sqlalchemy.orm import Session
from services.graph_service import GraphService
from reasoning.rules import RuleEngine
from models.issue import Issue
from typing import List
from core.logging import get_logger

logger = get_logger(__name__)


class IssueDetector:
    
    @staticmethod
    def detect_issues(db: Session) -> List[Issue]:
        """Detect architectural issues"""
        G = GraphService.get_graph_from_db(db)
        issues = RuleEngine.run_all_rules(G)
        logger.info(f"Detected {len(issues)} issues")
        return issues

