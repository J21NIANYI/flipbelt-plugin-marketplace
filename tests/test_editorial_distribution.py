from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_editorial import ADAPTERS, NAMES, TEAM_FILES, build, inventory, sha256


class EditorialSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source = Path(self.temporary.name) / "source"
        self.target = Path(self.temporary.name) / "target"
        for name in NAMES:
            self.write(self.source, f"skills/{name}/SKILL.md", f"canonical role {name}\n")
        for relative in ADAPTERS:
            self.write(self.source, relative, "canonical environment guidance\n")
            self.write(self.target, relative, "reviewed team environment guidance\n")
        self.write(self.source, ".codex-plugin/plugin.json", json.dumps({
            "name": "flipbelt-editorial-office", "version": "0.1.0",
        }))
        for relative in TEAM_FILES:
            self.write(self.target, relative, "reviewed team metadata\n")
        self.write(self.source, "skills/flipbelt-reference-desk/references/term-library-private.md", "internal snapshot\n")
        self.write(self.source, "skills/flipbelt-editorial-chief/scripts/helper.py", "privileged helper\n")
        self.refresh_manifest()

    def write(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def refresh_manifest(self):
        files = {name.removeprefix("skills/"): sha256(data)
                 for name, data in inventory(self.source).items() if name.startswith("skills/")}
        self.write(self.source, "source-manifest.json", json.dumps({"files": files}))

    def test_sync_preserves_source_and_excludes_internal_material(self):
        before = inventory(self.source)
        build(self.source, self.target)
        self.assertEqual(inventory(self.source), before)
        self.assertFalse((self.target / "skills/flipbelt-reference-desk/references/term-library-private.md").exists())
        self.assertFalse((self.target / "skills/flipbelt-editorial-chief/scripts/helper.py").exists())
        provenance = json.loads((self.target / "SOURCE-PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertNotIn(".codex-plugin/plugin.json", provenance["copied_files"])
        for relative, digest in provenance["copied_files"].items():
            self.assertEqual(sha256((self.target / relative).read_bytes()), digest)
        build(self.source, self.target, check=True)

    def test_unreviewed_extra_stops_before_any_write(self):
        self.write(self.target, "unexpected.md", "unreviewed file\n")
        before = inventory(self.target)
        with self.assertRaisesRegex(ValueError, "Stale downstream"):
            build(self.source, self.target)
        self.assertEqual(inventory(self.target), before)

    def test_changed_upstream_adapter_requires_review(self):
        build(self.source, self.target)
        self.write(self.source, ADAPTERS[0], "new canonical guidance\n")
        self.refresh_manifest()
        before = inventory(self.target)
        with self.assertRaisesRegex(ValueError, "Upstream adapter changed"):
            build(self.source, self.target)
        self.assertEqual(inventory(self.target), before)

    def test_stale_source_manifest_stops_before_any_write(self):
        self.write(self.source, f"skills/{NAMES[0]}/SKILL.md", "changed source role\n")
        before = inventory(self.target)
        with self.assertRaisesRegex(ValueError, "source manifest is stale"):
            build(self.source, self.target)
        self.assertEqual(inventory(self.target), before)

    def test_same_source_and_target_are_rejected(self):
        before = inventory(self.source)
        with self.assertRaisesRegex(ValueError, "separate directories"):
            build(self.source, self.source)
        self.assertEqual(inventory(self.source), before)


if __name__ == "__main__":
    unittest.main()
