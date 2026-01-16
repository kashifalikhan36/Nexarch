"""
Cache Management API
Admin endpoints for Redis cache management
"""
from fastapi import APIRouter, Depends
from core.cache import get_cache_manager
from core.auth import get_tenant_id
from core.logging import get_logger
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])
logger = get_logger(__name__)
cache_manager = get_cache_manager()


@router.get("/stats")
async def get_cache_stats(tenant_id: str = Depends(get_tenant_id)) -> Dict[str, Any]:
    """
    Get cache statistics
    Shows Redis stats if connected, or in-memory stats
    """
    stats = cache_manager.get_stats()
    stats["tenant_id"] = tenant_id
    stats["backend_type"] = "redis" if cache_manager.is_redis() else "in-memory"
    return stats


@router.delete("/invalidate")
async def invalidate_tenant_cache(tenant_id: str = Depends(get_tenant_id)) -> Dict[str, str]:
    """
    Invalidate all cache for current tenant
    Use when you want to force refresh of all cached data
    """
    cache_manager.invalidate(tenant_id)
    logger.info(f"Cache invalidated for tenant: {tenant_id}")
    return {
        "status": "success",
        "message": f"All cache invalidated for tenant {tenant_id}",
        "tenant_id": tenant_id
    }


@router.delete("/invalidate/{operation}")
async def invalidate_operation_cache(
    operation: str,
    tenant_id: str = Depends(get_tenant_id)
) -> Dict[str, str]:
    """
    Invalidate cache for specific operation
    Operations: dashboard_overview, architecture_map, services, etc.
    """
    cache_manager.invalidate(tenant_id, operation)
    logger.info(f"Cache invalidated for tenant {tenant_id}, operation: {operation}")
    return {
        "status": "success",
        "message": f"Cache invalidated for operation: {operation}",
        "tenant_id": tenant_id,
        "operation": operation
    }


@router.post("/warm/{operation}")
async def warm_cache(
    operation: str,
    tenant_id: str = Depends(get_tenant_id)
) -> Dict[str, str]:
    """
    Pre-warm cache for specific operation
    Useful for reducing latency before peak usage
    """
    # Import here to avoid circular dependency
    from api.dashboard import get_dashboard_overview, get_architecture_map
    from api.architecture import get_current_architecture
    from db.base import get_db
    
    db = next(get_db())
    
    try:
        if operation == "dashboard_overview":
            await get_dashboard_overview(tenant_id, db)
        elif operation == "architecture_map":
            await get_architecture_map(tenant_id, db)
        elif operation == "current_architecture":
            await get_current_architecture(tenant_id, db)
        else:
            return {
                "status": "error",
                "message": f"Unknown operation: {operation}"
            }
        
        return {
            "status": "success",
            "message": f"Cache warmed for operation: {operation}",
            "operation": operation
        }
    
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/health")
async def cache_health() -> Dict[str, Any]:
    """
    Check cache health
    Returns connection status and basic metrics
    """
    stats = cache_manager.get_stats()
    
    is_healthy = True
    if cache_manager.is_redis():
        is_healthy = stats.get("status") == "connected"
    
    return {
        "healthy": is_healthy,
        "backend": "redis" if cache_manager.is_redis() else "in-memory",
        "stats": stats
    }
