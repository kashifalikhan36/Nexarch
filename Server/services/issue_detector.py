import networkx as nx
from sqlalchemy.orm import Session
from schemas.architecture import Issue
from services.graph_service import GraphService
from core.config import get_settings
from typing import List
from core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class IssueDetector:
    
    @staticmethod
    def detect_issues(db: Session) -> List[Issue]:
        """Detect architectural issues"""
        G = GraphService.get_graph_from_db(db)
        issues = []
        
        # High latency edges
        issues.extend(IssueDetector._detect_high_latency_edges(G))
        
        # Deep sync chains
        issues.extend(IssueDetector._detect_deep_chains(G))
        
        # High error rate nodes
        issues.extend(IssueDetector._detect_high_error_nodes(G))
        
        # Fan-out overload
        issues.extend(IssueDetector._detect_fan_out(G))
        
        logger.info(f"Detected {len(issues)} issues")
        return issues
    
    @staticmethod
    def _detect_high_latency_edges(G: nx.DiGraph) -> List[Issue]:
        """High latency edges"""
        issues = []
        threshold = settings.HIGH_LATENCY_THRESHOLD_MS
        
        for source, target, data in G.edges(data=True):
            if data.get("avg_latency_ms", 0) > threshold:
                issues.append(Issue(
                    severity="high",
                    type="high_latency_edge",
                    description=f"Edge {source} → {target} has high latency",
                    affected_nodes=[source, target],
                    metric_value=data["avg_latency_ms"]
                ))
        
        return issues
    
    @staticmethod
    def _detect_deep_chains(G: nx.DiGraph) -> List[Issue]:
        """Deep synchronous chains"""
        issues = []
        max_depth = settings.MAX_SYNC_CHAIN_DEPTH
        
        try:
            for node in G.nodes():
                paths = nx.single_source_shortest_path_length(G, node)
                max_path = max(paths.values()) if paths else 0
                
                if max_path > max_depth:
                    issues.append(Issue(
                        severity="medium",
                        type="deep_sync_chain",
                        description=f"Service {node} has deep sync chain (depth={max_path})",
                        affected_nodes=[node],
                        metric_value=float(max_path)
                    ))
        except Exception as e:
            logger.error(f"Chain detection error: {e}")
        
        return issues
    
    @staticmethod
    def _detect_high_error_nodes(G: nx.DiGraph) -> List[Issue]:
        """High error rate nodes"""
        issues = []
        threshold = settings.HIGH_ERROR_RATE_THRESHOLD
        
        for node, data in G.nodes(data=True):
            metrics = data.get("metrics", {})
            error_rate = metrics.get("error_rate", 0)
            
            if error_rate > threshold:
                issues.append(Issue(
                    severity="critical",
                    type="high_error_rate",
                    description=f"Service {node} has high error rate ({error_rate*100:.1f}%)",
                    affected_nodes=[node],
                    metric_value=error_rate
                ))
        
        return issues
    
    @staticmethod
    def _detect_fan_out(G: nx.DiGraph) -> List[Issue]:
        """Fan-out overload"""
        issues = []
        max_fan_out = settings.MAX_FAN_OUT
        
        for node in G.nodes():
            out_degree = G.out_degree(node)
            
            if out_degree > max_fan_out:
                issues.append(Issue(
                    severity="medium",
                    type="fan_out_overload",
                    description=f"Service {node} calls too many services ({out_degree})",
                    affected_nodes=[node],
                    metric_value=float(out_degree)
                ))
        
        return issues
