from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AzureConfig:
    tenant_id: str | None
    client_id: str | None
    client_secret: str | None
    subscription_id: str | None
    log_analytics_workspace_id: str | None

    @property
    def is_configured(self) -> bool:
        return all(
            [
                self.tenant_id,
                self.client_id,
                self.client_secret,
                self.subscription_id,
                self.log_analytics_workspace_id,
            ]
        )


def _get_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def load_azure_config(*, strict: bool = False) -> AzureConfig:
    """
    Load Azure integration settings from environment variables.

    In Phase 2 (scaffolding), we support "mock mode" where these values may be absent.
    If strict=True, missing values raise ValueError.
    """

    cfg = AzureConfig(
        tenant_id=_get_env("AZURE_TENANT_ID"),
        client_id=_get_env("AZURE_CLIENT_ID"),
        client_secret=_get_env("AZURE_CLIENT_SECRET"),
        subscription_id=_get_env("AZURE_SUBSCRIPTION_ID"),
        log_analytics_workspace_id=_get_env("LOG_ANALYTICS_WORKSPACE_ID"),
    )

    if strict and not cfg.is_configured:
        missing = []
        if not cfg.tenant_id:
            missing.append("AZURE_TENANT_ID")
        if not cfg.client_id:
            missing.append("AZURE_CLIENT_ID")
        if not cfg.client_secret:
            missing.append("AZURE_CLIENT_SECRET")
        if not cfg.subscription_id:
            missing.append("AZURE_SUBSCRIPTION_ID")
        if not cfg.log_analytics_workspace_id:
            missing.append("LOG_ANALYTICS_WORKSPACE_ID")
        raise ValueError(f"Missing required Azure environment variables: {', '.join(missing)}")

    return cfg

