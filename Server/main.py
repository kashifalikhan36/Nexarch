from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import get_settings
from core.logging import setup_logging, get_logger
from core.rate_limit import RateLimitMiddleware
from core.cache import init_cache
from db.base import engine, Base
from api import ingest, architecture, workflows, health, admin, dashboard, ai_design, system, cache_api, auth



settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    setup_logging(settings.DEBUG)
    
    # Initialize cache
    if settings.ENABLE_CACHING:
        redis_url = settings.get_redis_url()
        cache_manager = init_cache(redis_url, settings.CACHE_TTL_SECONDS)
        if cache_manager.is_redis():
            logger.info("✅ Azure Cache for Redis initialized")
        else:
            logger.info("ℹ️  In-memory cache initialized (fallback)")
    else:
        logger.info("⚠️  Caching disabled")
    
    # Initialize database
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    logger.info(f"   Multi-tenant: {'✓' if settings.ENABLE_MULTI_TENANT else '✗'}")
    logger.info(f"   Caching: {'✓ Redis' if settings.ENABLE_CACHING and settings.get_redis_url() else '✓ Memory' if settings.ENABLE_CACHING else '✗'}")
    logger.info(f"   AI Generation: {'✓' if settings.ENABLE_AI_GENERATION else '✗'}")
    logger.info(f"   Rate Limiting: {'✓' if settings.ENABLE_RATE_LIMITING else '✗'}")
    
    yield
    
    logger.info(f"🛑 {settings.APP_NAME} shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    description="Nexarch - Multi-tenant Architecture Intelligence Platform with Azure Cache for Redis"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://run-time.in",
        "https://modelix.world",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Register routes
app.include_router(auth.router)  # Authentication endpoints (Google OAuth)
app.include_router(health.router)
app.include_router(system.router)  # System info and statistics
app.include_router(cache_api.router)  # Cache management API
app.include_router(admin.router)  # Admin routes for tenant management
app.include_router(dashboard.router)  # Dashboard endpoints with AI features
app.include_router(ai_design.router)  # AI-powered architecture design
app.include_router(ingest.router)
app.include_router(architecture.router)
app.include_router(workflows.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "features": {
            "multi_tenant": True,
            "rate_limiting": True,
            "caching": True,
            "authentication": "API Key"
        }
    }


if __name__ == "__main__":
    import uvicorn
    # FastAPI runs on 127.0.0.1 (localhost only)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
