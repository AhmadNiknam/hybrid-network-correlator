"""
Integration scaffolding modules.

Phase 2 introduces read-only integration surfaces (still mock-first).
"""

from .azure_client import AzureClient
from .config import AzureConfig, load_azure_config
from . import kql_queries

__all__ = [
    "AzureClient",
    "AzureConfig",
    "load_azure_config",
    "kql_queries",
]

