"""Optionally re-export the authored SVG and bind its PNG/PDF fingerprints.

Requires Node.js, Playwright with Chromium, and the existing pypdf dependency.
The normal analysis/figure/text/PDF rebuild uses the versioned exports instead.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import pypdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, ByteStringObject, NameObject

from public_inputs import PAPER
from build_study_design_svg import EXPECTED_BUDGET


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    parser.add_argument("--source-date-epoch", type=int, default=1794441600)
    args = parser.parse_args()
    source = PAPER / "figures/study-design-v04.svg"
    png = source.with_suffix(".png")
    pdf = source.with_suffix(".pdf")
    raw = PAPER / "build/study-design-export/raw.pdf"
    result = subprocess.run([
        args.node, str(Path(__file__).with_suffix(".cjs")), str(source), str(raw), str(png),
    ], capture_output=True, text=True, encoding="utf-8", check=True)
    renderer = json.loads(result.stdout.strip())
    reader = PdfReader(raw)
    assert len(reader.pages) == 1
    assert not list(reader.pages[0].images), "Figure 1 PDF must contain native vectors, not a raster image."
    native_text = reader.pages[0].extract_text() or ""
    assert all(label in native_text for label in ["Propose a check", "Frozen draft D", "Public issue", "expected outcome", "Advance-result continuation", "unavailable notice"])
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer._root_object.pop(NameObject("/Metadata"), None)
    date = datetime.fromtimestamp(args.source_date_epoch, timezone.utc).strftime("D:%Y%m%d%H%M%SZ")
    writer.add_metadata({
        "/Title": "Study B (R03/R04): shared-draft continuation design",
        "/Author": "Team xiakongxin",
        "/Subject": "Native SVG Figure 1; shared inputs and F-only precomputed result",
        "/Creator": "Authored SVG exported with Chromium; fixed metadata",
        "/Producer": "pypdf " + pypdf.__version__,
        "/CreationDate": date, "/ModDate": date,
    })
    identity = hashlib.sha256(source.read_bytes()).digest()[:16]
    writer._ID = ArrayObject([ByteStringObject(identity), ByteStringObject(identity)])
    with pdf.open("wb") as stream:
        writer.write(stream)
    verified = PdfReader(pdf)
    assert len(verified.pages) == 1 and not list(verified.pages[0].images)
    visible_text = [node.text or "" for node in ET.parse(source).getroot().iter("{http://www.w3.org/2000/svg}text")]
    record = {
        "version": "v0.4 native SVG Figure 1",
        "date": "2026-11-12",
        "svg": source.relative_to(PAPER).as_posix(),
        "svg_sha256": sha(source),
        "generator": "scripts/build_study_design_svg.py",
        "generator_sha256": sha(Path(__file__).with_name("build_study_design_svg.py")),
        "budgets": EXPECTED_BUDGET,
        "visible_text": visible_text,
        "source_date_epoch": args.source_date_epoch,
        "exporter": {**renderer, "pypdf": pypdf.__version__},
        "exports": {
            "png": {"path": png.relative_to(PAPER).as_posix(), "sha256": sha(png), "pixels": [3072, 2048]},
            "pdf": {"path": pdf.relative_to(PAPER).as_posix(), "sha256": sha(pdf), "pages": 1,
                    "native_text": True, "embedded_raster_images": 0,
                    "page_points": [float(verified.pages[0].mediabox.width), float(verified.pages[0].mediabox.height)]},
        },
        "scope": "Approved SVG v02. Default rebuild regenerates SVG, verifies the versioned PNG/PDF exports, and counts every visible label. Browser export is optional when artwork changes.",
    }
    output = PAPER / "evidence/study-design-svg-v04.json"
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"figure_1_exported": True, "svg_sha256": record["svg_sha256"], "vector_pdf": True, "png_pixels": [3072, 2048]}))


if __name__ == "__main__":
    main()
