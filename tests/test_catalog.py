"""Repository-local checks for the portable Cemu enhancement catalog."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "mh-cemu-enhancements.py"
RELEASE_SCRIPT = REPO / "scripts" / "next_release_version.py"

STATIC_ARM_PACKS = {
    5: "sharpness-never-decreases",
    6: "critical-display-hidden",
    7: "infinite-hp",
    11: "awakening",
    13: "underwater-speed-x2",
    14: "rock-steady",
    15: "unbreakable-pickaxes-bug-nets",
    16: "max-health-150",
    17: "theft-immunity",
    18: "mud-snow-immunity",
    21: "evade-extender",
    26: "bio-status-immunity",
    27: "status-immunity",
    29: "power-coating-anywhere",
    33: "guard-plus-2",
    34: "guard-up",
    35: "flaming-aura",
    36: "speed-eating-plus-2",
    37: "infinite-stamina",
    38: "focus",
    39: "combination-success-100",
    40: "maximum-combination-yield",
    41: "high-grade-earplugs",
    44: "windproof-high",
    45: "stun-immunity",
    46: "poison-paralysis-sleep-immunity",
    47: "tremor-resistance",
    48: "evasion-plus-2",
    49: "minimum-bowgun-recoil",
    50: "bowgun-steadiness",
    51: "minds-eye",
    52: "bow-auto-reload",
    53: "speed-sharpening",
    54: "map-always-visible",
    55: "capture-guru",
    56: "auto-marker-small-monsters",
    59: "faster-carve-gather",
    60: "fast-gathering",
    61: "fast-placement",
    63: "climate-temperature-adaptation",
    64: "rock-steady-activated",
    65: "combat-experience-enhancer",
    72: "affinity-100",
}

EXTERNAL_EQUIPMENT_PACKS = {
    "mh3g-hd-jp-v96-equipment-production-unlock",
    "mh3g-hd-jp-v96-equipment-crafting-upgrade-no-materials",
    "mh3g-hd-jp-v96-equipment-crafting-upgrade-no-money",
}

FPS60_FIX_PACKS = {
    "mh3g-hd-jp-v96-60fps-camera-speed": "60fps-camera-speed-fix",
    "mh3g-hd-jp-v96-60fps-hammer-golf-swing-fix": "60fps-hammer-golf-swing-fix",
    "mh3g-hd-jp-v96-60fps-knockback-distance": "60fps-knockback-distance-fix",
}


def static_pack_id(source_index: int, slug: str) -> str:
    return f"mh3g-hd-jp-v96-static-{source_index:02d}-{slug}"


def load_tool():
    spec = importlib.util.spec_from_file_location("enhancements", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_release_tool():
    spec = importlib.util.spec_from_file_location("next_release_version", RELEASE_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool()
        cls.release_tool = load_release_tool()

    def test_automatic_release_version_is_monotonic_and_idempotent(self):
        choose = self.release_tool.choose_release_version
        self.assertEqual((0, 1, 0), choose([], [], []))
        self.assertEqual(
            (0, 1, 24),
            choose([], ["mh-cemu-enhancements-0.1.24.zip"], []),
        )
        self.assertEqual(
            (0, 1, 25),
            choose(
                ["v0.1.24"],
                ["mh-cemu-enhancements-0.1.24.zip"],
                [],
            ),
        )
        self.assertEqual(
            (0, 1, 25),
            choose(
                ["v0.1.24", "not-a-release"],
                ["mh-cemu-enhancements-0.1.24.zip"],
                ["v0.1.25"],
            ),
        )

    def test_catalog_and_manifests_validate(self):
        result = self.tool.validate_repository(REPO)
        self.assertEqual([], result.errors, "\n".join(result.errors))
        self.assertEqual(
            {
                "mh3g-hd-jp-v96-fps-lock-30",
                "mh3g-hd-jp-v96-fps-lock-44",
                "mh3g-hd-jp-v96-lobby-full-item-box",
                "mh3g-hd-jp-v96-custom-felyne-food-skills",
                "mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental",
                "mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control",
                "mh3g-hd-jp-v96-quest-red-blue-full-item-box-experimental",
            }
            | EXTERNAL_EQUIPMENT_PACKS
            | set(FPS60_FIX_PACKS)
            | {
                static_pack_id(source_index, slug)
                for source_index, slug in STATIC_ARM_PACKS.items()
            },
            {pack["id"] for pack in result.packs},
        )

    def test_60fps_fixes_are_independent_bilingual_default_off_leaves(self):
        result = self.tool.validate_repository(REPO)
        packs = {pack["id"]: pack for pack in result.packs}

        for pack_id, directory in FPS60_FIX_PACKS.items():
            pack = packs[pack_id]
            self.assertEqual("Runtime Experimental", pack["status"])
            self.assertFalse(pack["default_install"])
            self.assertFalse(pack["auto_experimental_install"])
            self.assertEqual("available", pack["availability"])
            self.assertEqual(
                f"packs/wiiu/mh3g-hd/jp-v96/{directory}",
                pack["pack_dir"],
            )
            self.assertTrue(pack["preimages"])
            self.assertIn(" / ", pack["summary"])

            package_dir = REPO / pack["pack_dir"]
            self.assertTrue((package_dir / pack["rules"]).is_file())
            self.assertTrue((package_dir / pack["patch"]).is_file())
            rules = (package_dir / pack["rules"]).read_text()
            self.assertIn(" / ", next(line for line in rules.splitlines() if line.startswith("name = ")))
            self.assertIn(" / ", next(line for line in rules.splitlines() if line.startswith("description = ")))

    def test_60fps_fixes_preserve_control_flow_and_exact_patch_boundaries(self):
        result = self.tool.validate_repository(REPO)
        packs = {pack["id"]: pack for pack in result.packs}

        camera = packs["mh3g-hd-jp-v96-60fps-camera-speed"]
        self.assertEqual(
            {
                0x02286F74: 0x2C000000,
                0x02286F7C: 0x4182002C,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in camera["anchors"]
            },
        )
        camera_dir = REPO / camera["pack_dir"]
        camera_patch = (camera_dir / camera["patch"]).read_text().lower()
        self.assertEqual(2, camera_patch.count("srwi    r25, r25, 8"))
        self.assertNotIn("cmpwi   r0", camera_patch)

        hammer = packs["mh3g-hd-jp-v96-60fps-hammer-golf-swing-fix"]
        self.assertEqual(
            {0x0287F43C: 0xED6C002A},
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in hammer["preimages"]
            },
        )
        self.assertEqual(
            {0x0287F440: 0x3908FFFF},
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in hammer["anchors"]
            },
        )
        hammer_dir = REPO / hammer["pack_dir"]
        hammer_patch = (hammer_dir / hammer["patch"]).read_text().lower()
        self.assertNotIn("0x0287f440 = nop", hammer_patch)

        for pack_id in FPS60_FIX_PACKS:
            pack = packs[pack_id]
            rules = (REPO / pack["pack_dir"] / pack["rules"]).read_text()
            self.assertNotIn("[Option]", rules)
            self.assertIn("Runtime Experimental", rules)

    def test_43_static_arm_conversions_are_independent_bilingual_default_off_leaves(self):
        result = self.tool.validate_repository(REPO)
        packs = {
            pack["source_cheat_entries"][0]: pack
            for pack in result.packs
            if pack.get("conversion_kind") == "3ds-arm-static-to-wiiu-ppc"
        }

        self.assertEqual(set(STATIC_ARM_PACKS), set(packs))
        self.assertEqual(43, len(packs))
        for source_index, slug in STATIC_ARM_PACKS.items():
            pack = packs[source_index]
            self.assertEqual(static_pack_id(source_index, slug), pack["id"])
            self.assertEqual("Runtime Experimental", pack["status"])
            self.assertFalse(pack["default_install"])
            self.assertFalse(pack["auto_experimental_install"])
            self.assertEqual("available", pack["availability"])
            self.assertEqual([source_index], pack["source_cheat_entries"])
            self.assertTrue(pack["preimages"])
            self.assertEqual(len(pack["preimages"]), len({item["address"] for item in pack["preimages"]}))
            self.assertIn(" / ", pack["summary"])
            self.assertIn(" / ", pack["name_bilingual"])

            package_dir = REPO / pack["pack_dir"]
            rules = (package_dir / pack["rules"]).read_text()
            patch = (package_dir / pack["patch"]).read_text()
            self.assertIn("3DS Static Cheats", rules)
            self.assertIn(f"{source_index:02d} ", rules)
            self.assertIn("中文", rules)
            self.assertIn("English", rules)
            self.assertIn("默认关闭", rules)
            self.assertIn("Disabled by default", rules)
            self.assertIn("Runtime Experimental", rules)
            self.assertIn("中文", patch)
            self.assertIn("English", patch)

            description = next(
                line for line in rules.splitlines() if line.startswith("description = ")
            )
            self.assertTrue(description.startswith("description = 中文：效果："))
            for required_heading in (
                "边界：",
                "验证：",
                "来源/状态：",
                "/ English: Effect:",
                "Scope:",
                "Verify:",
                "Source/status:",
            ):
                self.assertIn(required_heading, description)
            self.assertGreaterEqual(len(description), 500)
            self.assertNotIn("PPC 编译器复制/合并的路径数量", description)

    def test_static_arm_conversions_can_be_explicitly_installed_with_44_fps(self):
        result = self.tool.validate_repository(REPO)
        selected_ids = ["mh3g-hd-jp-v96-fps-lock-44"] + [
            static_pack_id(source_index, slug)
            for source_index, slug in STATIC_ARM_PACKS.items()
        ]

        selected = self.tool.select_packs(
            result.packs,
            selected_ids,
            include_experimental=True,
        )

        self.assertEqual(set(selected_ids), {pack["id"] for pack in selected})
        self.assertEqual(44, len(selected))

    def test_external_equipment_cheats_preserve_source_semantics_and_preimages(self):
        result = self.tool.validate_repository(REPO)
        packs = {pack["id"]: pack for pack in result.packs}
        self.assertLessEqual(EXTERNAL_EQUIPMENT_PACKS, packs.keys())

        unlock = packs["mh3g-hd-jp-v96-equipment-production-unlock"]
        no_materials = packs[
            "mh3g-hd-jp-v96-equipment-crafting-upgrade-no-materials"
        ]
        no_money = packs["mh3g-hd-jp-v96-equipment-crafting-upgrade-no-money"]

        for pack in (unlock, no_materials, no_money):
            expected_status = "Runtime Verified"
            self.assertEqual(expected_status, pack["status"])
            self.assertFalse(pack["default_install"])
            self.assertFalse(pack["auto_experimental_install"])
            self.assertEqual("available", pack["availability"])
            rules = (REPO / pack["pack_dir"] / pack["rules"]).read_text()
            patch = (REPO / pack["pack_dir"] / pack["patch"]).read_text()
            self.assertIn("中文", rules)
            self.assertIn("English", rules)
            self.assertIn(expected_status, rules)
            self.assertIn("中文", patch)
            self.assertIn("English", patch)

        shared_group = "mh3g-hd-jp-v96-equipment-unlock-materials"
        self.assertEqual(shared_group, unlock["exclusive_group"])
        self.assertEqual(shared_group, no_materials["exclusive_group"])
        self.assertNotIn("exclusive_group", no_money)

        self.assertEqual(
            {0x02198FC8: 0x4182000C},
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in unlock["preimages"]
            },
        )
        unlock_patch = (REPO / unlock["pack_dir"] / unlock["patch"]).read_text().lower()
        self.assertIn("0x02198fc8 = nop", unlock_patch)

        count_call_preimages = {
            0x021C4014: 0x4BFD7611,
            0x021C4060: 0x4BFD75C5,
            0x021C40B0: 0x4BFD7575,
            0x021CB7C8: 0x4BFCFE5D,
            0x021D25F0: 0x4BFC9035,
            0x021D48B4: 0x4BFC6D71,
            0x021D4918: 0x4BFC6D0D,
            0x021D49FC: 0x4BFC6C29,
            0x021D4A80: 0x4BFC6BA5,
            0x021D80E0: 0x4BFC3545,
            0x021ECA44: 0x4BFAEBE1,
            0x021EEFEC: 0x4BFAC639,
            0x021EF95C: 0x4BFABCC9,
            0x021F79A8: 0x4BFA3C7D,
            0x02206D6C: 0x4BF948B9,
            0x0220967C: 0x4BF91FA9,
            0x0221B2B4: 0x4BF80371,
            0x0221BC38: 0x4BF7F9ED,
            0x0221C09C: 0x4BF7F589,
            0x0221C44C: 0x4BF7F1D9,
            0x0221C548: 0x4BF7F0DD,
            0x02226FB0: 0x4BF74675,
            0x02228298: 0x4BF7338D,
            0x02238858: 0x4BF62DCD,
            0x0269504C: 0x4BB065D9,
        }
        expected_no_materials = {
            0x02182C30: 0x48018935,
            0x02182C90: 0x480188D5,
            0x02198FC8: 0x4182000C,
            **count_call_preimages,
        }
        self.assertEqual(
            expected_no_materials,
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in no_materials["preimages"]
            },
        )
        self.assertEqual(28, len(no_materials["preimages"]))
        no_materials_patch = (
            REPO / no_materials["pack_dir"] / no_materials["patch"]
        ).read_text().lower()
        for address in count_call_preimages | {0x02182C30: 0, 0x02182C90: 0}:
            self.assertIn(f"0x{address:08x} = li r3, 99", no_materials_patch)
        self.assertIn("0x02198fc8 = nop", no_materials_patch)
        self.assertNotIn("0x021f74ac =", no_materials_patch)
        exempt_anchor = next(
            item
            for item in no_materials["anchors"]
            if self.tool._number(item["address"]) == 0x021F74AC
        )
        self.assertEqual(0x4BFA4179, self.tool._number(exempt_anchor["word"]))

        self.assertEqual(
            {
                0x021CDC7C: 0x4804F69D,
                0x0220B584: 0x48011D95,
                0x02206ECC: 0x4801459D,
                0x0221B694: 0x4BFFFDD5,
                0x0221C850: 0x4BFFF645,
                0x0221C96C: 0x4BFFFB69,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in no_money["preimages"]
            },
        )
        no_money_patch = (REPO / no_money["pack_dir"] / no_money["patch"]).read_text().lower()
        self.assertIn("0x021cdc7c = li r3, 0", no_money_patch)
        self.assertIn("0x0220b584 = li r3, 0", no_money_patch)
        self.assertIn("0x02206ecc = li r3, 0", no_money_patch)
        self.assertIn("0x0221b694 = li r3, 0", no_money_patch)
        self.assertIn("0x0221c850 = li r3, 0", no_money_patch)
        self.assertIn("0x0221c96c = li r3, 0", no_money_patch)
        self.assertNotIn("0x0215a86c =", no_money_patch)
        self.assertNotIn("0x0221b6a0 =", no_money_patch)
        self.assertNotIn("0x0221d224 =", no_money_patch)
        self.assertNotIn("0x026febec =", no_money_patch)
        self.assertNotIn("0x026fec14 =", no_money_patch)
        self.assertNotIn("0x02709644 =", no_money_patch)
        self.assertNotIn("0x02709668 =", no_money_patch)
        preserved_anchors = {
            self.tool._number(item["address"]): self.tool._number(item["word"])
            for item in no_money["anchors"]
        }
        self.assertEqual(0x40800028, preserved_anchors[0x0215A86C])
        self.assertEqual(0x90740008, preserved_anchors[0x02206ED4])
        self.assertEqual(0x90650004, preserved_anchors[0x021CDC94])
        self.assertEqual(0x81480004, preserved_anchors[0x021CDAD0])
        self.assertEqual(0x7C8A00D0, preserved_anchors[0x021CDAD8])
        self.assertEqual(0x4BFCF47D, preserved_anchors[0x021CDADC])
        self.assertEqual(0x9061000C, preserved_anchors[0x0220B58C])
        self.assertEqual(0x7CDBC12E, preserved_anchors[0x0220BB20])
        self.assertEqual(0x7D7BC12E, preserved_anchors[0x0220BB90])
        self.assertEqual(0x8005031C, preserved_anchors[0x0220BF64])
        self.assertEqual(0x4BF90FE9, preserved_anchors[0x0220BF70])
        self.assertEqual(0x8106031C, preserved_anchors[0x0220C554])
        self.assertEqual(0x4BF909F9, preserved_anchors[0x0220C560])
        self.assertEqual(0x38FD031C, preserved_anchors[0x0220C9F0])
        self.assertEqual(0x4800FD35, preserved_anchors[0x0220C9FC])
        self.assertEqual(0x9421FFC0, preserved_anchors[0x0221C730])
        self.assertEqual(0x3BE00000, preserved_anchors[0x0221C754])
        self.assertEqual(0x7FEBA92E, preserved_anchors[0x0221C784])
        self.assertEqual(0x4BF3D579, preserved_anchors[0x0221C79C])
        self.assertEqual(0x90750000, preserved_anchors[0x0221C854])
        self.assertEqual(0x90750000, preserved_anchors[0x0221C970])
        self.assertEqual(0x80A9031C, preserved_anchors[0x026A74F4])
        self.assertEqual(0x9421FFE0, preserved_anchors[0x0221D224])
        self.assertEqual(0x4BB1E639, preserved_anchors[0x026FEBEC])
        self.assertEqual(0x4BB1E611, preserved_anchors[0x026FEC14])
        self.assertEqual(0x4BB13BE1, preserved_anchors[0x02709644])
        self.assertEqual(0x4BB13BBD, preserved_anchors[0x02709668])

    def test_runtime_feedback_fixes_cover_lethal_hp_and_normal_skill_query_paths(self):
        result = self.tool.validate_repository(REPO)
        packs = {
            pack["source_cheat_entries"][0]: pack
            for pack in result.packs
            if pack.get("conversion_kind") == "3ds-arm-static-to-wiiu-ppc"
        }

        hp = packs[7]
        self.assertEqual(
            {
                0x02865FF8: 0xB18A0640,
                0x02866004: 0xB18A0640,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in hp["preimages"]
            },
        )
        hp_patch = (REPO / hp["pack_dir"] / hp["patch"]).read_text()
        self.assertIn("0x02865ff8 = nop", hp_patch)
        self.assertIn("0x02866004 = nop", hp_patch)

        combat = packs[65]
        self.assertEqual(
            {0x02890B14: 0x7C082040},
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in combat["preimages"]
            },
        )
        combat_patch = (REPO / combat["pack_dir"] / combat["patch"]).read_text()
        self.assertIn("0x02890b14 = cmplw r8, r8", combat_patch)
        self.assertNotIn("0x02890ae4 =", combat_patch)

        mapping = json.loads(
            (REPO / "docs" / "research" / "mh3g-static-arm-mapping.json").read_text()
        )
        rows = {entry["source_index"]: entry for entry in mapping["entries"]}
        self.assertEqual(["0x02865ff8", "0x02866004"], rows[7]["ppc_addresses"])
        self.assertEqual(["0x02890b14"], rows[65]["ppc_addresses"])

    def test_underwater_speed_corrects_displacement_not_only_action_rate(self):
        """#13 must cover ordinary-swim state 9 without altering its shared entry scalar."""
        result = self.tool.validate_repository(REPO)
        underwater = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-static-13-underwater-speed-x2"
        )

        preimages = {
            self.tool._number(item["address"]): self.tool._number(item["word"])
            for item in underwater["preimages"]
        }
        special_state_displacement_preimages = {
            0x028C6BDC: 0xC18AE224,
            0x028C7654: 0xC18BE224,
            0x028C76DC: 0xC18BE224,
            0x028C7744: 0xC18BE224,
            0x028C8C34: 0xC009E224,
            0x028C9BDC: 0xC1A9E224,
            0x028C9C9C: 0xC1A9E224,
        }
        ordinary_swim_preimages = {
            0x028C7B18: 0xC169E2D0,
            0x028C7E6C: 0xEC0907F2,
            0x028C7FE0: 0xEC0907F2,
        }
        expected_preimages = {
            **special_state_displacement_preimages,
            **ordinary_swim_preimages,
        }
        self.assertEqual(
            expected_preimages,
            {address: preimages[address] for address in expected_preimages},
        )

        patch = (REPO / underwater["pack_dir"] / underwater["patch"]).read_text().lower()
        for address in (0x028C7654, 0x028C76DC, 0x028C7744):
            self.assertIn(f"0x{address:08x} = lfs f12, -0x1e0c(r11)", patch)
        self.assertIn("0x028c6bdc = lfs f12, -0x1e0c(r10)", patch)
        self.assertIn("0x028c8c34 = lfs f0, -0x1e0c(r9)", patch)
        for address in (0x028C9BDC, 0x028C9C9C):
            self.assertIn(f"0x{address:08x} = lfs f13, -0x1e0c(r9)", patch)
        self.assertIn("0x028c7b18 = lfs f11, -0x1e08(r9)", patch)
        for address in (0x028C7E6C, 0x028C7FE0):
            self.assertIn(f"0x{address:08x} = fmr f0, f9", patch)
        self.assertNotIn("0x028c7924 =", patch)

        mapping = json.loads(
            (REPO / "docs" / "research" / "mh3g-static-arm-mapping.json").read_text()
        )
        row = next(entry for entry in mapping["entries"] if entry["source_index"] == 13)
        self.assertEqual(23, row["ppc_patch_count"])
        self.assertEqual(
            [f"0x{address:08x}" for address in sorted(expected_preimages)],
            [
                address
                for address in row["ppc_addresses"]
                if int(address, 16) in expected_preimages
            ],
        )
        risks = "\n".join(underwater["known_risks"])
        self.assertIn("动作表现加速", risks)
        self.assertIn("action-rate acceleration", risks.lower())
        self.assertIn("0.1.21", risks)
        self.assertIn("状态 9", risks)
        self.assertIn("original 3ds", risks.lower())

    def test_feedback_sensitive_packs_explain_isolated_gameplay_conditions(self):
        result = self.tool.validate_repository(REPO)
        packs = {
            pack["source_cheat_entries"][0]: pack
            for pack in result.packs
            if pack.get("conversion_kind") == "3ds-arm-static-to-wiiu-ppc"
        }
        expected_guidance = {
            13: ("同一路线计时", "time the same underwater route"),
            21: ("固定武器", "fixed weapon"),
            34: ("原本不可防御", "normally unblockable"),
            35: ("小型怪物行为", "small-monster behavior"),
            44: ("特殊或脚本化吹飞", "special or scripted knockback"),
            50: ("自带左右偏移", "built-in left/right deviation"),
            60: ("关闭 #59", "disable #59"),
        }

        for source_index, phrases in expected_guidance.items():
            with self.subTest(source_index=source_index):
                risks = "\n".join(packs[source_index]["known_risks"])
                self.assertIn(phrases[0], risks)
                self.assertIn(phrases[1], risks.lower())

    def test_skill_effect_comparisons_require_disabling_broad_skill_enhancer(self):
        result = self.tool.validate_repository(REPO)
        packs = {
            pack["source_cheat_entries"][0]: pack
            for pack in result.packs
            if pack.get("conversion_kind") == "3ds-arm-static-to-wiiu-ppc"
        }
        for source_index in (13, 21, 34, 50, 60):
            with self.subTest(source_index=source_index):
                risks = "\n".join(packs[source_index]["known_risks"])
                self.assertIn("关闭 #65", risks)
                self.assertIn("disable #65", risks.lower())
                rules = (
                    REPO / packs[source_index]["pack_dir"] / packs[source_index]["rules"]
                ).read_text()
                self.assertIn("关闭 #65", rules)
                self.assertIn("disable #65", rules.lower())

    def test_custom_felyne_food_skills_requires_explicit_experimental_selection(self):
        result = self.tool.validate_repository(REPO)
        pack_id = "mh3g-hd-jp-v96-custom-felyne-food-skills"

        with self.assertRaisesRegex(ValueError, "--include-experimental"):
            self.tool.select_packs(result.packs, [pack_id], include_experimental=False)

        selected = self.tool.select_packs(
            result.packs,
            [pack_id],
            include_experimental=True,
        )
        self.assertEqual([pack_id], [pack["id"] for pack in selected])

    def test_manifest_schema_is_json_and_exposes_required_statuses(self):
        schema = json.loads((REPO / "schemas" / "pack-manifest.schema.json").read_text())
        self.assertEqual(
            ["Static Verified", "Runtime Experimental", "Runtime Verified"],
            schema["properties"]["status"]["enum"],
        )

    def test_rules_paths_expose_each_pack_as_an_independent_cemu_leaf(self):
        expected_paths = {
            "fps-lock-30": "MH Cemu Enhancements/MH3G HD JP v96/Lock 30 FPS",
            "fps-lock-44": "MH Cemu Enhancements/MH3G HD JP v96/Lock 44 FPS (3DS Conversion)",
            "lobby-full-item-box": "MH Cemu Enhancements/MH3G HD JP v96/Lobby Full Item Box",
            "custom-felyne-food-skills": (
                "MH Cemu Enhancements/MH3G HD JP v96/Custom Felyne Food Skills"
            ),
            "quest-delivery-full-item-box-experimental": (
                "MH Cemu Enhancements/MH3G HD JP v96/"
                "Quest Red Delivery Box -> Full Item Box (Experimental)"
            ),
            "quest-blue-supply-box-full-item-box-control": (
                "MH Cemu Enhancements/MH3G HD JP v96/"
                "Quest Blue Supply Box -> Full Item Box (Control)"
            ),
            "quest-red-blue-full-item-box-experimental": (
                "MH Cemu Enhancements/MH3G HD JP v96/"
                "Quest Red & Blue Boxes -> Full Item Box (Experimental)"
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

        fps44_manifest = "packs/wiiu/mh3g-hd/jp-v96/fps-lock-44/manifest.json"
        errors = validate_after(
            fps44_manifest,
            lambda path: path.write_text(
                path.read_text().replace(
                    '"exclusive_group": "mh3g-hd-jp-v96-vsync-frequency"',
                    '"exclusive_group": "bad exclusive group"',
                )
            ),
        )
        self.assertTrue(any("exclusive_group" in error for error in errors))

        errors = validate_after(
            fps44_manifest,
            lambda path: path.write_text(path.read_text().replace('"source_cheat_entries": [71, 73]', '"source_cheat_entries": ["71"]')),
        )
        self.assertTrue(any("source_cheat_entries" in error for error in errors))

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

    def test_reference_verifier_accepts_file_backed_data_preimages(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference = Path(tmp) / "synthetic.rpx"
            section_offset = 0x40
            text_offset = 0x100
            data_offset = 0x110
            text = struct.pack(">I", 0x3B20040B)
            data = bytes(0x10) + struct.pack(">I", 0xC1900000)
            image = bytearray(data_offset + len(data))
            image[:52] = struct.pack(
                ">16sHHIIIIIHHHHHH",
                b"\x7fELF" + bytes(12),
                2,
                20,
                1,
                0,
                0,
                section_offset,
                0,
                52,
                0,
                0,
                40,
                3,
                0,
            )
            headers = (
                bytes(40)
                + struct.pack(">IIIIIIIIII", 0, 1, 6, 0x02000020, text_offset, len(text), 0, 0, 4, 0)
                + struct.pack(">IIIIIIIIII", 0, 1, 2, 0x1007E100, data_offset, len(data), 0, 0, 4, 0)
            )
            image[section_offset:section_offset + len(headers)] = headers
            image[text_offset:text_offset + len(text)] = text
            image[data_offset:data_offset + len(data)] = data
            reference.write_bytes(image)

            pack = {
                "id": "synthetic-text-and-data-pack",
                "source": {"rpx_sha256": self.tool.sha256_file(reference)},
                "preimages": [
                    {"address": "0x02000020", "word": "0x3B20040B"},
                    {"address": "0x1007E110", "word": "0xC1900000"},
                ],
                "anchors": [],
            }

            self.assertEqual([], self.tool.verify_reference(reference, [pack]))

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

    def test_include_experimental_adds_only_available_fps_packs(self):
        result = self.tool.validate_repository(REPO)

        selected = self.tool.select_packs(result.packs, [], include_experimental=True)

        self.assertEqual(
            {
                "mh3g-hd-jp-v96-fps-lock-30",
                "mh3g-hd-jp-v96-fps-lock-44",
            },
            {pack["id"] for pack in selected},
        )

    def test_old_quest_candidates_are_runtime_blocked(self):
        result = self.tool.validate_repository(REPO)

        with self.assertRaisesRegex(ValueError, "runtime-blocked"):
            self.tool.select_packs(
                result.packs,
                ["mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental"],
                include_experimental=True,
            )

        with self.assertRaisesRegex(ValueError, "runtime-blocked"):
            self.tool.select_packs(
                result.packs,
                ["mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control"],
                include_experimental=True,
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

    def test_44_fps_is_a_bilingual_3ds_conversion_and_is_mutually_exclusive_with_30(self):
        result = self.tool.validate_repository(REPO)
        fps = next(pack for pack in result.packs if pack["id"] == "mh3g-hd-jp-v96-fps-lock-44")

        self.assertEqual("Runtime Experimental", fps["status"])
        self.assertFalse(fps["default_install"])
        self.assertEqual("available", fps["availability"])
        self.assertEqual("mh3g-hd-jp-v96-vsync-frequency", fps["exclusive_group"])
        self.assertEqual([], fps.get("preimages", []))
        self.assertEqual([71, 73], fps["source_cheat_entries"])

        rules = (REPO / fps["pack_dir"] / fps["rules"]).read_text()
        self.assertIn("name = MH3G HD JP v96 - Lock 44 FPS (3DS Conversion)", rules)
        self.assertIn("44 FPS", rules)
        self.assertIn("不要与 30 FPS", rules)
        self.assertIn("Do not enable together with 30 FPS", rules)
        self.assertIn("vsyncFrequency = 44", rules)

    def test_custom_felyne_food_skills_has_complete_bilingual_three_slot_contract(self):
        result = self.tool.validate_repository(REPO)
        custom = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-custom-felyne-food-skills"
        )

        self.assertEqual("Runtime Experimental", custom["status"])
        self.assertFalse(custom["default_install"])
        self.assertFalse(custom["auto_experimental_install"])
        self.assertEqual("available", custom["availability"])
        self.assertIn(" / ", custom["name_bilingual"])
        self.assertIn(" / ", custom["summary"])
        risks = "\n".join(custom["known_risks"])
        self.assertIn("重新吃饭", risks)
        self.assertIn("eat again", risks.lower())
        self.assertIn("重启或重新载入游戏", risks)
        self.assertIn("restart or reload the title", risks.lower())
        self.assertIn("互斥", risks)
        self.assertIn("incompatible", risks.lower())

        self.assertEqual(
            {
                0x021D865C: 0x38E00000,
                0x021D8660: 0x38000000,
                0x021D8664: 0x7C080378,
                0x021D8668: 0x7C083800,
                0x021D866C: 0x40800028,
                0x021D8670: 0x7CDA38AE,
                0x021D8674: 0x550C083C,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in custom["preimages"]
            },
        )
        anchors = {
            self.tool._number(item["address"]): self.tool._number(item["word"])
            for item in custom["anchors"]
        }
        self.assertLessEqual(
            {
                0x021D8568: 0x3F400001,
                0x021D856C: 0x84DD5C50,
                0x021D8570: 0x3B5A83F4,
                0x021D8574: 0x84794278,
                0x021D857C: 0x7F7ED214,
                0x021D8658: 0x4BFFF341,
                0x021D86B4: 0xA1980006,
                0x021D8740: 0x54EC083C,
                0x021D8744: 0x817F0140,
                0x021D8748: 0x7D3B6214,
                0x021D874C: 0x7C19622E,
                0x021D8750: 0x7D4B6214,
                0x021D8754: 0x38E70001,
                0x021D8758: 0xB009000A,
                0x021D875C: 0x2C070003,
                0x021D8760: 0xB00A0E3E,
                0x021D8764: 0x4180FFDC,
                0x021D8768: 0x3C601020,
                0x021D876C: 0x8063D9CC,
                0x021D8774: 0x4BF42581,
            }.items(),
            anchors.items(),
        )

        rules = (REPO / custom["pack_dir"] / custom["rules"]).read_text()
        self.assertIn("$skill1:int = 0x06", rules)
        self.assertIn("$skill2:int = 0x36", rules)
        self.assertIn("$skill3:int = 0x00", rules)
        category_variables = {
            "技能槽 1 / Skill Slot 1": "$skill1:int",
            "技能槽 2 / Skill Slot 2": "$skill2:int",
            "技能槽 3 / Skill Slot 3": "$skill3:int",
        }
        presets = []
        for block in re.split(r"(?m)^\[Preset\]\s*$", rules)[1:]:
            fields = {}
            for line in block.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    fields[key.strip()] = value.strip()
            presets.append(fields)

        self.assertEqual(198, len(presets))
        for category, variable in category_variables.items():
            category_presets = [preset for preset in presets if preset.get("category") == category]
            self.assertEqual(66, len(category_presets))
            values = [int(preset[variable], 0) for preset in category_presets]
            self.assertEqual(list(range(0x42)), values)
            for value, preset in zip(values, category_presets, strict=True):
                self.assertTrue(preset["name"].startswith(f"{value:02X} "))
                self.assertIn(" / ", preset["name"])

        patch = (REPO / custom["pack_dir"] / custom["patch"]).read_text()
        self.assertEqual(
            [f"0x{address:08x}" for address in range(0x021D865C, 0x021D8678, 4)],
            re.findall(r"(?mi)^(0x[0-9a-f]{8})\s*=", patch),
        )
        for instruction in (
            "0x021d865c = li r0, $skill1",
            "0x021d8660 = sth r0, 0x0068(r31)",
            "0x021d8664 = li r0, $skill2",
            "0x021d8668 = sth r0, 0x006a(r31)",
            "0x021d866c = li r0, $skill3",
            "0x021d8670 = sth r0, 0x006c(r31)",
            "0x021d8674 = b 0x021d86b4",
        ):
            self.assertIn(instruction, patch)
        self.assertNotIn("codecave", patch.lower())

    def test_custom_felyne_food_skills_overrides_generator_slots_before_native_writeback(self):
        """Selected IDs must replace the temporary meal slots before native writeback."""
        result = self.tool.validate_repository(REPO)
        custom = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-custom-felyne-food-skills"
        )
        patch = (REPO / custom["pack_dir"] / custom["patch"]).read_text()

        # The generator's temporary slots are the source consumed by the native
        # final writeback loop. Replacing only the later mirror writes leaves
        # the source meal slots generated/random and can diverge from the result.
        for instruction in (
            "0x021d865c = li r0, $skill1",
            "0x021d8660 = sth r0, 0x0068(r31)",
            "0x021d8664 = li r0, $skill2",
            "0x021d8668 = sth r0, 0x006a(r31)",
            "0x021d866c = li r0, $skill3",
            "0x021d8670 = sth r0, 0x006c(r31)",
            "0x021d8674 = b 0x021d86b4",
        ):
            self.assertIn(instruction, patch)

        # Keep the original finalizer's state-mirroring loop untouched.
        for address in range(0x021D8740, 0x021D8768, 4):
            self.assertNotIn(f"0x{address:08x} =", patch.lower())

    def test_3ds_cheat_conversion_matrix_covers_the_live_source_without_silent_drops(self):
        matrix = json.loads(
            (REPO / "docs" / "research" / "mh3g-3ds-cheat-conversion.json").read_text()
        )

        self.assertEqual(1, matrix["schema_version"])
        self.assertEqual("0004000000048100", matrix["source"]["title_id"])
        self.assertEqual(
            "6add19f3237edcefd05d3bd9cdbf96662e82452c32b51ca7883135b19279711a",
            matrix["source"]["sha256"],
        )
        self.assertEqual(73, matrix["source"]["entry_count"])
        self.assertEqual(73, len(matrix["entries"]))
        self.assertTrue(matrix["analysis_evidence"]["matching_3ds_code_binary_available"])
        self.assertEqual(
            "3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77",
            matrix["analysis_evidence"]["matching_3ds_code_sha256"],
        )
        self.assertEqual(
            "3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77",
            matrix["analysis_evidence"]["prior_jp_control_code_sha256"],
        )

        entries = {entry["source_index"]: entry for entry in matrix["entries"]}
        self.assertEqual(set(range(1, 74)), set(entries))
        self.assertEqual("excluded-fps60", entries[67]["disposition"])
        self.assertEqual("excluded-fps60", entries[70]["disposition"])
        self.assertEqual("implemented", entries[71]["disposition"])
        self.assertEqual("mh3g-hd-jp-v96-fps-lock-44", entries[71]["cemu_pack"])
        self.assertEqual(71, entries[73]["duplicate_of"])
        self.assertEqual(9, entries[22]["duplicate_of"])
        self.assertEqual(13, entries[43]["duplicate_of"])
        self.assertEqual(18, entries[42]["duplicate_of"])
        self.assertEqual("not-applicable", entries[69]["disposition"])
        self.assertEqual("not-supported", entries[68]["disposition"])
        self.assertTrue(all(entry["name_zh"] and entry["name_en"] for entry in matrix["entries"]))
        for source_index, slug in STATIC_ARM_PACKS.items():
            self.assertEqual("implemented-static-experimental", entries[source_index]["disposition"])
            self.assertEqual(static_pack_id(source_index, slug), entries[source_index]["cemu_pack"])

    def test_quest_red_delivery_box_redirect_is_narrow_and_fail_closed(self):
        result = self.tool.validate_repository(REPO)
        quest = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental"
        )

        self.assertEqual("Runtime Experimental", quest["status"])
        self.assertFalse(quest["default_install"])
        self.assertEqual("runtime-blocked", quest["availability"])
        self.assertIn("任务场景", quest["availability_reason"])
        self.assertIn("quest scene", quest["availability_reason"])
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
        self.assertEqual("runtime-blocked", blue["availability"])
        self.assertIn("任务看板", blue["availability_reason"])
        self.assertIn("quest board", blue["availability_reason"])
        self.assertEqual(
            {
                0x02219DF0: 0x4182007C,
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
                0x0214E084: 0x480CBC8D,
                0x0215165C: 0x89835350,
                0x02151698: 0x480000B4,
                0x0215174C: 0x4809F5BC,
                0x021F0D08: 0x7C0802A6,
                0x021F0D98: 0x981F0000,
                0x021F0D9C: 0x4BF52485,
                0x02219DDC: 0x859D4278,
                0x02219DE0: 0x38800006,
                0x02219DE4: 0x386C0340,
                0x02219DE8: 0x4BF9E021,
                0x02219DEC: 0x2C030000,
                0x02219DF4: 0x819D0000,
                0x02219DF8: 0x356C03D0,
                0x02219DFC: 0x41820070,
                0x02219E00: 0x892B0020,
                0x02219E04: 0x2C090000,
                0x02219E08: 0x40820064,
                0x02219E4C: 0x7FE3FB78,
                0x02219E50: 0x4BF3780D,
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
        self.assertIn("0x02219df0 = nop", patch)
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

    def test_quest_red_blue_combined_pack_consumes_and_attaches_task_local_box_transition(
        self,
    ):
        result = self.tool.validate_repository(REPO)
        combined = next(
            pack
            for pack in result.packs
            if pack["id"] == "mh3g-hd-jp-v96-quest-red-blue-full-item-box-experimental"
        )

        self.assertEqual("Runtime Experimental", combined["status"])
        self.assertFalse(combined["default_install"])
        self.assertEqual("runtime-blocked", combined["availability"])
        self.assertIn("暂停", combined["availability_reason"])
        self.assertIn("paused", combined["availability_reason"].lower())
        self.assertIn("任务", combined["summary"])
        self.assertIn("quest", combined["summary"].lower())
        self.assertEqual(
            {
                0x021B0E50: 0x386003F0,
                0x021B0E54: 0x38800010,
                0x021B0E58: 0x484439D5,
                0x021B0E5C: 0x2C030000,
                0x021B0E60: 0x7C641B78,
                0x021B0E64: 0x4182000C,
                0x021B0E68: 0x48443BB5,
                0x021B0E6C: 0x7C641B78,
                0x021B0ED4: 0x38600410,
                0x021B0ED8: 0x38800010,
                0x021B0EDC: 0x48461A35,
                0x021B0EE0: 0x2C030000,
                0x021B0EE4: 0x7C641B78,
                0x021B0EE8: 0x4182000C,
                0x021B0EEC: 0x48461C15,
                0x021B0EF0: 0x7C641B78,
                0x021D5BA8: 0x4E800020,
                0x021D5BAC: 0x4E800020,
                0x021D5BB0: 0x4E800020,
                0x021D5BB4: 0x4E800020,
                0x021D5BB8: 0x4E800020,
                0x021D5BBC: 0x4E800020,
                0x021D5BC0: 0x4E800020,
                0x021D5BC4: 0x4E800020,
                0x021D5BC8: 0x4E800020,
                0x021D5BCC: 0x4E800020,
                0x021D5BD8: 0x4E800020,
                0x021D5BDC: 0x4E800020,
                0x021D5BE0: 0x4E800020,
                0x0268AB20: 0x4BC01E8D,
                0x026FD1B0: 0x4BB8F7FD,
                0x028C2770: 0x819E0E30,
                0x028C2774: 0x3D601008,
                0x028C2778: 0x39000001,
                0x028C277C: 0xC00BE204,
                0x028C2780: 0x38800000,
                0x028C2784: 0x990C0BAE,
                0x028C2788: 0x7C862378,
                0x028C278C: 0x7FC3F378,
                0x028C2790: 0xD00C0BB4,
                0x028C5824: 0x38800001,
                0x028C5838: 0x38A0000F,
                0x028C5E80: 0x38800001,
            },
            {
                self.tool._number(item["address"]): self.tool._number(item["word"])
                for item in combined["preimages"]
            },
        )
        anchors = {
            self.tool._number(item["address"]): self.tool._number(item["word"])
            for item in combined["anchors"]
        }
        self.assertLessEqual(
            {
                0x021BB628: 0x9421FFA8,
                0x021F0A8C: 0x9421FFD8,
                0x021F0D08: 0x7C0802A6,
                0x02201A94: 0x7C0802A6,
                0x02201AF8: 0x9421FFC8,
                0x0228C9AC: 0x7C0802A6,
                0x028C2768: 0x2C1F0000,
                0x028C276C: 0x40820048,
                0x028C27F8: 0x3D201008,
            }.items(),
            anchors.items(),
        )
        patch = (REPO / combined["pack_dir"] / combined["patch"]).read_text()
        for instruction in (
            "0x028c2770 = lis r3, 0x1031",
            "0x028c2774 = lwz r3, 0x44a0(r3)",
            "0x028c2778 = mr r4, r30",
            "0x028c277c = li r5, 0",
            "0x028c2780 = bl 0x021f0a8c",
            "0x028c2784 = lis r3, 0x1031",
            "0x028c2788 = lwz r3, 0x44a0(r3)",
            "0x028c278c = bl 0x021f0d08",
            "0x028c2790 = b 0x021d5ba8",
            "0x021d5ba8 = lis r3, 0x1031",
            "0x021d5bac = lwz r3, 0x44a0(r3)",
            "0x021d5bb0 = bl 0x02201af8",
            "0x021d5bb4 = lis r3, 0x1031",
            "0x021d5bb8 = lwz r3, 0x44a0(r3)",
            "0x021d5bbc = lbz r0, 0x6e10(r3)",
            "0x021d5bc0 = cmpwi r0, 0x20",
            "0x021d5bc4 = bne 0x021d5bcc",
            "0x021d5bc8 = bl 0x02201a94",
            "0x021d5bcc = b 0x028c27f8",
            "0x028c5824 = li r4, 0",
            "0x028c5838 = li r5, 0xe",
            "0x028c5e80 = li r4, 0",
            "0x021b0e50 = mr r3, r27",
            "0x021b0e6c = b 0x021bb628",
            "0x021b0ed4 = mr r3, r27",
            "0x021b0ef0 = b 0x021bb628",
            "0x0268ab20 = bl 0x021d5bd8",
            "0x026fd1b0 = bl 0x021d5bd8",
            "0x021d5bdc = stw r0, 0xf0(r3)",
            "0x021d5be0 = b 0x0228c9ac",
        ):
            self.assertIn(instruction, patch)
        self.assertIn("任务本地一次性激活", patch)
        self.assertIn("task-local one-shot activation", patch.lower())
        self.assertIn("消费完整仓库状态转换", patch)
        self.assertIn("consume the full-item-box state transition", patch.lower())
        self.assertIn("补齐任务场景缺失的最终 ui 挂接", patch.lower())
        self.assertIn("complete the final ui attachment missing from quest scenes", patch.lower())
        self.assertIn("保留大厅 gui 资源", patch.lower())
        self.assertIn("retain the hub gui resources", patch.lower())
        for forbidden in (
            "0x02219de0 =",
            "0x02219df0 =",
            "0x021afe74 =",
            "bl 0x0215165c",
            "bl 0x021f0b64",
        ):
            self.assertNotIn(forbidden, patch.lower())

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
