# Website Layout Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the docs website's top menu and headings with its actual content: one shared stylesheet, every section under a labelled `.shead` heading, install/configuration as real site pages, one metadata footer, and a static check script that holds the line.

**Architecture:** Five static HTML pages in `docs/` (index, install, tools, configuration, licensing) served by GitHub Pages, all linking one new `docs/site.css` merged from the current per-page `<style>` blocks (they share one design lineage) plus new `.shead`, `blockquote`, and footer-grid rules. A stdlib-only Python script (`scripts/check_docs_site.py`) verifies links, stylesheet linkage, and heading wrappers.

**Tech Stack:** Static HTML/CSS, Python 3 stdlib (html.parser, pathlib), no build step, no new JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-10-website-layout-alignment.md` (review pair clean: FCL Round 2, ARL Round 3)

**Execution order:** Tasks 1, 2, 6, 3, 4, 5, 7, 8, 9, 10. Task 6 defines the shared nav and footer blocks that Tasks 3-5 and 7-8 copy verbatim; read it before starting Task 3.

## Global Constraints

- The validate workflow (`.github/workflows/validate.yml:2-4`) MUST NOT execute checked-out repository code; the check script is NOT wired into CI (spec R8).
- No new JavaScript. The existing tools.html tier-filter `<script>` block (tools.html:376-398) stays as-is.
- COMMIT POLICY: commit only files this plan CREATES (`docs/site.css`, `docs/install.html`, `docs/configuration.html`, `scripts/check_docs_site.py`, plan artifacts) plus the pointer line in `docs/configuration.md` (that file had no pre-existing edits, so committing it is safe). Files that were already modified in the working tree before this plan (`docs/index.html`, `docs/tools.html`, `docs/licensing.html`, `docs/install.md`, `README.md`) are edited but LEFT UNCOMMITTED; the user's in-flight release edits in those files must not be folded into these commits. Before starting Task 1, capture `git status --short` to a scratch file; Task 10 compares against that baseline. Verify with `git status` before each commit; use explicit paths in `git add`.
- Every `.py` file needs the header `Copyright (c) 2026 JG Systems Consulting Ltd.` (validate.yml scans `**/*.py`).
- All revision strings stay `0.1.1`; product name `jgs-magic-sysmlv1-mcp`; contact `support@jgsystemsconsulting.com`; repo `https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp`.
- Keep every existing `id` on every page (nav anchors, hero CTAs, and `aria-labelledby` point at them). New ids only where a section had none.
- English copy only; no em dashes in new prose; sentence-case labels inside sentences, uppercase styling comes from CSS `text-transform`.

## Research

research: skipped (no external APIs, libraries, or version-sensitive choices; every hard-coded artifact is a local file verified 2026-09-10 during spec audit and review)

Verified facts the tasks rely on (checked 2026-09-10):
- `docs/index.html`: `<style>` block at L42-148; masthead/nav L154-168; hero L172-187; sections `sec-problem` §01, `sec-how` §02, `sec-airgap` §03, `sec-install` §04 (section element id `install`), `sec-tiers` §05; ad-hoc Upgrade panel L253-265 with `h2 id="sec-upgrade"`; footer L267-272.
- `docs/tools.html`: `<style>` L28-104 (includes `.catnav` L77-79, `.sec-label` L83, tier accents `--free/--pro/--ent`); nav L108-126; 11 `section.cat` blocks L168-367 with h2 ids `lifecycle-tools-h` … `v1-vocabulary-tools-h`; footer L368-373; filter `<script>` L376-398.
- `docs/licensing.html`: `<style>` L27-109; nav L115-127; sections `sec-matrix`, `sec-place`, `sec-verify`, `sec-cta` (ad-hoc Upgrade label L195, h2 L196); footer L205-210.
- `README.md:79` links `docs/usage.md`, deleted in the working tree.
- Archie reference (read-only source, do not modify): `C:\Users\gower\OneDrive\Documents\GitHub\jgs-archi-skills\docs\site.css` provides `.shead`, `.tblock`, `.foot-note` patterns; this repo's pages share its token set. Note: tools.html's `:root` (L34-43) adds `--free/--pro/--ent` and drops `--ink-4` relative to index.html:48-57.
- `docs/.nojekyll` present; GitHub Pages serves `docs/` at `https://jgsystemsconsulting.github.io/jgs-magic-sysmlv1-mcp/`.

## File Structure

- Create `docs/site.css`; the single stylesheet: fonts, tokens, base, masthead/nav, sections/`.shead`, hero/buttons, grids/chain/cta, `pre`, tables and tools-page rules, `blockquote`, footer `.tblock`, focus/skip/reduced-motion/responsive.
- Create `docs/install.html`; rendered twin of `docs/install.md`.
- Create `docs/configuration.html`; rendered twin of `docs/configuration.md`.
- Create `scripts/check_docs_site.py`; the R8 static check.
- Modify `docs/index.html`, `docs/tools.html`, `docs/licensing.html`; delete `<style>` block, link `site.css`, convert h2s to `.shead`, extend nav, replace footer.
- Modify `docs/install.md`, `docs/configuration.md`; one pointer line to the rendered twin.
- Modify `README.md:79-83`; repoint the dead `usage.md` link.

---

### Task 1: Static check script

**Files:**
- Create: `scripts/check_docs_site.py`

**Interfaces:**
- Produces: `python scripts/check_docs_site.py` → exit 0 when all checks pass, exit 1 with per-finding lines `docs/<page>.html: <message>`. Checks (spec R8): (1) every local `href`/`src` resolves to an existing file relative to `docs/`, and every fragment resolves to an `id` in its target file (bare `#frag` = same file); (2) every page links `site.css` and contains no `<style>` element; (3) every `<h2>` sits inside an element with class `shead`.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
"""Static checks for the docs website.

Implements R8 of docs/superpowers/specs/2026-09-10-website-layout-alignment.md:
link integrity, single stylesheet, and .shead-wrapped h2 headings.
Stdlib only. Not wired into CI: validate.yml must not execute checked-out code.
"""
import sys
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
SKIP_PREFIXES = ("http://", "https://", "mailto:", "data:", "javascript:")


class PageParser(HTMLParser):
    def __init__(self, name: str) -> None:
        super().__init__(convert_charrefs=True)
        self.name = name
        self.problems: list[str] = []
        self.hrefs: list[tuple[str, int]] = []
        self.ids: set[str] = set()
        self.has_style = False
        self.links_site_css = False
        self.stack: list[tuple[str, str]] = []  # (tag, class attr)

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        a = dict(attrs)
        cls = a.get("class", "")
        if tag == "style":
            self.has_style = True
        if tag == "link" and a.get("rel") == "stylesheet" and a.get("href") == "site.css":
            self.links_site_css = True
        for key in ("href", "src"):
            if key in a:
                self.hrefs.append((a[key], line))
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h2" and not any(t == "div" and "shead" in c.split() for t, c in self.stack):
            self.problems.append(f"{self.name}:{line} h2 not inside .shead")
        void = {"meta", "link", "img", "br", "hr", "input", "source", "wbr", "col", "area", "track", "base", "embed"}
        if tag not in void:
            self.stack.append((tag, cls))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i]
                return

    def check_links(self) -> None:
        for href, line in self.hrefs:
            if href.startswith(SKIP_PREFIXES):
                continue
            path, _, frag = href.partition("#")
            if path:
                target = DOCS / path
                if not target.is_file():
                    self.problems.append(f"{self.name}:{line} broken link: {href}")
                    continue
                if frag:
                    self._check_fragment(target, frag, href, line)
            elif frag:
                self._check_fragment(DOCS / self.name, frag, href, line)

    def _check_fragment(self, target: Path, frag: str, href: str, line: int) -> None:
        if target.resolve() == (DOCS / self.name).resolve():
            ids = self.ids
        else:
            other = PageParser(target.name)
            other.feed(target.read_text(encoding="utf-8"))
            ids = other.ids
        if frag not in ids:
            self.problems.append(f"{self.name}:{line} fragment #{frag} not found for {href}")


def main() -> int:
    pages = sorted(DOCS.glob("*.html"))
    if not pages:
        print("no HTML pages found under docs/")
        return 1
    total = 0
    for page in pages:
        parser = PageParser(page.name)
        parser.feed(page.read_text(encoding="utf-8"))
        parser.check_links()
        if parser.has_style:
            parser.problems.append(f"{page.name}: inline <style> block (must use site.css)")
        if not parser.links_site_css:
            parser.problems.append(f"{page.name}: does not link site.css")
        for problem in parser.problems:
            print(problem)
        total += len(parser.problems)
    print(f"{len(pages)} pages checked, {total} findings")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it and confirm it fails on the current tree**

Run: `python scripts/check_docs_site.py`
Expected: exit 1 with findings for every page (`inline <style> block`, `does not link site.css`, `h2 not inside .shead`) and no `broken link` lines. If any `broken link` appears, stop and fix the script's link classification before proceeding.

- [ ] **Step 3: Commit**

```bash
git add scripts/check_docs_site.py
git commit -m "docs: add static site check script (R8)"
```

---

### Task 2: Shared stylesheet

**Files:**
- Create: `docs/site.css`

**Interfaces:**
- Produces: `docs/site.css` providing, at minimum, the selectors listed below. Every selector used by any of the five HTML pages must have a rule here when Tasks 5-7 finish.

- [ ] **Step 1: Write the merged stylesheet**

Build the file in this order. Rules marked (index Lnn) are copied from the current `docs/index.html` `<style>` block; (tools) and (licensing) rules are copied from those pages' blocks; rules marked NEW are written as given.

1. `@font-face` x4: (index L43-46), unchanged. Font URLs stay relative (`fonts/...`).
2. `:root` (index L48-57) plus the tier accents from the tools block: `--free:`, `--pro:`, `--ent:` with the exact values found in `docs/tools.html:28-76`.
3. Base: `*`, `html`, `body`, `.wrap`, `a`, `h1/h2/h3`, `code/.mono` (index L59-69).
4. `.label` (index L71-74).
5. Masthead and `.site-nav` (index L76-88).
6. Sections: `section`, `.sec-label`, `.lead-in` (index L90-93) plus NEW:

```css
.shead { margin: 0 0 24px; }
.shead .label { display: block; margin: 0 0 6px; }
.shead h2 { margin: 0; font-size: clamp(1.4rem, 3vw, 1.9rem); scroll-margin-top: 64px; }
```

7. Hero, `.btns`, `.btn` (index L95-105).
8. `.grid`, `.cell`, `.chain` (index L107-122).
9. `pre` (index L124-129).
10. `.cta` (index L131-134).
11. NEW blockquote:

```css
blockquote { margin: 0; border-left: 2px solid var(--line-2); padding: 4px 0 4px 18px; color: var(--text); }
```

12. Tables and page-specific rules: port EVERY rule from the tools block (`docs/tools.html:28-104`) and the licensing block (`docs/licensing.html:27-109`) into this file. Their selector inventories include `.catnav`, `.tools`, `.filter`, `.hide`, `.ct`, `.cat`, `.counts`, `.controls`, `.tbl-scroll`, the tier accent rules referencing `--free/--pro/--ent`, and licensing's `.note`, `.matrix-scroll`, and its table/caption rules; do not drop any selector that the pages' markup uses. Then add these base table rules (NEW):
```css
table.data { width: 100%; border-collapse: collapse; font-size: 0.9375rem; }
table.data th, table.data td { text-align: left; vertical-align: top; padding: 14px 16px; border-bottom: 1px solid var(--line); }
table.data th { font: 700 0.6875rem/1.4 var(--mono); letter-spacing: 0.12em; text-transform: uppercase; color: var(--mute); background: var(--ink-3); }
table.data td { color: var(--text); }
table.data code { font: 400 0.8125rem var(--mono); color: var(--text-hi); }
table.data caption { caption-side: bottom; text-align: left; padding: 12px 0 0; font: 400 0.8125rem/1.5 var(--mono); color: var(--mute); }
```
Dedupe: where the identical selector appears on two pages with identical declarations, keep one copy (prefer the index version). Where the same selector carries DIFFERENT declarations on different pages, never leave two conflicting copies: scope each to its page's markup as it exists (e.g. `table.tools th` for the tools catalogue; licensing's table styling under its own table class found in the markup), or fold the difference into the shared rule when it is safe for every page.
13. Footer: drop the old `footer p` typography only in favour of NEW:

```css
footer { padding: 40px 0 64px; }
.tblock { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--line); border: 1px solid var(--line); }
.tblock div { background: var(--ink-2); padding: 18px 24px; }
.tblock .label { display: block; margin-bottom: 6px; }
.tblock b { color: var(--text); font: 700 0.875rem var(--mono); }
.tblock a { color: var(--text); text-decoration: none; }
.tblock a:hover { color: var(--text-hi); }
.foot-note { margin-top: 1.5rem; font: 400 0.8125rem/1.6 var(--mono); color: var(--mute); }
.foot-note a { color: var(--mute-2); }
```

14. Accessibility and responsive (index L139-147) plus NEW in the `@media (max-width: 860px)` block: `.tblock { grid-template-columns: 1fr; }`.

- [ ] **Step 2: Sanity-check the file**

Run: `python -c "open('docs/site.css',encoding='utf-8').read(); print('ok')"` and confirm the file contains `.shead`, `.tblock`, `.catnav`, `.counts`, `.note`, `table.data`, `--pro`, and the `@media (max-width: 860px)` block.
Expected: `ok`, all five markers present.

- [ ] **Step 3: Commit**

```bash
git add docs/site.css
git commit -m "docs: add shared site.css merged from per-page styles"
```

---

### Task 3: install.html from install.md

**Files:**
- Create: `docs/install.html`
- Modify: `docs/install.md` (one pointer line, left uncommitted per policy)

**Interfaces:**
- Consumes: `docs/site.css` (Task 2).
- Produces: page with nav per Task 6's nav block (`aria-current="page"` on the Install link), sections with h2 ids `install-prereq`, `install-step1` … `install-step6`, `install-trouble`, each wrapped in `.shead` with §NN labels.

- [ ] **Step 1: Write the page skeleton**

Head: `<!DOCTYPE html>`, copyright comment `<!-- Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved. -->`, plus `<!-- Canonical text: docs/install.md; edit the .md first, then this page. -->`, charset, viewport, the same favicon `data:` URI as index.html:11, `<title>Install | JGS SysML v1 MCP Bridge</title>`, `<meta name="description" content="Install the JGS SysML v1 MCP Bridge: plugin, Python MCP server, licence file, write secret, and MCP client wiring.">`, `<link rel="stylesheet" href="site.css">`. Body: skip-link, masthead (copy index.html:154-168 exactly, with the Task 6 nav block and `aria-current="page"` moved to the Install link), `<main class="wrap" id="main-content">`, hero:

```html
<section class="hero">
  <p class="label">Install guide</p>
  <h1>From download to first ping in six steps.</h1>
  <p class="lede">Everything below runs locally. No cloud service, no model export, no telemetry.</p>
</section>
```

- [ ] **Step 2: Convert the content**

Map `docs/install.md` (from `## Prerequisites` to the end of Troubleshooting) with this mapping: `## X` → `<section aria-labelledby="..."><div class="shead"><p class="label">§NN</p><h2 id="...">X</h2></div>` then content then `</section>`; fenced code → `<pre>`; `- item` → `<ul><li>`; `1.` list → `<ol><li>`; `> note` → `<blockquote>`; pipe tables → `<table class="data">` with `<thead>`/`<tbody>`; `` `code` `` → `<code>`; `**text**` → `<strong>`; escape `<`, `>`, and `&` as HTML entities inside `<pre>` content. Sections in order: §01 Prerequisites (`id="install-prereq"`), §02 Step 1: Install the plugin (`install-step1`), §03 Step 2: Install the Python MCP server (`install-step2`), §04 Step 3: Place your licence file (`install-step3`), §05 Step 4: Configure the write secret (`install-step4`), §06 Step 5: Configure your MCP client (`install-step5`), §07 Step 6: Start CATIA Magic and verify (`install-step6`), §08 Troubleshooting (`install-trouble`). Transfer the text verbatim; keep all code blocks intact including the PowerShell and JSON ones.

- [ ] **Step 3: Close the page**

Footer: the Task 6 footer block, verbatim. Then `</main></body></html>`.

- [ ] **Step 4: Add the pointer line to the .md**

In `docs/install.md`, directly under the `# JGS SysML v1 MCP Bridge: Installation Guide` heading, insert:
`> Rendered version: [install.html](install.html) on the project site.`

- [ ] **Step 5: Run the check and inspect**

Run: `python scripts/check_docs_site.py`
Expected: exactly one finding names `install.html`, and it is the forward link to the page Task 4 creates: `install.html:... broken link: configuration.html`. No other findings mention `install.html`; the not-yet-migrated pages still report their expected pre-migration findings.

- [ ] **Step 6: Commit**

```bash
git add docs/install.html
git commit -m "docs: add install.html rendering of install.md for the site nav"
```

---

### Task 4: configuration.html from configuration.md

**Files:**
- Create: `docs/configuration.html`
- Modify: `docs/configuration.md` (one pointer line, left uncommitted per policy)

**Interfaces:**
- Consumes: `docs/site.css` (Task 2), nav block (Task 6).
- Produces: sections §01 Environment variables (`id="config-env"`), §02 Safety tiers (`config-tiers`), §03 MCP client configuration patterns (`config-client`).

- [ ] **Step 1: Write the skeleton**

Same head pattern as Task 3 (title `Configuration | JGS SysML v1 MCP Bridge`; description `Environment variables, safety tiers, and MCP client configuration patterns for the JGS SysML v1 MCP Bridge.`; canonical-text comment naming `docs/configuration.md`). Masthead with `aria-current="page"` on the Configuration link. Hero:

```html
<section class="hero">
  <p class="label">Configuration reference</p>
  <h1>Two environment variables. Three safety tiers.</h1>
  <p class="lede">Sessions start read-only; writes need a licence tier and an explicit elevation call.</p>
</section>
```

- [ ] **Step 2: Convert the content**

Apply the Task 3 mapping to `docs/configuration.md`. Section §01 keeps its two `###` subsections (Auto-Discovery, Override the Endpoint) as `<h3>`; its two pipe tables become `table.data`. §02 keeps the safety-tier table. §03 renders the three JSON variants as `<pre>` blocks, each introduced by an `<h3>` (Read-only, With write secret, With explicit endpoint override).

- [ ] **Step 3: Close the page and add the pointer**

Footer block from Task 6, then `</main></body></html>`. In `docs/configuration.md`, under the `#` title, insert:
`> Rendered version: [configuration.html](configuration.html) on the project site.`

- [ ] **Step 4: Run the check**

Run: `python scripts/check_docs_site.py`
Expected: no findings mention `configuration.html`, and the Task 3 `broken link: configuration.html` finding is gone.

- [ ] **Step 5: Commit**

```bash
git add docs/configuration.html docs/configuration.md
git commit -m "docs: add configuration.html rendering of configuration.md"
```

---

### Task 5: Switch index.html to the shared stylesheet and .shead headings

**Files:**
- Modify: `docs/index.html` (L42-148 style block, L161-166 nav, L189-265 sections, L267-272 footer)

**Interfaces:**
- Consumes: `docs/site.css` (Task 2), nav/footer blocks (Task 6), `docs/install.html`, `docs/configuration.html` (Tasks 3-4).

- [ ] **Step 1: Replace the style block with the link**

Delete lines 42-148 (`<style>` … `</style>`) and insert `<link rel="stylesheet" href="site.css">` in its place.

- [ ] **Step 2: Convert the six section headings**

Line numbers below are anchors from the pre-edit file; they shift once Step 1 deletes the style block, so locate each heading by its quoted text, not by line number. Keep each `<section>` wrapper and every `aria-labelledby`. Replace each combined heading with the split pattern. Exact mappings:

- L190 `<h2 class="label sec-label" id="sec-problem">§01 · The problem</h2>` → `<div class="shead"><p class="label">§01</p><h2 id="sec-problem">The problem</h2></div>`
- L203 same shape: label `§02`, h2 `How it works`, id `sec-how`
- L217: label `§03`, h2 `Why air-gapped matters`, id `sec-airgap`
- L231: label `§04`, h2 `Install`, id `sec-install`
- L243: label `§05`, h2 `Licence tiers`, id `sec-tiers`
- L255-256 (Upgrade panel): replace the ad-hoc `<p class="label" style="margin:0 0 12px">Upgrade</p>` + `<h2 id="sec-upgrade">…</h2>` with `<div class="shead"><p class="label">§06</p><h2 id="sec-upgrade">Let the AI write to the model, not just read it.</h2></div>`

- [ ] **Step 3: Extend the nav and replace the footer**

Nav: replace the four links inside `<nav aria-label="Site" class="site-nav">` with the Task 6 nav block, `aria-current="page"` on Home, and the in-page anchor list `§01`-`§06` targeting `#sec-problem` … `#sec-upgrade`. Footer: replace the ENTIRE existing `<footer>…</footer>` element with THE FOOTER BLOCK from Task 6 (the block includes its own `<footer>` wrapper; do not nest it inside the old one).

- [ ] **Step 4: Run the check and eyeball the page**

Run: `python scripts/check_docs_site.py`
Expected: no findings mention `index.html`. Then open `docs/index.html` in a browser: fonts load, masthead/nav render, each section shows the small `§NN` label above a larger h2, footer grid shows six cells.

- [ ] **Step 5: Commit (index.html stays uncommitted per policy)**

No commit. Record in the task log: `index.html migrated; left uncommitted (pre-existing working-tree edits).`

---

### Task 6: Lock the shared nav and footer blocks

**Files:**
- Reference only; this task's blocks are consumed by Tasks 3-5 and 7-8. Perform it by writing the blocks into the plan execution notes before Task 3 runs, then applying the remaining pages (tools, licensing) in Tasks 7-8.

**Interfaces:**
- Produces: THE NAV BLOCK and THE FOOTER BLOCK, used verbatim on all five pages.

- [ ] **Step 1: Fix the two blocks**

THE NAV BLOCK (page links in this exact order; keep `GitHub →`; append the page's own in-page anchors after a `·` separator span; `aria-current="page"` on the page's own link; tools.html uses its existing `.catnav` as the in-page anchor row per spec R3 intent; do not add 11 anchors to its masthead):

```html
<a href="index.html">Home</a>
<a href="install.html">Install</a>
<a href="tools.html">Tools</a>
<a href="configuration.html">Configuration</a>
<a href="licensing.html">Licence</a>
<a href="https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp">GitHub →</a>
<span class="label" style="margin:0">·</span>
<a href="#sec-problem" title="The problem">§01</a>
<a href="#sec-how" title="How it works">§02</a>
<a href="#sec-airgap" title="Why air-gapped matters">§03</a>
<a href="#sec-install" title="Install">§04</a>
<a href="#sec-tiers" title="Licence tiers">§05</a>
<a href="#sec-upgrade" title="Upgrade">§06</a>
```

(Anchor list per page: index `§01`-`§06` as above; install `§01`-`§08` targeting `#install-prereq`, `#install-step1`...`#install-step6`, `#install-trouble`; configuration `§01`-`§03` targeting `#config-env`, `#config-tiers`, `#config-client`; licensing `§01`-`§04` targeting `#sec-matrix`, `#sec-place`, `#sec-verify`, `#sec-cta`; tools: none in masthead. Each anchor carries a `title` attribute with its section's h2 text, e.g. for install.html: `<a href="#install-prereq" title="Prerequisites">§01</a>` through `<a href="#install-trouble" title="Troubleshooting">§08</a>`.)

THE FOOTER BLOCK (identical on all five pages):

```html
<footer>
  <div class="tblock">
    <div><span class="label">Product</span><b>jgs-magic-sysmlv1-mcp</b></div>
    <div><span class="label">Licence</span><b><a href="licensing.html">Proprietary · FREE / PRO / ENTERPRISE</a></b></div>
    <div><span class="label">Repository</span><b><a href="https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp">github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp</a></b></div>
    <div><span class="label">Contact</span><b><a href="mailto:support@jgsystemsconsulting.com">support@jgsystemsconsulting.com</a></b></div>
    <div><span class="label">Requires</span><b>CATIA Magic 2026x · Python 3.11+</b></div>
    <div><span class="label">Revision</span><b>0.1.1</b></div>
  </div>
  <p class="foot-note">Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved. Tool catalogue generated from <a href="https://github.com/jgsystemsconsulting/jgs-magic-sysmlv1-mcp/blob/main/docs/TOOL-REFERENCE.md">docs/TOOL-REFERENCE.md</a>.</p>
</footer>
```

- [ ] **Step 2: Confirm nothing to commit**

This task only standardises the blocks; page applications happen in Tasks 3-5, 7-8. No commit.

---

### Task 7: Switch tools.html

**Files:**
- Modify: `docs/tools.html` (L28-104 style, L117-122 nav, h2s L169-353, L368-373 footer)

**Interfaces:**
- Consumes: Task 2 stylesheet, Task 6 blocks. The filter `<script>` L376-398 stays untouched.

- [ ] **Step 1: Style swap**

Delete the `<style>`...`</style>` block (approx. L28-104; locate by tags), insert `<link rel="stylesheet" href="site.css">`. (All tools-specific rules were ported in Task 2 step 12.)

- [ ] **Step 2: Convert the eleven category headings** (line numbers approximate; locate each heading by its quoted text)

For each of the 11 `section.cat` blocks, replace `<h2 class="label sec-label" id="X">Name <span class="ct">N</span></h2>` with `<div class="shead"><p class="label">§NN</p><h2 id="X">Name <span class="ct">N</span></h2></div>`. Numbering in page order: §01 Lifecycle (`lifecycle-tools-h`), §02 Safety, §03 Batch, §04 Read, §05 Write, §06 Modify, §07 Relationship, §08 Quality, §09 Diagram, §10 Macro, §11 V1 Vocabulary.

- [ ] **Step 3: Nav and footer**

Apply THE NAV BLOCK with `aria-current="page"` on Tools and NO §NN anchors (the `.catnav` under the h1 remains the section-anchor row). Replace the ENTIRE existing `<footer>…</footer>` element with THE FOOTER BLOCK (the block includes its own `<footer>` wrapper).

- [ ] **Step 4: Run the check and test the filter**

Run: `python scripts/check_docs_site.py`; Expected: no findings mention `tools.html`. Open the page in a browser and click two tier filter buttons: rows hide/show, category sections collapse when empty, no console errors.

- [ ] **Step 5: No commit**; record: `tools.html migrated; left uncommitted (pre-existing working-tree edits).`

---

### Task 8: Switch licensing.html

**Files:**
- Modify: `docs/licensing.html` (L27-109 style, L122-127 nav, L144-196 h2s, L205-210 footer)

- [ ] **Step 1: Style swap**; delete the `<style>`...`</style>` block (approx. L27-109; locate by tags), insert `<link rel="stylesheet" href="site.css">`.

- [ ] **Step 2: Convert the four headings** (line numbers approximate; locate by quoted text)

- `sec-matrix`: label `§01`, h2 `What each tier unlocks`
- `sec-place`: label `§02`, h2 `Place your licence file`
- `sec-verify`: label `§03`, h2 `Verify your licence`
- L195-196 (cta panel): replace ad-hoc `<p class="label" …>Upgrade</p>` + `<h2 id="sec-cta">…</h2>` with `<div class="shead"><p class="label">§04</p><h2 id="sec-cta">Need write access, or scripting?</h2></div>`

Keep the matrix table markup as-is (its caption inline styles stay; they reference existing CSS variables).

- [ ] **Step 3: Nav and footer**; THE NAV BLOCK with `aria-current="page"` on Licence and anchors `§01`-`§04`; replace the ENTIRE existing `<footer>...</footer>` element with THE FOOTER BLOCK (the block includes its own `<footer>` wrapper).

- [ ] **Step 4: Run the check**

Run: `python scripts/check_docs_site.py`
Expected: `5 pages checked, 0 findings`, exit 0. This is the R8 gate for the whole site.

- [ ] **Step 5: No commit**; record: `licensing.html migrated; left uncommitted (pre-existing working-tree edits).`

---

### Task 9: README dead-link fix

**Files:**
- Modify: `README.md:79-83` (left uncommitted per policy)

- [ ] **Step 1: Repoint the Usage paragraph**

Replace:

```markdown
## Usage

[docs/usage.md](docs/usage.md) walks the first session and the everyday
workflows: exploring the model, auditing requirement coverage, authoring a
change under a PRO licence, and producing diagrams. The per-tool reference is
[docs/TOOL-REFERENCE.md](docs/TOOL-REFERENCE.md).
```

with:

```markdown
## Usage

[docs/TOOL-REFERENCE.md](docs/TOOL-REFERENCE.md) is the per-tool reference,
and [docs/install.md](docs/install.md) plus
[docs/configuration.md](docs/configuration.md) cover setup and configuration.
The same pages render on the project site with the full tool catalogue.
```

(The first-session walkthrough content lived only in the deleted usage.md; the install and configuration pages plus TOOL-REFERENCE cover the remaining links. If the walkthrough text is wanted later it needs a new home, which is out of scope here.)

- [ ] **Step 2: Verify no other usage.md references**

Run: `grep -rn "usage\.md" README.md .github/ || echo clean`
Expected: `clean`. (The plan and spec files under `docs/superpowers/` discuss the dead link by name; they are pipeline artifacts, not shipped docs, so the grep scopes to README and workflow files.)

- [ ] **Step 3: No commit.** Record: `README.md fixed; left uncommitted (pre-existing working-tree edits).`

---

### Task 10: Full verification

- [ ] **Step 1: Script gate**

Run: `python scripts/check_docs_site.py`
Expected: `5 pages checked, 0 findings`, exit 0.

- [ ] **Step 2: Manual pass (spec Verification section)**

Open each of the five pages in a browser and confirm: masthead nav shows Home · Install · Tools · Configuration · Licence · GitHub plus the page's §NN anchors (tools: catnav instead); every section shows its §NN label above its h2; heading order on every page is exactly one h1 followed by h2 sections, with h3s only inside them and no skipped levels (spec R5); the footer grid shows the six metadata cells identically on every page; mobile width (~400px) collapses grids and the footer to one column. Confirm `docs/.nojekyll` is still present so Pages serves the new pages as static files.

- [ ] **Step 3: Diff review (spec Verification section)**

Run: `git status --short` and `git diff --stat`, and compare the working-tree list against the baseline snapshot captured before Task 1.
Expected: committed new files = `docs/site.css`, `docs/install.html`, `docs/configuration.html`, `scripts/check_docs_site.py` (+ plan artifacts) plus the `docs/configuration.md` pointer line; uncommitted modified files = `docs/index.html`, `docs/tools.html`, `docs/licensing.html`, `docs/install.md`, `README.md` (each carrying this plan's edits on top of the user's pre-existing edits) plus the user's pre-existing edits elsewhere (server/, CHANGELOG, etc.; untouched by this plan). No other files changed versus the baseline.

- [ ] **Step 4: Report**

Summarise: script result, per-page manual-pass confirmation, the uncommitted-file list with the reason, and any deviation from the plan.
