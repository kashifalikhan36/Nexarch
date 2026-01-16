"""
Nexarch SDK Client - Main entry point for FastAPI integration
"""
from fastapi import FastAPI
from .middleware import NexarchMiddleware
from .router import nexarch_router
from .loggers import NexarchLogger
from typing import Optional


class NexarchSDK:
    """
    Nexarch SDK for FastAPI applications.
    
    Automatically instruments your FastAPI app to:
    - Capture all API requests/responses
    - Log errors and exceptions
    - Track performance metrics
    - Auto-inject internal router for SDK management
    """
    
    def __init__(
        self,
        api_key: str,
        environment: str = "production",
        log_file: str = "nexarch_telemetry.json",
        observation_duration: str = "3h",
        sampling_rate: float = 1.0,
        enable_local_logs: bool = True
    ):
        """
        Initialize Nexarch SDK.
        
        Args:
            api_key: Your Nexarch API key from the platform
            environment: Environment name (production, staging, development)
            log_file: Local JSON log file path
            observation_duration: How long to observe (e.g., "3h", "2h")
            sampling_rate: Fraction of requests to sample (0.0 to 1.0)
            enable_local_logs: Whether to write logs locally
        """
        self.api_key = api_key
        self.environment = environment
        self.log_file = log_file
        self.observation_duration = observation_duration
        self.sampling_rate = sampling_rate
        self.enable_local_logs = enable_local_logs
        
        # Initialize logger
        NexarchLogger.initialize(
            log_file=log_file,
            enable_local_logs=enable_local_logs
        )
    
    def init(self, app: FastAPI) -> None:
        """
        Initialize Nexarch SDK with a FastAPI application.
        
        This method:
        1. Attaches middleware to capture all requests/responses
        2. Auto-injects internal router for SDK endpoints
        3. Starts local telemetry collection
        
        Args:
            app: FastAPI application instance
            
        Example:
            ```python
            from fastapi import FastAPI
            from nexarch import NexarchSDK
            
            app = FastAPI()
            sdk = NexarchSDK(api_key="your_api_key")
            sdk.init(app)
            ```
        """
        # Attach middleware for observability
        app.add_middleware(
            NexarchMiddleware,
            api_key=self.api_key,
            environment=self.environment,
            sampling_rate=self.sampling_rate
        )
        
        # Auto-inject internal router
        app.include_router(
            nexarch_router,
            prefix="/__nexarch",
            tags=["Nexarch Internal"],
            include_in_schema=False  # Hide from OpenAPI docs
        )
        
        print(f"✓ Nexarch SDK initialized successfully")
        print(f"  Environment: {self.environment}")
        print(f"  Local logs: {self.log_file if self.enable_local_logs else 'disabled'}")
        print(f"  Internal endpoints: /__nexarch/*")
    
    @staticmethod
    def start(app: FastAPI, api_key: str, **kwargs) -> None:
        """
        Convenience method to initialize SDK in one line.
        
        Example:
            ```python
            from fastapi import FastAPI
            from nexarch import NexarchSDK
            
            app = FastAPI()
            NexarchSDK.start(app, api_key="your_api_key")
            ```
        """
        sdk = NexarchSDK(api_key=api_key, **kwargs)
        sdk.init(app)
