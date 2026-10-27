#!/usr/bin/env python3
"""Build a static HTML site from the Markdown manual in docs/.

Local-first, zero dependencies (Python 3 stdlib only).

Usage:
  python3 build.py            # build the site into site/
  python3 build.py --check    # build, then verify internal links; exit 1 if broken
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
STYLE = ROOT / "assets" / "style.css"

SITE_NAME = "SSA Paperwork Calm Guide"
TAGLINE = "Social Security paperwork, translated like a friend would"

CHAPTERS = [
    ("index.md", "Start Here"),
    ("01-one-picture.md", "1. Social Security in One Picture"),
    ("02-which-appointment.md", "2. Which Appointment You Likely Need"),
    ("03-document-grab-list.md", "3. The Document Grab-List"),
    ("04-phone-field-online.md", "4. Phone, Field Office, or Online"),
    ("05-spouse-claims.md", "5. Spouse Claims, Patiently"),
    ("06-survivor-claims.md", "6. Survivor Claims, Patiently"),
    ("07-avoiding-scams.md", "7. Avoiding Impersonation Scams"),
    ("08-claim-binder.md", "8. Your Claim Binder"),
    ("09-glossary.md", "9. Glossary"),
    ("disclaimer.md", "The Education-Only Promise"),
    ("worksheets/appointment-finder-worksheet.md", "Worksheet: Appointment Finder"),
    ("worksheets/document-grab-list-checklist.md", "Worksheet: Document Grab-List Checklist"),
    ("worksheets/claim-timeline-worksheet.md", "Worksheet: My Claim Timeline"),
    ("worksheets/phone-call-notes-worksheet.md", "Worksheet: Phone Call Notes"),
    ("worksheets/binder-inventory-worksheet.md", "Worksheet: Binder Inventory"),
]


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)  # strip any inline tags we added
    text = text.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


# ---------------------------------------------------------------------------
# Markdown -> HTML (our documented subset: headings, paragraphs, bold/italic/
# inline code, links, GFM tables, simple lists with one nesting level,
# blockquotes, horizontal rules, fenced code blocks).
# ---------------------------------------------------------------------------

def convert_inline(text: str) -> str:
    """Process inline markdown on escaped text."""
    text = html.escape(text, quote=False)

    # code spans
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", text)

    # links: [text](target)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+?)(#[^)\s]*)?\)", _make_link, text)

    # bold and italic (after links, so link URLs aren't mangled);
    # bold uses a lazy match so inner italic `*emphasis*` can nest,
    # and DOTALL so bold spanning a wrapped line still parses
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*([^*\s][^*]*)\*(?!\*)", r"<em>\1</em>", text)
    return text


_current_page = ""


def _site_rel_from_page(site_target: Path) -> str:
    """Href that reaches site_target from the current page's directory."""
    cur_dir = SITE / Path(_current_page).parent
    return os.path.relpath(site_target, cur_dir).replace(os.sep, "/")


def resolve_md_link(target: str, anchor: str) -> str:
    """Map a markdown doc link to a site-relative html path plus anchor.

    Targets are resolved against the current page's directory in docs/,
    and may point back up outside their subfolder (e.g. '../01-one-picture.md').
    """
    base = (DOCS / _current_page).parent
    resolved = (base / target).resolve()
    if resolved.suffix.lower() != ".md" or not resolved.exists():
        if target.lower().endswith(".md"):
            return doc_name_fallback(target, anchor)
        return f"{target}{anchor}"
    try:
        resolved.relative_to(DOCS)
    except ValueError:
        return doc_name_fallback(target, anchor)
    rel_html = resolved.relative_to(DOCS).with_suffix(".html")
    return _site_rel_from_page(SITE / rel_html) + anchor


def doc_name_fallback(target: str, anchor: str) -> str:
    """Match a link by basename against the known chapters."""
    if not target.lower().endswith(".md"):
        return f"{target}{anchor}"
    base = (DOCS / _current_page).parent
    plain = (base / target).resolve()
    for filename, _ in CHAPTERS:
        resolved = (DOCS / filename).resolve()
        if plain == resolved:
            rel = Path(filename).with_suffix(".html")
            return _site_rel_from_page(SITE / rel) + anchor
    return f"{target}{anchor}"  # give up: leave original


def _make_link(m: re.Match) -> str:
    label, target, anchor = m.group(1), m.group(2), m.group(3) or ""
    if re.match(r"^[a-z]+:", target) or target.startswith("//"):
        return f'<a href="{target}">{label}</a>'
    href = resolve_md_link(target, anchor)
    return f'<a href="{href}">{label}</a>'


def convert_markdown(source: str) -> str:
    lines = source.splitlines()
    out: list[str] = []
    paragraphs: list[str] = []
    list_stack: list[str] | None = None
    table_buf: list[str] | None = None
    quote_buf: list[str] | None = None

    code_fences: list[str] = []

    # Pull out fenced code blocks first so nothing else mangles them.
    i = 0
    result_lines: list[str] = []
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # skip the closing fence
            fenceset = html.escape("\n".join(block))
            index = len(code_fences)
            code_fences.append(f"<pre><code>{fenceset}\n</code></pre>")
            result_lines.append(f"\x00FENCE{index}\x00")
        else:
            result_lines.append(line)
            i += 1
    lines = result_lines

    def flush_paragraphs() -> None:
        nonlocal paragraphs
        if paragraphs:
            # convert once after joining raw lines, so emphasis that
            # wrapped across lines still parses
            joined = convert_inline("\n".join(paragraphs))
            out.append(f"<p>{joined.replace(chr(10), '<br />')}</p>")
            paragraphs = []

    def flush_table() -> None:
        nonlocal table_buf
        if table_buf:
            rows_out: list[str] = []
            separator_pattern = re.compile(r"^\|[\s\-|:]+\|$")
            cells_open = True  # first row(s) before the separator are header cells
            for row in table_buf:
                if separator_pattern.match(row.strip()):
                    cells_open = False
                    continue
                cells = [convert_inline(c.strip()) for c in row.strip().strip("|").split("|")]
                tag = "th" if cells_open else "td"
                rows_out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            out.append("<table>" + "".join(rows_out) + "</table>")
            table_buf = None

    def flush_quote() -> None:
        nonlocal quote_buf
        if quote_buf is None:
            return
        text = "\n".join(l.lstrip("> ").rstrip() for l in quote_buf)
        blocks = []
        parts = re.split(r"\n\s*\n", text)
        for part in parts:
            if part.strip():
                blocks.append(f'<p>{convert_inline(" ".join(l.strip() for l in part.splitlines()))}</p>')
        out.append("<blockquote>" + "".join(blocks) + "</blockquote>")
        quote_buf = None

    def close_list() -> None:
        nonlocal list_stack, li_raw
        if list_stack:
            # finalize the pending list item with a single inline pass,
            # so emphasis that wrapped across lines still parses
            if li_raw is not None:
                out[-1] = out[-1][: -len("</li>")] + convert_inline(li_raw) + "</li>"
                li_raw = None
            out.append(f"</{list_stack}>")
            list_stack = None

    li_pattern = re.compile(r"^(\s*)([-*]|\d+[.)])\s+(.*)$")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.*)$")
    li_raw: str | None = None

    def flush_all_before_block() -> None:
        flush_paragraphs()
        flush_quote()
        close_list()

    for line in lines:
        stripped = line.strip()
        m_li = li_pattern.match(line)
        m_h = heading_pattern.match(line)

        # tables: any |...| row while buffering; otherwise close any open one
        if stripped.startswith("|") and stripped.endswith("|"):
            if table_buf is not None:
                table_buf.append(stripped)
            else:
                flush_all_before_block()
                table_buf = [stripped]
            continue
        flush_table()

        fence_m = re.match(r"^\x00FENCE(\d+)\x00$", stripped) or re.match(r"^FENCE(\d+)$", stripped)
        if fence_m:
            flush_all_before_block()
            out.append(code_fences[int(fence_m.group(1))])
            continue

        if not stripped:
            flush_paragraphs()
            continue

        if stripped.startswith(">"):
            flush_paragraphs()
            close_list()
            if quote_buf is None:
                quote_buf = []
            quote_buf.append(line.lstrip())
            continue

        if re.match(r"^-{3,}$", stripped):
            flush_paragraphs()
            flush_quote()
            close_list()
            out.append("<hr />")
            continue

        if m_h:
            flush_paragraphs()
            flush_quote()
            close_list()
            level = len(m_h.group(1))
            content = convert_inline(m_h.group(2))
            out.append(f'<h{level} id="{slugify(m_h.group(2))}">{content}</h{level}>')
            continue

        if m_li:
            flush_paragraphs()
            flush_quote()
            kind = "ul" if m_li.group(2) in "-*" else "ol"
            if list_stack is None:
                out.append(f"<{kind}>")
                list_stack = kind
            elif kind != list_stack:
                close_list()
                out.append(f"<{kind}>")
                list_stack = kind
            elif li_raw is not None:
                # finalize the previous same-list item
                out[-1] = out[-1][: -len("</li>")] + convert_inline(li_raw) + "</li>"
            out.append("<li></li>")
            li_raw = m_li.group(3)
            continue

        # Wrapped continuation of the previous list item (indented text
        # without a marker while a list is open) joins that item.
        if (
            list_stack is not None
            and li_raw is not None
            and re.match(r"^\s{2,}", line)
        ):
            li_raw += " " + stripped
            continue

        close_list()
        flush_quote()
        paragraphs.append(stripped)

    flush_paragraphs(); flush_table(); flush_quote(); close_list()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Site assembly
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {site_name}</title>
<link rel="stylesheet" href="{style}">
</head>
<body>
<header class="site-header">
  <a class="brand" href="{brand}">{site_name}</a>
  <span class="tagline">{tagline}</span>
</header>
<div class="layout">
<nav class="sidebar" aria-label="Chapters">
<h2>Contents</h2>
<ul>{nav_items}</ul>
<p class="disclaimer"><strong>Education and paperwork help only.</strong>
This guide never recommends a claim and never gives benefits advice. For
your own situation, call Social Security at 1-800-772-1213 or visit
ssa.gov. Read offline, any time.</p>
</nav>
<main>
{body}
<footer class="page-footer">
<p><small>{site_name} · Copyright (c) 2026 Asdale Dynamics, LLC · MIT license · education only, never benefits advice. Not affiliated with or endorsed by the Social Security Administration.</small></p>
</footer>
</main>
</div>
</body>
</html>
"""


def build_nav(current_rel: str) -> str:
    items = []
    for filename, label in CHAPTERS:
        href = _site_rel_from_page(SITE / Path(filename).with_suffix(".html"))
        active = " class=\"active\"" if Path(filename) == Path(current_rel) else ""
        items.append(f'<li><a href="{href}"{active}>{label}</a></li>')
    return "".join(items)


def build() -> list[str]:
    """Build the site; return list of written files (relative to repo root)."""
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    written: list[str] = []
    for filename, _ in CHAPTERS:
        src = DOCS / filename
        if not src.exists():
            raise SystemExit(f"Missing source doc: {src}")
        global _current_page
        _current_page = filename
        text = src.read_text(encoding="utf-8")
        body = convert_markdown(text)
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body)
        title = re.sub(r"<[^>]+>", "", m.group(1)) if m else Path(filename).stem
        if title.lower() == "the ssa paperwork calm guide":
            title = "Start Here"
        rel_out = Path(filename).with_suffix(".html")
        dest = SITE / rel_out
        dest.parent.mkdir(parents=True, exist_ok=True)
        page = PAGE_TEMPLATE.format(
            title=html.escape(title),
            site_name=SITE_NAME,
            tagline=TAGLINE,
            brand=_site_rel_from_page(SITE / "index.html"),
            style=("../" * (len(rel_out.parents) - 1)) + "style.css",
            nav_items=build_nav(filename),
            body=body,
        )
        dest.write_text(page, encoding="utf-8")
        written.append(str(Path("site") / rel_out))

    shutil.copy(STYLE, SITE / "style.css")
    written.append("site/style.css")
    return written


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []  # (attr, value)
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(("href", d["href"]))
        if d.get("id"):
            self.ids.add(d["id"])


def check_links(files: list[str] | None = None) -> list[str]:
    """Verify every internal link in site/ resolves to a file and anchor."""
    broken: list[str] = []
    pages: dict[str, str] = {}
    for html_file in sorted(SITE.rglob("*.html")):
        rel = html_file.relative_to(SITE).as_posix()
        pages[rel] = html_file.read_text(encoding="utf-8")

    ids_by_page: dict[str, set[str]] = {}
    for rel, text in pages.items():
        parser = _LinkParser()
        parser.feed(text)
        ids_by_page[rel] = {i for i in parser.ids if i}

    for rel, text in pages.items():
        parser = _LinkParser()
        parser.feed(text)
        for _attr, href in parser.links:
            if href.startswith(("http://", "https://", "mailto:", "#")):
                anchor_target = href if href.startswith("#") else None
                if anchor_target:
                    value = href[1:]
                    if value and value not in ids_by_page[rel]:
                        broken.append(f"{rel}: broken anchor #{value}")
                continue
            target, _, anchor = href.partition("#")
            target_path = (SITE / rel).parent / target
            if not os.path.exists(target_path):
                broken.append(f"{rel}: missing file {href}")
                continue
            if anchor:
                normalized = Path(os.path.normpath(str(target_path)))
                target_rel = normalized.relative_to(SITE).as_posix()
                if anchor not in ids_by_page.get(target_rel, set()):
                    broken.append(f"{rel}: missing anchor #{anchor} in {target_rel}")
    return broken


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="build and verify internal links")
    args = ap.parse_args()
    files = build()
    print(f"Built {len(files)} files into site/:")
    for f in files:
        print(f"  {f}")
    if args.check:
        broken = check_links()
        if broken:
            print("\nBROKEN LINKS:")
            for b in broken:
                print(f"  {b}")
            return 1
        print("Link check: all internal links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
