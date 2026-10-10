#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PROVENANCE = ROOT / "SOURCE-PROVENANCE.json"
EXPECTED = {
    "flipbelt-product-intelligence": 8,
    "flipbelt-color-naming": 1,
    "design-seamless-patterns": 1,
    "flipbelt-editorial-office": 8,
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SECRET = re.compile(
    r"(?i)(access[_-]?key|client[_-]?secret|private[_-]?key|password)\s*[:=]\s*[\"']?[a-z0-9+/_.-]{12,}"
    r"|bearer\s+[a-z0-9._-]{20,}"
)
ABSOLUTE_PATH = re.compile(r"(?i)(?:\b[a-z]:[\\/]|/users/|/home/)")


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


def synced_tree_sha256(plugin: Path) -> tuple[int, str]:
    files = sorted(
        (path for area in ("shared", "skills") for path in (plugin / area).rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(plugin).as_posix(),
    )
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(plugin).as_posix()
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(f"{relative}\0{file_hash}\n".encode())
    return len(files), digest.hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


def tree_sha256(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in sorted(files.items()):
        digest.update(f"{relative}\0{file_hash}\n".encode())
    return digest.hexdigest()


def validate_editorial(errors: list[str]) -> None:
    from sync_editorial import ADAPTERS, CONTRACT, NAMES, PROVENANCE, generated

    plugin = ROOT / "plugins" / "flipbelt-editorial-office"
    provenance = load_json(plugin / PROVENANCE, errors)
    actual = file_hashes(plugin)
    actual.pop(PROVENANCE, None)
    if provenance.get("role") != "downstream-public-distribution":
        errors.append("editorial: missing downstream provenance role")
    if provenance.get("target_plugin") != "flipbelt-editorial-office":
        errors.append("editorial: provenance target mismatch")
    if not provenance.get("canonical_version") or not re.fullmatch(r"[0-9a-f]{64}", str(provenance.get("canonical_tree_sha256", ""))):
        errors.append("editorial: missing canonical snapshot version or digest")
    if provenance.get("distribution_files") != actual or provenance.get("distribution_tree_sha256") != tree_sha256(actual):
        errors.append("editorial: distributed files or tree digest mismatch")
    copied = provenance.get("copied_files", {})
    if not isinstance(copied, dict):
        copied = {}
        errors.append("editorial: copied_files must be an object")
    for relative, digest in copied.items():
        if actual.get(relative) != digest:
            errors.append(f"editorial: canonical copy changed: {relative}")
    for name in NAMES:
        if f"skills/{name}/SKILL.md" not in copied:
            errors.append(f"editorial: role entry must remain a canonical copy: {name}")
    adapted = provenance.get("adapted_source_files", {})
    if not isinstance(adapted, dict) or set(adapted) != set(ADAPTERS):
        errors.append("editorial: reviewed adapter list mismatch")
    expected_copied = {relative for relative in actual
                       if relative.startswith(("skills/", "assets/"))
                       and relative not in ADAPTERS and not generated(relative)}
    if set(copied) != expected_copied:
        errors.append("editorial: unrecorded or unexpected canonical copy")
    if any("/term-library-" in relative or "/scripts/" in relative for relative in actual):
        errors.append("editorial: internal term snapshots or privileged helpers distributed")

    skill_hashes = {relative.removeprefix("skills/"): digest
                    for relative, digest in actual.items() if relative.startswith("skills/")}
    source_manifest = load_json(plugin / "source-manifest.json", errors)
    contract = load_json(plugin / CONTRACT, errors)
    if source_manifest.get("skills") != NAMES or source_manifest.get("files") != skill_hashes:
        errors.append("editorial: source-manifest integrity mismatch")
    contract_hashes = dict(skill_hashes)
    contract_hashes.pop(CONTRACT.removeprefix("skills/"), None)
    if contract.get("skills") != NAMES or contract.get("files") != contract_hashes:
        errors.append("editorial: editorial-contract integrity mismatch")
    for name in NAMES:
        link = load_json(plugin / f"skills/{name}/editorial-link.json", errors)
        if link != {"contract": "../flipbelt-editorial-chief/editorial-contract.json",
                    "entry_sha256": skill_hashes.get(f"{name}/SKILL.md")}:
            errors.append(f"editorial: invalid role contract link: {name}")
    for path in (plugin / "skills").rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip("<>")
            if not target or re.match(r"^[a-zA-Z]+:", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(plugin.resolve()) or not resolved.is_file():
                errors.append(f"{path.relative_to(ROOT)}: missing or escaping dependency: {target}")
    manifest = load_json(plugin / ".codex-plugin/plugin.json", errors)
    app_manifest = load_json(plugin / ".app.json", errors)
    app = app_manifest.get("apps", {}).get("flipbelt-knowledge", {})
    if manifest.get("apps") != "./.app.json" or app.get("id") != "asdk_app_6a96a5e762008191a4ec2f8b129cc671" or app.get("required") is not True:
        errors.append("editorial: existing required Workspace App must be referenced")
    for key in ("logo", "logoDark", "composerIcon"):
        icon = manifest.get("interface", {}).get(key)
        path = plugin / str(icon)
        if icon != "./assets/flipbelt-editorial-owl.png" or not path.is_file() or not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"editorial: invalid {key}")


def main() -> int:
    errors: list[str] = []
    marketplace = load_json(MARKETPLACE, errors)
    provenance = load_json(PROVENANCE, errors)
    if marketplace.get("name") != "flipbelt-team":
        errors.append("marketplace name must be flipbelt-team")

    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        entries = []
        errors.append("marketplace plugins must be an array")
    names = [entry.get("name") for entry in entries if isinstance(entry, dict)]
    if names != list(EXPECTED):
        errors.append(f"marketplace order mismatch: {names}")

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("marketplace entry must be an object")
            continue
        name = entry.get("name")
        source = entry.get("source", {})
        policy = entry.get("policy", {})
        if source != {"source": "local", "path": f"./plugins/{name}"}:
            errors.append(f"{name}: invalid local source")
        if policy.get("installation") not in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}:
            errors.append(f"{name}: invalid installation policy")
        if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            errors.append(f"{name}: invalid authentication policy")
        if not entry.get("category"):
            errors.append(f"{name}: category is required")

    for name, expected_skill_count in EXPECTED.items():
        plugin = ROOT / "plugins" / name
        manifest_path = plugin / ".codex-plugin" / "plugin.json"
        manifest = load_json(manifest_path, errors)
        if manifest.get("name") != name:
            errors.append(f"{name}: manifest name mismatch")
        version = manifest.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            errors.append(f"{name}: version must be strict semver")
        for key in ("description", "author", "skills", "interface"):
            if not manifest.get(key):
                errors.append(f"{name}: missing manifest field {key}")
        if manifest.get("skills") != "./skills/":
            errors.append(f"{name}: skills path must be ./skills/")
        if (plugin / ".mcp.json").exists() or "mcpServers" in manifest:
            errors.append(f"{name}: bundled MCP config would make the plugin desktop-only")

        skill_root = plugin / "skills"
        skills = sorted(path for path in skill_root.iterdir() if path.is_dir()) if skill_root.is_dir() else []
        if len(skills) != expected_skill_count:
            errors.append(f"{name}: expected {expected_skill_count} skills, found {len(skills)}")
        for skill in skills:
            skill_md = skill / "SKILL.md"
            if not skill_md.is_file():
                errors.append(f"{skill.relative_to(ROOT)}: missing SKILL.md")
                continue
            text = skill_md.read_text(encoding="utf-8")
            if not re.search(rf"(?m)^name:\s*{re.escape(skill.name)}\s*$", text):
                errors.append(f"{skill.relative_to(ROOT)}: frontmatter name mismatch")

    product = ROOT / "plugins" / "flipbelt-product-intelligence"
    source_commit = provenance.get("canonical_commit")
    if provenance.get("role") != "downstream-public-distribution":
        errors.append("SOURCE-PROVENANCE.json: invalid distribution role")
    if provenance.get("canonical_repository") != "flipbelt-product-intelligence (local-only)":
        errors.append("SOURCE-PROVENANCE.json: invalid canonical repository")
    if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        errors.append("SOURCE-PROVENANCE.json: canonical_commit must be a full Git SHA")
    if provenance.get("canonical_version") != "0.2.1":
        errors.append("SOURCE-PROVENANCE.json: unexpected canonical version")
    if provenance.get("target_plugin") != "flipbelt-product-intelligence":
        errors.append("SOURCE-PROVENANCE.json: target plugin mismatch")
    if provenance.get("synced_paths") != ["shared", "skills"]:
        errors.append("SOURCE-PROVENANCE.json: synced paths mismatch")
    file_count, tree_hash = synced_tree_sha256(product)
    if provenance.get("synced_file_count") != file_count:
        errors.append("SOURCE-PROVENANCE.json: synced file count mismatch")
    if provenance.get("synced_tree_sha256") != tree_hash:
        errors.append("SOURCE-PROVENANCE.json: synced tree SHA-256 mismatch")
    product_manifest = load_json(product / ".codex-plugin" / "plugin.json", errors)
    app_manifest = load_json(product / ".app.json", errors)
    if product_manifest.get("apps") != "./.app.json":
        errors.append("flipbelt-product-intelligence: .app.json must be referenced")
    app = app_manifest.get("apps", {}).get("flipbelt-knowledge", {})
    if app.get("id") != "asdk_app_6a96a5e762008191a4ec2f8b129cc671":
        errors.append("flipbelt-product-intelligence: invalid Workspace App reference")
    review = product / "skills" / "flipbelt-review-specialist"
    for relative in [
        "references/document-review-contract.md",
        "scripts/compare_size_chart.ps1",
        "evals/cases.json",
    ]:
        if not (review / relative).is_file():
            errors.append(f"flipbelt-product-intelligence: missing review parity asset {relative}")
    review_text = (review / "SKILL.md").read_text(encoding="utf-8") if (review / "SKILL.md").is_file() else ""
    for marker in ["PASS", "FAIL", "MISSING", "NO-SOURCE", "search_flipbelt_kb", "get_flipbelt_page", "get_flipbelt_asset"]:
        if marker not in review_text:
            errors.append(f"flipbelt-product-intelligence: Review Specialist missing contract marker {marker}")

    validate_editorial(errors)

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in path.parts for part in (".git", ".tmp", "__pycache__")) or path.suffix.lower() == ".png":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{path.relative_to(ROOT)}: unexpected binary file")
            continue
        if path.resolve() != Path(__file__).resolve():
            if SECRET.search(text):
                errors.append(f"{path.relative_to(ROOT)}: possible secret pattern")
            if ABSOLUTE_PATH.search(text):
                errors.append(f"{path.relative_to(ROOT)}: user-specific absolute path")
        if any(line.endswith((" ", "\t")) for line in text.splitlines()):
            errors.append(f"{path.relative_to(ROOT)}: trailing whitespace")
        if re.search(r"(?m)^(<<<<<<< .+|=======|>>>>>>> .+)$", text):
            errors.append(f"{path.relative_to(ROOT)}: merge marker")

    if errors:
        print("MARKETPLACE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"MARKETPLACE VALIDATION PASSED: plugins={len(EXPECTED)} skills={sum(EXPECTED.values())} bundled_mcp=0 app_backed_plugins=2 shared_apps=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
