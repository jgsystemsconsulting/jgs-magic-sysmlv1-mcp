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
        """Run built-in model validation and return structural violations.

        Spelling suite violations (Cameo spell-checker noise) are separated into
        a ``spelling`` array and excluded from the ``violations`` count so that
        the 0-errors gate only reflects structural/semantic issues.
        """
        return await server.client.validate_model()

    @server.mcp.tool()
    async def check_requirement_coverage(
        scope: str = "authored",
    ) -> dict[str, Any]:
        """Return coverage statistics for requirements.

        ``scope`` controls which requirements are counted:
        - ``"authored"`` (default) — only user-model requirements, excluding SysML
          library and profile elements that inflate the denominator.
        - ``"all"`` — every requirement in the model (legacy behaviour).

        New fields: ``tracedCoverage`` (Satisfy + Refine + DeriveReqt + Verify),
        ``orphans`` (requirements with zero traceability links). Legacy fields
        ``total``, ``satisfied``, ``unsatisfied``, ``satisfyCoverage`` are preserved.
        """
        return await server.client.check_requirement_coverage(scope=scope)

    @server.mcp.tool()
    async def check_documentation_coverage(
        scope: str = "authored",
    ) -> dict[str, Any]:
        """Return the fraction of named elements that have documentation set.

        ``scope`` controls the denominator:
        - ``"authored"`` (default) — only user-model elements; avoids the ~25%
          ceiling caused by ~1840 undocumentable SysML library elements.
        - ``"all"`` — every named element (legacy behaviour).

        ``coverage`` reflects the scoped fraction; ``coverageModelWide`` is always
        reported for reference.
        """
        return await server.client.check_documentation_coverage(scope=scope)

    @server.mcp.tool()
    async def check_naming_conventions(
        scope: str = "authored",
        allowed_patterns: str = "",
    ) -> dict[str, Any]:
        """Return elements that violate UML naming conventions.

        ``scope`` controls which elements are checked:
        - ``"authored"`` (default) — user-model only; suppresses ~85 library
          internals (``base_*``, ``extension_*``, ``A_*``).
        - ``"all"`` — every element.

        ``allowed_patterns`` is an optional comma-separated list of regex patterns
        that exempt names from the default rules. Use this to allow requirement-ID
        schemes such as ``^[A-Z]{2,}-\\d+$`` or Magic Grid label patterns like
        ``^.+ Scenario$``.
        """
        return await server.client.check_naming_conventions(
            scope=scope, allowed_patterns=allowed_patterns
        )

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
