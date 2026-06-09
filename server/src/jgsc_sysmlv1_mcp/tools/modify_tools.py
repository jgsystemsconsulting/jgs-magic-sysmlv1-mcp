# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Modify tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_modify_v1_tools(server: DomainServer) -> None:
    """Register v1 modify/update tools."""

    @server.mcp.tool()
    async def rename_element(element_id: str, new_name: str) -> dict[str, Any]:
        """Rename a SysML v1 element."""
        return await server.client.rename_element(element_id, new_name)

    @server.mcp.tool()
    async def set_documentation(element_id: str, documentation: str) -> dict[str, Any]:
        """Set the documentation (owned Comment body) of an element."""
        return await server.client.set_documentation(element_id, documentation)

    @server.mcp.tool()
    async def delete_element(element_id: str) -> dict[str, Any]:
        """Permanently delete an element from the model."""
        return await server.client.delete_element(element_id)

    @server.mcp.tool()
    async def move_element(element_id: str, new_parent_id: str) -> dict[str, Any]:
        """Move an element to a new parent (re-owner)."""
        return await server.client.move_element(element_id, new_parent_id)

    @server.mcp.tool()
    async def set_type(feature_id: str, type_id: str) -> dict[str, Any]:
        """Set the type of a TypedElement (Property, Parameter, Port, etc.)."""
        return await server.client.set_type(feature_id, type_id)

    @server.mcp.tool()
    async def set_multiplicity(feature_id: str, lower: int, upper: int) -> dict[str, Any]:
        """Set multiplicity bounds on a MultiplicityElement (Property, etc.). Use -1 for upper=*."""
        return await server.client.set_multiplicity(feature_id, lower, upper)

    @server.mcp.tool()
    async def set_value(feature_id: str, value: str) -> dict[str, Any]:
        """Set the default value of a Property as a LiteralString."""
        return await server.client.set_value(feature_id, value)

    @server.mcp.tool()
    async def set_constraint(parent_id: str, expression: str, name: str = "", language: str = "", subject_ids: list[str] | None = None) -> dict[str, Any]:
        """Create a Constraint with an OpaqueExpression body on parent_id."""
        return await server.client.set_constraint(parent_id, expression, name=name, language=language, subject_ids=subject_ids)

    @server.mcp.tool()
    async def set_property(element_id: str, property_name: str, value: str) -> dict[str, Any]:
        """Set a tagged value (stereotype property) on an element via TagsHelper."""
        return await server.client.set_property(element_id, property_name, value)

    @server.mcp.tool()
    async def apply_stereotype(element_id: str, stereotype_qn: str) -> dict[str, Any]:
        """Apply a stereotype to an element by its qualified name."""
        return await server.client.apply_stereotype(element_id, stereotype_qn)

    @server.mcp.tool()
    async def remove_stereotype(element_id: str, stereotype_qn: str) -> dict[str, Any]:
        """Remove a stereotype from an element by its qualified name."""
        return await server.client.remove_stereotype(element_id, stereotype_qn)

    @server.mcp.tool()
    async def set_requirement_id(element_id: str, req_id: str) -> dict[str, Any]:
        """Set the SysML requirement ID tagged value on a Requirement element."""
        return await server.client.set_requirement_id(element_id, req_id)

    @server.mcp.tool()
    async def set_requirement_text(element_id: str, text: str) -> dict[str, Any]:
        """Set the normative requirement text on a Requirement element."""
        return await server.client.set_requirement_text(element_id, text)

    @server.mcp.tool()
    async def set_value_type_unit(element_id: str, unit_id: str) -> dict[str, Any]:
        """Set the unit of a SysML ValueType element."""
        return await server.client.set_value_type_unit(element_id, unit_id)

    @server.mcp.tool()
    async def set_flow_direction(element_id: str, direction: str) -> dict[str, Any]:
        """Set the direction of a Parameter. Valid values: IN, OUT, INOUT, RETURN."""
        return await server.client.set_flow_direction(element_id, direction)
