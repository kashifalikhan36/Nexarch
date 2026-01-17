from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Index, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base


class Tenant(Base):
    """Tenant/Organization table"""
    __tablename__ = "tenants"
    
    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    max_spans_per_day = Column(Integer, default=1000000)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    api_keys = relationship("APIKey", back_populates="tenant")
    spans = relationship("Span", back_populates="tenant")


class User(Base):
    """User table"""
    __tablename__ = "users"
    
    id = Column(String(64), primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    pending_signup = Column(Boolean, default=False)
    
    # OAuth fields
    auth_provider = Column(String(50), default="local")  # "local" or "google"
    google_id = Column(String(255), nullable=True, unique=True)
    picture = Column(String(512), nullable=True)
    
    # Password reset fields
    password_reset_token = Column(String(512), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # OTP fields
    signup_otp = Column(String(10), nullable=True)
    signup_otp_expires = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")


class APIKey(Base):
    """API Key table"""
    __tablename__ = "api_keys"
    
    key = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")


class Span(Base):
    __tablename__ = "spans"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    trace_id = Column(String(64), nullable=False, index=True)
    span_id = Column(String(64), nullable=False, index=True)
    parent_span_id = Column(String(64), nullable=True, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    operation = Column(String(255), nullable=False)
    kind = Column(String(32), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    latency_ms = Column(Float, nullable=False)
    status_code = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    downstream = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="spans")
    
    __table_args__ = (
        Index('idx_tenant_trace', 'tenant_id', 'trace_id'),
        Index('idx_tenant_service', 'tenant_id', 'service_name', 'start_time'),
        Index('idx_tenant_time', 'tenant_id', 'start_time'),
    )


class ArchitectureSnapshot(Base):
    __tablename__ = "architecture_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    snapshot_time = Column(DateTime, default=datetime.utcnow, index=True)
    nodes = Column(Text, nullable=False)  # JSON
    edges = Column(Text, nullable=False)  # JSON
    metrics = Column(Text, nullable=False)  # JSON
    issues = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)


class ArchitectureDiscovery(Base):
    """SDK auto-discovery data"""
    __tablename__ = "architecture_discoveries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    service_type = Column(String(64), nullable=False)
    version = Column(String(64), nullable=True)
    endpoints = Column(Text, nullable=False)  # JSON array of discovered endpoints
    databases = Column(Text, nullable=False)  # JSON array of database connections
    external_services = Column(Text, nullable=False)  # JSON array of external dependencies
    middleware = Column(Text, nullable=True)  # JSON array of middleware
    architecture_patterns = Column(Text, nullable=True)  # JSON dict of patterns
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_tenant_service_discovery', 'tenant_id', 'service_name', 'discovered_at'),
    )
