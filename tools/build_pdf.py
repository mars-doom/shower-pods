#!/usr/bin/env python3
"""
Combine the docs into one PDF with pandoc.

Runs automatically when you publish a GitHub release. To run it yourself you need
pandoc and xelatex installed:   python tools/build_pdf.py [VERSION]

Page order comes from `nav:` in mkdocs.yml.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import makers  # noqa: E402

ROOT = makers.ROOT
DOCS = ROOT / "docs"
BUILD = ROOT / "build"


def read_mkdocs():
    text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    def get(key):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
        return m.group(1).strip().strip("'\"") if m else ""

    nav = re.search(r"^nav:\s*\n((?:[ \t]+-.*\n?)+)", text, re.M).group(1)
    pages = re.findall(r":\s*([\w\-/]+\.md)\s*$", nav, re.M)
    return get("site_name"), get("site_author"), get("repo_url"), pages


def convert_admonitions(md):
    """MkDocs '!!! tip "Label"' blocks -> blockquotes pandoc understands."""
    lines, out, i = md.splitlines(), [], 0
    while i < len(lines):
        m = re.match(r'^(\s*)(!!!|\?\?\?\+?)\s+(\w+)(?:\s+"([^"]*)")?\s*$', lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        indent, label = m.group(1), m.group(4) or m.group(3).capitalize()
        out.append(f"{indent}> **{label}:**")
        i += 1
        while i < len(lines) and (lines[i].startswith(indent + "    ") or not lines[i].strip()):
            if not lines[i].strip() and (i + 1 >= len(lines) or not lines[i + 1].startswith(indent + "    ")):
                break
            out.append(f"{indent}> " + lines[i][len(indent) + 4:]); i += 1
        out.append("")
    return "\n".join(out)


def strip_icons(md):
    """Inline icons like :material-leaf: have no PDF equivalent."""
    return re.sub(r":(material|fontawesome|octicons|simple)-[\w-]+:", "", md)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else ""
    title, author, repo_url, pages = read_mkdocs()
    BUILD.mkdir(exist_ok=True)

    parts = []
    for page in pages:
        f = DOCS / page
        if not f.exists():
            continue
        md = f.read_text(encoding="utf-8")
        md = makers.strip_comments(makers.strip_frontmatter(md))
        md = makers.fill_markers(md, repo_url=repo_url, pdf=True)
        md = convert_admonitions(strip_icons(md))
        if page == "index.md":   # the cover already shows the project name
            md = re.sub(r"^# .*\n", "# Summary\n", md, count=1)
        parts.append(md)

    combined = BUILD / "combined.md"
    combined.write_text("\n\n\\newpage\n\n".join(parts), encoding="utf-8")

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "project"
    pdf = BUILD / f"{slug}{'-' + version if version else ''}.pdf"
    subtitle = "Mars College Dept of Makers" + (f" · {version}" if version else "")

    subprocess.run([
        "pandoc", str(combined),
        "--from", "markdown-yaml_metadata_block",
        "--metadata-file", str(ROOT / "pdf" / "metadata.yml"),
        "-M", f"title={title}", "-M", f"subtitle={subtitle}", "-M", f"author={author}",
        "--resource-path", str(DOCS),
        "--pdf-engine=xelatex", "--toc", "--toc-depth=2",
        "-o", str(pdf),
    ], check=True)
    print(pdf)


if __name__ == "__main__":
    main()
