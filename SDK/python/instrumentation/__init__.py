"""Instrumentation package"""
from .requests_patch import patch_requests
from .httpx_patch import patch_httpx

__all__ = ['patch_requests', 'patch_httpx']
