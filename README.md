<!--
Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
-->

# JGS SysML v1 MCP Bridge

AI-to-CATIA Magic bridge for SysML v1 models. Exposes your SysML v1 project to AI agents via the Model Context Protocol (MCP).

## Install with your AI agent

Copy everything in the block below and paste it into your coding agent
(Claude Code, Cursor, etc.). It will do the parts it safely can and hand back the
few desktop steps it cannot do for you.

```text
You are installing jgs-magic-sysmlv1-mcp, a proprietary MCP bridge (JG Systems Consulting
Ltd.) that lets MCP clients work with live SysML v1 models in CATIA Magic Systems of
Systems Architect (MSOSA 2026x). Repository: https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp (version 0.1.1).
Do this in order:

1. Read README.md, docs/install.md, docs/configuration.md, and docs/licensing.md in
   this repository so you understand the full install and prerequisites (CATIA Magic
   2026x, Python >= 3.11, an MCP client such as Claude Code).
2. Do the scriptable steps: install the Python server with `pip install ./server`
   (see docs/install.md for the exact command), create my MCP client config from
   `examples/.mcp.json.example` (fill in placeholders; never invent secrets/tokens),
   and place my licence file as described in docs/licensing.md.
3. STOP: these two steps run on my desktop app and you cannot do them for me:
     a. Copy the contents of `plugin/` into my CATIA Magic user plugins directory
        (the exact path is in docs/install.md).
     b. Restart CATIA Magic.
   Tell me the target path and wait for me to confirm I have done both.
4. After I confirm, verify the bridge by calling the `ping` MCP tool and report the
   result. If it fails, walk me through docs/configuration.md.
5. This is licensed software: point me at LICENSE and docs/licensing.md and note the
   FREE / PRO / ENTERPRISE tiers. Never invent, commit, or share licence keys.
```

## Install from the Claude Code marketplace

This repo ships a Claude Code plugin manifest, so you can add it as a marketplace and
install from inside Claude Code:

```text
/plugin marketplace add jgsystemsconsulting/jgs-magic-sysmlv1-mcp
/plugin install jgs-magic-sysmlv1-mcp
```

The marketplace install registers the bridge; the desktop steps (CATIA Magic plugin JAR
+ restart) still run on your machine. See [docs/install.md](docs/install.md).

## What's Included

- `plugin/`: CATIA Magic plugin JAR (copy to your plugins directory)
- `server/`: Python MCP server (install with `pip install ./server`)
- `docs/`: Installation guide and configuration reference
- `tools/`: Licence verification utility
- `examples/`: Sample `.mcp.json` configuration

## Quick Start

See [docs/install.md](docs/install.md) for full installation instructions.

## Requirements

- CATIA Magic Systems of Systems Architect 2026x
- Python 3.11 or later

## Support & Security

- **Support / licensing:** JG Systems Consulting Ltd.
- **Report a security issue:** open a [private security advisory](https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp/security/advisories/new)
  on this repository. Please do not open public issues for vulnerabilities, and do not
  email keys or licence material.

**Found a bug? (agents and humans)** If a tool returns malformed or incorrect output, open
an issue with the Bug Report form at `../../issues/new/choose`. Include the server version,
the tool name, and the exact tool call and its output. This is a *release* repo - the fix is
applied upstream by the maintainer, so please file an issue rather than a pull request.

## Licence

Proprietary: see [LICENSE](LICENSE) and [docs/licensing.md](docs/licensing.md).

Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.

