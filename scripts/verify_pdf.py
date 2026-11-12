"""Extract all readable PDF text and render every page for subsequent visual QA."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pdfplumber
from pypdf import PdfReader

PAPER = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=PAPER / "build/main.pdf")
    parser.add_argument("--poppler", required=True)
    parser.add_argument("--tag", default="v0.3")
    args = parser.parse_args()
    pdf = args.pdf.resolve()
    render = PAPER / "build" / ("pages-" + args.tag)
    render.mkdir(parents=True, exist_ok=True)
    for stale in render.glob("page-*.png"):
        stale.unlink()
    with pdfplumber.open(pdf) as document:
        pages = [page.extract_text() or "" for page in document.pages]
        layout_word_counts = [len(page.extract_words()) for page in document.pages]
    reader = PdfReader(pdf)
    alternate = [page.extract_text() or "" for page in reader.pages]
    count = lambda text: len(re.findall(r"\S+", text))
    page_counts = [count(text) for text in pages]
    text = "\n\n".join(f"PAGE {i + 1}\n{value}" for i, value in enumerate(pages))
    (PAPER / "build/extracted-text.txt").write_text(text, encoding="utf-8", newline="\n")
    log_paths = [PAPER / "build/main.log", PAPER / "build/main.blg"]
    diagnostics = []
    for path in log_paths:
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if re.search(r"Overfull|Underfull|undefined|Warning--|^! ", line):
                    diagnostics.append(line.strip())
    result = subprocess.run([
        args.poppler, "-r", "140", "-png", str(pdf), str(render / "page"),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr)
    images = sorted(render.glob("page-*.png"))
    assert len(images) == len(pages), "Rendered page count differs from final PDF."
    total = sum(page_counts)
    alternate_count = sum(count(value) for value in alternate)
    record = {
        "pdf": str(pdf), "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "pages": len(pages), "pdfplumber_whitespace_tokens_by_page": page_counts,
        "pdfplumber_whitespace_tokens_total": total,
        "pypdf_whitespace_tokens_total": alternate_count,
        "pdfplumber_layout_words_total": sum(layout_word_counts),
        "conservative_readable_token_count": max(total, alternate_count, sum(layout_word_counts)),
        "count_scope": "All extracted readable text, including title, captions, tables, figure labels, references, and page numbers.",
        "count_limit": 3000,
        "within_word_limit": max(total, alternate_count, sum(layout_word_counts)) <= 3000,
        "tex_diagnostics": diagnostics,
        "rendered_pages": [str(path.resolve()) for path in images],
        "visual_review": "Pending visual inspection of these exact rendered pages.",
    }
    (PAPER / "build/verification.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in record.items() if k != "rendered_pages"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
