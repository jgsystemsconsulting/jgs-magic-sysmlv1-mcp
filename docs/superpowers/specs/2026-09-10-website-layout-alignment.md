# Website layout alignment for jgs-magic-sysmlv1-mcp

Date: 2026-09-10
Status: draft
Scope: `docs/` website (GitHub Pages from `docs/`) plus the README links that point into it. No server code, no plugin code, no licensing terms.

## Problem

The site's top menu does not match what the pages contain. The nav offers Home, Tools, and Licence, while install and configuration instructions live in `install.md` and `configuration.md` that the nav never mentions and the index reaches only through raw GitHub blob URLs (`docs/index.html:233,235`). Heading conventions drift between pages: the index numbers its sections ("§01 · The problem") while tools.html and licensing.html use unnumbered label h2s, and the index's Upgrade section carries an ad-hoc label paragraph outside the shared section-heading pattern (`docs/index.html:255-256`). Each HTML page carries its own copy of the CSS with small drift between copies, so the same component looks slightly different per page. Separately, `README.md:79` links to `docs/usage.md`, which is deleted in the working tree.

The owner asked for two things: audit the site against the release standard (`release-repo-standard` skill) and the taste rubric (`taste-skill`), then bring across the layout of the JGS Archie skills site, which he considers well laid out.

## Reference pattern: the Archie skills site

Source: `C:\Users\gower\OneDrive\Documents\GitHub\jgs-archi-skills\docs\`, published at https://jgsystemsconsulting.github.io/jgs-archi-skills/

Its layout rests on five patterns the current site lacks or applies inconsistently:

1. One shared `site.css` (81 lines) holds every token, font, component, and the responsive rules. Pages carry content only.
2. On the pages that have sections (the index, guide, and engagement pages), the nav adds in-page section anchors, so every section on those pages is reachable from the top menu.
3. Every section opens the same way: a mono `.label` above the h2 (`.shead` wrapper). The reader always knows where they are.
4. A metadata masthead row and a structured footer block repeat on every page.
5. Polish lives in the stylesheet once: focus-visible ring, responsive break, table and code styling.

The current site already shares the Archie visual language (dark drafting aesthetic, mono labels, hairline grids), so the port is structural, not a redesign.

## Goals

- G1. Nav and page structure agree: every nav item resolves to a real page or section, and every major content area is reachable from the nav.
- G2. One stylesheet for the whole site; per-page CSS duplication removed.
- G3. One heading convention across all pages, matching the Archie `.shead` pattern.
- G4. Install and configuration content browsable on the site itself, not through GitHub blob URLs.
- G5. No dead links: the README's `usage.md` reference resolved.
- G6. Release-standard and taste findings from the audit (2026-09-10) addressed or explicitly waived.

## Non-goals

- No new JavaScript (the existing tools.html tier-filter script stays), no search, no dark/light toggle, no new framework or generator.
- No rewrite of page copy beyond headings, labels, and links.
- No changes to `server/`, `plugin/`, or licensing content.
- The `.md` files stay in the repo for GitHub readers; they are not deleted.

## Requirements

- R1. Create `docs/site.css` holding the shared tokens, fonts, masthead, nav, hero, `.shead`, grid, table, sheet, footer, focus-visible, and responsive rules. Merge the current per-page blocks into it (keeping the tier accent colors tools.html introduced). All HTML pages link it; no page keeps a duplicated copy of those rules.
- R2. Convert `install.md` and `configuration.md` into `docs/install.html` and `docs/configuration.html` in the site style. Each HTML page carries a source note naming its `.md` sibling as the canonical text, and each `.md` gains a one-line pointer to the rendered page. Content transfers as-is except for formatting to fit the page structure.
- R3. Every page's nav lists: Home, Install, Tools, Configuration, Licence, plus in-page section anchors for the page you are on (Archie pattern). No nav entry points at a GitHub blob URL.
- R4. Every h2 on every page sits in a `.shead` wrapper with a mono label; numbering follows the existing `§NN` convention, restarting per page. The current `sec-upgrade` heading gets a real label or is folded into the tier section.
- R5. Heading hierarchy stays h1 then h2 then h3 on every page; no skipped levels.
- R6. Masthead and footer markup are identical across pages (footer adopts the Archie metadata-block pattern with this repo's facts: product, licence model, repo, contact).
- R7. `README.md` stops linking to the deleted `docs/usage.md`; the link targets the new install page instead.
- R8. A small check script (`scripts/check_docs_site.py`) verifies in one pass: every local href/src in `docs/*.html` resolves to an existing file, and every fragment anchor resolves inside its target file; every page links `docs/site.css` and contains no inline `<style>` block; every h2 sits inside a `.shead`. It exits non-zero on violation. The validate workflow must not execute checked-out repository code (its header invariant), so the script is not wired into CI; it runs in this change's verification and before any release that touches `docs/`.
- R9. The `.md` siblings (`install.md`, `configuration.md`, `TOOL-REFERENCE.md`) remain the canonical text for repo readers; `tools.html` keeps its footer credit to `TOOL-REFERENCE.md`.

## Audit findings and dispositions (2026-09-10 audit, satisfies G6)

| Finding | Disposition |
|---------|-------------|
| Nav omits install/configuration/TOOL-REFERENCE content; index reaches it through GitHub blob URLs (`index.html:233,235`) | Addressed: R2, R3 |
| Each HTML page carries a drifted copy of the shared CSS (masthead, nav, `:root`) | Addressed: R1 |
| Heading label conventions differ per page; index Upgrade section uses an ad-hoc label | Addressed: R4 |
| `README.md:79` links the deleted `docs/usage.md` | Addressed: R7 |
| Feedback channels named in README but not linked from any docs page | Addressed: R6 (footer carries repo and contact links) |
| No `docs/DISTRIBUTION.md` ledger | Waived: release-process artifact, outside this website scope |
| Taste: CSS duplication, mixed tier accent handling, inconsistent h2 labels, licensing page missing an install path | Addressed: R1 (single stylesheet, tier accents included), R3, R4 |
| Taste: the `§NN` numbering reads as arbitrary | Design: kept as a deliberate drafting convention, restart per page (R4) |

## Approaches considered

- A. Minimal: keep three pages, add anchors and md links, unify labels inline. Rejected: nav still has no install/configuration pages, blob URLs survive, CSS drift survives.
- B. Port the Archie structure (chosen): shared stylesheet, nav that mirrors pages plus sections, `.shead` headings, install/configuration as real pages. Fits the existing visual language, closes every audit finding, no new tooling.
- C. Static site generator (MkDocs or similar). Rejected: new toolchain to maintain for a five-page site; the standard asks for consistency, not a build step.

## Verification

- R8's script is the runnable check; it must pass on the finished tree.
- Manual pass: open each page locally and confirm nav, labels, and footer match the requirements; confirm Pages will serve the new pages (static files beside `.nojekyll`). The script cannot judge nav contents, heading order, or masthead/footer identity; the manual pass is the guard for those.
- Diff review: no content changes outside `docs/` except `README.md:79` and the new `scripts/check_docs_site.py`.

## Risks

- The five pages now share one stylesheet: a bad merge could break a page that looked fine. Mitigation: the script plus a manual pass per page before commit.
- Content duplication between `.md` and `.html` twins can drift. Mitigation: R2's mutual pointer notes; accepted for a site this size.

## Research

research: skipped (static HTML/CSS layout work with no external API, library, or version-sensitive surface; the reference site and all evidence are local files inspected on 2026-09-10)

Reference URLs: https://jgsystemsconsulting.github.io/jgs-archi-skills/ (layout reference; layout verified from the local repo source, 2026-09-10); https://github.com/jgsystemsconsulting/jgs-archi-skills (its source repo)
