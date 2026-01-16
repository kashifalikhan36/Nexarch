from typing import Dict, Any, List
from sqlalchemy.orm import Session
from db.base import SessionLocal
from services.graph_service import GraphService
from services.metrics_service import MetricsService
from services.issue_detector import IssueDetector
from services.workflow_generator import WorkflowGenerator
from reasoning.graph_analysis import GraphAnalysis
from core.logging import get_logger

logger = get_logger(__name__)


class MCPTools:
    """MCP tool implementations - thin wrappers over services"""
    
    def __init__(self):
        self.workflow_generator = WorkflowGenerator()
    
    def _get_db(self) -> Session:
        """Get DB session"""
        return SessionLocal()
    
    def get_current_architecture(self) -> Dict[str, Any]:
        """Get architecture"""
        db = self._get_db()
        try:
            nodes, edges = GraphService.build_graph(db)
            metrics = MetricsService.compute_global_metrics(db)
            
            return {
                "nodes": [n.model_dump() for n in nodes],
                "edges": [e.model_dump() for e in edges],
                "metrics_summary": metrics
            }
        finally:
            db.close()
    
    def get_detected_issues(self) -> Dict[str, Any]:
        """Get issues"""
        db = self._get_db()
        try:
            issues = IssueDetector.detect_issues(db)
            
            # Categorize
            by_severity = {}
            for issue in issues:
                if issue.severity not in by_severity:
                    by_severity[issue.severity] = []
                by_severity[issue.severity].append(issue.model_dump())
            
            return {
                "issues": [i.model_dump() for i in issues],
                "total_count": len(issues),
                "by_severity": by_severity
            }
        finally:
            db.close()
    
    def generate_workflows(self) -> Dict[str, Any]:
        """Generate workflows"""
        db = self._get_db()
        try:
            issues = IssueDetector.detect_issues(db)
            workflows = self.workflow_generator.generate_workflows(db, issues)
            
            return {
                "workflows": [w.model_dump() for w in workflows],
                "count": len(workflows)
            }
        finally:
            db.close()
    
    def compare_workflows(self) -> Dict[str, Any]:
        """Compare workflows"""
        db = self._get_db()
        try:
            issues = IssueDetector.detect_issues(db)
            workflows = self.workflow_generator.generate_workflows(db, issues)
            
            # Comparison matrix
            comparison = {
                "complexity": {w.name: w.complexity_score for w in workflows},
                "risk": {w.name: w.risk_score for w in workflows},
                "changes": {w.name: len(w.proposed_changes) for w in workflows}
            }
            
            # Recommendation
            best = min(workflows, key=lambda w: w.complexity_score + w.risk_score)
            
            return {
                "workflows": [w.model_dump() for w in workflows],
                "comparison_matrix": comparison,
                "recommendation": {
                    "workflow": best.name,
                    "reason": f"Best balance of complexity ({best.complexity_score}) and risk ({best.risk_score})"
                }
            }
        finally:
            db.close()
    
    def explain_decision(self, workflow_id: str) -> Dict[str, Any]:
        """Explain workflow decision"""
        db = self._get_db()
        try:
            issues = IssueDetector.detect_issues(db)
            workflows = self.workflow_generator.generate_workflows(db, issues)
            
            # Find workflow
            workflow = next((w for w in workflows if w.id == workflow_id), None)
            
            if not workflow:
                return {"error": "Workflow not found"}
            
            # Build explanation
            return {
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "reasoning": {
                    "issues_addressed": len([i for i in issues if any(n in workflow.description for n in i.affected_nodes)]),
                    "total_issues": len(issues),
                    "changes_proposed": len(workflow.proposed_changes),
                    "complexity_justification": self._explain_complexity(workflow),
                    "risk_justification": self._explain_risk(workflow)
                },
                "decision_factors": {
                    "pros": workflow.pros,
                    "cons": workflow.cons,
                    "expected_impact": workflow.expected_impact
                }
            }
        finally:
            db.close()
    
    def get_graph_analysis(self) -> Dict[str, Any]:
        """Advanced graph analysis"""
        db = self._get_db()
        try:
            G = GraphService.get_graph_from_db(db)
            analysis = GraphAnalysis.analyze_architecture(G)
            
            return {
                "graph_metrics": analysis,
                "insights": self._generate_insights(analysis)
            }
        finally:
            db.close()
    
    def _explain_complexity(self, workflow) -> str:
        """Explain complexity score"""
        score = workflow.complexity_score
        if score <= 3:
            return "Simple changes with minimal new components"
        elif score <= 6:
            return "Moderate changes requiring new infrastructure"
        else:
            return "Complex changes requiring significant architectural shifts"
    
    def _explain_risk(self, workflow) -> str:
        """Explain risk score"""
        score = workflow.risk_score
        if score <= 3:
            return "Low risk with easy rollback"
        elif score <= 6:
            return "Moderate risk requiring careful testing"
        else:
            return "High risk with potential for service disruption"
    
    def _generate_insights(self, analysis: Dict) -> List[str]:
        """Generate insights"""
        insights = []
        
        if not analysis.get("is_dag"):
            insights.append("⚠️ Circular dependencies detected")
        
        if len(analysis.get("bottlenecks", [])) > 0:
            insights.append(f"⚠️ {len(analysis['bottlenecks'])} bottleneck services found")
        
        if len(analysis.get("critical_paths", [])) > 0:
            insights.append(f"📊 {len(analysis['critical_paths'])} critical execution paths")
        
        avg_degree = analysis.get("avg_degree", 0)
        if avg_degree > 5:
            insights.append("⚠️ High coupling detected")
        
        return insights
