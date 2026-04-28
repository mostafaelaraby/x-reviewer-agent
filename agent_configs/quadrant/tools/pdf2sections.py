"""Split a paper PDF (or its extracted text) into named sections.

CLI:
    python pdf2sections.py <pdf> [--out <dir>]
    python pdf2sections.py --text <text_file> [--out <dir>]

Library:
    from pdf2sections import extract_text, split_sections
    text = extract_text(Path("paper.pdf"))
    sections = split_sections(text)  # dict[str, str], keys lowercased
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Canonical lowercase section names. Order matters only for matching priority.
_HEADINGS = (
    "abstract",
    "introduction",
    "background",
    "preliminaries",
    "related work",
    "method",
    "methods",
    "approach",
    "experimental setup",
    "experiments",
    "results",
    "evaluation",
    "analysis",
    "discussion",
    "limitations",
    "conclusion",
    "broader impact",
    "ethics statement",
    "acknowledgments",
    "acknowledgements",
    "references",
    "appendix",
    "supplementary material",
)

# Match a heading-only line. Optional ordinal prefix ("1", "1.", "1.1", "I.", "A.")
# followed by the heading name (case-insensitive). Whole line must match.
_HEADING_RE = re.compile(
    r"^[\s]*"
    r"(?:(?:\d+(?:\.\d+)*\.?)|(?:[IVX]+\.?)|(?:[A-Z]\.))?"
    r"[\s]*"
    r"(" + "|".join(re.escape(h) for h in _HEADINGS) + r")"
    r"[\s.:]*$",
    re.IGNORECASE,
)


def _normalize_key(name: str) -> str:
    return re.sub(r"[\s_-]+", "_", name.strip().lower())


def split_sections(text: str) -> dict[str, str]:
    """Split paper text into a dict keyed by lowercase section name.

    Returns an empty dict if no recognizable headings are found. Section
    bodies are stripped of trailing whitespace; insertion order matches
    appearance order in the source text.
    """
    if not text.strip():
        return {}

    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        m = _HEADING_RE.match(stripped) if stripped else None
        if m:
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = _normalize_key(m.group(1))
            current_lines = []
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def extract_text(pdf_path: Path) -> str:
    """Extract text from a PDF using pypdf. One string, page breaks as \\n\\n."""
    import pypdf

    reader = pypdf.PdfReader(str(pdf_path))
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(parts)


def write_sections(sections: dict[str, str], out_dir: Path) -> list[Path]:
    """Write each section to a numbered markdown file. Returns the file paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for i, (key, body) in enumerate(sections.items()):
        path = out_dir / f"{i:02d}_{key}.md"
        path.write_text(f"# {key}\n\n{body}\n", encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("pdf", nargs="?", type=Path, help="Path to PDF file.")
    src.add_argument("--text", type=Path, help="Path to a pre-extracted text file.")
    parser.add_argument("--out", type=Path, default=None,
                        help="Directory to write per-section files (default: stdout headings).")
    args = parser.parse_args(argv)

    if args.text is not None:
        text = args.text.read_text(encoding="utf-8")
    else:
        text = extract_text(args.pdf)

    sections = split_sections(text)
    if not sections:
        print("no recognizable section headings found", file=sys.stderr)
        return 2

    if args.out:
        paths = write_sections(sections, args.out)
        for p in paths:
            print(p)
    else:
        for key, body in sections.items():
            print(f"## {key}  ({len(body)} chars)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
