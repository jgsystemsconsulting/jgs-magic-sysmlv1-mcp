# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Diagram tools for the SysML v1 MCP bridge."""
from __future__ import annotations
from typing import Any
from magic_mcp_core.domain_server import DomainServer


def register_diagram_v1_tools(server: DomainServer) -> None:
    """Register v1 diagram tools."""

    @server.mcp.tool()
    async def create_diagram(parent_id: str, name: str, kind: str) -> dict[str, Any]:
        """Create a SysML v1 diagram. Kinds: BDD, IBD, Parametric, Requirement, Activity, StateMachine, UseCase, Package, Sequence."""
        return await server.client.create_diagram(parent_id, name, kind)

    @server.mcp.tool()
    async def list_diagrams(parent_id: str) -> dict[str, Any]:
        """List diagrams owned by a package or element."""
        return await server.client.list_diagrams(parent_id)

    @server.mcp.tool()
    async def list_diagram_kinds() -> dict[str, Any]:
        """Return supported diagram kinds for SysML v1."""
        return await server.client.list_diagram_kinds()

    @server.mcp.tool()
    async def add_symbol(diagram_id: str, element_id: str) -> dict[str, Any]:
        """Add an element symbol to a diagram. Phase B stub."""
        return await server.client.add_symbol(diagram_id, element_id)

    @server.mcp.tool()
    async def remove_symbol(diagram_id: str, element_id: str) -> dict[str, Any]:
        """Remove an element symbol from a diagram. Phase B stub."""
        return await server.client.remove_symbol(diagram_id, element_id)

    @server.mcp.tool()
    async def populate_diagram(diagram_id: str, element_ids: list[str]) -> dict[str, Any]:
        """Add multiple element symbols to a diagram. Phase B stub."""
        return await server.client.populate_diagram(diagram_id, element_ids)

    @server.mcp.tool()
    async def auto_layout_diagram(diagram_id: str) -> dict[str, Any]:
        """Apply Cameo's automatic layout to a diagram."""
        return await server.client.auto_layout_diagram(diagram_id)

    @server.mcp.tool()
    async def list_diagram_symbols(diagram_id: str) -> dict[str, Any]:
        """List all symbols currently in a diagram. Phase B stub."""
        return await server.client.list_diagram_symbols(diagram_id)

    @server.mcp.tool()
    async def export_diagram_image(diagram_id: str) -> list:
        """Export a diagram as a JPEG image (base64 encoded, max 1024px).

        Returns MCP ImageContent containing the resized diagram image.
        The image is re-encoded as JPEG for compatibility with the Claude API.
        """
        import json
        from mcp.types import ImageContent, TextContent
        from magic_mcp_core.errors import BridgeError
        from magic_mcp_core.image_utils import ImageDecodeError, shrink_and_encode

        try:
            result = await server.client.export_diagram_image(diagram_id)
        except (BridgeError, RuntimeError) as be:
            return [TextContent(type="text", text=json.dumps({"error": str(be)}))]

        b64_png = result.get("base64")
        if not b64_png:
            return [TextContent(type="text", text=json.dumps({"error": "bridge returned no image data"}))]

        try:
            b64_jpeg, mime = shrink_and_encode(b64_png)
        except ImageDecodeError as exc:
            return [TextContent(type="text", text=json.dumps({"error": f"image processing failed: {exc}"}))]

        return [ImageContent(type="image", data=b64_jpeg, mimeType=mime)]

    @server.mcp.tool()
    async def list_layout_styles() -> dict[str, Any]:
        """Return supported diagram layout styles."""
        return await server.client.list_layout_styles()

    @server.mcp.tool()
    async def compare_layout_styles(diagram_id: str) -> dict[str, Any]:
        """Compare available layout styles for a diagram. Phase B stub."""
        return await server.client.compare_layout_styles(diagram_id)

    @server.mcp.tool()
    async def apply_custom_layout(diagram_id: str, style: str) -> dict[str, Any]:
        """Apply a named layout style to a diagram."""
        return await server.client.apply_custom_layout(diagram_id, style)

    @server.mcp.tool()
    async def move_symbol(diagram_id: str, element_id: str, x: int, y: int) -> dict[str, Any]:
        """Move a symbol to specific coordinates. Phase B stub."""
        return await server.client.move_symbol(diagram_id, element_id, x, y)

    @server.mcp.tool()
    async def resize_symbol(diagram_id: str, element_id: str, width: int, height: int) -> dict[str, Any]:
        """Resize a symbol in a diagram. Phase B stub."""
        return await server.client.resize_symbol(diagram_id, element_id, width, height)

    @server.mcp.tool()
    async def set_symbol_style(diagram_id: str, element_id: str, style_properties: str) -> dict[str, Any]:
        """Set visual style properties on a diagram symbol. Phase B stub."""
        return await server.client.set_symbol_style(diagram_id, element_id, style_properties)

    @server.mcp.tool()
    async def set_compartment_visibility(diagram_id: str, element_id: str, compartment: str, visible: bool) -> dict[str, Any]:
        """Show or hide a compartment on a symbol. Phase B stub."""
        return await server.client.set_compartment_visibility(diagram_id, element_id, compartment, visible)

    @server.mcp.tool()
    async def add_path(diagram_id: str, relationship_id: str) -> dict[str, Any]:
        """Add a relationship path to a diagram. Phase B stub."""
        return await server.client.add_path(diagram_id, relationship_id)

    @server.mcp.tool()
    async def route_path(diagram_id: str, relationship_id: str, routing_style: str) -> dict[str, Any]:
        """Set routing style for a relationship path. Phase B stub."""
        return await server.client.route_path(diagram_id, relationship_id, routing_style)

    @server.mcp.tool()
    async def add_diagram_note(diagram_id: str, text: str, x: int = 0, y: int = 0) -> dict[str, Any]:
        """Add a text note to a diagram. Phase B stub."""
        return await server.client.add_diagram_note(diagram_id, text, x, y)
