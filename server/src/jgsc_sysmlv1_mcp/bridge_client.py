# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""V1-specific facade over HttpClient.

Tool modules should import V1BridgeClient rather than HttpClient directly.
"""
from __future__ import annotations

from magic_mcp_core.config import DomainConfig
from jgsc_sysmlv1_mcp.http_client import HttpClient


class V1BridgeClient(HttpClient):
    """HttpClient pre-configured for the SysML v1 bridge."""

    def __init__(self, config: DomainConfig) -> None:
        super().__init__(
            config.endpoint,
            token=config.bearer_token,
            token_file=config.bearer_token_path,
        )
