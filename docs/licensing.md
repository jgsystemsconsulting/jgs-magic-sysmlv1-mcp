<!--
Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
-->

# JGS SysML v1 MCP Bridge: Licensing

## Licence Tiers

| Tier | Plugin JAR | Read tools | Write tools | Execute Groovy | Delete |
|---|---|---|---|---|---|
| **Free** | jgs-magic-sysmlv1.jar only | ✓ | ✗ | ✗ | ✗ |
| **Pro** | + jgs-pro/jgs-sysmlv1-pro.jar | ✓ | ✓ | ✗ | ✗ |
| **Enterprise** | + jgs-pro/jgs-sysmlv1-pro.jar | ✓ | ✓ | ✓ | ✓ |

## Licence File Placement

Your licence file (`jgsc-sysmlv1-pro.licence`) is issued by JG Systems Consulting Ltd. Place it at:

```
plugins/com.jgsc.magicmcp.sysmlv1/jgs-pro/jgsc-sysmlv1-pro.licence
```

The plugin reads it on startup. Confirm it was detected with the `get_licence` MCP tool after restarting CATIA Magic.

## Verify Your Licence

```bash
python tools/verify_licence.py path/to/jgsc-sysmlv1-pro.licence
```

Expected output: `Licence valid: customer=..., tier=..., seats=..., expires=...`

## Contact

Licensing enquiries: support@jgsystemsconsulting.com

Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
Brookfield Court, Selby Road, Garforth, Leeds, England, LS25 1NB

