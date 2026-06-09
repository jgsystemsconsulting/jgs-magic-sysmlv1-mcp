# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
#
# This file is part of magic-development, proprietary software of
# JG Systems Consulting Ltd. Unauthorized copying, modification,
# distribution, reverse engineering, or use of this file, via any
# medium, is strictly prohibited without a valid written licence
# from JG Systems Consulting Ltd. See LICENSE at the repository
# root for the full terms.
#
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary

"""Shared Cameo MCP infrastructure used by all per-domain plugin servers (v2, v1, future).

Hosts the FastMCP ``DomainServer`` base class, the per-domain
``DomainConfig``, the ``BridgeHttpClient`` (also re-exported as
``HttpClient``), the legacy ``BridgeConfig`` token+port loader, and the
RFC 7807 error type hierarchy.

Introduced in Plan 3 Task 0 (Phase 2 Stream A — v2 Python → FastMCP
migration). v2 tools and ``server.py`` import infrastructure from here;
the v1 plugin (Plan 4 Stream B) will do the same.
"""
from __future__ import annotations

from .config import BridgeConfig, ConfigError, DomainConfig
from .domain_server import DomainServer
from .errors import (
    BridgeError,
    NotFoundError,
    PluginNotRunningError,
    TierDeniedError,
    UnauthorizedError,
    problem_to_exception,
)
from .http_client import BridgeHttpClient

#: Spec-level alias for :class:`BridgeHttpClient`. Future generic clients
#: that consume :class:`DomainConfig` directly may replace this; the alias
#: lets ``from magic_mcp_core import HttpClient`` resolve today.
HttpClient = BridgeHttpClient

__all__ = [
    "BridgeConfig",
    "BridgeError",
    "BridgeHttpClient",
    "ConfigError",
    "DomainConfig",
    "DomainServer",
    "HttpClient",
    "NotFoundError",
    "PluginNotRunningError",
    "TierDeniedError",
    "UnauthorizedError",
    "problem_to_exception",
]
