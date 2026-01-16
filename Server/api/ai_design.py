"""
AI Design API - Endpoints for AI-powered architecture design
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.base import get_db
from core.auth import get_tenant_id
from core.logging import get_logger
from services.ai_architecture_designer import (
    get_architecture_designer,
    ArchitectureRequirements,
    ArchitectureDesign
)
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/api/v1/ai-design", tags=["AI Architecture Design"])
logger = get_logger(__name__)


class DesignRequest(BaseModel):
    """Request for new architecture design"""
    business_domain: str
    expected_scale: str
    key_features: List[str]
    performance_requirements: Dict[str, Any]
    constraints: Dict[str, Any]
    existing_tech_stack: Optional[List[str]] = None
    compliance_requirements: Optional[List[str]] = None
    num_alternatives: int = 3


class DecompositionRequest(BaseModel):
    """Request for monolith decomposition"""
    monolith_description: str
    business_capabilities: List[str]


class EventDrivenRequest(BaseModel):
    """Request for event-driven design"""
    use_cases: List[str]
    data_flows: List[Dict[str, str]]


class OptimizationRequest(BaseModel):
    """Request for architecture optimization"""
    pain_points: List[str]
    optimization_goals: List[str]


@router.post("/design-new", response_model=List[ArchitectureDesign])
async def design_new_architecture(
    request: DesignRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    🎨 Design a completely NEW architecture from scratch using Azure OpenAI
    
    This is THE CRAZY STUFF - AI designs your entire architecture!
    
    Example request:
    ```json
    {
        "business_domain": "food delivery",
        "expected_scale": "1M orders/day",
        "key_features": ["real-time tracking", "payment processing", "rider matching"],
        "performance_requirements": {
            "max_latency_ms": 100,
            "availability": "99.99%"
        },
        "constraints": {
            "budget": "medium",
            "timeline": "6 months",
            "team_size": 10
        },
        "existing_tech_stack": ["python", "react", "postgresql"],
        "compliance_requirements": ["PCI-DSS", "GDPR"],
        "num_alternatives": 3
    }
    ```
    
    Returns 3 completely different architecture designs with:
    - Full service breakdown
    - Database strategy
    - Deployment plan
    - Cost estimates
    - Implementation roadmap
    """
    try:
        designer = get_architecture_designer()
        
        requirements = ArchitectureRequirements(
            business_domain=request.business_domain,
            expected_scale=request.expected_scale,
            key_features=request.key_features,
            performance_requirements=request.performance_requirements,
            constraints=request.constraints,
            existing_tech_stack=request.existing_tech_stack,
            compliance_requirements=request.compliance_requirements
        )
        
        designs = await designer.design_new_architecture(
            requirements=requirements,
            num_alternatives=request.num_alternatives
        )
        
        logger.info(f"Generated {len(designs)} architecture designs for tenant {tenant_id}")
        return designs
    
    except Exception as e:
        logger.error(f"Architecture design failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decompose-monolith")
async def decompose_monolith(
    request: DecompositionRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    🔨 AI-powered monolith → microservices decomposition
    
    Example:
    ```json
    {
        "monolith_description": "E-commerce platform with 200K LOC, handles users, products, orders, payments",
        "business_capabilities": ["user management", "catalog", "ordering", "payment", "shipping"]
    }
    ```
    
    Returns:
    - Microservices list with bounded contexts
    - Data ownership strategy
    - Migration order (which to extract first)
    - API contracts between services
    """
    try:
        designer = get_architecture_designer()
        
        result = await designer.generate_microservices_decomposition(
            monolith_description=request.monolith_description,
            business_capabilities=request.business_capabilities
        )
        
        logger.info(f"Generated microservices decomposition for tenant {tenant_id}")
        return result
    
    except Exception as e:
        logger.error(f"Decomposition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event-driven-design")
async def design_event_driven(
    request: EventDrivenRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    ⚡ Design event-driven architecture with AI
    
    Example:
    ```json
    {
        "use_cases": [
            "User places order",
            "Payment is processed",
            "Inventory is updated",
            "Notifications are sent"
        ],
        "data_flows": [
            {"from": "order-service", "to": "payment-service", "description": "order details"},
            {"from": "payment-service", "to": "inventory-service", "description": "payment confirmed"}
        ]
    }
    ```
    
    Returns:
    - Domain events catalog
    - Event streams/topics
    - CQRS patterns
    - Saga patterns for distributed transactions
    - Event store design
    """
    try:
        designer = get_architecture_designer()
        
        result = await designer.generate_event_driven_design(
            use_cases=request.use_cases,
            data_flows=request.data_flows
        )
        
        logger.info(f"Generated event-driven design for tenant {tenant_id}")
        return result
    
    except Exception as e:
        logger.error(f"Event-driven design failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-architecture")
async def optimize_architecture(
    request: OptimizationRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    🚀 AI-powered optimization of existing architecture
    
    Example:
    ```json
    {
        "pain_points": [
            "Database bottleneck at 1000 QPS",
            "API response time > 500ms",
            "Frequent 503 errors during peak"
        ],
        "optimization_goals": [
            "Reduce latency to <100ms",
            "Scale to 10000 QPS",
            "99.99% availability"
        ]
    }
    ```
    
    Returns:
    - Specific optimization actions
    - Priority order (high impact, low effort first)
    - Implementation steps
    - Risk assessment
    - Expected impact
    """
    try:
        from services.graph_service import GraphService
        
        designer = get_architecture_designer()
        
        # Get current architecture
        nodes, edges = GraphService.build_graph(db, tenant_id)
        current_architecture = {
            "services": [{"name": n.id, "metrics": n.metrics.model_dump()} for n in nodes],
            "dependencies": [{"from": e.source, "to": e.target} for e in edges]
        }
        
        result = await designer.optimize_existing_architecture(
            current_architecture=current_architecture,
            pain_points=request.pain_points,
            optimization_goals=request.optimization_goals
        )
        
        logger.info(f"Generated optimization plan for tenant {tenant_id}")
        return result
    
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/design-templates")
async def get_design_templates():
    """
    📚 Get pre-built architecture templates
    
    Returns common architecture patterns:
    - Microservices e-commerce
    - Serverless SaaS
    - Event-driven fintech
    - Real-time gaming
    - IoT platform
    """
    return {
        "templates": [
            {
                "name": "Microservices E-Commerce",
                "domain": "e-commerce",
                "scale": "1M users",
                "features": ["product catalog", "cart", "checkout", "payments", "shipping"],
                "architecture_type": "microservices",
                "estimated_cost": "$2000-5000/month"
            },
            {
                "name": "Serverless SaaS",
                "domain": "saas",
                "scale": "100K users",
                "features": ["authentication", "subscription", "analytics", "webhooks"],
                "architecture_type": "serverless",
                "estimated_cost": "$500-1500/month"
            },
            {
                "name": "Event-Driven Fintech",
                "domain": "fintech",
                "scale": "10K TPS",
                "features": ["transactions", "fraud detection", "reporting", "compliance"],
                "architecture_type": "event-driven",
                "estimated_cost": "$3000-8000/month"
            },
            {
                "name": "Real-Time Gaming",
                "domain": "gaming",
                "scale": "500K concurrent",
                "features": ["matchmaking", "leaderboard", "chat", "analytics"],
                "architecture_type": "real-time",
                "estimated_cost": "$5000-15000/month"
            }
        ]
    }
