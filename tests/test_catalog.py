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
                "mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental",
                "mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control",
            },
            {pack["id"] for pack in result.packs},
        )

    def test_manifest_schema_is_json_and_exposes_required_statuses(self):
        schema = json.loads((REPO / "schemas" / "pack-manifest.schema.json").read_text())
        self.assertEqual(
            ["Static Verified", "Runtime Experimental", "Runtime Verified"],
            schema["properties"]["status"]["enum"],
        )

    def test_rules_paths_expose_each_pack_as_an_independent_cemu_leaf(self):
        expected_paths = {
            "fps-lock-30": "MH Cemu Enhancements/MH3G HD JP v96/Lock 30 FPS",
            "lobby-full-item-box": "MH Cemu Enhancements/MH3G HD JP v96/Lobby Full Item Box",
            "quest-delivery-full-item-box-experimental": (
                "MH Cemu Enhancements/MH3G HD JP v96/"
                "Quest Red Delivery Box -> Full Item Box (Experimental)"
            ),
            "quest-blue-supply-box-full-item-box-control": (
                "MH Cemu Enhancements/MH3G HD JP v96/"
                "Quest Blue Supply Box -> Full Item Box (Control)"
            ),
        }

        for feature, expected_path in expected_paths.items():
            rules = (
                REPO / "packs" / "wiiu" / "mh3g-hd" / "jp-v96" / feature / "rules.txt"
            ).read_text()
            self.assertIn(f"path = {expected_path}\n", rules)

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
            lambda path: path.write_text(
                path.read_text().replace('"status": "Runtime Verified"', '"status": "not-a-status"')
            ),
        )
        self.assertTrue(any("unknown status" in error for error in errors))

        quest_manifest = (
            "packs/wiiu/mh3g-hd/jp-v96/"
            "quest-delivery-full-item-box-experimental/manifest.json"
        )
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
            selected = self.tool.select_packs(
                result.packs,
                ["mh3g-hd-jp-v96-lobby-full-item-box"],
                include_experimental=False,
            )
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
            self.assertTrue((base / "MH3G HD JP v96 - Lobby Full Item Box" / "rules.txt").is_file())
            self.assertFalse((base / "MH3G HD JP v96 - Lock 30 FPS").exists())
            self.assertFalse(
                (base / "MH3G HD JP v96 - Quest Red Delivery Box - Full Item Box (Experimental)").exists()
            )

            self.tool.install(REPO, cemu_root, selected, reference_rpx=None, verify=False)
            self.assertTrue((base / ".install-receipt.json").is_file())

            self.tool.uninstall(cemu_root)
            self.assertFalse(base.exists())
            self.tool.uninstall(cemu_root)
            self.assertFalse(base.exists())

    def test_include_experimental_adds_experimental_packs_to_defaults(self):
        result = self.tool.validate_repository(REPO)

        selected = self.tool.select_packs(result.packs, [], include_experimental=True)

        self.assertEqual(
            {
                "mh3g-hd-jp-v96-fps-lock-30",
                "mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental",
                "mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control",
            },
            {pack["id"] for pack in selected},
        )

    def test_explicit_lobby_selection_is_verified_and_excludes_quest(self):
        result = self.tool.validate_repository(REPO)
        selected = self.tool.select_packs(
            result.packs,
            ["mh3g-hd-jp-v96-lobby-full-item-box"],
            include_experimental=False,
        )
        self.assertEqual(
            {"mh3g-hd-jp-v96-lobby-full-item-box"},
            {pack["id"] for pack in selected},
        )

    def test_lobby_candidate_maps_restricted_box_mode_to_full_mode(self):
        result = self.tool.validate_repository(REPO)
        lobby = next(pack for pack in result.packs if pack["id"] == "mh3g-hd-jp-v96-lobby-full-item-box")

        self.assertEqual("Runtime Verified", lobby["status"])
        self.assertFalse(lobby["default_install"])
        self.assertEqual("available", lobby["availability"])
        self.assertEqual(
            set(),
            {pack["id"] for pack in self.tool.select_packs(result.packs, [], include_experimental=False)},
        )
        self.assertEqual(
            {
                0x02799678: 0x38A00001,
            },
            {self.tool._number(item["address"]): self.tool._number(item["word"]) for item in lobby["preimages"]},
        )
        self.assertEqual(
            {
                0x021F0AD0: 0x9BFC6E12,
                0x021F0AF0: 0x2C1F0001,
                0x021F0AF4: 0x38000006,
                0x021F0AF8: 0x40820008,
                0x021F0AFC: 0x38000003,
                0x021F0B00: 0xB01D000C,
                0x027995F8: 0x38A00000,
                0x02799600: 0x4BA5748D,
                0x02799680: 0x4BA5740D,
            },
            {self.tool._number(item["address"]): self.tool._number(item["word"]) for item in lobby["anchors"]},
        )
        patch = (REPO / lobby["pack_dir"] / lobby["patch"]).read_text()
        self.assertIn("0x02799678 = li r5, 0", patch)
        self.assertNotIn("codecave", patch.lower())

    def test_fps_lock_records_the_unstable_runtime_result(self):
        result = self.tool.validate_repository(REPO)
        fps = next(pack for pack in result.packs if pack["id"] == "mh3g-hd-jp-v96-fps-lock-30")

        self.assertEqual("Runtime Experimental", fps["status"])
        self.assertFalse(fps["default_install"])

    def test_quest_red_delivery_box_redirect_is_narrow_and_fail_closed(self):
        result = self.tool.validate_repository(REPO)
        quest = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental"
        )

        self.assertEqual("Runtime Experimental", quest["status"])
        self.assertFalse(quest["default_install"])
        self.assertEqual("available", quest["availability"])
        self.assertEqual(
            {
                0x028C5824: 0x38800001,
                0x028C5838: 0x38A0000F,
                0x028C27C4: 0x3FE01031,
                0x028C27C8: 0x807F507C,
                0x028C27CC: 0x4B8B75F1,
                0x028C27D0: 0x807F507C,
                0x028C27D4: 0x4B8B742D,
                0x028C27D8: 0x2C030000,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in quest["preimages"]
            },
        )
        self.assertEqual(
            {
                0x020F0628: 0x7CBD2B78,
                0x020F0698: 0x7FA5EB78,
                0x020F069C: 0x38800002,
                0x020F06A0: 0x4E800421,
                0x020F06B8: 0x38A10008,
                0x020F06C4: 0x4BFFFEF1,
                0x0216B410: 0x2C000008,
                0x0216B418: 0x2C000003,
                0x0216B428: 0x2C000005,
                0x0216B430: 0x2C000007,
                0x0216B438: 0x2C040000,
                0x0216B43C: 0x4182000C,
                0x0216B440: 0x3860FFFF,
                0x0216B448: 0x38600000,
                0x021F0AD0: 0x9BFC6E12,
                0x021F0AF0: 0x2C1F0001,
                0x021F0AF4: 0x38000006,
                0x021F0AFC: 0x38000003,
                0x028A97DC: 0x38A0000E,
                0x028A97E8: 0x4BFE891D,
                0x028C2768: 0x2C1F0000,
                0x028C276C: 0x40820048,
                0x028C5828: 0x4B8A5BD5,
                0x028C582C: 0x2C030000,
                0x028C5830: 0x40820018,
                0x028C583C: 0x38800001,
                0x028C5844: 0x4BFCC8C1,
                0x028C5E78: 0x38800000,
                0x028C5E7C: 0x4BFFC874,
                0x028C5E80: 0x38800001,
                0x028C5E84: 0x4BFFC86C,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in quest["anchors"]
            },
        )
        patch = (REPO / quest["pack_dir"] / quest["patch"]).read_text()
        self.assertIn("0x028c5824 = li r4, 0", patch)
        self.assertIn("0x028c5838 = li r5, 0xe", patch)
        self.assertIn("0x028c27c4 = lis r3, 0x1031", patch)
        self.assertIn("0x028c27c8 = lwz r3, 0x44a0(r3)", patch)
        self.assertIn("0x028c27cc = mr r4, r30", patch)
        self.assertIn("0x028c27d0 = li r5, 0", patch)
        self.assertIn("0x028c27d4 = bl 0x021f0a8c", patch)
        self.assertIn("0x028c27d8 = b 0x028c27f8", patch)
        self.assertNotIn("0x021b0e90", patch.lower())
        self.assertNotIn("0x021b0f14", patch.lower())
        self.assertNotIn("codecave", patch.lower())

    def test_quest_blue_supply_box_control_is_global_and_isolated(self):
        result = self.tool.validate_repository(REPO)
        blue = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control"
        )

        self.assertEqual("Runtime Experimental", blue["status"])
        self.assertFalse(blue["default_install"])
        self.assertEqual("available", blue["availability"])
        self.assertEqual(
            {
                0x028C2770: 0x819E0E30,
                0x028C2774: 0x3D601008,
                0x028C2778: 0x39000001,
                0x028C277C: 0xC00BE204,
                0x028C2780: 0x38800000,
                0x028C2784: 0x990C0BAE,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in blue["preimages"]
            },
        )
        self.assertEqual(
            {
                0x021F0AD0: 0x9BFC6E12,
                0x021F0AF0: 0x2C1F0001,
                0x021F0AF4: 0x38000006,
                0x021F0AFC: 0x38000003,
                0x028C2768: 0x2C1F0000,
                0x028C276C: 0x40820048,
                0x028C27B4: 0x7FC3F378,
                0x028C27F8: 0x3D201008,
                0x028C5E78: 0x38800000,
                0x028C5E7C: 0x4BFFC874,
                0x028C5E80: 0x38800001,
                0x028C5E84: 0x4BFFC86C,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in blue["anchors"]
            },
        )
        patch = (REPO / blue["pack_dir"] / blue["patch"]).read_text()
        self.assertIn("0x028c2770 = lis r3, 0x1031", patch)
        self.assertIn("0x028c2774 = lwz r3, 0x44a0(r3)", patch)
        self.assertIn("0x028c2778 = mr r4, r30", patch)
        self.assertIn("0x028c277c = li r5, 0", patch)
        self.assertIn("0x028c2780 = bl 0x021f0a8c", patch)
        self.assertIn("0x028c2784 = b 0x028c27f8", patch)
        self.assertNotIn("0x021b0e90", patch.lower())
        self.assertNotIn("0x021b0f14", patch.lower())
        self.assertNotIn("0x028c27c4", patch.lower())
        self.assertNotIn("quest id", patch.lower())
        self.assertNotIn("codecave", patch.lower())

    def test_inspect_reports_installed_pack_that_is_not_enabled(self):
        result = self.tool.validate_repository(REPO)
        with tempfile.TemporaryDirectory() as tmp:
            cemu_root = Path(tmp) / "Library" / "Application Support" / "Nemessix Dev" / "cemu"
            selected = self.tool.select_packs(
                result.packs,
                ["mh3g-hd-jp-v96-fps-lock-30"],
                include_experimental=True,
            )
            self.tool.install(REPO, cemu_root, selected, reference_rpx=None, verify=False)
            self.assertTrue(
                (
                    cemu_root
                    / "data"
                    / "graphicPacks"
                    / "mh-cemu-enhancements"
                    / "MH3G HD JP v96 - Lock 30 FPS"
                    / "rules.txt"
                ).is_file()
            )
            config = cemu_root / "config" / "settings.xml"
            config.parent.mkdir(parents=True)
            config.write_text("<?xml version='1.0'?><content><GraphicPack/></content>\n")

            report = self.tool.inspect_cemu_root(cemu_root, result.packs)

            self.assertEqual("isolated", report["config_layout"])
            self.assertEqual(config, report["config_path"])
            fps = next(pack for pack in report["packs"] if pack["id"] == "mh3g-hd-jp-v96-fps-lock-30")
            self.assertTrue(fps["installed"])
            self.assertFalse(fps["enabled"])

    def test_isolated_launch_command_pins_the_requested_data_root(self):
        cemu_root = Path("/tmp/Library/Application Support/Nemessix Dev/cemu")
        app = Path("/tmp/Cemu.app")

        command = self.tool.isolated_launch_command(app, cemu_root)

        self.assertIn("NEMESSIX_CEMU_DATA_ROOT", command)
        self.assertIn("'/tmp/Library/Application Support/Nemessix Dev/cemu'", command)
        self.assertIn("/tmp/Cemu.app/Contents/MacOS/Cemu_release", command)
        with self.assertRaises(ValueError):
            self.tool.isolated_launch_command(app, Path("/tmp/not-a-nemessix-root"))

    def test_install_migrates_only_receipted_legacy_isolated_location(self):
        result = self.tool.validate_repository(REPO)
        with tempfile.TemporaryDirectory() as tmp:
            cemu_root = Path(tmp) / "Library" / "Application Support" / "Nemessix Dev" / "cemu"
            selected = self.tool.select_packs(
                result.packs,
                ["mh3g-hd-jp-v96-lobby-full-item-box"],
                include_experimental=False,
            )
            legacy = cemu_root / "graphicPacks" / "mh-cemu-enhancements"
            legacy.mkdir(parents=True)
            (legacy / ".install-receipt.json").write_text("{}\n")
            self.tool.install(REPO, cemu_root, selected, reference_rpx=None, verify=False)

            self.assertFalse(legacy.exists())
            self.assertTrue(
                (
                    cemu_root
                    / "data"
                    / "graphicPacks"
                    / "mh-cemu-enhancements"
                    / "MH3G HD JP v96 - Lobby Full Item Box"
                    / "rules.txt"
                ).is_file()
            )

    def test_uninstall_removes_receipted_legacy_isolated_location_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            cemu_root = Path(tmp) / "Library" / "Application Support" / "Nemessix Dev" / "cemu"
            legacy = cemu_root / "graphicPacks" / "mh-cemu-enhancements"
            legacy.mkdir(parents=True)
            (legacy / ".install-receipt.json").write_text("{}\n")
            foreign = cemu_root / "graphicPacks" / "foreign-pack"
            foreign.mkdir()
            (foreign / "rules.txt").write_text("foreign\n")

            self.tool.uninstall(cemu_root)

            self.assertFalse(legacy.exists())
            self.assertTrue((foreign / "rules.txt").is_file())

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
            self.assertFalse(any(name.startswith(".idea/") for name in names))


if __name__ == "__main__":
    unittest.main()
