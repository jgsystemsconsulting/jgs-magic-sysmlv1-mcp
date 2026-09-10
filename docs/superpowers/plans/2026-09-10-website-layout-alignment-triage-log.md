| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1: Task 3 check expects no install.html findings but nav links configuration.html (Task 4) | R1 | R1 | Genuine | Nav block links configuration.html; broken-link finding fires at Task 3 Step 5, blocking the executor. |
| C2: CSS dedupe leaks page-specific rules globally and omits used selectors | R1 | R1 | Genuine | Comments do not scope CSS selectors; tools/licensing variants would restyle every page; .counts/.catnav/.note have no rules. |
| M1: README links install.html raw but configuration as .md | R1 | R1 | Genuine | Inconsistent targets; GitHub renders .md but shows install.html as raw HTML; point both at .md. |
| M2: Tasks 5/7/8 paste footer-wrapping block inside existing footer | R1 | R1 | Genuine | THE FOOTER BLOCK includes <footer> tags; pasting inside the existing <footer> nests footers; instructions must say replace the element. |
| M3: Spec R5 heading hierarchy verified nowhere | R1 | R1 | Genuine | Script checks only .shead wrapping; Task 10 Step 2 manual pass omits heading order; spec names manual pass as the guard. |
| M4: Commit policy omits docs/configuration.md from pre-dirty list | R1 | R1 | Genuine | Task 4 edits configuration.md uncommitted; Task 10 Step 3 expects it uncommitted; policy line 17 must list it. |
| M5: Tasks 5/7/8 line ranges shift after earlier same-file deletions | R1 | R1 | Advisory-skipped | Steps give exact content mappings (full h2 text, ids), so anchors exist; note ranges are pre-deletion approximations. |
| A1: Task 6 sits after tasks that consume its blocks | R1 | R1 | FP | Task 6 Files section already instructs writing the blocks before Task 3 runs. |
| A2: h2 check tolerates unclosed divs; void set omits col/area/track | R1 | R1 | Advisory-skipped | Check weakness does not affect the plan's stated checks; void-set extension is optional hardening. |
| A3: endswith('site.css') accepts external URLs | R1 | R1 | Advisory-skipped | No page links an external site.css; exact-match tightening is optional. |
| A4: Task 10 diff expectation unverifiable without baseline | R1 | R1 | Advisory-skipped | git status at Task 1 gives an implicit baseline; capturing it explicitly is optional. |
| A5: Nav HTML given only for index anchors | R1 | R1 | FP | Plan L401 lists each page's anchor targets; page links are identical across pages. |
| A6: md mapping omits emphasis/escaping; table.data rules unspecified | R1 | R1 | Advisory-skipped | Add strong/escape mapping and a table.data rule if cheap during Task 2; non-blocking. |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| Task 3 check fires on not-yet-created configuration.html | saboteur, new_hire | CRIT | Genuine | Fixed (Round 1) |
| CSS dedupe leaks page-specific rules globally; selector list not closed | saboteur, new_hire | CRIT | Genuine | Fixed (Round 1) |
| Task 9 README links install.html (raw HTML on GitHub) | saboteur | MAJ | Genuine | Fixed: links point at .md twins (Round 1) |
| Footer block nests footer inside footer | new_hire | MAJ | Genuine | Fixed: replace entire footer element (Round 1) |
| Spec R5 heading order verified nowhere | auditor | MAJ | Genuine | Fixed: manual pass now checks hierarchy (Round 1) |
| Commit policy omits configuration.md | auditor | MAJ | Genuine | Fixed: pointer line committable, baseline snapshot added (Round 1) |
| Line anchors shift mid-task | saboteur, auditor | MAJ | Genuine | Fixed: locate-by-content notes added (Round 1) |
| Task 6 ordering | saboteur | ADV | Advisory | Fixed: execution-order line in header (Round 1) |
| Parser void set / unclosed divs | saboteur | ADV | Advisory | Partially fixed (void set extended); balance tracking skipped, manual pass guards (Round 1) |
| endswith('site.css') bypass | saboteur | ADV | Advisory | Fixed: exact href match (Round 1) |
| Unverifiable diff expectation | saboteur | ADV | Advisory | Fixed: baseline snapshot (Round 1) |
| Nav HTML missing per page | new_hire | ADV | Advisory | Fixed: title-attr example + per-page anchor spec (Round 1) |
| md mapping gaps (strong/escaping/table.data) | new_hire | ADV | Advisory | Fixed (Round 1) |

Fixes applied: 12 (6 genuine CRITICAL/MAJOR + 6 advisory)
Inflation rate: 0% (0 of 7 CRITICAL+MAJOR findings triaged FP/Design)
Validation: SKIP
