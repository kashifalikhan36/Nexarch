"""Nexarch SDK Client"""
from fastapi import FastAPI
from .middleware import NexarchMiddleware
from .router import nexarch_router
from .loggers import NexarchLogger
from .exporters import LocalJSONExporter, HttpExporter
from .queue import get_log_queue
from .instrumentation import patch_requests, patch_httpx
from typing import Optional


class NexarchSDK:
    def __init__(
        self,
        api_key: str,
        environment: str = "production",
        log_file: str = "nexarch_telemetry.json",
        observation_duration: str = "3h",
        sampling_rate: float = 1.0,
        enable_local_logs: bool = True,
        enable_http_export: bool = False,
        http_endpoint: Optional[str] = None
    ):
        self.api_key = api_key
        self.environment = environment
        self.log_file = log_file
        self.observation_duration = observation_duration
        self.sampling_rate = sampling_rate
        self.enable_local_logs = enable_local_logs
        self.enable_http_export = enable_http_export
        self.http_endpoint = http_endpoint
        
        # Init logger
        NexarchLogger.initialize(
            log_file=log_file,
            enable_local_logs=enable_local_logs
        )
        
        # Setup exporter
        if enable_http_export and http_endpoint:
            exporter = HttpExporter(http_endpoint, api_key)
        else:
            exporter = LocalJSONExporter(log_file)
        
        queue = get_log_queue()
        queue.set_exporter(exporter)
        queue.start()
        
        patch_requests()
        patch_httpx()
    
    def init(self, app: FastAPI) -> None:
        """Attach SDK to FastAPI"""
        
        # Add middleware
        app.add_middleware(
            NexarchMiddleware,
            api_key=self.api_key,
            environment=self.environment,
            sampling_rate=self.sampling_rate
        )
        
        # Auto-inject router
        app.include_router(
            nexarch_router,
            prefix="/__nexarch",
            tags=["Nexarch Internal"],
            include_in_schema=False
        )
    
    @staticmethod
    def start(app: FastAPI, api_key: str, **kwargs) -> None:
        """One-line init"""
        sdk = NexarchSDK(api_key=api_key, **kwargs)
        sdk.init(app)
