# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
"""FastMCP base class for per-domain Cameo MCP servers.

Introduced for Plan 3 (Phase 2 Stream A â€” v2 Python â†’ FastMCP migration).
``DomainServer`` is a thin wrapper that owns the ``FastMCP`` instance, the
:class:`DomainConfig`, and a placeholder for the domain-specific HTTP client.
Per-domain subclasses (or composition wrappers) register tools via the
``@self.mcp.tool(...)`` decorator.

This file is added in Plan 3 Task 0 but **not yet wired into ``server.py``**.
Task 1 cuts ``jgs_sysmlv2_mcp.server`` over from ``mcp.server.Server`` to
``DomainServer``; Plan 4 (Stream B) reuses ``DomainServer`` for the v1 plugin.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import DomainConfig


class DomainServer:
    """Base class for any Cameo MCP server (v2, v1, future).

    Owns the FastMCP instance and the :class:`DomainConfig`. Per-domain
    subclasses register their tools via ``@self.mcp.tool()`` on the
    ``self.mcp`` attribute.

    The HTTP client is intentionally *not* constructed here â€” different
    domains use different client signatures. The v2 plugin uses
    :class:`magic_mcp_core.BridgeHttpClient` (loaded from
    :class:`BridgeConfig`); future domains may use a generic
    :class:`HttpClient` instantiated directly from ``DomainConfig.endpoint``
    + ``DomainConfig.write_token``. Subclasses construct the appropriate
    client in their own ``__init__``.
    """

    def __init__(self, config: DomainConfig, client: object | None = None) -> None:
        self.config = config
        self.mcp = FastMCP(name=config.mcp_name)
        #: Per-domain HTTP client. Constructed by the per-domain entry point
        #: (jgs_sysmlv2_mcp builds a :class:`BridgeHttpClient`); re-exposed
        #: here so tool registration callbacks (native ``@mcp.tool()`` decorators)
        #: have a single canonical handle.
        self.client = client

    def mount_into(self, target_mcp) -> None:
        """Mount all registered tools from this server into target_mcp with tool_prefix prepended.

        Reaches into FastMCP internals — pin to the FastMCP version in pyproject.toml.
        If FastMCP renames _tool_manager or _tools, this breaks loudly (AttributeError).
        ToolManager.add_tool(fn, ...) requires a Callable — pass tool.fn, not tool itself.
        """
        tools = self.mcp._tool_manager._tools
        for name, tool in tools.items():
            target_mcp._tool_manager.add_tool(tool.fn, name=name,
                                              description=tool.description)

    def run_stdio(self) -> None:
        """Run the server over stdio (the standard MCP transport).

        Uses FastMCP's built-in stdio transport â€” no manual ``stdio_server``
        wrapping needed.
        """
        self.mcp.run()
