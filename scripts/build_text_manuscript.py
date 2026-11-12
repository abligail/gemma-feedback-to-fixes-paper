"""Export the current LaTeX content as a readable Markdown manuscript.

Handles this manuscript's explicit subset of LaTeX. No TeX/PDF tool is invoked.
Unknown commands or unresolved references fail rather than silently disappearing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

PAPER = Path(__file__).resolve().parents[1]
INPUTS = {}


def read(path):
    raw = path.read_bytes()
    INPUTS[path.relative_to(PAPER).as_posix()] = hashlib.sha256(raw).hexdigest()
    return raw.decode("utf-8")


def group(text, start):
    assert text[start] == "{"
    depth = 1
    i = start + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if not depth:
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError("Unbalanced group")


def macro(text, name, callback):
    pattern = re.compile(r"\\" + name + r"\{")
    while m := pattern.search(text):
        value, end = group(text, m.end() - 1)
        text = text[:m.start()] + callback(value) + text[end:]
    return text


def expand(path, stack=()):
    assert path not in stack, "input cycle"
    text = read(path)
    def include(value):
        target = PAPER / value
        if not target.suffix:
            target = target.with_suffix(".tex")
        return expand(target, stack + (path,))
    return macro(text, "input", include)


def plain(text):
    for original, replacement in [
        (r'{\"u}', "ü"), (r'{\"a}', "ä"), (r"{\'e}", "é"), (r"{\'c}", "ć"), (r"{\v{c}}", "č"),
        (r"\_", "_"), (r"\%", "%"), (r"\&", "&"), (r"\$", "$"),
    ]:
        text = text.replace(original, replacement)
    return text.replace("---", "—").replace("--", "–").replace("~", " ")


def bibliography():
    text = read(PAPER / "references/references.bib")
    refs = {}
    for m in re.finditer(r"@misc\{([^,]+),", text):
        entry, _ = group(text, m.start() + len("@misc"))
        fields = {}
        for name in ("author", "title", "year", "note", "howpublished"):
            f = re.search(r"\b" + name + r"\s*=\s*\{", entry)
            assert f
            fields[name] = group(entry, f.end() - 1)[0]
        url = re.search(r"\\href\{([^}]+)\}", fields["howpublished"])
        authors = []
        for author in fields["author"].split(" and "):
            surname, given = author.split(", ", 1)
            authors.append(plain(given + " " + surname))
        refs[m[1]] = {"authors": ", ".join(authors), "title": plain(fields["title"]).strip("{}"),
                      "year": fields["year"], "note": fields["note"], "url": url[1]}
    return refs


def main():
    source = read(PAPER / "main.tex")
    title_match = re.search(r"\\title\{", source)
    title = group(source, title_match.end() - 1)[0].replace(r"\\", " ")
    title = re.sub(r"\s+", " ", plain(title)).strip()
    author_match = re.search(r"\\author\{", source)
    author = group(source, author_match.end() - 1)[0].replace(r"\\", " · ") if author_match else ""
    author = re.sub(r"\s+", " ", plain(author)).strip()
    body = expand(PAPER / "main.tex").split(r"\begin{document}", 1)[1].split(r"\end{document}", 1)[0]
    body = re.sub(r"(?m)^%.*$", "", body)
    body = re.sub(r"\{\\small\s*\\bibliographystyle\{[^}]+\}\s*\\bibliography\{[^}]+\}\s*\}", "", body)
    refs = bibliography()
    visuals = json.loads(read(PAPER / "evidence/visuals-v04.json"))["figures"]
    figure_text = []
    figure_files = []
    cited = []
    labels = {}
    counts = {"table": 0, "figure": 0}
    for m in re.finditer(r"\\begin\{(figure|table)\}(.*?)\\end\{\1\}", body, re.S):
        kind, block = m[1], m[2]
        counts[kind] += 1
        for label in re.findall(r"\\label\{([^}]+)\}", block):
            assert label not in labels
            labels[label] = str(counts[kind])

    def inline(text):
        text = re.sub(r"\\href\{([^{}]+)\}\{([^{}]+)\}",
                      lambda m: f"[{plain(m[2])}]({m[1]})", text)
        text = macro(text, "texttt", lambda v: "\x60" + plain(v) + "\x60")
        text = macro(text, "textbf", lambda v: "**" + plain(v) + "**")
        text = macro(text, "emph", lambda v: "*" + plain(v) + "*")
        text = macro(text, "ref", lambda v: labels[v])
        def cite(keys):
            out = []
            for k in keys.split(","):
                assert k in refs
                if k not in cited:
                    cited.append(k)
                out.append(str(cited.index(k) + 1))
            return "[" + ", ".join(out) + "]"
        text = macro(text, "cite", cite)
        text = plain(text).replace("$", "")
        return text

    counts = {"table": 0, "figure": 0}
    def display(m):
        kind, block = m[1], m[2]
        counts[kind] += 1
        cap = re.search(r"\\caption\{", block)
        caption = inline(group(block, cap.end() - 1)[0])
        if kind == "figure":
            asset = re.search(r"\\includegraphics\[[^]]+\]\{([^}]+)\}", block)[1]
            visual = visuals[Path(asset).stem]
            extension = Path(asset).suffix.removeprefix(".")
            assert visual["outputs"][extension]["path"] == asset
            assert hashlib.sha256((PAPER / asset).read_bytes()).hexdigest() == visual["outputs"][extension]["sha256"]
            preview = visual["outputs"]["png"]["path"]
            assert hashlib.sha256((PAPER / preview).read_bytes()).hexdigest() == visual["outputs"]["png"]["sha256"]
            figure_text.extend(visual["visible_text"])
            figure_files.append(preview)
            return (f"\n\n![{visual['alt']}]({preview})\n\n"
                    f"**Figure {counts[kind]}.** {caption}\n\n")
        match = re.search(r"\\begin\{tabular\}\{([^}]+)\}(.*?)\\end\{tabular\}", block, re.S)
        assert match
        headers, lines = [], []
        in_header = True
        for line in match[2].splitlines():
            line = line.strip()
            if line.startswith("\\midrule"):
                in_header = False
                continue
            if not line or line.startswith(("\\toprule", "\\cmidrule", "\\bottomrule", "%")):
                continue
            assert line.endswith(r"\\"), line
            cells = []
            for cell in line[:-2].split("&"):
                cell = cell.strip()
                span = re.fullmatch(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}", cell)
                cells.extend([inline(span[2])] * int(span[1]) if span else [inline(cell)])
            (headers if in_header else lines).append(cells)
        width = len(headers[0])
        assert all(len(row) == width for row in headers + lines)
        names = [" ".join(row[i] for row in headers if row[i]) for i in range(width)]
        alignment = re.findall(r"[lrc]", match[1])
        assert len(alignment) == width
        separators = [{"l": "---", "r": "---:", "c": ":---:"}[a] for a in alignment]
        table = ["| " + " | ".join(names) + " |", "| " + " | ".join(separators) + " |"]
        table += ["| " + " | ".join(row) + " |" for row in lines]
        return "\n\n**Table " + str(counts[kind]) + ".** " + caption + "\n\n" + "\n".join(table) + "\n\n"

    displays = []
    def preserve_display(m):
        displays.append(display(m))
        return f"@@DISPLAY{len(displays) - 1}@@"
    body = re.sub(r"\\begin\{(figure|table)\}(.*?)\\end\{\1\}", preserve_display, body, flags=re.S)
    body = body.replace(r"\begin{abstract}", "## Abstract\n").replace(r"\end{abstract}", "")
    body = macro(body, "section", lambda v: "\n\n## " + v + "\n")
    body = macro(body, "subsection", lambda v: "\n\n### " + v + "\n")
    body = macro(body, "paragraph", lambda v: "\n\n**" + v + "** ")
    for command in (r"\maketitle", r"\FloatBarrier"):
        body = body.replace(command, "")
    body = inline(body)
    for i, rendered in enumerate(displays):
        body = body.replace(f"@@DISPLAY{i}@@", rendered)
    assert not re.search(r"\\[A-Za-z]+", body), "Unconverted LaTeX command"
    assert "{" not in body and "}" not in body, "Unconverted group"
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    entries = []
    for i, k in enumerate(cited, 1):
        r = refs[k]
        punctuated_title = r['title'] if r['title'].endswith(('.', '?', '!')) else r['title'] + '.'
        entries.append(f"{i}. {r['authors']}. **{punctuated_title}** {r['year']}. {r['note']}. [Fixed arXiv version]({r['url']}).")
    header = f"# {title}\n\n**{author}**\n\n" if author else f"# {title}\n\n"
    output = f"{header}{body}\n\n## References\n\n" + "\n\n".join(entries) + "\n"
    assert not re.search(r"\\[A-Za-z]+|[{}]", output), "Unconverted content in reading copy"
    assert len(re.findall(r"(?m)^\|(?: :?---:? \|)+$", output)) == counts['table'], "Invalid Markdown table separators"
    local_links = [url for url in re.findall(r"\[[^\]]+\]\(([^)]+)\)", output)
                   if not re.match(r"https?://", url)]
    assert all((PAPER / url.split("#", 1)[0]).is_file() for url in local_links), "Missing linked companion file"
    # Image alt text is replaced by the text actually rendered inside each figure.
    visible = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", output)
    visible = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", visible)
    def word_count(text):
        return {"whitespace": len(text.split()),
                "word_tokens": len(re.findall(r"[A-Za-z0-9]+(?:['’–-][A-Za-z0-9]+)*", text))}
    drawn_text = "\n".join(figure_text)
    word_counts = word_count(visible + "\n" + drawn_text)
    body_word_counts = word_count(visible.split("\n## References\n", 1)[0] + "\n" + drawn_text)
    assert body_word_counts["whitespace"] <= 3000, f"Main text exceeds the conservative 3,000-word check: {body_word_counts}"
    (PAPER / "manuscript.md").write_text(output, encoding="utf-8", newline="\n")
    report = {"version": "current-baseline", "revision": "2026-11-11 baseline rewrite (v0.1-v0.4 archived)", "source_files": INPUTS, "tables": counts["table"], "figures": counts["figure"], "figure_files": figure_files,
              "citations": cited, "reading_copy_word_counts": word_counts,
              "main_text_word_counts_excluding_references": body_word_counts,
              "figure_text_word_counts": word_count(drawn_text),
              "word_count_scope": "Local counts include title, author attribution, tables, captions, and the actual labels, numbers, and legends drawn in both figures (not duplicate image alt text). Main-text counts exclude references, as clarified by the Paper Track host. PDF text extraction and page rendering are checked separately by verify_pdf.py.",
              "verified_local_links": local_links,
              "markdown_sha256": hashlib.sha256((PAPER / "manuscript.md").read_bytes()).hexdigest(),
              "unresolved_references_or_commands": 0}
    (PAPER / "review/text-verification-v04-20261110.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"word_counts": word_counts, "main_text_excluding_references": body_word_counts,
                      "tables": counts["table"], "cited": len(cited)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
