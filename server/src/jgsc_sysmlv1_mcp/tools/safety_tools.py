# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Safety/write-gate tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_safety_v1_tools(server: DomainServer) -> None:
    """Register v1 safety/write-gate tools."""

    @server.mcp.tool()
    async def enable_writes(secret: str) -> dict[str, Any]:
        """Enable write operations. Requires the write secret."""
        return await server.client.enable_writes(secret)

    @server.mcp.tool()
    async def disable_writes(secret: str) -> dict[str, Any]:
        """Disable write operations. Requires the write secret."""
        return await server.client.disable_writes(secret)

    @server.mcp.tool()
    async def enable_dangerous_writes(secret: str) -> dict[str, Any]:
        """Enable dangerous write operations (delete, structural changes). Requires the write secret."""
        return await server.client.enable_dangerous_writes(secret)

    @server.mcp.tool()
    async def enable_dev_mode(secret: str) -> dict[str, Any]:
        """Enable developer mode. Requires the write secret."""
        return await server.client.enable_dev_mode(secret)

    @server.mcp.tool()
    async def disable_dev_mode(secret: str) -> dict[str, Any]:
        """Disable developer mode. Requires the write secret."""
        return await server.client.disable_dev_mode(secret)
