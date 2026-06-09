# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary

"""Lifecycle and safety tools for the SysML v1 MCP bridge."""

from typing import Any

from magic_mcp_core.domain_server import DomainServer


def register_lifecycle_v1_tools(server: DomainServer) -> None:
    """Register ping, get_safety_state, and get_licence tools."""

    @server.mcp.tool()
    async def ping() -> dict[str, Any]:
        """Liveness probe. Calls the SysML v1 bridge plugin and returns its build metadata."""
        return await server.client.ping()

    @server.mcp.tool()
    async def get_safety_state() -> dict[str, Any]:
        """Return the current safety tier (READ, WRITE, or DANGEROUS) plus dev mode status."""
        return await server.client.get_safety_state()

    @server.mcp.tool()
    async def get_licence() -> dict[str, Any]:
        """Return the current licence status: tier, customer, expiry, validity."""
        return await server.client.get_licence()

    @server.mcp.tool()
    async def save_project(comment: str = "") -> dict[str, Any]:
        """Save the current Cameo project. Pass an optional comment for audit log."""
        return await server.client.save_project(comment=comment)

    @server.mcp.tool()
    async def get_edit_history(max_entries: int = 20) -> dict[str, Any]:
        """Return recent edit history (undo stack) from the open project."""
        return await server.client.get_edit_history(max_entries=max_entries)

    @server.mcp.tool()
    async def undo() -> dict[str, Any]:
        """Undo the last model edit."""
        return await server.client.undo()

    @server.mcp.tool()
    async def redo() -> dict[str, Any]:
        """Redo the last undone model edit."""
        return await server.client.redo()
