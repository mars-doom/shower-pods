"""
Dept of Makers project helpers.

This file does two jobs:
  1. It's an MkDocs hook (listed under `hooks:` in mkdocs.yml). When the site builds,
     it fills in {{ parts_list }} and {{ files_list }} on the How it works page.
  2. tools/build_pdf.py imports it so the PDF shows the same things.

Makers don't need to edit this.
"""
import csv
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
PARTS_CSV = ROOT / "parts.csv"
FILES_DIR = ROOT / "files"

# Words in the cost column that mean "cost nothing".
FREE_WORDS = {"free", "salvaged", "salvage", "scavenged", "gifted", "donated",
              "found", "reused", "scrap", "repurposed"}

# Relative column widths in the PDF.
PDF_WIDTHS = {"item": 5, "details": 5, "source": 4, "notes": 5, "qty": 1, "cost_each": 2}

HEADER_LABELS = {"qty": "Qty", "cost_each": "Cost each", "item": "Item",
                 "details": "Details", "source": "Source", "notes": "Notes"}


# ---------------------------------------------------------------- pages

def strip_frontmatter(md):
    return re.sub(r"\A---[ \t]*\n.*?\n---[ \t]*\n", "", md, count=1, flags=re.S)


def strip_comments(md):
    return re.sub(r"<!--.*?-->", "", md, flags=re.S)


# ---------------------------------------------------------------- parts

def _cost(value):
    """Return (number or None, is_free)."""
    v = (value or "").strip().lower()
    if not v:
        return None, False
    if v in FREE_WORDS:
        return 0.0, True
    try:
        return float(v.replace("$", "").replace(",", "")), False
    except ValueError:
        return None, False


def _qty(value):
    try:
        return float((value or "").strip() or "1")
    except ValueError:
        return 1.0


def _money(x):
    return f"${x:,.2f}"


def _read_parts():
    if not PARTS_CSV.exists():
        return [], []
    with open(PARTS_CSV, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
    if len(rows) < 2:
        return (rows[0] if rows else []), []
    header = [h.strip() for h in rows[0]]
    body = [(r + [""] * len(header))[:len(header)] for r in rows[1:]]
    return header, body


def _table(header, rows, pdf):
    keys = [h.lower() for h in header]

    def cell(key, value):
        value = value.replace("|", "\\|").replace("\n", " ").strip()
        if key == "cost_each":
            n, free = _cost(value)
            if n is not None and not free:
                return _money(n)
        return value

    labels = [HEADER_LABELS.get(k, h.replace("_", " ").capitalize()) for k, h in zip(keys, header)]
    if pdf:
        sep = "|" + "|".join("-" * (PDF_WIDTHS.get(k, 3) * 6) for k in keys) + "|"
    else:
        sep = "|" + "|".join(" --- " for _ in keys) + "|"
    lines = ["| " + " | ".join(labels) + " |", sep]
    for r in rows:
        lines.append("| " + " | ".join(cell(k, c) for k, c in zip(keys, r)) + " |")
    return "\n".join(lines)


def _subtotal(header, rows):
    keys = [h.lower() for h in header]
    if "cost_each" not in keys:
        return None, 0
    ci = keys.index("cost_each")
    qi = keys.index("qty") if "qty" in keys else None
    total, unpriced = 0.0, 0
    for r in rows:
        n, _ = _cost(r[ci])
        if n is None:
            unpriced += 1
        else:
            total += n * (_qty(r[qi]) if qi is not None else 1)
    return total, unpriced


def _cost_line(label, total, unpriced):
    if total is None:
        return ""
    if total == 0 and unpriced:
        return ""          # no prices entered at all: say nothing
    note = f" ({unpriced} item{'s' if unpriced != 1 else ''} not priced)" if unpriced else ""
    return f"**{label}: {_money(total)}**{note}"


def parts_markdown(pdf=False, level=3):
    """The parts list, grouped by section, as Markdown tables with subtotals."""
    header, body = _read_parts()
    if not body:
        return "*No parts listed yet. Add them to `parts.csv`.*"

    keys = [h.lower() for h in header]
    # Hide columns nobody has filled in.
    keep = [i for i, k in enumerate(keys) if k == "section" or any(r[i].strip() for r in body)]
    header = [header[i] for i in keep]
    body = [[r[i] for i in keep] for r in body]
    keys = [h.lower() for h in header]

    out = ["\\small", ""] if pdf else []
    hashes = "#" * level

    sections = {}
    if "section" in keys:
        si = keys.index("section")
        for r in body:
            sections.setdefault(r[si].strip() or "Other", []).append([c for i, c in enumerate(r) if i != si])
        header = [h for i, h in enumerate(header) if i != si]
    else:
        sections[""] = body

    grand, grand_unpriced, any_cost = 0.0, 0, False
    for name, rows in sections.items():
        if name and not (len(sections) == 1 and name == "Other"):
            if pdf:
                out += ["\\needspace{14\\baselineskip}", ""]
            out += [f"{hashes} {name}", ""]
        out += [_table(header, rows, pdf), ""]
        total, unpriced = _subtotal(header, rows)
        if total is not None:
            any_cost = True
            grand += total
            grand_unpriced += unpriced
            if len(sections) > 1:
                line = _cost_line("Subtotal", total, unpriced)
                if line:
                    out += [line, ""]
    if any_cost:
        line = _cost_line("Total", grand, grand_unpriced)
        if line:
            out += [line, ""]
    if pdf:
        out += ["\\normalsize"]
    return "\n".join(out)


# ---------------------------------------------------------------- files

def _size(n):
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1024


def files_markdown(repo_url=None, branch="main"):
    """A list of everything in files/, linked to GitHub."""
    if not FILES_DIR.exists():
        return "*No design files yet.*"
    found = sorted(p for p in FILES_DIR.rglob("*")
                   if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ROOT).parts)
                   and p.name.lower() != "readme.md")
    if not found:
        return "*No design files yet. Put them in the `files` folder.*"
    lines = []
    for p in found:
        rel = p.relative_to(ROOT).as_posix()
        label = p.relative_to(FILES_DIR).as_posix()
        if repo_url and "ORG-NAME" not in repo_url:
            url = f"{repo_url.rstrip('/')}/blob/{branch}/{quote(rel)}"
            lines.append(f"- [{label}]({url}) · {_size(p.stat().st_size)}")
        else:
            lines.append(f"- `{label}` · {_size(p.stat().st_size)}")
    return "\n".join(lines)


def fill_markers(md, repo_url=None, pdf=False):
    if "{{ parts_list }}" in md:
        md = md.replace("{{ parts_list }}", parts_markdown(pdf=pdf))
    if "{{ files_list }}" in md:
        md = md.replace("{{ files_list }}", files_markdown(repo_url))
    return md


# ---------------------------------------------------------------- MkDocs hooks

def on_page_markdown(markdown, page, config, files):
    return fill_markers(markdown, repo_url=config.get("repo_url"))
