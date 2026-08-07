"""Coverage gates for the remaining MH3G 3DS dynamic conversions."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]
CONVERSION = REPO / "docs" / "research" / "mh3g-3ds-cheat-conversion.json"
DYNAMIC = REPO / "docs" / "research" / "mh3g-dynamic-ppc-mapping.json"
TRACE_ROOT = REPO / "docs" / "research" / "traces"


class DynamicMappingTests(unittest.TestCase):
    def setUp(self):
        self.conversion = json.loads(CONVERSION.read_text(encoding="utf-8"))
        self.dynamic = json.loads(DYNAMIC.read_text(encoding="utf-8"))

    def test_all_and_only_requires_ppc_entries_have_a_dynamic_ledger_row(self):
        expected = {
            entry["source_index"]: entry
            for entry in self.conversion["entries"]
            if entry["disposition"] == "requires-ppc-mapping"
        }
        actual = {entry["source_index"]: entry for entry in self.dynamic["entries"]}

        self.assertEqual(21, len(expected))
        self.assertEqual(set(expected), set(actual))
        for source_index, row in actual.items():
            with self.subTest(source_index=source_index):
                self.assertEqual(
                    expected[source_index]["source_mechanism"], row["source_mechanism"]
                )
                self.assertEqual(expected[source_index]["name_zh"], row["name_zh"])
                self.assertEqual(expected[source_index]["name_en"], row["name_en"])

    def test_dynamic_mechanism_counts_and_batches_are_exact(self):
        rows = self.dynamic["entries"]
        self.assertEqual(
            {
                "arm-runtime-pointer": 10,
                "arm-hotkey-routine": 6,
                "arm-code-cave": 5,
            },
            dict(Counter(row["source_mechanism"] for row in rows)),
        )
        self.assertEqual(
            {"source-decoded": 16, "ppc-candidate": 5, "ppc-mapped": 0},
            self.dynamic["summary"]["mapping_counts"],
        )
        self.assertEqual(
            {"source-decoded": 16, "ppc-candidate": 5},
            dict(Counter(row["mapping_state"] for row in rows)),
        )
        batches = {batch["id"]: batch for batch in self.dynamic["probe_batches"]}
        self.assertEqual(
            {
                "direct-native-hooks",
                "player-inventory-roots",
                "weapon-runtime-state",
                "controller-action-hooks",
                "monster-runtime-state",
            },
            set(batches),
        )
        batched = [source for batch in batches.values() for source in batch["source_indices"]]
        self.assertEqual(21, len(batched))
        self.assertEqual({row["source_index"] for row in rows}, set(batched))
        self.assertEqual(len(batched), len(set(batched)))
        for row in rows:
            self.assertIn(row["probe_batch"], batches)
            self.assertIn(row["source_index"], batches[row["probe_batch"]]["source_indices"])

    def test_no_dynamic_pack_exists_before_ppc_and_runtime_evidence(self):
        for row in self.dynamic["entries"]:
            with self.subTest(source_index=row["source_index"]):
                self.assertIn(row["mapping_state"], {"source-decoded", "ppc-candidate"})
                self.assertEqual("not-traced", row["runtime_state"])
                self.assertEqual("not-created", row["pack_state"])
                self.assertNotIn("pack_id", row)
                self.assertTrue(row["source_sites"])
                self.assertGreaterEqual(len(row["source_semantics_zh"]), 25)
                self.assertGreaterEqual(len(row["source_semantics_en"]), 25)
                self.assertGreaterEqual(len(row["target_strategy_zh"]), 25)
                self.assertGreaterEqual(len(row["target_strategy_en"]), 25)

    def test_static_ppc_candidates_are_pinned_and_have_trace_specs(self):
        candidates = [
            row for row in self.dynamic["entries"] if row["mapping_state"] == "ppc-candidate"
        ]
        self.assertEqual([8, 12, 19, 20, 62], [row["source_index"] for row in candidates])

        for row in candidates:
            with self.subTest(source_index=row["source_index"]):
                candidate = row["ppc_candidate"]
                self.assertRegex(candidate["function_entry"], r"^0x[0-9a-f]{8}$")
                self.assertRegex(
                    candidate["function_entry_preimage"], r"^0x[0-9a-f]{8}$"
                )
                trace_path = REPO / candidate["trace_spec"]
                self.assertTrue(trace_path.is_file())
                trace = json.loads(trace_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    self.dynamic["target"]["title_id"], trace["target"]["title_id"]
                )
                self.assertEqual(
                    self.dynamic["target"]["module_checksum"],
                    trace["target"]["module_checksum"],
                )
                self.assertEqual(
                    self.dynamic["target"]["rpx_sha256"],
                    trace["target"]["rpx_sha256"],
                )

        item_delta = candidates[0]["ppc_candidate"]
        self.assertEqual("0x0219b6f0", item_delta["delta_capture"])
        self.assertEqual(
            "0x7cba2b78", item_delta["delta_capture_preimage"]
        )
        item_cap = candidates[1]["ppc_candidate"]
        self.assertEqual(20, item_cap["item_record_size"])
        self.assertEqual(3, item_cap["carry_cap_offset"])
        attack = candidates[2]["ppc_candidate"]
        self.assertEqual("0x0286769c", attack["derived_attack_load"])
        self.assertEqual("0xa14906e8", attack["derived_attack_load_preimage"])
        self.assertEqual("0x06e8", attack["attack_offset"])
        self.assertEqual(700, attack["native_cap"])
        defense = candidates[3]["ppc_candidate"]
        self.assertEqual("0x02867d14", defense["derived_defense_load"])
        self.assertEqual("0xa00a06ea", defense["derived_defense_load_preimage"])
        self.assertEqual("0x06ea", defense["defense_offset"])
        oxygen = candidates[4]["ppc_candidate"]
        self.assertEqual("0x02863f0c", oxygen["delta_capture"])
        self.assertEqual("0xa96a065c", oxygen["delta_capture_preimage"])
        self.assertEqual("0x065c", oxygen["current_oxygen_offset"])
        self.assertEqual("0x065e", oxygen["maximum_oxygen_offset"])

    def test_dynamic_target_is_the_same_fail_closed_jp_v96_identity(self):
        target = self.dynamic["target"]
        self.assertEqual("0005000010104D00", target["title_id"])
        self.assertEqual("0x348600a0", target["module_checksum"])
        self.assertEqual("8cb62099", target["cemu_rpx_hash"])
        self.assertEqual(
            "7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0",
            target["rpx_sha256"],
        )
        self.assertEqual("0x02000020", target["ppc_text_base"])
        self.assertEqual(
            "066b458aa2b08c9b13a163dcb47efd4f9d48d873780d1103b5ae2bec8ad0e3b3",
            target["ppc_text_sha256"],
        )
        self.assertEqual(
            self.conversion["analysis_evidence"]["matching_3ds_code_sha256"],
            self.dynamic["source"]["matching_code_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
