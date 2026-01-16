from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from datetime import datetime
from core.config import get_settings
from core.logging import get_logger
import sys

router = APIRouter(prefix="/api/v1", tags=["health"])
logger = get_logger(__name__)
settings = get_settings()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with component status"""
    settings = get_settings()
    
    # Check database
    db_healthy = True
    try:
        db.execute("SELECT 1")
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    # Check AI client
    ai_healthy = False
    try:
        from core.ai_client import get_ai_client
        ai_client = get_ai_client()
        ai_healthy = ai_client.llm is not None
    except Exception as e:
        logger.warning(f"AI client health check failed: {e}")
        ai_healthy = False
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "ai_client": "configured" if ai_healthy else "not_configured",
            "multi_tenant": "enabled" if settings.ENABLE_MULTI_TENANT else "disabled",
            "caching": "enabled" if settings.ENABLE_CACHING else "disabled",
            "ai_generation": "enabled" if settings.ENABLE_AI_GENERATION else "disabled"
        },
        "features": {
            "auto_discovery": True,
            "ai_architecture_design": settings.ENABLE_AI_GENERATION,
            "dashboard": True,
            "multi_tenancy": settings.ENABLE_MULTI_TENANT
        }
    }


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready"}, 503


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}
