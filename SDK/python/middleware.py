"""
Nexarch Middleware - Captures all HTTP requests/responses and errors
"""
import time
import traceback
import uuid
from datetime import datetime
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from .loggers import NexarchLogger
from .models import SpanData, ErrorData


class NexarchMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures telemetry data for every request.
    
    Captures:
    - Request metadata (method, path, headers)
    - Response metadata (status code, latency)
    - Errors and exceptions with full tracebacks
    - Downstream dependency calls (future)
    """
    
    def __init__(
        self,
        app,
        api_key: str,
        environment: str = "production",
        sampling_rate: float = 1.0
    ):
        super().__init__(app)
        self.api_key = api_key
        self.environment = environment
        self.sampling_rate = sampling_rate
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        """
        Intercept every request and log telemetry.
        """
        # Generate trace ID for this request
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        # Skip internal Nexarch endpoints
        if request.url.path.startswith("/__nexarch"):
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            # Create span data for successful request
            span = SpanData(
                trace_id=trace_id,
                span_id=span_id,
                parent_id=None,
                service=self.environment,
                operation=f"{request.method} {request.url.path}",
                kind="server",
                timestamp=timestamp,
                latency_ms=latency_ms,
                status_code=response.status_code,
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
                status="ok" if response.status_code < 400 else "error",
                error=None,
                downstream=[]  # Will be populated by dependency tracking
            )
            
            # Log the span
            NexarchLogger.log_span(span)
            
            return response
        
        except Exception as e:
            # Calculate latency even for errors
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            # Create error data
            error_data = ErrorData(
                trace_id=trace_id,
                span_id=span_id,
                timestamp=timestamp,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc(),
                service=self.environment,
                operation=f"{request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params)
            )
            
            # Log the error
            NexarchLogger.log_error(error_data)
            
            # Also create a failed span
            span = SpanData(
                trace_id=trace_id,
                span_id=span_id,
                parent_id=None,
                service=self.environment,
                operation=f"{request.method} {request.url.path}",
                kind="server",
                timestamp=timestamp,
                latency_ms=latency_ms,
                status_code=500,
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
                status="error",
                error=str(e),
                downstream=[]
            )
            
            NexarchLogger.log_span(span)
            
            # Re-raise the exception
            raise
