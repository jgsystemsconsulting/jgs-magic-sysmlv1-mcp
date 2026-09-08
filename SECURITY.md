<!-- Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE. -->

# Security Policy

## Reporting a vulnerability

Report security issues privately via a
[GitHub security advisory](https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp/security/advisories/new).
Please do not open a public issue for a suspected vulnerability.

We aim to acknowledge reports within 5 business days. Please include the
affected version (see RELEASE-INFO.txt), reproduction steps, and impact.

## Scope notes

- The bridge binds to `127.0.0.1` and makes no outbound calls. A report that
  model data leaves the workstation is in scope.
- `JGS_V1_WRITE_SECRET` gates write-tier elevation, and licences are validated
  offline against an Ed25519 public key (`tools/verify_licence.py`). Weaknesses
  in the write gate or licence validation are in scope.
- The plugin JAR runs inside CATIA Magic with the user's privileges. Escalation
  through plugin HTTP endpoints is in scope.

## General support

Non-security questions: open an issue, or contact support@jgsystemsconsulting.com.
