<!--
Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
-->

# Changelog

All notable changes to the JGS SysML v1 MCP Bridge are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] — 2026-06-18

### Fixed
- `validate_model` no longer throws `ScriptException` when a validation result targets a
  presentation element (PartView / diagram symbol) — the `localID` access is now guarded to
  model `Element`s only.
- `create_association` / `create_association_block` no longer corrupt the model (the
  "model inconsistency" dialog): association ends are validated and built atomically with
  rollback instead of leaving malformed 4-end associations.
- `create_allocation` now accepts Action sources into a valid container; `create_transition`
  3-argument calls succeed (name defaults to empty); `set_constraint` makes `name` optional.
- Activity / StateMachine behavioral containment is now surfaced by `get_element_structure`,
  `list_children`, and `walk_tree` (Activity nodes/edges, StateMachine regions/states/
  transitions) — previously reported as empty.
- Sequence-diagram Message arrows now render when populating a diagram.
- WRITE-tier deletion of orphan-leaf elements (no children, no incoming references).

### Added
- `set_aggregation` tool — set a Property's UML aggregation (composite / shared / none).

### Quality
- Full v1 contract QA suite hardened to green: 509 / 518 PASS, 0 FAIL, 0 SKIP
  (remaining 7 expected-fail tool-reality gaps + 2 deferred dispatcher gaps).
- Cross-case test contamination eliminated (deep-clean fixture reset).

## [0.1.0] — 2026-06-02

### Added
- Initial release of the JGS SysML v1 MCP Bridge.
- CATIA Magic plugin (free tier) with read and navigation tools.
- Python MCP server with automatic bridge endpoint discovery via port and token files.
- Pro tier: write tools for creating and modifying SysML v1 elements.
- Enterprise tier: `execute_groovy` and `delete_element` capabilities.
