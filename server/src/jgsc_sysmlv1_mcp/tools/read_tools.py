# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary

"""Read tools for the SysML v1 MCP bridge."""

from __future__ import annotations

from typing import Any

from magic_mcp_core.domain_server import DomainServer


def register_read_v1_tools(server: DomainServer) -> None:
    """Register v1 read/explore tools."""

    @server.mcp.tool()
    async def get_element(element_id: str) -> dict[str, Any]:
        """Retrieve a single SysML v1 element by its local ID. Returns type, name, and owner ID."""
        return await server.client.get_element(element_id)

    @server.mcp.tool()
    async def find_by_name(name: str) -> dict[str, Any]:
        """Find all elements whose name contains the given string. Returns list of matches."""
        return await server.client.find_by_name(name)

    @server.mcp.tool()
    async def find_by_type(type_name: str) -> dict[str, Any]:
        """Find all elements matching a SysML v1 type name (e.g. Block, Requirement, FlowPort)."""
        return await server.client.find_by_type(type_name)

    @server.mcp.tool()
    async def find_by_qualified_name(qualified_name: str) -> dict[str, Any]:
        """Find an element by its fully-qualified name (e.g. 'Model::Package::Block')."""
        return await server.client.find_by_qualified_name(qualified_name)

    @server.mcp.tool()
    async def get_qualified_name(element_id: str) -> dict[str, Any]:
        """Return the fully-qualified name of an element."""
        return await server.client.get_qualified_name(element_id)

    @server.mcp.tool()
    async def get_root_package() -> dict[str, Any]:
        """Return the root model package of the open project."""
        return await server.client.get_root_package()

    @server.mcp.tool()
    async def list_children(parent_id: str) -> dict[str, Any]:
        """List direct children of an element. Returns list with id, name, type."""
        return await server.client.list_children(parent_id)

    @server.mcp.tool()
    async def walk_tree(root_id: str, max_depth: int = 5, max_elements: int = 200) -> dict[str, Any]:
        """Walk the containment tree from root_id. Returns nested tree structure."""
        return await server.client.walk_tree(root_id, max_depth=max_depth, max_elements=max_elements)

    @server.mcp.tool()
    async def search(query: str, max_results: int = 50) -> dict[str, Any]:
        """Full-text search across element names."""
        return await server.client.search(query, max_results=max_results)

    @server.mcp.tool()
    async def describe_element(element_id: str) -> dict[str, Any]:
        """Return rich description of an element including stereotypes and tagged values."""
        return await server.client.describe_element(element_id)

    @server.mcp.tool()
    async def get_element_structure(element_id: str) -> dict[str, Any]:
        """Return the structural hierarchy under an element (parts, ports, properties)."""
        return await server.client.get_element_structure(element_id)

    @server.mcp.tool()
    async def get_relationships(element_id: str) -> dict[str, Any]:
        """Return all relationships involving an element."""
        return await server.client.get_relationships(element_id)

    @server.mcp.tool()
    async def get_ports(element_id: str) -> dict[str, Any]:
        """Return all ports owned by an element."""
        return await server.client.get_ports(element_id)

    @server.mcp.tool()
    async def get_allocations(element_id: str) -> dict[str, Any]:
        """List all Allocate relationships from and to an element."""
        return await server.client.get_allocations(element_id)

    @server.mcp.tool()
    async def list_applied_stereotypes(element_id: str) -> dict[str, Any]:
        """List all stereotypes applied to an element."""
        return await server.client.list_applied_stereotypes(element_id)

    @server.mcp.tool()
    async def find_unit(name: str) -> dict[str, Any]:
        """Search the model for SysML Unit-stereotyped elements by name substring."""
        return await server.client.find_unit(name)

    @server.mcp.tool()
    async def find_quantity_kind(name: str) -> dict[str, Any]:
        """Search the model for SysML QuantityKind-stereotyped elements by name substring."""
        return await server.client.find_quantity_kind(name)

