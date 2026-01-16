"""
Setup test data for MCP server testing
"""
import sys
from datetime import datetime, timedelta

# Add parent to path
sys.path.insert(0, ".")

from db.base import SessionLocal, Base, engine
from db.models import Span, Tenant

def setup_test_data():
    """Create test data for MCP server"""
    print("🔧 Setting up test database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        tenant_id = "test_tenant_001"
        
        # Create tenant if it doesn't exist
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            tenant = Tenant(
                id=tenant_id,
                name="Test Tenant",
                is_active=True
            )
            db.add(tenant)
            db.commit()
            print(f"✅ Created tenant: {tenant_id}")
        else:
            print(f"ℹ️  Tenant already exists: {tenant_id}")
        
        # Check if data already exists
        existing = db.query(Span).filter(Span.tenant_id == tenant_id).count()
        if existing > 0:
            print(f"ℹ️  Test data already exists ({existing} spans)")
            return
        
        # Create test spans for microservices architecture
        tenant_id = "test_tenant_001"
        base_time = datetime.utcnow()
        
        services = [
            {"name": "api-gateway", "downstream": ["user-service", "order-service", "payment-service"]},
            {"name": "user-service", "downstream": ["user-db"]},
            {"name": "order-service", "downstream": ["order-db", "inventory-service"]},
            {"name": "payment-service", "downstream": ["payment-db", "payment-gateway"]},
            {"name": "inventory-service", "downstream": ["inventory-db"]},
            {"name": "user-db", "downstream": []},
            {"name": "order-db", "downstream": []},
            {"name": "payment-db", "downstream": []},
            {"name": "inventory-db", "downstream": []},
            {"name": "payment-gateway", "downstream": []}
        ]
        
        span_id = 1
        for service in services:
            for _ in range(5):  # Create 5 spans per service
                for downstream in service["downstream"] if service["downstream"] else [None]:
                    span = Span(
                        tenant_id=tenant_id,
                        trace_id=f"trace-{span_id}",
                        span_id=f"span-{span_id}",
                        parent_span_id=f"span-{span_id-1}" if span_id > 1 else None,
                        service_name=service["name"],
                        operation=f"GET /{service['name'].replace('-service', '')}",
                        kind="SERVER",
                        start_time=base_time - timedelta(minutes=span_id),
                        end_time=base_time - timedelta(minutes=span_id-1),
                        latency_ms=50 + (span_id % 100),
                        status_code=200 if span_id % 20 != 0 else 500,
                        error=None if span_id % 20 != 0 else "Internal Server Error",
                        downstream=downstream
                    )
                    db.add(span)
                    span_id += 1
        
        db.commit()
        total_spans = db.query(Span).filter(Span.tenant_id == tenant_id).count()
        print(f"✅ Created {total_spans} test spans for tenant: {tenant_id}")
        
        # Print summary
        services_count = db.query(Span.service_name).filter(Span.tenant_id == tenant_id).distinct().count()
        errors = db.query(Span).filter(Span.tenant_id == tenant_id, Span.error != None).count()
        print(f"   - Services: {services_count}")
        print(f"   - Total spans: {total_spans}")
        print(f"   - Errors: {errors}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("🎉 Test data setup complete!")


if __name__ == "__main__":
    setup_test_data()
