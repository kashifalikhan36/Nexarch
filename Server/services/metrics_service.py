from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import Span
from typing import Dict, Any
from core.logging import get_logger

logger = get_logger(__name__)


class MetricsService:
    
    @staticmethod
    def compute_node_metrics(db: Session, service_name: str, tenant_id: str) -> Dict[str, Any]:
        """Compute metrics for node with tenant isolation"""
        spans = db.query(Span).filter(
            Span.tenant_id == tenant_id,
            Span.service_name == service_name
        ).all()
        
        if not spans:
            return {
                "avg_latency_ms": 0.0,
                "error_rate": 0.0,
                "call_count": 0
            }
        
        total_calls = len(spans)
        error_count = sum(1 for s in spans if s.error or (s.status_code and s.status_code >= 500))
        avg_latency = sum(s.latency_ms for s in spans) / total_calls
        
        return {
            "avg_latency_ms": round(avg_latency, 2),
            "error_rate": round(error_count / total_calls, 4),
            "call_count": total_calls
        }
    
    @staticmethod
    def compute_edge_metrics(db: Session, source: str, target: str, tenant_id: str) -> Dict[str, Any]:
        """Compute metrics for edge with tenant isolation"""
        spans = db.query(Span).filter(
            Span.tenant_id == tenant_id,
            Span.service_name == source,
            Span.downstream == target
        ).all()
        
        if not spans:
            return {
                "call_count": 0,
                "avg_latency_ms": 0.0,
                "error_rate": 0.0
            }
        
        total_calls = len(spans)
        error_count = sum(1 for s in spans if s.error or (s.status_code and s.status_code >= 500))
        avg_latency = sum(s.latency_ms for s in spans) / total_calls
        
        return {
            "call_count": total_calls,
            "avg_latency_ms": round(avg_latency, 2),
            "error_rate": round(error_count / total_calls, 4)
        }
    
    @staticmethod
    def compute_global_metrics(db: Session, tenant_id: str) -> Dict[str, Any]:
        """Compute global summary with tenant isolation"""
        total_spans = db.query(func.count(Span.id)).filter(
            Span.tenant_id == tenant_id
        ).scalar()
        
        if not total_spans:
            return {
                "total_spans": 0,
                "unique_services": 0,
                "avg_latency_ms": 0.0,
                "error_rate": 0.0
            }
        
        all_spans = db.query(Span).filter(Span.tenant_id == tenant_id).all()
        unique_services = len(set(s.service_name for s in all_spans))
        error_count = sum(1 for s in all_spans if s.error or (s.status_code and s.status_code >= 500))
        avg_latency = sum(s.latency_ms for s in all_spans) / total_spans
        
        return {
            "total_spans": total_spans,
            "unique_services": unique_services,
            "avg_latency_ms": round(avg_latency, 2),
            "error_rate": round(error_count / total_spans, 4)
        }
