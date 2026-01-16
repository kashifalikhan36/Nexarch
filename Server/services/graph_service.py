import networkx as nx
from sqlalchemy.orm import Session
from db.models import Span
from schemas.architecture import Node, Edge, NodeMetrics
from services.metrics_service import MetricsService
from typing import List, Tuple
from core.logging import get_logger

logger = get_logger(__name__)


class GraphService:
    
    @staticmethod
    def build_graph(db: Session) -> Tuple[List[Node], List[Edge]]:
        """Build dependency graph"""
        spans = db.query(Span).all()
        
        if not spans:
            return [], []
        
        # Build NetworkX graph
        G = nx.DiGraph()
        
        # Track all nodes
        services = set(s.service_name for s in spans)
        downstreams = set(s.downstream for s in spans if s.downstream)
        all_nodes = services.union(downstreams)
        
        # Add nodes
        for node_id in all_nodes:
            node_type = GraphService._classify_node(node_id)
            G.add_node(node_id, type=node_type)
        
        # Add edges
        edges_data = {}
        for span in spans:
            if span.downstream:
                edge_key = (span.service_name, span.downstream)
                if edge_key not in edges_data:
                    edges_data[edge_key] = []
                edges_data[edge_key].append(span)
        
        for (source, target), edge_spans in edges_data.items():
            G.add_edge(source, target, spans=edge_spans)
        
        # Build response
        nodes = []
        for node_id in G.nodes():
            metrics = MetricsService.compute_node_metrics(db, node_id)
            nodes.append(Node(
                id=node_id,
                type=G.nodes[node_id]["type"],
                metrics=NodeMetrics(**metrics)
            ))
        
        edges = []
        for source, target in G.edges():
            metrics = MetricsService.compute_edge_metrics(db, source, target)
            edges.append(Edge(
                source=source,
                target=target,
                **metrics
            ))
        
        logger.info(f"Built graph: {len(nodes)} nodes, {len(edges)} edges")
        return nodes, edges
    
    @staticmethod
    def _classify_node(node_id: str) -> str:
        """Classify node type"""
        node_lower = node_id.lower()
        
        if any(db in node_lower for db in ["postgres", "mysql", "mongo", "redis", "dynamodb", "cosmosdb"]):
            return "database"
        
        if any(ext in node_lower for ext in ["http://", "https://", "api.", "external"]):
            return "external"
        
        return "service"
    
    @staticmethod
    def get_graph_from_db(db: Session) -> nx.DiGraph:
        """Get NetworkX graph"""
        nodes, edges = GraphService.build_graph(db)
        
        G = nx.DiGraph()
        for node in nodes:
            G.add_node(node.id, type=node.type, metrics=node.metrics.model_dump())
        
        for edge in edges:
            G.add_edge(edge.source, edge.target, 
                      call_count=edge.call_count,
                      avg_latency_ms=edge.avg_latency_ms,
                      error_rate=edge.error_rate)
        
        return G
