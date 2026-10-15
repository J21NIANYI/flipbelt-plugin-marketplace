from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_marketplace as validator


class AIAssetDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.plugin = self.root / "plugins" / validator.AI_ASSET_NAME
        for name in validator.AI_ASSET_SKILLS:
            self.write(f"skills/{name}/SKILL.md", f"---\nname: {name}\n---\nSource guidance.\n")
            self.write(f"skills/{name}/references/CONNECTOR.md", "Per-user connector authorization.\n")
            self.write(f"skills/{name}/references/PILOT.md", "Private drafts and explicit confirmation.\n")
        self.write(".codex-plugin/plugin.json", json.dumps({
            "name": validator.AI_ASSET_NAME, "version": "0.1.0", "description": "AI Asset Center",
            "author": {"name": "FlipBelt"}, "skills": "./skills/",
            "interface": {"displayName": "AI Asset Center"},
        }))
        self.write("README.md", "Two Skills with separate connector dependencies.\n")
        self.write("CONNECTORS.md", "Windows local stdio MCP: 16 tools; configure separately.\n")
        self.refresh_provenance()

    def write(self, relative, value):
        path = self.plugin / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def refresh_provenance(self):
        files = {path.relative_to(self.plugin).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in self.plugin.rglob("*")
                 if path.is_file() and path.name != "SOURCE-PROVENANCE.json"}
        copied = {name: digest for name, digest in files.items() if name.startswith("skills/")}
        self.write("SOURCE-PROVENANCE.json", json.dumps({
            "schema_version": "1.0", "role": "downstream-distribution",
            "canonical_repository": "flipbelt-ai-asset-center", "canonical_commit": "a" * 40,
            "canonical_version": "0.1.0", "canonical_worktree_dirty": True,
            "source_tree_sha256": validator.tree_sha256(copied),
            "target_plugin": validator.AI_ASSET_NAME, "synced_paths": ["skills"],
            "copied_files": copied, "distribution_files": files,
            "distribution_tree_sha256": validator.tree_sha256(files),
        }))

    def errors(self):
        errors = []
        with patch.object(validator, "ROOT", self.root):
            validator.validate_ai_asset(errors)
        return errors

    def test_exact_two_skills_and_provenance_pass(self):
        self.assertEqual(self.errors(), [])

    def test_backend_or_connector_source_is_rejected_even_with_valid_hashes(self):
        self.write("backend/server.py", "server implementation\n")
        self.refresh_provenance()
        self.assertTrue(any("unexpected distribution file" in error for error in self.errors()))

    def test_bundled_mcp_or_app_is_rejected_even_with_valid_hashes(self):
        for relative in (".mcp.json", ".app.json"):
            with self.subTest(relative=relative):
                self.write(relative, "{}\n")
                self.refresh_provenance()
                self.assertTrue(any("unexpected distribution file" in error for error in self.errors()))
                (self.plugin / relative).unlink()
        self.refresh_provenance()

    def test_secret_local_path_or_fabricated_app_id_is_rejected(self):
        examples = (
            ("password = " + "x" * 24, "possible secret"),
            ("C" + ":" + chr(92) + "Users" + chr(92) + "person", "local absolute path"),
            ("asdk" + "_app_" + "a" * 32, "Workspace App ID"),
        )
        for content, expected in examples:
            with self.subTest(expected=expected):
                self.write("README.md", content)
                self.refresh_provenance()
                self.assertTrue(any(expected in error for error in self.errors()))

    def test_extra_skill_is_rejected_even_with_valid_hashes(self):
        self.write("skills/unapproved/SKILL.md", "Unapproved skill\n")
        self.refresh_provenance()
        self.assertTrue(any("exact two-Skill" in error for error in self.errors()))

    def test_tampered_skill_and_provenance_are_rejected(self):
        entry = "skills/" + sorted(validator.AI_ASSET_SKILLS)[0] + "/SKILL.md"
        self.write(entry, "Changed without refreshing source evidence.\n")
        errors = self.errors()
        self.assertTrue(any("copied Skill hashes" in error for error in errors))
        self.assertTrue(any("distribution file or tree hashes" in error for error in errors))

    def test_shipped_marketplace_preserves_existing_plugin_contracts(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = validator.main()
        self.assertEqual(result, 0, output.getvalue())


if __name__ == "__main__":
    unittest.main()
