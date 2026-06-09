# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Quality and traceability tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_quality_v1_tools(server: DomainServer) -> None:
    """Register v1 quality/traceability tools."""

    @server.mcp.tool()
    async def impact_analysis(element_id: str) -> dict[str, Any]:
        """Return elements that use or are used by the given element."""
        return await server.client.impact_analysis(element_id)

    @server.mcp.tool()
    async def validate_model() -> dict[str, Any]:
        """Run built-in model validation and return any rule violations."""
        return await server.client.validate_model()

    @server.mcp.tool()
    async def check_requirement_coverage() -> dict[str, Any]:
        """Return coverage statistics: how many requirements are satisfied/verified."""
        return await server.client.check_requirement_coverage()

    @server.mcp.tool()
    async def check_documentation_coverage() -> dict[str, Any]:
        """Return fraction of named elements that have documentation set."""
        return await server.client.check_documentation_coverage()

    @server.mcp.tool()
    async def check_naming_conventions() -> dict[str, Any]:
        """Return elements that violate UpperCamelCase / lowerCamelCase conventions."""
        return await server.client.check_naming_conventions()

    @server.mcp.tool()
    async def find_unused_types() -> dict[str, Any]:
        """Return classifiers that are not used as a type anywhere in the model."""
        return await server.client.find_unused_types()

    @server.mcp.tool()
    async def find_duplicates() -> dict[str, Any]:
        """Return elements that share the same type+name combination."""
        return await server.client.find_duplicates()

    @server.mcp.tool()
    async def export_requirements_matrix() -> dict[str, Any]:
        """Return a full requirements traceability matrix with satisfy/verify links."""
        return await server.client.export_requirements_matrix()

    @server.mcp.tool()
    async def trace_requirement(requirement_id: str) -> dict[str, Any]:
        """Return full traceability chain for one requirement (derive, satisfy, verify)."""
        return await server.client.trace_requirement(requirement_id)

    @server.mcp.tool()
    async def generate_model_summary() -> dict[str, Any]:
        """Return a high-level summary of model element counts and coverage."""
        return await server.client.generate_model_summary()

    @server.mcp.tool()
    async def get_model_metrics() -> dict[str, Any]:
        """Return raw element counts broken down by UML/SysML type."""
        return await server.client.get_model_metrics()
