# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""SysML v1 vocabulary wrappers — thin aliases over generic HttpClient methods."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_v1_vocabulary_tools(server: DomainServer) -> None:
    """Register SysML v1 vocabulary convenience tools."""

    @server.mcp.tool()
    async def create_block(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML v1 Block under parent_id."""
        return await server.client.create_element(parent_id, name, "Block")

    @server.mcp.tool()
    async def create_part_property(parent_id: str, name: str) -> dict[str, Any]:
        """Create a PartProperty (typed composite part) under a Block."""
        return await server.client.create_element(parent_id, name, "PartProperty")

    @server.mcp.tool()
    async def create_value_property(parent_id: str, name: str) -> dict[str, Any]:
        """Create a ValueProperty (scalar attribute) under a Block."""
        return await server.client.create_element(parent_id, name, "ValueProperty")

    @server.mcp.tool()
    async def create_reference_property(parent_id: str, name: str) -> dict[str, Any]:
        """Create a ReferenceProperty under a Block."""
        return await server.client.create_element(parent_id, name, "ReferenceProperty")

    @server.mcp.tool()
    async def create_interface_block(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML InterfaceBlock under parent_id."""
        return await server.client.create_element(parent_id, name, "InterfaceBlock")

    @server.mcp.tool()
    async def create_value_type(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML ValueType under parent_id."""
        return await server.client.create_element(parent_id, name, "ValueType")

    @server.mcp.tool()
    async def create_constraint_block(parent_id: str, name: str) -> dict[str, Any]:
        """Create a SysML ConstraintBlock under parent_id."""
        return await server.client.create_element(parent_id, name, "ConstraintBlock")

    @server.mcp.tool()
    async def create_use_case(parent_id: str, name: str) -> dict[str, Any]:
        """Create a UseCase element under parent_id."""
        return await server.client.create_element(parent_id, name, "UseCase")

    @server.mcp.tool()
    async def create_actor(parent_id: str, name: str) -> dict[str, Any]:
        """Create an Actor element under parent_id."""
        return await server.client.create_element(parent_id, name, "Actor")
