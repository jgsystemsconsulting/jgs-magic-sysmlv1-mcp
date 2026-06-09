# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Batch session tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_batch_v1_tools(server: DomainServer) -> None:
    """Register v1 batch tools."""

    @server.mcp.tool()
    async def begin_batch() -> dict[str, Any]:
        """Open a batch session. All write operations within the batch are committed atomically when commit_batch fires."""
        return await server.client.begin_batch()

    @server.mcp.tool()
    async def commit_batch(batch_id: str) -> dict[str, Any]:
        """Commit all queued operations in the given batch session."""
        return await server.client.commit_batch(batch_id)

    @server.mcp.tool()
    async def abort_batch(batch_id: str) -> dict[str, Any]:
        """Roll back all queued operations in the given batch session."""
        return await server.client.abort_batch(batch_id)
