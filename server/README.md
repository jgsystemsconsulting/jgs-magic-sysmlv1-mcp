<!--
Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
-->

# JGS SysML v1 MCP Server

Python MCP server bridging AI agents to SysML v1 models in CATIA Magic.

## Installation

```bash
pip install .
```

## Usage

```bash
# Via CLI entry point
jgs-magic-sysmlv1-mcp

# Via module (recommended for .mcp.json)
python -m jgsc_sysmlv1_mcp
```

## Dependencies

- `mcp >= 1.0`
- `httpx >= 0.27`
- `pydantic >= 2.6`
- `pyyaml >= 6.0`
- `pillow >= 10.0`

The server auto-discovers the running CATIA Magic bridge via port and token files written to `%LOCALAPPDATA%\.magic.systems.of.systems.architect\2026x\` on Windows. No manual endpoint configuration is required in most deployments.

## Configuration

See [../docs/configuration.md](../docs/configuration.md) for the full environment variable reference.

Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.

