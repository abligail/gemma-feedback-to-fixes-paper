"""Write BibTeX only from the fixed-version metadata verified during review."""
from datetime import datetime
import json
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]


def latex(value: str) -> str:
    replacements = {
        "ä": r"{\"a}", "ü": r"{\"u}", "é": r"{\'e}",
        "č": r"{\v{c}}", "ć": r"{\'c}",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def main() -> None:
    document = json.loads((PAPER / "review/reference-check-20261109.json").read_text(encoding="utf-8"))
    entries = ["% Verified fixed-version arXiv metadata; no venue metadata inferred."]
    for source in document["sources"]:
        assert source["status"] == 200
        meta = source["metadata"]
        authors = meta["citation_author"]
        assert authors and all(", " in name for name in authors)
        date = datetime.strptime(meta["citation_online_date"][0], "%Y/%m/%d")
        version_date = f"{date.day} {date.strftime('%B')} {date.year}"
        entries.extend([
            "@misc{" + source["key"] + ",",
            "  author = {" + latex(" and ".join(authors)) + "},",
            "  title = {{" + latex(meta["citation_title"][0]) + "}},",
            "  year = {" + meta["citation_date"][0][:4] + "},",
            "  note = {Version dated " + version_date + "},",
            "  howpublished = {\\href{" + source["url"] + "}{arXiv:" + source["fixed_version"] + "}}",
            "}", "",
        ])
    (PAPER / "references/references.bib").write_text("\n".join(entries), encoding="utf-8")
    print(f"Updated {len(document['sources'])} references from verified metadata.")


if __name__ == "__main__":
    main()
