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
    "flipbelt-ai-asset-center": 2,
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


AI_ASSET_NAME = "flipbelt-ai-asset-center"
AI_ASSET_TARGET = "team"
AI_ASSET_REMOTE_URL = "https://jtzhzt.flipbeltchina.com/mcp"
AI_ASSET_KNOWLEDGE_APP_ID = "asdk_app_6a96a5e762008191a4ec2f8b129cc671"

AI_ASSET_SKILLS = {
    "flipbelt-ai-asset-registrar",
    "flipbelt-ai-workflow-incubator",
}


def validate_ai_asset(errors: list[str]) -> None:
    plugin = ROOT / "plugins" / AI_ASSET_NAME
    manifest = load_json(plugin / ".codex-plugin/plugin.json", errors)
    provenance = load_json(plugin / "SOURCE-PROVENANCE.json", errors)
    version = manifest.get("version")
    remote = version == "0.2.0"
    if (manifest.get("name") != AI_ASSET_NAME or not isinstance(version, str)
            or version not in {"0.1.0", "0.2.0"}):
        errors.append("ai-asset: plugin name or version mismatch")
    for key in ("description", "author", "interface"):
        if not manifest.get(key):
            errors.append(f"ai-asset: missing manifest field {key}")
    if manifest.get("skills") != "./skills/":
        errors.append("ai-asset: skills path must be ./skills/")

    app_id = None
    if not remote:
        if any(key in manifest for key in ("apps", "mcpServers")):
            errors.append("ai-asset: legacy connection dependencies must not be bundled")
    elif AI_ASSET_TARGET == "team":
        if manifest.get("apps") != "./.app.json" or "mcpServers" in manifest:
            errors.append("ai-asset: remote team distribution requires only the Workspace App reference")
        app_manifest = load_json(plugin / ".app.json", errors)
        apps = app_manifest.get("apps")
        entry = apps.get("flipbelt-ai-assets") if isinstance(apps, dict) else None
        app_id = entry.get("id") if isinstance(entry, dict) else None
        if (not isinstance(app_id, str) or len(app_id) > 200
                or not re.fullmatch(r"asdk_app_[A-Za-z0-9][A-Za-z0-9_-]*", app_id)):
            errors.append("ai-asset: a normalized asset Workspace App ID is required")
        elif app_id == AI_ASSET_KNOWLEDGE_APP_ID:
            errors.append("ai-asset: the read-only Knowledge App cannot bind the asset service")
        if (app_manifest != {"apps": {"flipbelt-ai-assets": {"id": app_id, "required": True}}}
                or not isinstance(entry, dict) or entry.get("required") is not True):
            errors.append("ai-asset: the asset Workspace App must be the sole required App")
    else:
        if manifest.get("mcpServers") != "./.mcp.json" or "apps" in manifest:
            errors.append("ai-asset: remote personal distribution requires only the MCP reference")
        mcp = load_json(plugin / ".mcp.json", errors)
        if mcp != {"mcpServers": {"flipbelt-ai-assets": {"type": "http", "url": AI_ASSET_REMOTE_URL}}}:
            errors.append("ai-asset: only the exact public asset HTTP MCP without credentials is allowed")

    if AI_ASSET_TARGET == "personal":
        root_manifest = load_json(plugin / "plugin.json", errors)
        if any(root_manifest.get(key) != manifest.get(key) for key in ("name", "version", "description")):
            errors.append("ai-asset: standard discovery manifest identity mismatch")
        if any(key in root_manifest for key in ("skills", "mcpServers", "apps", "interface", "policy")):
            errors.append("ai-asset: standard discovery manifest contains host-specific fields")

    skill_files = {f"skills/{name}/{relative}"
                   for name in AI_ASSET_SKILLS
                   for relative in ("SKILL.md", "references/CONNECTOR.md", "references/PILOT.md")}
    allowed_files = skill_files | {
        ".codex-plugin/plugin.json", "README.md", "CONNECTORS.md", "SOURCE-PROVENANCE.json",
    }
    if AI_ASSET_TARGET == "personal":
        allowed_files.add("plugin.json")
    if remote:
        allowed_files.add(".app.json" if AI_ASSET_TARGET == "team" else ".mcp.json")
    actual = {}
    for path in sorted(plugin.rglob("*")):
        relative = path.relative_to(plugin).as_posix()
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            errors.append(f"ai-asset: symlink or reparse point is forbidden: {relative}")
            continue
        if not path.is_file():
            continue
        actual[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        if relative not in allowed_files:
            errors.append(f"ai-asset: unexpected distribution file: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"ai-asset: binary file is forbidden: {relative}")
            continue
        if SECRET.search(text):
            errors.append(f"ai-asset: possible secret pattern: {relative}")
        if re.search(r"(?i)(?:\b[a-z]:[\\/]|/users/|/home/)", text):
            errors.append(f"ai-asset: local absolute path is forbidden: {relative}")
        if not remote and "asdk_app_" in text:
            errors.append(f"ai-asset: Workspace App ID is forbidden: {relative}")
        elif remote:
            # Prefix examples with an ellipsis are documentation, not App references.
            ids = re.findall(r"\b(?:plugin_)?asdk_app_[A-Za-z0-9][A-Za-z0-9_-]*\b", text)
            allowed_ids = {app_id} if AI_ASSET_TARGET == "team" and isinstance(app_id, str) and relative in {
                ".app.json", "SOURCE-PROVENANCE.json",
            } else set()
            if any(value not in allowed_ids for value in ids):
                errors.append(f"ai-asset: unexpected Workspace App ID: {relative}")
    if set(actual) != allowed_files:
        errors.append("ai-asset: exact two-Skill distribution file set mismatch")
    for name in AI_ASSET_SKILLS:
        entry = plugin / "skills" / name / "SKILL.md"
        if entry.is_file() and not re.search(
                rf"(?m)^name:\s*{re.escape(name)}\s*$", entry.read_text(encoding="utf-8")):
            errors.append(f"ai-asset: Skill frontmatter name mismatch: {name}")
    connection = plugin / "CONNECTORS.md"
    if connection.is_file():
        text = connection.read_text(encoding="utf-8").lower()
        markers = ("oauth", "13", AI_ASSET_REMOTE_URL) if remote else ("windows", "stdio", "16")
        if any(marker not in text for marker in markers):
            errors.append("ai-asset: missing remote OAuth connection description" if remote
                          else "ai-asset: missing local connector dependency description")

    if provenance.get("schema_version") != "1.0" or provenance.get("role") != "downstream-distribution":
        errors.append("ai-asset: provenance schema or role mismatch")
    expected_repository = ("https://github.com/FlipBelt/Digital-Asset-Management-Space" if remote
                           else "flipbelt-ai-asset-center")
    if (provenance.get("canonical_repository") != expected_repository
            or remote and provenance.get("canonical_project") != "flipbelt-ai-asset-center"):
        errors.append("ai-asset: canonical repository mismatch")
    if not re.fullmatch(r"[0-9a-f]{40}", str(provenance.get("canonical_commit", ""))):
        errors.append("ai-asset: canonical commit must be a full Git SHA")
    if provenance.get("canonical_version") != version or provenance.get("target_plugin") != AI_ASSET_NAME:
        errors.append("ai-asset: provenance version or target mismatch")
    if provenance.get("synced_paths") != ["skills"]:
        errors.append("ai-asset: synced paths mismatch")
    if not isinstance(provenance.get("canonical_worktree_dirty"), bool):
        errors.append("ai-asset: canonical worktree state is required")
    if not re.fullmatch(r"[0-9a-f]{64}", str(provenance.get("source_tree_sha256", ""))):
        errors.append("ai-asset: source tree SHA-256 is required")
    copied = {relative: digest for relative, digest in actual.items() if relative in skill_files}
    if provenance.get("copied_files") != copied:
        errors.append("ai-asset: copied Skill hashes mismatch")
    if remote:
        expected_profile = "workspace-app-candidate" if AI_ASSET_TARGET == "team" else "remote-oauth-candidate"
        if (provenance.get("target_host") != AI_ASSET_TARGET
                or provenance.get("connection_profile") != expected_profile
                or provenance.get("remote_mcp_url") != AI_ASSET_REMOTE_URL):
            errors.append("ai-asset: remote profile or service provenance mismatch")
        if "workspace_app_id" not in provenance or provenance.get("workspace_app_id") != app_id:
            errors.append("ai-asset: Workspace App provenance mismatch")
        for field in ("workspace_app_binding_verified", "remote_deployment_verified", "host_runtime_verified"):
            if not isinstance(provenance.get(field), bool):
                errors.append(f"ai-asset: explicit verification state is required: {field}")
        source_files = provenance.get("source_files")
        expected_sources = {".agents/" + relative for relative in skill_files} | {
            "plugin/metadata.json", "plugin/README.md", "plugin/CONNECTORS.md",
        }
        if (not isinstance(source_files, dict) or set(source_files) != expected_sources
                or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
                       for value in source_files.values())):
            errors.append("ai-asset: exact canonical source file hashes are required")
        else:
            if provenance.get("source_tree_sha256") != tree_sha256(source_files):
                errors.append("ai-asset: canonical source tree digest mismatch")
            if any(source_files.get(".agents/" + relative) != digest for relative, digest in copied.items()):
                errors.append("ai-asset: copied Skills differ from canonical source hashes")
    distribution = {relative: digest for relative, digest in actual.items()
                    if relative != "SOURCE-PROVENANCE.json"}
    if (provenance.get("distribution_files") != distribution
            or provenance.get("distribution_tree_sha256") != tree_sha256(distribution)):
        errors.append("ai-asset: distribution file or tree hashes mismatch")


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
        if name == AI_ASSET_NAME:
            asset_manifest = load_json(ROOT / "plugins" / name / ".codex-plugin/plugin.json", errors)
            if asset_manifest.get("version") == "0.2.0" and entry.get("version") != "0.2.0":
                errors.append("ai-asset: marketplace version must match the remote plugin")

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
    validate_ai_asset(errors)

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

    asset_app = int((ROOT / "plugins" / AI_ASSET_NAME / ".app.json").is_file())
    print(f"MARKETPLACE VALIDATION PASSED: plugins={len(EXPECTED)} skills={sum(EXPECTED.values())} bundled_mcp=0 app_backed_plugins={2 + asset_app} shared_apps={1 + asset_app}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
