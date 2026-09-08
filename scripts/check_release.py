# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Release gate (RR-B-15): required files, forbidden paths, forbidden
content, headers present, and version agreement. Exits non-zero on any
failure. Run from the repository root; stdlib only."""
import json
import pathlib
import re
import subprocess
import sys

fails: list[str] = []

REQUIRED = [
    # Base (RR-B)
    "LICENSE", "COPYRIGHT", "NOTICE", "README.md", "CHANGELOG.md",
    "RELEASE-INFO.txt", "CITATION.cff", "SECURITY.md", ".gitignore",
    # M-profile (RR-M) + distribution surface
    "docs/install.md", "docs/configuration.md", "docs/licensing.md",
    "docs/usage.md", "docs/TOOL-REFERENCE.md", "docs/index.html",
    "docs/.nojekyll", "examples/.mcp.json.example",
    "plugin/plugin.xml", "server/pyproject.toml", "tools/verify_licence.py",
    "glama.json", "smithery.yaml",
    ".claude-plugin/marketplace.json", ".claude-plugin/plugin.json",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/improvement.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]
for f in REQUIRED:
    if not pathlib.Path(f).is_file():
        fails.append(f"required file missing: {f}")

# forbidden paths: judge the TRACKED tree (local gitignored dirs are fine)
tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                         check=True).stdout.splitlines()
FORBIDDEN_PATH_PARTS = ["__pycache__", ".venv", ".worktrees", ".pytest_cache",
                        ".ruff_cache", ".bak"]
for f in tracked:
    if any(part in f for part in FORBIDDEN_PATH_PARTS):
        fails.append(f"forbidden tracked path: {f}")

FORBIDDEN_CONTENT = [re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
                     re.compile(r"CONFIDENTIAL\s+[-—]\s+Not for external distribution")]
SCAN_GLOBS = ["server/src/**/*.py", "docs/**/*.md", "docs/**/*.html",
              "*.md", "*.txt", "*.cff", "*.json", "*.yaml", "*.yml"]
for g in SCAN_GLOBS:
    for path in pathlib.Path(".").glob(g):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for rx in FORBIDDEN_CONTENT:
            if rx.search(text):
                fails.append(f"forbidden content in {path}: {rx.pattern}")

HEADER_SENTINEL = "Copyright (c) 2026 JG Systems Consulting Ltd"
for g in ["server/src/**/*.py", "tools/*.py", "scripts/*.py"]:
    for path in pathlib.Path(".").glob(g):
        if HEADER_SENTINEL not in path.read_text(encoding="utf-8", errors="ignore")[:300]:
            fails.append(f"header missing: {path}")

# version single-source agreement (RR-B-09/RR-B-10)
info = pathlib.Path("RELEASE-INFO.txt").read_text(encoding="utf-8")
if not re.search(r"(?m)^Version:\s*\S+", info):
    fails.append("RELEASE-INFO.txt has no Version: field")
if not re.search(r"(?m)^Tag:\s*v\S+", info):
    fails.append("RELEASE-INFO.txt has no Tag: field")
rel_version = re.search(r"(?m)^Version:\s*(\S+)", info)
version = rel_version.group(1) if rel_version else None

def changelog_top() -> str | None:
    for line in pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8",
                                                       errors="replace").splitlines():
        m = re.match(r"^##\s*\[?(\d+\.\d+\.\d+)\]?", line.strip())
        if m:
            return m.group(1)
    return None

top = changelog_top()
if version is None:
    fails.append("cannot read version from RELEASE-INFO.txt")
else:
    if top != version:
        fails.append(f"CHANGELOG top {top!r} != version {version!r}")
    py = pathlib.Path("server/pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', py)
    if not m or m.group(1) != version:
        errs_ver = m.group(1) if m else None
        fails.append(f"server/pyproject.toml version {errs_ver!r} != {version!r}")
    pj = json.loads(pathlib.Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if pj.get("version") != version:
        fails.append(f".claude-plugin/plugin.json version {pj.get('version')!r} != {version!r}")

if fails:
    print("RELEASE GATE FAILED:")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print(f"release gate: PASS (version {version})")
