#!/usr/bin/env python3
"""Sync canonical editorial guidance into the reviewed team distribution; no network or deletion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "plugins" / "flipbelt-editorial-office"
NAMES = ["flipbelt-" + name for name in (
    "editorial-chief", "product-editor", "size-editor", "extended-editor",
    "column-editor", "reference-desk", "editorial-review", "editorial-delivery",
)]
ADAPTERS = (
    "skills/flipbelt-editorial-chief/references/workspace-contract.md",
    "skills/flipbelt-editorial-chief/references/production-contract.md",
    "skills/flipbelt-editorial-chief/references/knowledge-operations.md",
    "skills/flipbelt-editorial-chief/references/dynamic-html.md",
    "skills/flipbelt-product-editor/references/history-routing.md",
    "skills/flipbelt-reference-desk/references/term-library.md",
    "skills/flipbelt-editorial-review/references/validation.md",
    "skills/flipbelt-editorial-delivery/references/html-publishing.md",
)
TEAM_FILES = (".codex-plugin/plugin.json", ".app.json", "README.md")
CONTRACT = "skills/flipbelt-editorial-chief/editorial-contract.json"
PROVENANCE = "SOURCE-PROVENANCE.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_hash(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for name, file_hash in sorted(files.items()):
        digest.update(f"{name}\0{file_hash}\n".encode())
    return digest.hexdigest()


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def generated(relative: str) -> bool:
    return relative in {CONTRACT, "source-manifest.json"} or relative.endswith("/editorial-link.json")


def excluded(relative: str) -> bool:
    return (generated(relative)
            or relative.startswith("assets/") and relative != "assets/flipbelt-editorial-owl.png"
            or relative.startswith("skills/flipbelt-editorial-chief/scripts/")
            or relative.startswith("skills/flipbelt-reference-desk/references/term-library-"))


def inventory(root: Path) -> dict[str, bytes]:
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlink requires explicit review")
        if path.is_file() and "__pycache__" not in path.parts and ".git" not in path.parts:
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def build(source: Path, target: Path = TARGET, check: bool = False) -> dict:
    source, target = source.resolve(), target.resolve()
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("Source and downstream must be separate directories")
    original = inventory(source)
    manifest = json.loads(original[".codex-plugin/plugin.json"])
    if manifest.get("name") != "flipbelt-editorial-office":
        raise ValueError("Source must be the canonical Editorial Office plugin")
    if {path.name for path in (source / "skills").iterdir() if path.is_dir()} != set(NAMES):
        raise ValueError("Canonical source must contain the eight approved roles")
    recorded = json.loads(original["source-manifest.json"])
    actual_skills = {name.removeprefix("skills/"): sha256(data)
                     for name, data in original.items() if name.startswith("skills/")}
    if recorded.get("files") != actual_skills:
        raise ValueError("Canonical source manifest is stale; refresh it in the sole source first")

    previous_path = target / PROVENANCE
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.is_file() else {}
    selected = {name: data for name, data in original.items()
                if name.startswith(("skills/", "assets/")) and not excluded(name)}
    for name in ADAPTERS:
        old_hash = previous.get("adapted_source_files", {}).get(name)
        if old_hash is not None and old_hash != sha256(original[name]):
            raise ValueError("Upstream adapter changed; review and update provenance before syncing: " + name)
        selected[name] = (target / name).read_bytes()
    for name in TEAM_FILES:
        selected[name] = (target / name).read_bytes()
    for name in NAMES:
        selected[f"skills/{name}/editorial-link.json"] = json_bytes({
            "contract": "../flipbelt-editorial-chief/editorial-contract.json",
            "entry_sha256": sha256(selected[f"skills/{name}/SKILL.md"]),
        })
    skill_hashes = {name.removeprefix("skills/"): sha256(data)
                    for name, data in selected.items() if name.startswith("skills/")}
    selected[CONTRACT] = json_bytes({"format_version": 1, "skills": NAMES, "files": skill_hashes})
    skill_hashes[CONTRACT.removeprefix("skills/")] = sha256(selected[CONTRACT])
    selected["source-manifest.json"] = json_bytes({"format_version": 1, "skills": NAMES, "files": skill_hashes})
    copied = {name: sha256(original[name]) for name in selected
              if name.startswith(("skills/", "assets/"))
              and name in original and name not in ADAPTERS and not generated(name)}
    provenance = {
        "schema_version": "1.0", "role": "downstream-public-distribution",
        "canonical_source": "personal-local/flipbelt-editorial-office (sole maintained source)",
        "canonical_version": manifest["version"],
        "canonical_file_count": len(original),
        "canonical_tree_sha256": tree_hash({name: sha256(data) for name, data in original.items()}),
        "target_plugin": "flipbelt-editorial-office", "copied_files": copied,
        "adapted_source_files": {name: sha256(original[name]) for name in ADAPTERS},
        "excluded_source_files": sorted(name for name in original if excluded(name)),
        "distribution_files": {name: sha256(data) for name, data in selected.items()},
        "distribution_tree_sha256": tree_hash({name: sha256(data) for name, data in selected.items()}),
        "allowed_differences": ["team semantic version and existing Workspace App reference",
                                "team workspace discovery and current-release read-only evidence",
                                "team validation, historical sources, term query and administrator handoff",
                                "omit internal snapshots, unused icons and privileged HTTP helpers",
                                "regenerate editorial links and contracts for the distributed files"],
    }
    selected[PROVENANCE] = json_bytes(provenance)
    current = inventory(target)
    extras = current.keys() - selected.keys()
    if extras:
        raise ValueError("Stale downstream files require explicit review; nothing deleted: " + ", ".join(sorted(extras)))
    if inventory(source) != original:
        raise ValueError("Canonical source changed during sync")
    if check:
        if current != selected:
            raise ValueError("Distribution differs from canonical source or reviewed metadata")
    else:
        for name, data in selected.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return {"files": len(selected), "copied": len(copied), "adapters": len(ADAPTERS), "source_unchanged": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    print(json.dumps(build(arguments.source, check=arguments.check)))
