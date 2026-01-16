"""
Test/Demo API - Endpoints for testing and demonstration
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from db.models import Span, Tenant
from models.span import Span as SpanModel
from core.auth import get_tenant_id
from datetime import datetime, timedelta
import random
import uuid

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])


@router.post("/generate-sample-data")
async def generate_sample_data(
    count: int = 100,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Generate sample telemetry data for testing
    Useful for populating dashboard with demo data
    """
    services = ["api-gateway", "user-service", "order-service", "payment-service", "notification-service"]
    operations = [
        "GET /users",
        "POST /orders",
        "GET /orders/:id",
        "POST /payments",
        "GET /notifications"
    ]
    
    spans_created = 0
    now = datetime.now()
    
    for i in range(count):
        # Random service and operation
        service = random.choice(services)
        operation = random.choice(operations)
        
        # Random latency (mostly good, some slow)
        if random.random() < 0.9:
            latency = random.uniform(10, 200)
        else:
            latency = random.uniform(500, 2000)
        
        # Random status (mostly success, some errors)
        if random.random() < 0.95:
            status_code = 200
            error = False
        else:
            status_code = random.choice([400, 500, 503])
            error = True
        
        # Random timestamp within last 24 hours
        timestamp = now - timedelta(hours=random.uniform(0, 24))
        
        # Create span
        span = Span(
            tenant_id=tenant_id,
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            parent_span_id=None,
            service_name=service,
            operation=operation,
            kind="server",
            start_time=timestamp,
            end_time=timestamp + timedelta(milliseconds=latency),
            latency_ms=latency,
            status_code=status_code,
            error=str(error) if error else None,
            downstream=None
        )
        
        db.add(span)
        spans_created += 1
    
    db.commit()
    
    return {
        "status": "success",
        "spans_created": spans_created,
        "services": services,
        "time_range": "last 24 hours"
    }


@router.delete("/clear-data")
async def clear_data(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Clear all span data for tenant (careful!)"""
    deleted = db.query(Span).filter(Span.tenant_id == tenant_id).delete()
    db.commit()
    
    return {
        "status": "success",
        "spans_deleted": deleted
    }


@router.get("/sample-scenarios")
async def get_sample_scenarios():
    """Get predefined test scenarios"""
    return {
        "scenarios": [
            {
                "name": "E-Commerce Platform",
                "services": ["api-gateway", "user-service", "product-service", "order-service", "payment-service", "inventory-service"],
                "description": "Typical e-commerce microservices architecture"
            },
            {
                "name": "Social Media App",
                "services": ["api-gateway", "auth-service", "post-service", "comment-service", "notification-service", "media-service"],
                "description": "Social media platform with content services"
            },
            {
                "name": "Fintech Application",
                "services": ["api-gateway", "account-service", "transaction-service", "fraud-detection", "reporting-service"],
                "description": "Financial services with compliance"
            }
        ]
    }


@router.post("/scenarios/{scenario_name}/apply")
async def apply_scenario(
    scenario_name: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Apply a predefined scenario with realistic data"""
    
    scenarios = {
        "ecommerce": {
            "services": ["api-gateway", "user-service", "product-service", "order-service", "payment-service", "inventory-service"],
            "operations": [
                "GET /products",
                "GET /products/:id",
                "POST /cart/add",
                "GET /cart",
                "POST /orders",
                "POST /payments",
                "GET /orders/:id"
            ]
        },
        "social": {
            "services": ["api-gateway", "auth-service", "post-service", "comment-service", "notification-service", "media-service"],
            "operations": [
                "POST /auth/login",
                "GET /feed",
                "POST /posts",
                "GET /posts/:id",
                "POST /comments",
                "GET /notifications"
            ]
        },
        "fintech": {
            "services": ["api-gateway", "account-service", "transaction-service", "fraud-detection", "reporting-service"],
            "operations": [
                "GET /accounts",
                "POST /transactions",
                "GET /transactions/:id",
                "POST /fraud/check",
                "GET /reports/monthly"
            ]
        }
    }
    
    scenario = scenarios.get(scenario_name.lower())
    if not scenario:
        return {"error": "Scenario not found"}
    
    spans_created = 0
    now = datetime.now()
    
    # Generate 200 spans for this scenario
    for i in range(200):
        service = random.choice(scenario["services"])
        operation = random.choice(scenario["operations"])
        
        latency = random.uniform(20, 300)
        status_code = 200 if random.random() < 0.96 else random.choice([400, 500])
        timestamp = now - timedelta(hours=random.uniform(0, 24))
        
        span = Span(
            tenant_id=tenant_id,
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            parent_span_id=None,
            service_name=service,
            operation=operation,
            kind="server",
            start_time=timestamp,
            end_time=timestamp + timedelta(milliseconds=latency),
            latency_ms=latency,
            status_code=status_code,
            error="Error" if status_code >= 400 else None,
            downstream=None
        )
        
        db.add(span)
        spans_created += 1
    
    db.commit()
    
    return {
        "status": "success",
        "scenario": scenario_name,
        "spans_created": spans_created,
        "services": scenario["services"]
    }
