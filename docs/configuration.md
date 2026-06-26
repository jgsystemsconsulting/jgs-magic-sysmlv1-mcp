<!--
Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
-->

# JGS SysML v1 MCP Bridge: Configuration Reference

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `JGS_V1_WRITE_SECRET` | No (needed for writes) | Shared secret for write-tier elevation |
| `JGS_V1_ENDPOINT` | No | Override bridge URL, bypasses auto-discovery |

### Auto-Discovery (default behaviour)

Without `JGS_V1_ENDPOINT`, the server reads two files written by the plugin at startup:

| File | Purpose |
|---|---|
| `%LOCALAPPDATA%\.magic.systems.of.systems.architect\2026x\jgs-sysmlv1-bridge.port` | Bridge HTTP port |
| `%LOCALAPPDATA%\.magic.systems.of.systems.architect\2026x\jgs-sysmlv1-bridge.token` | Auto-generated session token |

If these files are absent, the server falls back to `http://127.0.0.1:18751/v1` with no token.

### Override the Endpoint

```bash
export JGS_V1_ENDPOINT="http://127.0.0.1:18751/v1"
```

Use this when the port-file path is non-standard or when running the bridge on a remote host.

## Safety Tiers

Every session starts in **READ** tier (no model mutations possible). Write capabilities must be explicitly elevated per session:

| Tool | Action | Licence tier required |
|---|---|---|
| `enable_writes(secret)` | Elevate to WRITE tier | PRO or higher |
| `enable_dangerous_writes(secret)` | Elevate to DANGEROUS tier | ENTERPRISE |
| `disable_writes()` | Step back to READ tier | Any |
| `get_safety_state` | Inspect current tier, session ceiling, remaining elevations | Any |
| `get_licence` | Return customer name, tier, seat count, and expiry | Any |

## MCP Client Configuration Patterns

**Read-only (no env vars required if bridge is running):**
```json
{
  "mcpServers": {
    "jgs-sysmlv1": {
      "command": "python",
      "args": ["-m", "jgsc_sysmlv1_mcp"]
    }
  }
}
```

**With write secret:**
```json
{
  "mcpServers": {
    "jgs-sysmlv1": {
      "command": "python",
      "args": ["-m", "jgsc_sysmlv1_mcp"],
      "env": {
        "JGS_V1_WRITE_SECRET": "${JGS_V1_WRITE_SECRET}"
      }
    }
  }
}
```

**With explicit endpoint override:**
```json
{
  "mcpServers": {
    "jgs-sysmlv1": {
      "command": "python",
      "args": ["-m", "jgsc_sysmlv1_mcp"],
      "env": {
        "JGS_V1_ENDPOINT": "http://127.0.0.1:18751/v1",
        "JGS_V1_WRITE_SECRET": "${JGS_V1_WRITE_SECRET}"
      }
    }
  }
}
```
