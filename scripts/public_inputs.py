"""Resolve and verify the inputs of the lightweight companion release.

Original packet fingerprints remain provenance. Public exports have separate
fingerprints because task payloads and machine paths are omitted and text is LF.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
IS_MONOREPO = PAPER.name == "feedback-to-fixes" and PAPER.parent.name == "paper"
ROOT = PAPER.parents[1] if IS_MONOREPO else PAPER
_manifest = None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def release_manifest():
    global _manifest
    if _manifest is None:
        path = PAPER / "protocol/public-release-manifest.json"
        _manifest = json.loads(path.read_text(encoding="utf-8"))
        assert _manifest["mode"] == "lightweight-derived-inputs"
        sources = [item["source_path"] for item in _manifest["files"].values()]
        assert len(sources) == len(set(sources)), "Duplicate release source mapping"
        for name in _manifest["files"]:
            target = (PAPER / name).resolve()
            assert target.is_relative_to(PAPER), f"Release input escapes repository: {name}"
    return _manifest


def source_exports():
    return {item["source_path"]: (name, item)
            for name, item in release_manifest()["files"].items()}


def resolve_input(relative):
    if IS_MONOREPO:
        return ROOT / relative
    exports = source_exports()
    if relative in exports:
        return PAPER / exports[relative][0]
    if relative.startswith("paper/feedback-to-fixes/"):
        return PAPER / relative.removeprefix("paper/feedback-to-fixes/")
    return PAPER / relative


def verify_public_inputs():
    assert not IS_MONOREPO
    manifest = release_manifest()
    for name, item in manifest["files"].items():
        path = PAPER / name
        assert path.is_file(), f"Missing bundled input: {name}"
        assert sha(path) == item["sha256"], f"Frozen public input changed: {name}"
    return len(manifest["files"])


def verify_original_identity(relative, expected):
    if IS_MONOREPO:
        assert sha(ROOT / relative) == expected, f"Frozen input changed: {relative}"
        return
    exports = source_exports()
    assert relative in exports, f"Original source has no public export: {relative}"
    name, item = exports[relative]
    assert item["source_sha256"] == expected, f"Original source identity changed: {relative}"
    assert sha(PAPER / name) == item["sha256"], f"Frozen public input changed: {name}"


def verify_original_sources(records):
    """Check original bytes in the monorepo, or declared exports in the release."""
    if IS_MONOREPO:
        for item in records:
            verify_original_identity(item["path"], item["sha256"])
        return {"verified": len(records), "unbundled": 0}
    exports = source_exports()
    unbundled = release_manifest()["unbundled_process_sources"]
    verified = omitted = 0
    for item in records:
        relative, expected = item["path"], item["sha256"]
        if relative in exports:
            verify_original_identity(relative, expected)
            verified += 1
        else:
            assert unbundled.get(relative) == expected, f"Undeclared unbundled source: {relative}"
            omitted += 1
    return {"verified": verified, "unbundled": omitted}
