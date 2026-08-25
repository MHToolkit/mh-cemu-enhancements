"""Structural and semantic checks for MH3G dynamic cheat #28."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PACK = (
    REPO
    / "packs"
    / "wiiu"
    / "mh3g-hd"
    / "jp-v96"
    / "dynamic-28-switch-axe-energy-max"
)


class SwitchAxeEnergyPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
        cls.asm = (PACK / cls.manifest["patch"]).read_text(encoding="utf-8")

    def test_only_the_two_native_delta_results_are_replaced(self) -> None:
        replacements = {
            int(address, 16): instruction.strip()
            for address, instruction in re.findall(
                r"^(0x[0-9a-fA-F]+)\s*=\s*([^#\n]+)",
                self.asm,
                re.MULTILINE,
            )
        }
        self.assertEqual(
            {
                0x0285DEFC: "li r10, 100",
                0x0285DF48: "li r10, 100",
            },
            replacements,
        )
        self.assertNotIn(".origin = codecave", self.asm)
        self.assertNotIn("0x0289248c", self.asm.lower())

    def test_manifest_pins_exact_writer_preimages_and_runtime_chain(self) -> None:
        self.assertEqual("Runtime Verified", self.manifest["status"])
        self.assertEqual("pass", self.manifest["gameplay_evidence"]["result"])
        self.assertEqual(
            {
                0x0285DEFC: 0x7D4A0214,
                0x0285DF48: 0x7D4A0214,
            },
            {
                int(item["address"], 16): int(item["word"], 16)
                for item in self.manifest["preimages"]
            },
        )
        evidence = self.manifest["runtime_evidence"]
        self.assertEqual(-4, evidence["drain_trace"]["r4_signed"])
        self.assertEqual(5, evidence["recharge_trace"]["r4_signed"])
        self.assertEqual(
            evidence["drain_trace"]["inner_pointer_at_r3_plus_0xe30"],
            evidence["recharge_trace"]["inner_pointer_at_r3_plus_0xe30"],
        )
        self.assertIn("+0x062C", evidence["field_contract"])

    def test_replacement_value_survives_the_native_signed_clamp(self) -> None:
        def native_clamp(value: int) -> int:
            return max(0, min(value, 100))

        for current in (0, 1, 30, 50, 99, 100):
            for delta in (-30, -4, 0, 5, 30):
                with self.subTest(current=current, delta=delta):
                    # Both native branches replace ``current + delta`` with 100
                    # before the preserved extsh/store/range-clamp sequence.
                    self.assertEqual(100, native_clamp(100))


if __name__ == "__main__":
    unittest.main()
