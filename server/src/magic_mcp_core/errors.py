# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
"""Error types for the jgs_sysmlv2_mcp MCP server.

Maps RFC 7807 Problem Details from the bridge plugin to typed Python exceptions
so MCP tools can catch specific failure modes.
"""
from __future__ import annotations

from typing import Any


class BridgeError(RuntimeError):
    """Base class for errors returned by the Cameo bridge plugin."""

    def __init__(self, problem: dict[str, Any]) -> None:
        self.problem = problem
        self.problem_type: str = str(problem.get("type", ""))
        self.status: int = int(problem.get("status", 0))
        self.title: str = str(problem.get("title", ""))
        self.detail: str = str(problem.get("detail", ""))
        msg = f"{self.title} ({self.status}): {self.detail}" if self.detail else f"{self.title} ({self.status})"
        super().__init__(msg)


class UnauthorizedError(BridgeError):
    pass


class NotFoundError(BridgeError):
    pass


class TierDeniedError(BridgeError):
    pass


class PluginNotRunningError(BridgeError):
    pass


_TYPE_MAP: dict[str, type[BridgeError]] = {
    # v2 bridge error types
    "https://jgs-sysmlv2-mcp/errors/unauthorized": UnauthorizedError,
    "https://jgs-sysmlv2-mcp/errors/not-found": NotFoundError,
    "https://jgs-sysmlv2-mcp/errors/tier-denied": TierDeniedError,
    "https://jgs-sysmlv2-mcp/errors/plugin-not-running": PluginNotRunningError,
    # v1 bridge error types
    "https://jgsc-sysmlv1-mcp/errors/unauthorized": UnauthorizedError,
    "https://jgsc-sysmlv1-mcp/errors/not-found": NotFoundError,
    "https://jgsc-sysmlv1-mcp/errors/tier-denied": TierDeniedError,
    "https://jgsc-sysmlv1-mcp/errors/plugin-not-running": PluginNotRunningError,
    # DSL bridge error types
    "https://jgs-magic-dsl-mcp/errors/unauthorized": UnauthorizedError,
    "https://jgs-magic-dsl-mcp/errors/not-found": NotFoundError,
    "https://jgs-magic-dsl-mcp/errors/tier-denied": TierDeniedError,
    "https://jgs-magic-dsl-mcp/errors/plugin-not-running": PluginNotRunningError,
}


def problem_to_exception(problem: dict[str, Any]) -> BridgeError:
    """Map an RFC 7807 Problem dict to a typed BridgeError."""
    if "status" not in problem:
        raise ValueError(f"Problem document has no 'status' field: {problem!r}")
    cls = _TYPE_MAP.get(str(problem.get("type", "")), BridgeError)
    return cls(problem)
