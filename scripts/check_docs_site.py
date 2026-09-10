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
