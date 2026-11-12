"""Check companion input hashes, LF bytes, local links and publication boundaries."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

TEXT_SUFFIXES = {".md", ".py", ".ps1", ".cjs", ".json", ".csv", ".tex", ".bib", ".svg", ".txt"}
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
SECRET_PATTERNS = {
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "github_token": r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})",
    "api_token": r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}",
    "huggingface_token": r"\bhf_[A-Za-z0-9]{30,}",
    "aws_access_key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
}
OMITTED_PACKET_KEYS = {"original_public_problem", "original_public_hints", "public_input",
                       "public_task_messages", "problem_statement", "hints_text", "wire",
                       "reference_patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from packet_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from packet_keys(item)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--git-bytes", action="store_true",
                        help="Also require every tracked working file to match its HEAD blob byte for byte.")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "protocol/public-release-manifest.json").read_bytes())
    problems = []
    input_count = 0
    for name, item in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or sha(path) != item["sha256"]:
            problems.append({"kind": "frozen_input", "file": name})
        input_count += 1
    files = [path for path in root.rglob("*") if path.is_file()
             and not any(part in (".git", "build", "__pycache__") for part in path.relative_to(root).parts)]
    markdown_count = local_link_count = text_count = 0
    for path in files:
        if path.suffix not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        name = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        text_count += 1
        if b"\r\n" in raw or b"\r" in raw:
            problems.append({"kind": "non_lf_text", "file": name})
        try:
            text = raw.decode("utf-8")
        except UnicodeError:
            problems.append({"kind": "non_utf8_text", "file": name})
            continue
        if re.search(r"(?i)\b[A-Z]:(?:\\\\|\\|/)(?:Users|code-person)\b|/mnt/[a-z]/code-person/", text):
            problems.append({"kind": "local_machine_path", "file": name})
        for kind, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, text):
                problems.append({"kind": kind, "file": name})
        if path.suffix == ".json":
            value = json.loads(text)
            if name.startswith("protocol/packets/"):
                unwanted = sorted(set(packet_keys(value)) & OMITTED_PACKET_KEYS)
                if unwanted:
                    problems.append({"kind": "excluded_packet_fields", "file": name, "keys": unwanted})
        if path.suffix != ".md":
            continue
        markdown_count += 1
        # Each closing bracket finds both ordinary links and nested license badges.
        prose = re.sub(r"(?ms)^```.*?^```[^\n]*", "", text)
        links = re.findall(r"\]\((<[^>]+>|[^\n]*?)\)", prose)
        links += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(\S+)", prose)
        for target in links:
            target = target.strip()
            if target.startswith("<"):
                target = target[1:target.index(">")]
            else:
                target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            destination = unquote(target.split("#", 1)[0])
            if not destination:
                continue
            local_link_count += 1
            resolved = (path.parent / destination).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                problems.append({"kind": "broken_local_link", "file": name, "target": target})
    packets = [path for path in files if path.suffix == ".json" and "packets" in path.parts]
    prompts = list((root / "protocol/prompts").glob("*.md"))
    assert len(prompts) == manifest["stage_prompts"] == 5
    assert len(packets) == manifest["selected_study_a_packets"] + manifest["selected_study_b_packets"] == 14
    git_checked = 0
    if args.git_bytes:
        tree = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-rz", "HEAD"])
        entries = []
        for entry in tree.decode("utf-8").split("\0"):
            if not entry:
                continue
            metadata, name = entry.split("\t", 1)
            mode, kind, expected = metadata.split()
            assert kind == "blob"
            entries.append((name, expected))
        hashes = subprocess.check_output(["git", "-C", str(root), "hash-object", "--no-filters", "--",
                                          *[name for name, _ in entries]], text=True).splitlines()
        assert len(hashes) == len(entries)
        for (name, expected), actual in zip(entries, hashes):
            if actual != expected:
                problems.append({"kind": "working_bytes_differ_from_head", "file": name})
        git_checked = len(entries)
    report = {"mode": manifest["mode"], "verified_frozen_inputs": input_count,
              "text_files_checked": text_count, "markdown_files_checked": markdown_count,
              "local_links_checked": local_link_count, "selected_packets": len(packets),
              "stage_prompts": len(prompts), "head_blob_bytes_checked": git_checked,
              "files": len(files), "bytes": sum(path.stat().st_size for path in files),
              "problems": problems}
    if args.report:
        destination = args.report.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False))
    assert not problems, "Release checks failed; see the reported file names."


if __name__ == "__main__":
    main()
