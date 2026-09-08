<!--
Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
-->

# JGS SysML v1 MCP Bridge: Installation Guide

## Prerequisites

- CATIA Magic Systems of Systems Architect 2026x (installed and licensed)
- Python 3.11 or later

## Step 1: Install the Plugin

Copy the `plugin/` directory from this distribution into your CATIA Magic user plugins directory:

**Windows:**
```
%LOCALAPPDATA%\.magic.systems.of.systems.architect\2026x\plugins\com.jgsc.magicmcp.sysmlv1\
```

**macOS/Linux:**
```
~/.magic.systems.of.systems.architect/2026x/plugins/com.jgsc.magicmcp.sysmlv1/
```

After copying, the plugins directory should contain:
```
com.jgsc.magicmcp.sysmlv1/
├── plugin.xml
└── jgs-magic-sysmlv1.jar
```

The bundled JAR provides all **FREE-tier** functionality. **PRO / ENTERPRISE** tiers use an additional plugin JAR (`jgs-pro/jgs-sysmlv1-pro.jar`) that is **not included** in this distribution. After purchasing, download it from the link supplied with your licence and install it under a `jgs-pro/` subfolder following the instructions included with that download.

> **Do not restart CATIA Magic yet** if you have a licence file to place (see Step 3).

## Step 2: Install the Python MCP Server

```bash
python -m venv ~/.jgsc-sysmlv1/venv

# Activate (macOS/Linux):
source ~/.jgsc-sysmlv1/venv/bin/activate

# Activate (Windows PowerShell):
~\.jgsc-sysmlv1\venv\Scripts\Activate.ps1

pip install ./server
```

Verify the CLI is installed:

```bash
jgs-magic-sysmlv1-mcp --help
```

## Step 3: Place Your Licence File (Pro/Enterprise only)

Place `jgsc-sysmlv1-pro.licence` alongside the pro JAR:

```
com.jgsc.magicmcp.sysmlv1/jgs-pro/jgsc-sysmlv1-pro.licence
```

Inspect it with the bundled tool:

```bash
python tools/verify_licence.py path/to/jgsc-sysmlv1-pro.licence
```

Expected output: `Licence valid: customer=..., tier=..., seats=..., expires=...`

## Step 4: Configure the Write Secret

Set `JGS_V1_WRITE_SECRET` to the value provided with your licence:

**Windows (PowerShell, persists across sessions):**
```powershell
[System.Environment]::SetEnvironmentVariable("JGS_V1_WRITE_SECRET", "your-secret-here", "User")
```

**macOS/Linux:**
```bash
echo 'export JGS_V1_WRITE_SECRET="your-secret-here"' >> ~/.profile
source ~/.profile
```

## Step 5: Configure Your MCP Client

Copy `examples/.mcp.json.example` to your project root as `.mcp.json` and adjust the Python path if needed:

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

> **Tip:** If your venv Python is not on PATH, point `command` at the venv interpreter,
> e.g. `"command": "~/.jgsc-sysmlv1/venv/bin/python"` (macOS/Linux, expand `~` to your
> home directory) or `"command": "%USERPROFILE%\\.jgsc-sysmlv1\\venv\\Scripts\\python.exe"`
> (Windows, expand the variable).

## Step 6: Start CATIA Magic and Verify

1. Launch (or restart) CATIA Magic.
2. Open any SysML v1 project.
3. In your AI agent or MCP client, call the `ping` tool.

Expected response:
```json
{
  "status": "ok",
  "plugin_version": "0.1.0",
  "protocol_version": "1",
  "timestamp_utc": "2026-..."
}
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Connection refused` on `ping` | Plugin not loaded / CATIA Magic not running | Verify plugin directory structure; restart CATIA Magic |
| `401 Unauthorized` | Wrong or missing write secret | Verify `JGS_V1_WRITE_SECRET` matches the value supplied with your licence |
| `403 Forbidden` on write tools | Session in READ tier | Call `enable_writes` with the correct secret |
| Tools return errors immediately | No project open in CATIA Magic | Open a SysML v1 project before using tools |

