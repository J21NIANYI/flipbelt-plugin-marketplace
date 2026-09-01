#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
EXPECTED = {
    "flipbelt-product-intelligence": 8,
    "flipbelt-color-naming": 1,
    "design-seamless-patterns": 1,
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SECRET = re.compile(
    r"(?i)(access[_-]?key|client[_-]?secret|private[_-]?key|password)\s*[:=]\s*[\"']?[a-z0-9+/_.-]{12,}"
    r"|bearer\s+[a-z0-9._-]{20,}"
)
ABSOLUTE_PATH = re.compile(r"(?i)(?:[a-z]:\\users\\|/users/|/home/)")


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


def main() -> int:
    errors: list[str] = []
    marketplace = load_json(MARKETPLACE, errors)
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
    product_manifest = load_json(product / ".codex-plugin" / "plugin.json", errors)
    app_manifest = load_json(product / ".app.json", errors)
    if product_manifest.get("apps") != "./.app.json":
        errors.append("flipbelt-product-intelligence: .app.json must be referenced")
    app = app_manifest.get("apps", {}).get("flipbelt-knowledge", {})
    if app.get("id") != "asdk_app_6a96a5e762008191a4ec2f8b129cc671":
        errors.append("flipbelt-product-intelligence: invalid Workspace App reference")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() == ".png":
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

    print("MARKETPLACE VALIDATION PASSED: plugins=3 skills=10 bundled_mcp=0 required_apps=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
