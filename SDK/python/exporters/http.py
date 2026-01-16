"""HTTP exporter stub"""
from typing import Dict, Any
from .base import Exporter


class HttpExporter(Exporter):
    """HTTP exporter (stub)"""
    
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
    
    def export(self, data: Dict[str, Any]):
        """Export via HTTP"""
        # TODO: Implement
        pass
    
    def close(self):
        """Close"""
        pass
