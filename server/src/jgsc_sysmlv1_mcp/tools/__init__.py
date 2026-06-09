# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Tool module registry — call register_all_v1_tools(server) to wire every tool module."""
from __future__ import annotations

from magic_mcp_core.domain_server import DomainServer

from .lifecycle_tools import register_lifecycle_v1_tools
from .read_tools import register_read_v1_tools
from .write_tools import register_write_v1_tools
from .modify_tools import register_modify_v1_tools
from .relationship_tools import register_relationship_v1_tools
from .v1_tools import register_v1_vocabulary_tools
from .diagram_tools import register_diagram_v1_tools
from .quality_tools import register_quality_v1_tools
from .safety_tools import register_safety_v1_tools
from .batch_tools import register_batch_v1_tools
from .macro_tools import register_macro_v1_tools

__all__ = ["register_all_v1_tools"]


def register_all_v1_tools(server: DomainServer) -> None:
    """Register all Phase B tool modules with the MCP server."""
    register_lifecycle_v1_tools(server)
    register_read_v1_tools(server)
    register_write_v1_tools(server)
    register_modify_v1_tools(server)
    register_relationship_v1_tools(server)
    register_v1_vocabulary_tools(server)
    register_diagram_v1_tools(server)
    register_quality_v1_tools(server)
    register_safety_v1_tools(server)
    register_batch_v1_tools(server)
    register_macro_v1_tools(server)
