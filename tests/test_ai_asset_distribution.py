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

    def read_json(self, relative):
        return json.loads((self.plugin / relative).read_text(encoding="utf-8"))

    def refresh_provenance(self):
        files = {path.relative_to(self.plugin).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in self.plugin.rglob("*")
                 if path.is_file() and path.name != "SOURCE-PROVENANCE.json"}
        copied = {name: digest for name, digest in files.items() if name.startswith("skills/")}
        version = self.read_json(".codex-plugin/plugin.json")["version"]
        evidence = {
            "schema_version": "1.0", "role": "downstream-distribution",
            "canonical_repository": "flipbelt-ai-asset-center", "canonical_commit": "a" * 40,
            "canonical_version": version, "canonical_worktree_dirty": True,
            "source_tree_sha256": validator.tree_sha256(copied),
            "target_plugin": validator.AI_ASSET_NAME, "synced_paths": ["skills"],
            "copied_files": copied, "distribution_files": files,
            "distribution_tree_sha256": validator.tree_sha256(files),
        }
        if version == "0.2.0":
            sources = {".agents/" + name: digest for name, digest in copied.items()}
            sources.update({"plugin/" + name: files[name] for name in ("README.md", "CONNECTORS.md")})
            sources["plugin/metadata.json"] = hashlib.sha256(b"synthetic source metadata fixture").hexdigest()
            evidence.update({
                "canonical_repository": "https://github.com/FlipBelt/Digital-Asset-Management-Space",
                "canonical_project": "flipbelt-ai-asset-center",
                "target_host": validator.AI_ASSET_TARGET,
                "connection_profile": ("workspace-app-candidate" if validator.AI_ASSET_TARGET == "team"
                                       else "remote-oauth-candidate"),
                "remote_mcp_url": validator.AI_ASSET_REMOTE_URL,
                "workspace_app_id": self.fixture_app_id if validator.AI_ASSET_TARGET == "team" else None,
                "workspace_app_binding_verified": False, "remote_deployment_verified": False,
                "host_runtime_verified": False, "source_files": sources,
                "source_tree_sha256": validator.tree_sha256(sources),
            })
        self.write("SOURCE-PROVENANCE.json", json.dumps(evidence))

    def remote_fixture(self):
        # This ID exists only in a temporary test package; it is not a real App binding.
        self.fixture_app_id = "asdk" + "_app_" + "syntheticAssetFixture123"
        manifest = self.read_json(".codex-plugin/plugin.json")
        manifest["version"] = "0.2.0"
        if validator.AI_ASSET_TARGET == "team":
            manifest["apps"] = "./.app.json"
            self.write(".app.json", json.dumps({
                "apps": {"flipbelt-ai-assets": {"id": self.fixture_app_id, "required": True}},
            }))
        else:
            manifest["mcpServers"] = "./.mcp.json"
            self.write(".mcp.json", json.dumps({
                "mcpServers": {"flipbelt-ai-assets": {"type": "http", "url": validator.AI_ASSET_REMOTE_URL}},
            }))
            root_manifest = self.read_json("plugin.json")
            root_manifest["version"] = "0.2.0"
            self.write("plugin.json", json.dumps(root_manifest))
        self.write(".codex-plugin/plugin.json", json.dumps(manifest))
        self.write("README.md", "OAuth candidate; format example: " + "asdk" + "_app_...\n")
        self.write("CONNECTORS.md", "Remote OAuth: 13 tools; " + validator.AI_ASSET_REMOTE_URL + "\n")
        self.refresh_provenance()

    def change_provenance(self, **changes):
        evidence = self.read_json("SOURCE-PROVENANCE.json")
        evidence.update(changes)
        self.write("SOURCE-PROVENANCE.json", json.dumps(evidence))

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

    def test_remote_profile_passes_without_claiming_runtime_verification(self):
        self.remote_fixture()
        self.assertEqual(self.errors(), [])
        evidence = self.read_json("SOURCE-PROVENANCE.json")
        self.assertIs(evidence["host_runtime_verified"], False)
        self.assertIs(evidence["remote_deployment_verified"], False)

    def test_remote_connection_reference_cannot_be_missing_or_mixed(self):
        self.remote_fixture()
        manifest = self.read_json(".codex-plugin/plugin.json")
        del manifest["apps" if validator.AI_ASSET_TARGET == "team" else "mcpServers"]
        self.write(".codex-plugin/plugin.json", json.dumps(manifest))
        self.refresh_provenance()
        self.assertTrue(any("requires only" in error for error in self.errors()))
        self.remote_fixture()
        extra = ".mcp.json" if validator.AI_ASSET_TARGET == "team" else ".app.json"
        self.write(extra, "{}\n")
        self.refresh_provenance()
        self.assertTrue(any("unexpected distribution file" in error for error in self.errors()))

    def test_remote_missing_connection_file_is_rejected(self):
        self.remote_fixture()
        path = ".app.json" if validator.AI_ASSET_TARGET == "team" else ".mcp.json"
        (self.plugin / path).unlink()
        self.refresh_provenance()
        self.assertTrue(any("exact two-Skill" in error for error in self.errors()))

    def test_malformed_manifest_version_is_rejected_without_crashing(self):
        self.remote_fixture()
        for version in ([], {}, None, "0.3.0"):
            with self.subTest(version=version):
                manifest = self.read_json(".codex-plugin/plugin.json")
                manifest["version"] = version
                self.write(".codex-plugin/plugin.json", json.dumps(manifest))
                self.assertTrue(any("plugin name or version mismatch" in error for error in self.errors()))

    def test_remote_connection_payload_is_strict(self):
        self.remote_fixture()
        if validator.AI_ASSET_TARGET == "team":
            for identifier in (None, [], {}, True, "plugin_" + self.fixture_app_id,
                               validator.AI_ASSET_KNOWLEDGE_APP_ID):
                with self.subTest(identifier=identifier):
                    self.write(".app.json", json.dumps({
                        "apps": {"flipbelt-ai-assets": {"id": identifier, "required": True}},
                    }))
                    self.refresh_provenance()
                    self.assertTrue(self.errors())
            for required in (False, 1, 1.0, "true", None):
                with self.subTest(required=required):
                    self.remote_fixture()
                    self.write(".app.json", json.dumps({
                        "apps": {"flipbelt-ai-assets": {"id": self.fixture_app_id, "required": required}},
                    }))
                    self.refresh_provenance()
                    self.assertTrue(any("sole required App" in error for error in self.errors()))
        else:
            for server in (
                {"type": "http", "url": "https://wiki.flipbeltchina.com/mcp"},
                {"type": "http", "url": validator.AI_ASSET_REMOTE_URL + "?test=1"},
                {"type": "http", "url": validator.AI_ASSET_REMOTE_URL, "headers": {}},
                {"command": "python", "args": ["server.py"]},
            ):
                with self.subTest(server=server):
                    self.write(".mcp.json", json.dumps({"mcpServers": {"flipbelt-ai-assets": server}}))
                    self.refresh_provenance()
                    self.assertTrue(any("exact public asset HTTP MCP" in error for error in self.errors()))

    def test_remote_app_identity_must_match_provenance_and_not_leak_into_prose(self):
        self.remote_fixture()
        wrong_id = "asdk" + "_app_" + "otherSyntheticFixture456"
        self.change_provenance(workspace_app_id=wrong_id)
        self.assertTrue(any("App provenance" in error for error in self.errors()))
        self.remote_fixture()
        self.write("README.md", "Unexpected concrete reference: " + self.fixture_app_id)
        self.refresh_provenance()
        self.assertTrue(any("unexpected Workspace App ID" in error for error in self.errors()))

    def test_remote_profile_and_explicit_verification_states_are_required(self):
        self.remote_fixture()
        for change in (
            {"connection_profile": "local-legacy"},
            {"remote_mcp_url": "https://wiki.flipbeltchina.com/mcp"},
            {"target_host": "qwenwork"},
            {"host_runtime_verified": "yes"},
            {"remote_deployment_verified": None},
            {"workspace_app_binding_verified": 1},
        ):
            with self.subTest(change=change):
                self.refresh_provenance()
                self.change_provenance(**change)
                self.assertTrue(self.errors())
        self.refresh_provenance()
        evidence = self.read_json("SOURCE-PROVENANCE.json")
        del evidence["workspace_app_id"]
        self.write("SOURCE-PROVENANCE.json", json.dumps(evidence))
        self.assertTrue(any("App provenance" in error for error in self.errors()))

    def test_remote_canonical_source_tree_and_skill_copy_are_verified(self):
        self.remote_fixture()
        evidence = self.read_json("SOURCE-PROVENANCE.json")
        evidence["source_files"]["plugin/metadata.json"] = "b" * 64
        self.change_provenance(source_files=evidence["source_files"])
        self.assertTrue(any("source tree digest" in error for error in self.errors()))
        self.refresh_provenance()
        evidence = self.read_json("SOURCE-PROVENANCE.json")
        source_skill = ".agents/skills/" + sorted(validator.AI_ASSET_SKILLS)[0] + "/SKILL.md"
        evidence["source_files"][source_skill] = "c" * 64
        self.change_provenance(source_files=evidence["source_files"],
                               source_tree_sha256=validator.tree_sha256(evidence["source_files"]))
        self.assertTrue(any("differ from canonical source" in error for error in self.errors()))
        self.refresh_provenance()
        evidence = self.read_json("SOURCE-PROVENANCE.json")
        del evidence["source_files"]["plugin/metadata.json"]
        self.change_provenance(source_files=evidence["source_files"])
        self.assertTrue(any("exact canonical source file" in error for error in self.errors()))

    def test_remote_backend_or_extra_skill_remains_forbidden(self):
        self.remote_fixture()
        self.write("backend/server.py", "Not public plugin content.\n")
        self.refresh_provenance()
        self.assertTrue(any("unexpected distribution file" in error for error in self.errors()))

    def test_shipped_marketplace_preserves_existing_plugin_contracts(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = validator.main()
        self.assertEqual(result, 0, output.getvalue())

    def test_marketplace_asset_version_cannot_lag_remote_plugin(self):
        original_load = validator.load_json

        def stale_marketplace(path, errors):
            value = original_load(path, errors)
            if path == validator.MARKETPLACE:
                for entry in value["plugins"]:
                    if entry["name"] == validator.AI_ASSET_NAME:
                        entry["version"] = "0.1.0"
            return value

        output = io.StringIO()
        with patch.object(validator, "load_json", side_effect=stale_marketplace):
            with contextlib.redirect_stdout(output):
                result = validator.main()
        self.assertEqual(result, 1)
        self.assertIn("marketplace version must match", output.getvalue())


if __name__ == "__main__":
    unittest.main()
