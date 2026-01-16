from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Index
from datetime import datetime
from db.base import Base


class Span(Base):
    __tablename__ = "spans"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(64), nullable=False, index=True)
    span_id = Column(String(32), nullable=False, unique=True, index=True)
    parent_span_id = Column(String(32), nullable=True, index=True)
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
    
    __table_args__ = (
        Index('idx_trace_start', 'trace_id', 'start_time'),
        Index('idx_service_time', 'service_name', 'start_time'),
    )


class ArchitectureSnapshot(Base):
    __tablename__ = "architecture_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_time = Column(DateTime, default=datetime.utcnow, index=True)
    nodes = Column(Text, nullable=False)  # JSON
    edges = Column(Text, nullable=False)  # JSON
    metrics = Column(Text, nullable=False)  # JSON
    issues = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
