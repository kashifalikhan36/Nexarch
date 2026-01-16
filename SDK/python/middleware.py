"""Nexarch Middleware"""
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
from .tracing import set_trace_context, clear_trace_context, Span, Sampler
from .queue import get_log_queue


class NexarchMiddleware(BaseHTTPMiddleware):
    """Captures all requests"""
    
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
        self.sampler = Sampler(sampling_rate)
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        """Intercept and log"""
        
        # Skip internal
        if request.url.path.startswith("/__nexarch"):
            return await call_next(request)
        
        # Sampling decision
        if not self.sampler.should_sample():
            return await call_next(request)
        
        # Generate IDs
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        # Set context
        set_trace_context(trace_id, span_id)
        
        # Create span
        span = Span.create_server_span(
            trace_id=trace_id,
            span_id=span_id,
            service=self.environment,
            operation=f"{request.method} {request.url.path}"
        )
        span.tags = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params)
        }
        
        start_time = time.time()
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Finish span
            span.finish(status_code=response.status_code)
            
            # Enqueue span
            get_log_queue().enqueue({
                "type": "span",
                "timestamp": timestamp,
                "data": span.to_dict()
            })
            
            # Legacy format
            latency_ms = round((time.time() - start_time) * 1000, 2)
            legacy_span = SpanData(
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
                downstream=[]
            )
            
            NexarchLogger.log_span(legacy_span)
            
            return response
        
        except Exception as e:
            # Finish span with error
            span.finish(status_code=500, error=str(e))
            
            # Enqueue span
            get_log_queue().enqueue({
                "type": "span",
                "timestamp": timestamp,
                "data": span.to_dict()
            })
            
            # Log error
            latency_ms = round((time.time() - start_time) * 1000, 2)
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
            
            NexarchLogger.log_error(error_data)
            
            # Legacy span
            legacy_span = SpanData(
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
            
            NexarchLogger.log_span(legacy_span)
            
            raise
        
        finally:
            # Clear context
            clear_trace_context()
