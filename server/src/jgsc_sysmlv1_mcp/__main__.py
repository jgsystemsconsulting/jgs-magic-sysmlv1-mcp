# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Entry point for the SysML v1 MCP bridge server. Supports single-domain and unified modes."""
from __future__ import annotations

import os


def _parse_domains() -> set[str]:
    raw = os.environ.get("MAGIC_MCP_DOMAINS", "v1")
    return {d.strip() for d in raw.split(",") if d.strip()}


def _build_v1_domain_server():
    """Build a DomainServer for the v1 bridge."""
    from magic_mcp_core.config import DomainConfig
    from magic_mcp_core.domain_server import DomainServer
    from jgsc_sysmlv1_mcp.http_client import HttpClient
    from jgsc_sysmlv1_mcp.tools import register_all_v1_tools

    base_url = os.environ.get("V1_BASE_URL", "http://127.0.0.1:18751")
    token = os.environ.get("V1_TOKEN", "")
    config = DomainConfig(
        mcp_name="jgs-sysmlv1",
        endpoint=base_url,
        write_token=token or None,
        domain_id="sysmlv1",
    )
    client = HttpClient(base_url, token=token or None)
    server = DomainServer(config, client=client)
    register_all_v1_tools(server)
    return server


def _build_v2_domain_server():
    """Build a DomainServer for the v2 bridge (requires jgsc_sysmlv2_mcp package)."""
    try:
        from jgsc_sysmlv2_mcp.server import build_server  # type: ignore[import]
    except (ImportError, AttributeError) as exc:
        raise RuntimeError(
            "MAGIC_MCP_DOMAINS includes 'v2' but the jgsc_sysmlv2_mcp package is not installed."
        ) from exc
    return build_server()


def main() -> None:
    domains = _parse_domains()

    if "v1" in domains and "v2" not in domains:
        # Single v1 domain -- use standard entry point
        from jgsc_sysmlv1_mcp.server import run
        run()
        return

    if "v2" in domains and "v1" not in domains:
        # Single v2 domain
        server = _build_v2_domain_server()
        server.run_stdio()
        return

    # Combined v1+v2 unified server
    from mcp.server.fastmcp import FastMCP

    combined = FastMCP("JGS SysML v1+v2 Bridge")
    v1_srv = _build_v1_domain_server()
    v2_srv = _build_v2_domain_server()
    v1_srv.mount_into(combined)
    v2_srv.mount_into(combined)
    combined.run()


if __name__ == "__main__":
    main()
