"""Coverage gates for the remaining MH3G 3DS dynamic conversions."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]
CONVERSION = REPO / "docs" / "research" / "mh3g-3ds-cheat-conversion.json"
DYNAMIC = REPO / "docs" / "research" / "mh3g-dynamic-ppc-mapping.json"
RUNTIME_EVIDENCE = REPO / "docs" / "research" / "mh3g-dynamic-runtime-evidence.json"
TRACE_ROOT = REPO / "docs" / "research" / "traces"


class DynamicMappingTests(unittest.TestCase):
    def setUp(self):
        self.conversion = json.loads(CONVERSION.read_text(encoding="utf-8"))
        self.dynamic = json.loads(DYNAMIC.read_text(encoding="utf-8"))
        self.runtime_evidence = json.loads(RUNTIME_EVIDENCE.read_text(encoding="utf-8"))

    def test_all_dynamic_research_entries_have_a_ledger_row(self):
        expected = {
            entry["source_index"]: entry
            for entry in self.conversion["entries"]
            if entry["disposition"]
            in {"requires-ppc-mapping", "implemented-dynamic-runtime-verified"}
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
            {"source-decoded": 3, "ppc-candidate": 17, "ppc-mapped": 1},
            self.dynamic["summary"]["mapping_counts"],
        )
        self.assertEqual(
            {"source-decoded": 3, "ppc-candidate": 17, "ppc-mapped": 1},
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

    def test_dynamic_pack_creation_requires_complete_ppc_and_runtime_evidence(self):
        for row in self.dynamic["entries"]:
            with self.subTest(source_index=row["source_index"]):
                if row["source_index"] == 28:
                    self.assertEqual("ppc-mapped", row["mapping_state"])
                    self.assertEqual("gameplay-traced", row["runtime_state"])
                    self.assertEqual("runtime-verified-created", row["pack_state"])
                    self.assertEqual(
                        "mh3g-hd-jp-v96-dynamic-28-switch-axe-energy-max",
                        row["pack_id"],
                    )
                    self.assertIn("runtime_mapping", row)
                else:
                    self.assertIn(
                        row["mapping_state"], {"source-decoded", "ppc-candidate"}
                    )
                    self.assertIn(
                        row["runtime_state"],
                        {"not-traced", "partial-runtime-evidence"},
                    )
                    self.assertEqual("not-created", row["pack_state"])
                    self.assertNotIn("pack_id", row)
                self.assertTrue(row["source_sites"])
                self.assertGreaterEqual(len(row["source_semantics_zh"]), 25)
                self.assertGreaterEqual(len(row["source_semantics_en"]), 25)
                self.assertGreaterEqual(len(row["target_strategy_zh"]), 25)
                self.assertGreaterEqual(len(row["target_strategy_en"]), 25)

    def test_partial_runtime_evidence_is_pinned_and_fail_closed(self):
        expected_partial = {1, 2, 3, 9, 19, 20, 23, 31, 32, 57, 58, 62}
        actual_partial = {
            row["source_index"]
            for row in self.dynamic["entries"]
            if row["runtime_state"] == "partial-runtime-evidence"
        }
        self.assertEqual(expected_partial, actual_partial)
        self.assertEqual(
            {
                "not-traced": 8,
                "partial-runtime-evidence": 12,
                "gameplay-traced": 1,
            },
            self.dynamic["summary"]["runtime_counts"],
        )
        self.assertEqual(
            "docs/research/mh3g-dynamic-runtime-evidence.json",
            self.dynamic["summary"]["runtime_evidence_ledger"],
        )

        captures = self.runtime_evidence["captures"]
        captures_by_id = {capture["id"]: capture for capture in captures}
        self.assertEqual(len(captures), len(captures_by_id))
        self.assertEqual(
            self.dynamic["target"]["title_id"],
            self.runtime_evidence["target"]["title_id"],
        )
        self.assertEqual(
            self.dynamic["target"]["module_checksum"],
            self.runtime_evidence["target"]["module_checksum"],
        )
        self.assertEqual(
            self.dynamic["target"]["rpx_sha256"],
            self.runtime_evidence["target"]["rpx_sha256"],
        )
        runtime = self.runtime_evidence["runtime"]
        self.assertRegex(runtime["nemessix_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(
            "https://github.com/MHToolkit/nemessix/pull/19",
            runtime["nemessix_pr"],
        )
        self.assertTrue(runtime["persistent_breakpoint_evidence_path"].startswith("/"))
        self.assertRegex(
            runtime["persistent_breakpoint_evidence_sha256"], r"^[0-9a-f]{64}$"
        )
        for capture in captures:
            with self.subTest(capture=capture["id"]):
                self.assertRegex(capture["raw_sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(capture["raw_size"], 0)
                self.assertTrue(capture["raw_path"].startswith("/"))
                self.assertGreaterEqual(len(capture["proves"]), 30)
                self.assertGreaterEqual(len(capture["does_not_prove"]), 30)

        for row in self.dynamic["entries"]:
            refs = row.get("runtime_evidence_refs", [])
            with self.subTest(source_index=row["source_index"]):
                if row["runtime_state"] in {
                    "partial-runtime-evidence",
                    "gameplay-traced",
                }:
                    self.assertGreaterEqual(len(refs), 1)
                    for ref in refs:
                        self.assertIn(ref, captures_by_id)
                        self.assertIn(row["source_index"], captures_by_id[ref]["source_indices"])
                else:
                    self.assertEqual([], refs)

        evidence_state = {
            int(source_index): state
            for source_index, state in self.runtime_evidence["entry_runtime_state"].items()
        }
        expected_evidence_state = {
            source_index: "partial-runtime-evidence"
            for source_index in expected_partial
        }
        expected_evidence_state[28] = "gameplay-traced"
        self.assertEqual(expected_evidence_state, evidence_state)
        summary = self.runtime_evidence["summary"]
        self.assertEqual(12, summary["partial_runtime_evidence"])
        self.assertEqual(1, summary["gameplay_traced"])
        self.assertEqual(1, summary["ppc_mapped"])
        self.assertEqual(1, summary["installable_dynamic_packs"])
        self.assertEqual("passed", summary["persistent_breakpoint_gate"])
        self.assertGreaterEqual(summary["same_process_independent_attach_count"], 4)

    def test_static_ppc_candidates_are_pinned_and_have_trace_specs(self):
        candidates = [
            row for row in self.dynamic["entries"] if row["mapping_state"] == "ppc-candidate"
        ]
        self.assertEqual(
            [1, 2, 3, 4, 8, 9, 12, 19, 20, 23, 24, 30, 31, 32, 57, 58, 62],
            [row["source_index"] for row in candidates],
        )

        for row in candidates:
            with self.subTest(source_index=row["source_index"]):
                candidate = row["ppc_candidate"]
                self.assertRegex(candidate["function_entry"], r"^0x[0-9a-f]{8}$")
                self.assertRegex(
                    candidate["function_entry_preimage"], r"^0x[0-9a-f]{8}$"
                )
                for key, value in candidate.items():
                    if not key.endswith("_preimage"):
                        continue
                    address_key = key.removesuffix("_preimage")
                    self.assertIn(address_key, candidate)
                    self.assertRegex(candidate[address_key], r"^0x[0-9a-f]{8}$")
                    self.assertRegex(value, r"^0x[0-9a-f]{8}$")

                trace_specs = list(candidate.get("trace_specs", []))
                trace_specs.extend(
                    candidate[key]
                    for key in ("trace_spec", "input_trace_spec")
                    if key in candidate
                )
                self.assertGreaterEqual(len(trace_specs), 1)
                self.assertEqual(len(trace_specs), len(set(trace_specs)))
                for trace_spec in trace_specs:
                    trace_path = REPO / trace_spec
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

        by_source = {row["source_index"]: row["ppc_candidate"] for row in candidates}
        speed_3x = by_source[1]
        self.assertEqual("0x028924ac", speed_3x["multiplier_load"])
        self.assertEqual("0xc1070608", speed_3x["multiplier_load_preimage"])
        self.assertEqual("0x0608", speed_3x["multiplier_offset"])
        self.assertEqual("0x0440", speed_3x["accumulator_offset"])
        self.assertEqual(3.0, speed_3x["requested_multiplier"])
        self.assertEqual("0x00000100", speed_3x["normalized_button_mask"])
        speed_2x = by_source[2]
        self.assertEqual(2.0, speed_2x["requested_multiplier"])
        self.assertEqual("L", speed_2x["required_button"])
        speed_1x = by_source[3]
        self.assertEqual(1.0, speed_1x["requested_multiplier"])
        self.assertEqual("R", speed_1x["required_button"])
        self.assertEqual("0x00000200", speed_1x["normalized_button_mask"])
        sharpness = by_source[4]
        self.assertEqual("0x0285f0f4", sharpness["ordinary_delta_load"])
        self.assertEqual("0xa9870afc", sharpness["ordinary_delta_load_preimage"])
        self.assertEqual("0x0afc", sharpness["current_sharpness_offset"])
        self.assertEqual("0x0afe", sharpness["maximum_sharpness_offset"])
        item_delta = by_source[8]
        self.assertEqual("0x0219b6f0", item_delta["delta_capture"])
        self.assertEqual("0x7cba2b78", item_delta["delta_capture_preimage"])
        pouch_slot = by_source[9]
        self.assertEqual("0x0219b830", pouch_slot["quantity_write"])
        self.assertEqual("0xb19b0002", pouch_slot["quantity_write_preimage"])
        self.assertEqual("0x10315c50", pouch_slot["global_root_address"])
        self.assertEqual("0x00e0", pouch_slot["first_record_offset"])
        self.assertEqual("0x0002", pouch_slot["quantity_offset"])
        item_cap = by_source[12]
        self.assertEqual(20, item_cap["item_record_size"])
        self.assertEqual(3, item_cap["carry_cap_offset"])
        attack = by_source[19]
        self.assertEqual("0x0286769c", attack["derived_attack_load"])
        self.assertEqual("0xa14906e8", attack["derived_attack_load_preimage"])
        self.assertEqual("0x06e8", attack["attack_offset"])
        self.assertEqual(700, attack["native_cap"])
        defense = by_source[20]
        self.assertEqual("0x02867d14", defense["derived_defense_load"])
        self.assertEqual("0xa00a06ea", defense["derived_defense_load_preimage"])
        self.assertEqual("0x06ea", defense["defense_offset"])
        item_box = by_source[23]
        self.assertEqual("0x021f1900", item_box["first_quantity_load"])
        self.assertEqual("0xa8fd0002", item_box["first_quantity_load_preimage"])
        self.assertEqual("0x10315c50", item_box["global_root_address"])
        self.assertEqual("0x01c0", item_box["first_record_offset"])
        self.assertEqual("0x0002", item_box["quantity_offset"])
        self.assertEqual(4, item_box["record_size"])
        self.assertEqual(101, item_box["record_count"])
        gunlance = by_source[24]
        self.assertEqual("0x02856cec", gunlance["source_count_load"])
        self.assertEqual("0x045a", gunlance["current_count_offset"])
        self.assertEqual("0x045b", gunlance["source_count_offset"])
        bowgun = by_source[30]
        self.assertEqual("0x02856d7c", bowgun["source_count_load"])
        self.assertEqual("0x02856d90", bowgun["current_count_write"])
        hp = by_source[31]
        self.assertEqual("0x02865fec", hp["current_hp_load"])
        self.assertEqual("0xa98a0640", hp["current_hp_load_preimage"])
        self.assertEqual("0x0640", hp["current_hp_offset"])
        self.assertEqual("0x0642", hp["maximum_hp_offset"])
        self.assertEqual("0x00002000", hp["normalized_button_mask"])
        drink = by_source[32]
        self.assertEqual("0x02893154", drink["first_pair_capture"])
        self.assertEqual("0x028932b4", drink["second_pair_capture"])
        self.assertEqual(
            ["0x0974", "0x0978", "0x0980", "0x0984"],
            drink["timer_pair_offsets"],
        )
        destroy_placed = by_source[57]
        self.assertEqual("0x0218a394", destroy_placed["threshold_compare"])
        self.assertEqual("0x7c056010", destroy_placed["threshold_compare_preimage"])
        self.assertEqual("0x0007", destroy_placed["record_threshold_offset"])
        self.assertEqual(12, destroy_placed["record_size"])
        self.assertEqual(64, destroy_placed["record_count"])
        self.assertEqual(
            "0x00000080", destroy_placed["normalized_left_button_mask"]
        )
        placed = by_source[58]
        self.assertEqual("0x0289a018", placed["zero_limit_check"])
        self.assertEqual("0x0289a618", placed["three_limit_check"])
        self.assertEqual("0x0289a738", placed["two_limit_check"])
        self.assertEqual(3, len(placed["trace_specs"]))
        oxygen = by_source[62]
        self.assertEqual("0x02863f0c", oxygen["delta_capture"])
        self.assertEqual("0xa96a065c", oxygen["delta_capture_preimage"])
        self.assertEqual("0x065c", oxygen["current_oxygen_offset"])
        self.assertEqual("0x065e", oxygen["maximum_oxygen_offset"])

    def test_unmapped_entries_keep_partial_evidence_fail_closed(self):
        rows = {
            row["source_index"]: row
            for row in self.dynamic["entries"]
            if row["mapping_state"] == "source-decoded"
        }
        self.assertEqual({10, 25, 66}, set(rows))
        self.assertEqual("0x0270e63c", rows[10]["static_partial"]["target_manager_accessor"])
        self.assertEqual("0x1030be28", rows[10]["static_partial"]["target_global_root"])
        self.assertEqual("hypothesis", rows[25]["static_partial"]["confidence"])
        self.assertEqual(8, len(rows[25]["static_partial"]["hypothesized_target_ammo_offsets"]))
        self.assertEqual("source-only", rows[66]["static_partial"]["confidence"])
        for source_index, row in rows.items():
            with self.subTest(source_index=source_index):
                partial = row["static_partial"]
                self.assertNotIn("ppc_candidate", row)
                for key, value in partial.items():
                    if not key.endswith("_preimage"):
                        continue
                    address_key = key.removesuffix("_preimage")
                    self.assertIn(address_key, partial)
                    self.assertRegex(partial[address_key], r"^0x[0-9a-f]{8}$")
                    self.assertRegex(value, r"^0x[0-9a-f]{8}$")
                self.assertGreaterEqual(len(partial["evidence_zh"]), 40)
                self.assertGreaterEqual(len(partial["evidence_en"]), 40)
                self.assertGreaterEqual(len(partial["unresolved_zh"]), 20)
                self.assertGreaterEqual(len(partial["unresolved_en"]), 20)

    def test_switch_axe_mapping_is_live_and_runtime_verified(self):
        row = next(
            row for row in self.dynamic["entries"] if row["source_index"] == 28
        )
        self.assertEqual("ppc-mapped", row["mapping_state"])
        self.assertEqual("gameplay-traced", row["runtime_state"])
        self.assertEqual("runtime-verified-created", row["pack_state"])
        mapping = row["runtime_mapping"]
        self.assertEqual("0x062C", mapping["target_energy_offset"])
        self.assertEqual(16, mapping["target_width_bits"])
        self.assertEqual("big-endian", mapping["target_byte_order"])
        self.assertEqual("0x0285DE70", mapping["native_delta_writer"])
        self.assertEqual(-4, mapping["drain_delta"])
        self.assertEqual(5, mapping["recharge_delta"])
        self.assertEqual(
            ["0x0285DEFC", "0x0285DF48"], mapping["patch_sites"]
        )
        self.assertEqual("0x7D4A0214", mapping["patch_preimage"])
        self.assertEqual("0x39400064", mapping["patch_replacement"])
        self.assertEqual("pass", mapping["gameplay_result"])

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
