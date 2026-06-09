# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Macro-category MCP tools for v1: execute_groovy — arbitrary code execution in CATIA Magic's JVM."""
from __future__ import annotations

import json
from typing import Annotated, Any

from magic_mcp_core.domain_server import DomainServer
from magic_mcp_core.errors import BridgeError


def register_macro_v1_tools(server: DomainServer) -> None:
    """Register all v1 macro tools onto the FastMCP server natively.

    Tools registered:
      - execute_groovy(script: str) -> str

    The tool is always visible in the MCP catalogue; the bridge enforces
    enterprise-tier + dev-mode at call time and returns 403 if the session
    is not properly elevated.
    """

    @server.mcp.tool()
    async def execute_groovy(
        script: Annotated[str, "Groovy script source code to execute inside CATIA Magic's JVM"],
    ) -> str:
        """Execute Groovy script inside CATIA Magic's JVM with full SysML v1 API access. \
Requires dev mode active on the plugin side (see enable_dev_mode). Dev mode is a \
plugin-lifetime capability: it can only be enabled if JGS_V2_DEV_SECRET was set in \
the CATIA Magic process environment at startup, and the client must supply the \
matching secret value to enable_dev_mode. Dev mode is independent of licence tier: \
a FREE-tier client whose plugin was launched with JGS_V2_DEV_SECRET set can still \
enable dev mode and call execute_groovy. The env var is the security control.

A 'helpers' object is pre-loaded with convenience methods for the v1 (UML/MagicDraw-profile) API.
All stereotype names are SysML profile names (e.g. "Block", "Requirement", "Satisfy") — strings, NOT classes:

  helpers.findByQN('Model::Pkg::Element')
      — find by qualified name; returns the Element or null.

  helpers.createElement(parent, 'name', factoryFn, stereotypeName=null)
      — create element under `parent`. `factoryFn` is a 0-arg closure returning a fresh
        element from project.elementsFactory, e.g.
          { project.elementsFactory.createClassInstance() }   (for Block / Requirement)
          { project.elementsFactory.createPackageInstance() } (for Package)
        Optionally applies a SysML stereotype by name.

  helpers.applyStereotype(element, 'Block')
      — apply a SysML stereotype by name (uses StereotypesHelper internally).

  helpers.setTaggedValue(element, 'Requirement', 'id', 'REQ-001')
      — set a stereotype-tagged property value.

  helpers.getTaggedValue(element, 'Requirement', 'id')
      — read a stereotype-tagged property value; returns a List (may be empty) or null.

The 'project' binding is pre-loaded with the currently-open Project instance.

Returns a pretty-printed JSON string (str, not dict — intentional: LLM consumers parse the
indented JSON for readability, matching v2's macro_tools convention; other v1 tools return
dict because FastMCP auto-serialises them, which is fine for non-LLM-facing payloads).

JSON shape (matches v2's executeGroovyStatic exactly):
  success (bool): true on successful eval, false on exception
  result  (str):  script return value via String.valueOf, "null" if script returned null. Only present when success.
  output  (str):  captured stdout/stderr from the script
  error   (str):  exception message. Only present when not success."""
        try:
            result = await server.client.execute_groovy(script)
            return json.dumps(result, indent=2)
        except BridgeError as be:
            return f"error: {be}"
