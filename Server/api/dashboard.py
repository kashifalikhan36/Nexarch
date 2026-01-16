"""
Dashboard API - Comprehensive endpoints for frontend visualization
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.base import get_db
from db.models import Span
from core.auth import get_tenant_id
from core.cache import cache_manager
from core.ai_client import get_ai_client
from services.graph_service import GraphService
from services.metrics_service import MetricsService
from services.issue_detector import IssueDetector
from services.workflow_generator import WorkflowGenerator
from reasoning.graph_analysis import GraphAnalysis
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.logging import get_logger

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
logger = get_logger(__name__)


class DashboardOverview(BaseModel):
    """High-level dashboard overview"""
    total_services: int
    total_requests: int
    avg_latency_ms: float
    error_rate: float
    health_score: int
    critical_issues: int
    warnings: int
    architecture_complexity: float
    active_incidents: int
    uptime_percentage: float
    last_updated: str


class ServiceDetail(BaseModel):
    """Detailed service information"""
    name: str
    type: str
    request_count: int
    avg_latency_ms: float
    error_rate: float
    dependencies: List[str]
    dependents: List[str]
    health_status: str
    last_seen: str


class TrendData(BaseModel):
    """Time-series trend data"""
    timestamp: str
    value: float
    metric_name: str


class InsightData(BaseModel):
    """AI-generated insights"""
    type: str
    severity: str
    title: str
    description: str
    recommendation: str
    confidence: float


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get high-level dashboard overview with all key metrics
    Cached for 2 minutes (frequently accessed)
    """
    # Check cache
    cached = cache_manager.get(tenant_id, "dashboard_overview")
    if cached:
        logger.info(f"✓ Cache HIT: dashboard_overview for tenant {tenant_id}")
        return DashboardOverview(**cached)
    
    logger.info(f"✗ Cache MISS: dashboard_overview for tenant {tenant_id}")
    
    # Build graph
    nodes, edges = GraphService.build_graph(db, tenant_id)
    metrics = MetricsService.compute_global_metrics(db, tenant_id)
    issues = await IssueDetector.detect_issues(db, tenant_id)
    
    # Calculate health score (0-100)
    health_score = 100
    if metrics['error_rate'] > 0.05:
        health_score -= 30
    if metrics['avg_latency_ms'] > 1000:
        health_score -= 20
    critical_issues = len([i for i in issues if i.severity == "critical"])
    health_score -= critical_issues * 10
    health_score = max(0, min(100, health_score))
    
    # Calculate architecture complexity
    G = GraphService.get_graph_from_db(db, tenant_id)
    analysis = GraphAnalysis.analyze_architecture(G)
    complexity = analysis.get("avg_degree", 0)
    
    # Calculate uptime (simplified - based on error rate)
    uptime = (1 - metrics['error_rate']) * 100
    
    overview = {
        "total_services": len(nodes),
        "total_requests": metrics['total_spans'],
        "avg_latency_ms": metrics['avg_latency_ms'],
        "error_rate": metrics['error_rate'],
        "health_score": health_score,
        "critical_issues": critical_issues,
        "warnings": len([i for i in issues if i.severity in ["high", "medium"]]),
        "architecture_complexity": complexity,
        "active_incidents": critical_issues,
        "uptime_percentage": round(uptime, 2),
        "last_updated": datetime.now().isoformat()
    }
    
    # Cache result for 2 minutes (120 seconds) - frequently accessed
    cache_manager.set(tenant_id, "dashboard_overview", overview, ttl=120)
    
    return DashboardOverview(**overview)


@router.get("/architecture-map")
async def get_architecture_map(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get architecture graph data optimized for visualization
    """
    nodes, edges = GraphService.build_graph(db, tenant_id)
    G = GraphService.get_graph_from_db(db, tenant_id)
    analysis = GraphAnalysis.analyze_architecture(G)
    
    # Enrich nodes with position hints for visualization
    for i, node in enumerate(nodes):
        node_dict = node.model_dump()
        node_dict['position'] = {
            'x': (i % 5) * 200,
            'y': (i // 5) * 150
        }
        nodes[i] = node_dict
    
    return {
        "nodes": nodes,
        "edges": [e.model_dump() for e in edges],
        "graph_stats": {
            "total_nodes": analysis.get("node_count", 0),
            "total_edges": analysis.get("edge_count", 0),
            "is_dag": analysis.get("is_dag", True),
            "avg_degree": analysis.get("avg_degree", 0)
        },
        "bottlenecks": analysis.get("bottlenecks", []),
        "critical_paths": analysis.get("critical_paths", [])
    }


@router.get("/services", response_model=List[ServiceDetail])
async def get_services(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about all services
    """
    nodes, edges = GraphService.build_graph(db, tenant_id)
    G = GraphService.get_graph_from_db(db, tenant_id)
    
    services = []
    for node in nodes:
        # Get dependencies (outgoing edges)
        dependencies = [e.target for e in edges if e.source == node.id]
        
        # Get dependents (incoming edges)
        dependents = [e.source for e in edges if e.target == node.id]
        
        # Determine health status
        if node.metrics.error_rate > 0.1:
            health_status = "critical"
        elif node.metrics.error_rate > 0.05:
            health_status = "warning"
        elif node.metrics.avg_latency_ms > 2000:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        # Get last seen (most recent span)
        last_span = db.query(Span).filter(
            Span.tenant_id == tenant_id,
            Span.service_name == node.id
        ).order_by(Span.start_time.desc()).first()
        
        last_seen = last_span.start_time.isoformat() if last_span else "unknown"
        
        services.append(ServiceDetail(
            name=node.id,
            type=node.type,
            request_count=node.metrics.call_count,
            avg_latency_ms=node.metrics.avg_latency_ms,
            error_rate=node.metrics.error_rate,
            dependencies=dependencies,
            dependents=dependents,
            health_status=health_status,
            last_seen=last_seen
        ))
    
    return services


@router.get("/services/{service_name}/metrics")
async def get_service_metrics(
    service_name: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get metrics for a specific service"""
    nodes, edges = GraphService.build_graph(db, tenant_id)
    node = next((n for n in nodes if n.id == service_name), None)
    
    if not node:
        raise HTTPException(status_code=404, detail="Service not found")
        
    return node.metrics


@router.get("/trends")
async def get_trends(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    hours: int = Query(default=24, ge=1, le=168)  # 1 hour to 7 days
):
    """
    Get time-series trends for latency, error rate, and volume
    """
    # Calculate time window
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # Query spans in time window
    spans = db.query(Span).filter(
        Span.tenant_id == tenant_id,
        Span.start_time >= start_time,
        Span.start_time <= end_time
    ).all()
    
    if not spans:
        return {"latency": [], "error_rate": [], "volume": []}
    
    # Group by hour
    hourly_buckets = {}
    for span in spans:
        bucket = span.start_time.replace(minute=0, second=0, microsecond=0)
        if bucket not in hourly_buckets:
            hourly_buckets[bucket] = []
        hourly_buckets[bucket].append(span)
    
    # Calculate metrics per bucket
    latency_trends = []
    error_trends = []
    volume_trends = []
    
    for bucket_time in sorted(hourly_buckets.keys()):
        bucket_spans = hourly_buckets[bucket_time]
        
        # Latency
        avg_latency = sum(s.latency_ms for s in bucket_spans) / len(bucket_spans)
        latency_trends.append({
            "timestamp": bucket_time.isoformat(),
            "value": round(avg_latency, 2)
        })
        
        # Error rate
        error_count = sum(1 for s in bucket_spans if s.error or (s.status_code and s.status_code >= 500))
        error_rate = error_count / len(bucket_spans)
        error_trends.append({
            "timestamp": bucket_time.isoformat(),
            "value": round(error_rate, 4)
        })
        
        # Volume
        volume_trends.append({
            "timestamp": bucket_time.isoformat(),
            "value": len(bucket_spans)
        })
    
    return {
        "latency": latency_trends,
        "error_rate": error_trends,
        "volume": volume_trends,
        "period_hours": hours,
        "timeline": volume_trends  # Alias for timeline compatibility
    }


@router.get("/traces/timeline")
async def get_trace_timeline(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    hours: int = Query(default=24, ge=1, le=168)
):
    """Get trace volume timeline (alias for trends)"""
    return await get_trends(tenant_id, db, hours)


@router.get("/insights")
async def get_ai_insights(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered insights and anomalies
    """
    # Check cache
    cached = cache_manager.get(tenant_id, "ai_insights")
    if cached:
        return cached
    
    try:
        # Get current metrics and trends
        metrics = MetricsService.compute_global_metrics(db, tenant_id)
        
        # Get trends for anomaly detection
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        recent_spans = db.query(Span).filter(
            Span.tenant_id == tenant_id,
            Span.start_time >= start_time
        ).all()
        
        trends = []
        if recent_spans:
            hourly_latencies = {}
            for span in recent_spans:
                hour = span.start_time.replace(minute=0, second=0, microsecond=0)
                if hour not in hourly_latencies:
                    hourly_latencies[hour] = []
                hourly_latencies[hour].append(span.latency_ms)
            
            for hour, latencies in hourly_latencies.items():
                trends.append({
                    "timestamp": hour.isoformat(),
                    "avg_latency": sum(latencies) / len(latencies)
                })
        
        # Get AI client
        ai_client = get_ai_client()
        
        if ai_client.llm:
            # Generate insights using AI
            insights_data = await ai_client.generate_dashboard_insights(metrics, trends)
            
            # Cache result
            cache_manager.set(tenant_id, "ai_insights", insights_data)
            
            return insights_data
        else:
            # Fallback to rule-based insights
            insights = []
            
            if metrics['error_rate'] > 0.05:
                insights.append({
                    "type": "alert",
                    "severity": "high",
                    "title": "High Error Rate Detected",
                    "description": f"Error rate is {metrics['error_rate']*100:.1f}%, above the 5% threshold",
                    "recommendation": "Review recent deployments and check service logs",
                    "confidence": 0.95
                })
            
            if metrics['avg_latency_ms'] > 1000:
                insights.append({
                    "type": "alert",
                    "severity": "medium",
                    "title": "High Latency Detected",
                    "description": f"Average latency is {metrics['avg_latency_ms']:.0f}ms",
                    "recommendation": "Consider adding caching or optimizing database queries",
                    "confidence": 0.90
                })
            
            # Check for trend anomalies
            if len(trends) > 2:
                recent_avg = sum(t['avg_latency'] for t in trends[-3:]) / 3
                if recent_avg > metrics['avg_latency_ms'] * 1.5:
                    insights.append({
                        "type": "anomaly",
                        "severity": "medium",
                        "title": "Latency Spike Detected",
                        "description": "Recent latency is 50% higher than average",
                        "recommendation": "Investigate recent changes or increased load",
                        "confidence": 0.85
                    })
            
            result = {
                "insights": insights,
                "anomalies": [],
                "recommendations": [
                    "Enable Redis caching to improve response times",
                    "Implement circuit breakers for external API calls",
                    "Add database read replicas to distribute load"
                ]
            }
            
            cache_manager.set(tenant_id, "ai_insights", result)
            return result
    
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return {
            "insights": [],
            "anomalies": [],
            "recommendations": [],
            "error": str(e)
        }


@router.get("/health")
async def get_system_health(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get system health scores by category
    """
    nodes, edges = GraphService.build_graph(db, tenant_id)
    metrics = MetricsService.compute_global_metrics(db, tenant_id)
    issues = await IssueDetector.detect_issues(db, tenant_id)
    G = GraphService.get_graph_from_db(db, tenant_id)
    analysis = GraphAnalysis.analyze_architecture(G)
    
    # Performance score (based on latency)
    performance_score = 100
    if metrics['avg_latency_ms'] > 2000:
        performance_score = 50
    elif metrics['avg_latency_ms'] > 1000:
        performance_score = 70
    elif metrics['avg_latency_ms'] > 500:
        performance_score = 85
    
    # Reliability score (based on error rate)
    reliability_score = 100
    if metrics['error_rate'] > 0.1:
        reliability_score = 50
    elif metrics['error_rate'] > 0.05:
        reliability_score = 70
    elif metrics['error_rate'] > 0.02:
        reliability_score = 85
    
    # Architecture score (based on complexity and issues)
    architecture_score = 100
    architecture_score -= len([i for i in issues if i.severity == "critical"]) * 15
    architecture_score -= len([i for i in issues if i.severity == "high"]) * 10
    architecture_score = max(0, architecture_score)
    
    # Scalability score (based on graph structure)
    scalability_score = 100
    if not analysis.get("is_dag"):
        scalability_score -= 20  # Circular dependencies hurt scalability
    if len(analysis.get("bottlenecks", [])) > 2:
        scalability_score -= 15
    
    # Overall health
    overall_health = int((performance_score + reliability_score + architecture_score + scalability_score) / 4)
    
    return {
        "overall_health": overall_health,
        "categories": {
            "performance": {
                "score": performance_score,
                "status": "good" if performance_score >= 80 else "warning" if performance_score >= 60 else "critical",
                "metrics": {
                    "avg_latency_ms": metrics['avg_latency_ms']
                }
            },
            "reliability": {
                "score": reliability_score,
                "status": "good" if reliability_score >= 80 else "warning" if reliability_score >= 60 else "critical",
                "metrics": {
                    "error_rate": metrics['error_rate']
                }
            },
            "architecture": {
                "score": architecture_score,
                "status": "good" if architecture_score >= 80 else "warning" if architecture_score >= 60 else "critical",
                "metrics": {
                    "critical_issues": len([i for i in issues if i.severity == "critical"]),
                    "total_issues": len(issues)
                }
            },
            "scalability": {
                "score": scalability_score,
                "status": "good" if scalability_score >= 80 else "warning" if scalability_score >= 60 else "critical",
                "metrics": {
                    "bottlenecks": len(analysis.get("bottlenecks", [])),
                    "has_cycles": not analysis.get("is_dag", True)
                }
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/dependencies")
async def get_dependency_matrix(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get dependency matrix for visualization
    """
    nodes, edges = GraphService.build_graph(db, tenant_id)
    
    # Build matrix
    service_names = [n.id for n in nodes]
    matrix = []
    
    for source in service_names:
        row = {}
        for target in service_names:
            # Find edge
            edge = next((e for e in edges if e.source == source and e.target == target), None)
            if edge:
                row[target] = {
                    "has_dependency": True,
                    "call_count": edge.call_count,
                    "avg_latency_ms": edge.avg_latency_ms,
                    "error_rate": edge.error_rate
                }
            else:
                row[target] = {"has_dependency": False}
        matrix.append({"service": source, "dependencies": row})
    
    return {
        "services": service_names,
        "matrix": matrix
    }


@router.get("/bottlenecks")
async def get_bottlenecks(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get critical path analysis and bottlenecks
    """
    G = GraphService.get_graph_from_db(db, tenant_id)
    analysis = GraphAnalysis.analyze_architecture(G)
    
    return {
        "bottlenecks": analysis.get("bottlenecks", []),
        "critical_paths": analysis.get("critical_paths", []),
        "cycles": analysis.get("cycles", []),
        "recommendations": [
            f"Service '{b}' is a bottleneck - consider adding redundancy"
            for b in analysis.get("bottlenecks", [])[:3]
        ]
    }


@router.get("/workflows")
async def generate_workflow_alternatives(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    goal: str = Query(default="optimize_performance", description="Optimization goal: optimize_performance, reduce_cost, improve_reliability")
):
    """
    Generate AI-powered workflow alternatives using Azure OpenAI + LangGraph
    This is THE KILLER FEATURE - generates 5 different architecture refactoring workflows
    """
    # Check cache
    cache_key = f"workflows_{goal}"
    cached = cache_manager.get(tenant_id, cache_key)
    if cached:
        logger.info(f"Returning cached workflows for tenant {tenant_id}, goal {goal}")
        return cached
    
    try:
        # Get current architecture
        nodes, edges = GraphService.build_graph(db, tenant_id)
        issues = await IssueDetector.detect_issues(db, tenant_id)
        G = GraphService.get_graph_from_db(db, tenant_id)
        analysis = GraphAnalysis.analyze_architecture(G)
        
        # Build architecture summary
        architecture = {
            "services": [{"name": n.id, "type": n.type, "metrics": n.metrics.model_dump()} for n in nodes],
            "dependencies": [{"from": e.source, "to": e.target, "metrics": e.model_dump()} for e in edges],
            "analysis": {
                "is_dag": analysis.get("is_dag", True),
                "bottlenecks": analysis.get("bottlenecks", []),
                "critical_paths": analysis.get("critical_paths", [])
            }
        }
        
        # Get AI client
        ai_client = get_ai_client()
        
        if ai_client.llm:
            # Use AI to generate workflow alternatives
            logger.info(f"Generating AI-powered workflows for tenant {tenant_id} with goal {goal}")
            ai_result = await ai_client.generate_workflow_alternatives(
                architecture=architecture,
                issues=[i.model_dump() for i in issues],
                goal=goal
            )
            
            # Also use LangGraph pipeline for additional strategy
            workflows = WorkflowGenerator.generate_workflows(db, tenant_id)
            
            # Combine AI and LangGraph results
            result = {
                "ai_workflows": ai_result.get("workflows", []),
                "langgraph_workflow": workflows[0].model_dump() if workflows else None,
                "goal": goal,
                "architecture_summary": {
                    "total_services": len(nodes),
                    "total_dependencies": len(edges),
                    "critical_issues": len([i for i in issues if i.severity == "critical"])
                },
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache result
            cache_manager.set(tenant_id, cache_key, result)
            
            return result
        else:
            # Fallback to LangGraph only
            logger.warning("Azure OpenAI not configured, using LangGraph fallback")
            workflows = WorkflowGenerator.generate_workflows(db, tenant_id)
            
            result = {
                "workflows": [w.model_dump() for w in workflows],
                "goal": goal,
                "architecture_summary": {
                    "total_services": len(nodes),
                    "total_dependencies": len(edges),
                    "critical_issues": len([i for i in issues if i.severity == "critical"])
                },
                "note": "Azure OpenAI not configured - using LangGraph pipeline only",
                "generated_at": datetime.now().isoformat()
            }
            
            cache_manager.set(tenant_id, cache_key, result)
            return result
    
    except Exception as e:
        logger.error(f"Error generating workflows: {e}")
        return {
            "workflows": [],
            "error": str(e),
            "note": "Failed to generate workflows - check logs for details"
        }


@router.get("/recommendations")
async def get_ai_architecture_recommendations(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered architecture recommendations based on current state
    Uses Azure OpenAI GPT-4 to analyze architecture and suggest improvements
    """
    # Check cache
    cached = cache_manager.get(tenant_id, "ai_recommendations")
    if cached:
        return cached
    
    try:
        # Get current architecture
        nodes, edges = GraphService.build_graph(db, tenant_id)
        issues = await IssueDetector.detect_issues(db, tenant_id)
        G = GraphService.get_graph_from_db(db, tenant_id)
        analysis = GraphAnalysis.analyze_architecture(G)
        
        architecture = {
            "services": [{"name": n.id, "type": n.type, "metrics": n.metrics.model_dump()} for n in nodes],
            "dependencies": [{"from": e.source, "to": e.target} for e in edges],
            "is_dag": analysis.get("is_dag", True),
            "bottlenecks": analysis.get("bottlenecks", [])
        }
        
        # Get AI client
        ai_client = get_ai_client()
        
        if ai_client.llm:
            # Generate recommendations using AI
            recommendations = await ai_client.generate_architecture_recommendation(
                architecture=architecture,
                issues=[i.model_dump() for i in issues],
                constraints={"budget": "medium", "timeline": "3-6 months"}
            )
            
            result = {
                "recommendations": recommendations,
                "current_state": {
                    "services": len(nodes),
                    "dependencies": len(edges),
                    "critical_issues": len([i for i in issues if i.severity == "critical"]),
                    "architecture_type": "microservices" if len(nodes) > 5 else "monolith"
                },
                "generated_at": datetime.now().isoformat()
            }
            
            cache_manager.set(tenant_id, "ai_recommendations", result)
            return result
        else:
            # Fallback recommendations
            result = {
                "recommendations": {
                    "architecture_type": "microservices" if len(nodes) > 5 else "monolith",
                    "patterns": ["circuit-breaker", "rate-limiting", "caching"],
                    "optimizations": [
                        "Add Redis caching layer",
                        "Implement async processing for long-running tasks",
                        "Add database connection pooling"
                    ],
                    "migrations": [],
                    "risk_assessment": "medium",
                    "estimated_effort": "2-3 months",
                    "priority": "medium"
                },
                "note": "Azure OpenAI not configured - using rule-based recommendations",
                "generated_at": datetime.now().isoformat()
            }
            
            cache_manager.set(tenant_id, "ai_recommendations", result)
            return result
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {"error": str(e), "recommendations": None}
