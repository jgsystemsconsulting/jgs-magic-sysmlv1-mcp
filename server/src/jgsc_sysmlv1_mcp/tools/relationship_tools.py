# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Relationship tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_relationship_v1_tools(server: DomainServer) -> None:
    """Register v1 relationship tools."""

    @server.mcp.tool()
    async def add_satisfy(satisfying_element_id: str, requirement_id: str) -> dict[str, Any]:
        """Create a Satisfy relationship from a satisfying element to a requirement."""
        return await server.client.add_satisfy(satisfying_element_id, requirement_id)

    @server.mcp.tool()
    async def add_verify(verifying_element_id: str, requirement_id: str) -> dict[str, Any]:
        """Create a Verify relationship from a verifying element to a requirement."""
        return await server.client.add_verify(verifying_element_id, requirement_id)

    @server.mcp.tool()
    async def add_derive(derived_req_id: str, source_req_id: str) -> dict[str, Any]:
        """Create a DeriveReqt relationship between two requirements."""
        return await server.client.add_derive(derived_req_id, source_req_id)

    @server.mcp.tool()
    async def set_connection_ends(connection_id: str, source_end_id: str, target_end_id: str) -> dict[str, Any]:
        """Set source and target ConnectorEnd roles on a Connector."""
        return await server.client.set_connection_ends(connection_id, source_end_id, target_end_id)

    @server.mcp.tool()
    async def add_dependency(client_id: str, supplier_id: str, name: str = "") -> dict[str, Any]:
        """Create a UML Dependency between a client and supplier element."""
        return await server.client.add_dependency(client_id, supplier_id, name=name)
