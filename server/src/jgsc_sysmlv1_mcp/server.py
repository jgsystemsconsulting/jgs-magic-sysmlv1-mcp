# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary

"""Entry point for the jgs-sysmlv1 MCP server.

Builds a :class:`magic_mcp_core.DomainServer` configured from ``JGS_V1_*``
env vars and wires up the v1 HttpClient + tool set.
"""

from __future__ import annotations

import logging

from magic_mcp_core.config import DomainConfig
from magic_mcp_core.domain_server import DomainServer

from .http_client import HttpClient
from .tools import register_all_v1_tools

logger = logging.getLogger(__name__)


def build_server() -> DomainServer:
    config = DomainConfig.from_env_v1()
    client = HttpClient(
        config.endpoint,
        token=config.bearer_token or config.write_token,
        token_file=config.bearer_token_path,
    )
    server = DomainServer(config, client=client)
    register_all_v1_tools(server)
    return server


def run() -> None:
    server = build_server()
    server.run_stdio()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    run()
