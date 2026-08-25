"""Unit coverage for the fail-closed MH3G #28 research helpers."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
ANALYZER = REPO / "scripts" / "analyze-switch-axe-snapshots.py"
SCANNER = REPO / "scripts" / "scan-ppc-dform-offsets.py"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SwitchAxeSnapshotAnalyzerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_script("switch_axe_snapshot_analyzer", ANALYZER)

    def write_trace(
        self,
        root: Path,
        role: str,
        data: bytes,
        *,
        base: int = 0x2FF7D610,
        complete: bool = True,
    ) -> Path:
        target = {
            "title_id": "0005000010104D00",
            "module_checksum": "0x348600a0",
            "cemu_rpx_hash": "8cb62099",
            "rpx_sha256": (
                "7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0"
            ),
        }
        rows = [
            {"event": "status", "target": target},
            {
                "event": "hit",
                "snapshot": {
                    "register_memory": {
                        "player_state": {
                            "base_value": f"0x{base:08x}",
                            "offset": 0,
                            "size": len(data),
                            "hex": data.hex(),
                        }
                    }
                },
            },
        ]
        if complete:
            rows.append({"event": "complete"})
        path = root / f"{role}.jsonl"
        path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        return path

    def make_snapshots(self, root: Path, *, changed_base_role: str | None = None):
        role_values = {
            "full": 100,
            "consume_1": 80,
            "consume_2": 60,
            "recharge_1": 70,
            "recharge_2": 90,
        }
        relaxed_values = {
            "full": 90,
            "consume_1": 80,
            "consume_2": 70,
            "recharge_1": 75,
            "recharge_2": 85,
        }
        snapshots = []
        for role in self.analyzer.ROLE_NAMES:
            data = bytearray(128)
            data[0x6C] = role_values[role]
            data[0x20] = relaxed_values[role]
            path = self.write_trace(
                root,
                role,
                bytes(data),
                base=0x2FF7D710 if role == changed_base_role else 0x2FF7D610,
            )
            snapshots.append(self.analyzer.load_snapshot(role, path, "player_state"))
        return snapshots

    def test_strict_0_to_100_sequence_isolated_and_hypothesis_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self.analyzer.analyze(self.make_snapshots(Path(tmp)))

        self.assertEqual("strict-candidates-found", report["status"])
        self.assertEqual(1, report["strict_candidate_count"])
        self.assertEqual("0x006c", report["strict_candidates"][0]["offset"])
        self.assertTrue(
            report["strict_candidates"][0]["matches_plus_8_layout_hypothesis"]
        )
        self.assertFalse(report["expected_offsets"]["0x0064"]["strict"])
        self.assertTrue(report["expected_offsets"]["0x006c"]["strict"])
        self.assertEqual("field-candidate-only-not-writer-proof", report["scope"])

    def test_changed_player_base_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshots = self.make_snapshots(Path(tmp), changed_base_role="recharge_2")
            with self.assertRaisesRegex(
                self.analyzer.AnalysisError, "player-object base changed"
            ):
                self.analyzer.analyze(snapshots)

    def test_incomplete_trace_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_trace(
                Path(tmp), "full", bytes(128), complete=False
            )
            with self.assertRaisesRegex(
                self.analyzer.AnalysisError, "exactly one complete"
            ):
                self.analyzer.load_snapshot("full", path, "player_state")


class PPCDFormScannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scanner = load_script("ppc_dform_offset_scanner", SCANNER)

    @staticmethod
    def dform(opcode: int, register: int, base: int, displacement: int) -> bytes:
        word = (
            (opcode << 26)
            | (register << 21)
            | (base << 16)
            | (displacement & 0xFFFF)
        )
        return word.to_bytes(4, "big")

    def test_scan_filters_width_access_stack_and_address_range(self):
        text = b"".join(
            (
                self.dform(34, 3, 7, 0x6C),
                self.dform(38, 4, 7, 0x6C),
                self.dform(44, 5, 7, 0x64),
                self.dform(38, 6, 1, 0x6C),
                b"\x38\x60\x00\x64",
            )
        )
        byte_rows = self.scanner.scan(
            0x02800000, text, {0x64, 0x6C}, width="byte"
        )
        self.assertEqual(["lbz", "stb"], [row["mnemonic"] for row in byte_rows])
        stores = self.scanner.scan(
            0x02800000, text, {0x6C}, width="byte", access="store"
        )
        self.assertEqual(["0x02800004"], [row["address"] for row in stores])
        with_stack = self.scanner.scan(
            0x02800000,
            text,
            {0x6C},
            width="byte",
            include_stack=True,
            start_address=0x02800004,
            end_address=0x02800010,
        )
        self.assertEqual(
            ["0x02800004", "0x0280000c"],
            [row["address"] for row in with_stack],
        )

    def build_elf(self, text: bytes) -> bytes:
        text_offset = 0x100
        names_offset = 0x140
        section_offset = 0x200
        names = b"\0.text\0.shstrtab\0"
        size = section_offset + 3 * 40
        data = bytearray(size)
        data[:16] = b"\x7fELF\x01\x02\x01" + bytes(9)
        struct.pack_into(
            ">HHIIIIIHHHHHH",
            data,
            16,
            1,
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
            2,
        )
        data[text_offset : text_offset + len(text)] = text
        data[names_offset : names_offset + len(names)] = names
        struct.pack_into(">IIIIIIIIII", data, section_offset, *([0] * 10))
        struct.pack_into(
            ">IIIIIIIIII",
            data,
            section_offset + 40,
            1,
            1,
            6,
            0x02000020,
            text_offset,
            len(text),
            0,
            0,
            4,
            0,
        )
        struct.pack_into(
            ">IIIIIIIIII",
            data,
            section_offset + 80,
            7,
            3,
            0,
            0,
            names_offset,
            len(names),
            0,
            0,
            1,
            0,
        )
        return bytes(data)

    def test_load_text_reads_elf32_big_endian_section(self):
        text = self.dform(38, 4, 7, 0x6C)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.elf"
            path.write_bytes(self.build_elf(text))
            address, loaded = self.scanner.load_text(path)
        self.assertEqual(0x02000020, address)
        self.assertEqual(text, loaded)


if __name__ == "__main__":
    unittest.main()
