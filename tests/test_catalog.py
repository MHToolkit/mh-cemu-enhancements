"""Repository-local checks for the portable Cemu enhancement catalog."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "mh-cemu-enhancements.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("enhancements", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool()

    def test_catalog_and_manifests_validate(self):
        result = self.tool.validate_repository(REPO)
        self.assertEqual([], result.errors, "\n".join(result.errors))
        self.assertEqual(
            {
                "mh3g-hd-jp-v96-fps-lock-30",
                "mh3g-hd-jp-v96-lobby-full-item-box",
                "mh3g-hd-jp-v96-quest-full-item-box-experimental",
            },
            {pack["id"] for pack in result.packs},
        )

    def test_manifest_schema_is_json_and_exposes_required_statuses(self):
        schema = json.loads((REPO / "schemas" / "pack-manifest.schema.json").read_text())
        self.assertEqual(
            ["Static Verified", "Runtime Experimental", "Runtime Verified"],
            schema["properties"]["status"]["enum"],
        )

    def test_validator_rejects_identity_status_and_ppc_gate_regressions(self):
        def validate_after(relative: str, edit):
            with tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "repo"
                shutil.copytree(REPO, copied, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
                path = copied / relative
                edit(path)
                return self.tool.validate_repository(copied).errors

        lobby_manifest = "packs/wiiu/mh3g-hd/jp-v96/lobby-full-item-box/manifest.json"
        errors = validate_after(
            lobby_manifest,
            lambda path: path.write_text(path.read_text().replace('"status": "Static Verified"', '"status": "not-a-status"')),
        )
        self.assertTrue(any("unknown status" in error for error in errors))

        quest_manifest = "packs/wiiu/mh3g-hd/jp-v96/quest-full-item-box-experimental/manifest.json"
        errors = validate_after(
            quest_manifest,
            lambda path: path.write_text(path.read_text().replace('"default_install": false', '"default_install": true')),
        )
        self.assertTrue(any("experimental pack" in error for error in errors))

        errors = validate_after(
            lobby_manifest,
            lambda path: path.write_text(path.read_text().replace('"title_slug": "mh3g-hd"', '"title_slug": "wrong-title"')),
        )
        self.assertTrue(any("pack_dir does not match" in error for error in errors))

        errors = validate_after(
            "packs/wiiu/mh3g-hd/jp-v96/lobby-full-item-box/patch_lobby_full_item_box.asm",
            lambda path: path.write_text(path.read_text().replace("0x348600a0", "0x00000000")),
        )
        self.assertTrue(any("module checksum is not pinned" in error for error in errors))

    def test_ppc_preimages_match_the_pinned_reference(self):
        reference = Path(
            "/Volumes/GameHub/Development/Games/Nemessix/"
            "nemessix-multi-engine-apple-design-worktree/.build/"
            "mh3g-offline-hunter-debug-20260725T132604Z/mh3g_cafe.rpx"
        )
        if not reference.is_file():
            self.skipTest("local immutable RPX reference is unavailable")
        result = self.tool.validate_repository(REPO)
        errors = self.tool.verify_reference(reference, result.packs)
        self.assertEqual([], errors, "\n".join(errors))

    def test_install_and_uninstall_are_idempotent_and_skip_experimental(self):
        result = self.tool.validate_repository(REPO)
        with tempfile.TemporaryDirectory() as tmp:
            cemu_root = Path(tmp) / "cemu"
            selected = self.tool.select_packs(result.packs, [], include_experimental=False)
            unrelated = cemu_root / "graphicPacks" / "Unrelated Pack" / "rules.txt"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("unrelated\n")
            owned_collision = cemu_root / "graphicPacks" / "mh-cemu-enhancements"
            owned_collision.mkdir()
            (owned_collision / "user-file.txt").write_text("preserve by backup\n")
            self.tool.install(REPO, cemu_root, selected, reference_rpx=None, verify=False)
            base = cemu_root / "graphicPacks" / "mh-cemu-enhancements"
            backups = list(base.parent.glob("mh-cemu-enhancements.backup-*"))
            self.assertEqual(1, len(backups))
            self.assertTrue((backups[0] / "user-file.txt").is_file())
            self.assertTrue(unrelated.is_file())
            self.assertTrue((base / "MH3G HD JP v96 - Lock 30 FPS" / "rules.txt").is_file())
            self.assertTrue((base / "MH3G HD JP v96 - Lobby Full Item Box" / "patch_lobby_full_item_box.asm").is_file())
            self.assertFalse((base / "MH3G HD JP v96 - Quest Full Item Box (Experimental)").exists())

            self.tool.install(REPO, cemu_root, selected, reference_rpx=None, verify=False)
            self.assertTrue((base / ".install-receipt.json").is_file())

            self.tool.uninstall(cemu_root)
            self.assertFalse(base.exists())
            self.tool.uninstall(cemu_root)
            self.assertFalse(base.exists())

    def test_archive_is_reproducible_and_contains_no_game_assets(self):
        result = self.tool.validate_repository(REPO)
        self.assertEqual([], result.errors, "\n".join(result.errors))
        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / "one.zip"
            two = Path(tmp) / "two.zip"
            self.tool.package_repository(REPO, one)
            self.tool.package_repository(REPO, two)
            self.assertEqual(self.tool.sha256_file(one), self.tool.sha256_file(two))
            names = self.tool.zip_member_names(one)
            self.assertNotIn("mh3g_cafe.rpx", names)
            self.assertFalse(any(name.startswith(".ruff_cache/") for name in names))


if __name__ == "__main__":
    unittest.main()
