"""Unit checks for the asset-free Cemu GDB tracing helper."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "cemu-gdb-probe.py"
COMMITTED_TRACES = REPO / "docs" / "research" / "traces"


def load_probe():
    spec = importlib.util.spec_from_file_location("cemu_gdb_probe", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CemuGDBProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe = load_probe()

    def write_spec(self, root: Path, **updates) -> Path:
        data = {
            "schema_version": 1,
            "name": "unit trace",
            "target": {
                "title_id": "0005000010104D00",
                "module_checksum": "0x348600a0",
                "cemu_rpx_hash": "8cb62099",
                "rpx_sha256": (
                    "7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0"
                ),
            },
            "breakpoints": [
                {
                    "label": "player_update",
                    "address": "0x028c7b18",
                    "expected_word": "0xc169e2d0",
                }
            ],
            "fixed_memory": [
                {"label": "manager", "address": "0x103144a0", "size": 4}
            ],
            "register_memory": [
                {"label": "player", "register": "r31", "offset": -16, "size": 64}
            ],
        }
        data.update(updates)
        path = root / "trace.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_packet_codec_round_trips_and_rejects_corruption(self):
        packet = self.probe.encode_packet("m28c7b18,4")
        self.assertEqual("m28c7b18,4", self.probe.decode_packet(packet))
        escaped = b"a}" + bytes([ord("#") ^ 0x20]) + b"b"
        framed = b"$" + escaped + f"#{sum(escaped) & 0xff:02x}".encode()
        self.assertEqual("a#b", self.probe.decode_packet(framed))
        with self.assertRaisesRegex(self.probe.ProbeError, "checksum mismatch"):
            self.probe.decode_packet(packet[:-2] + b"00")

    def test_rsp_ok_is_not_misclassified_as_console_output(self):
        client_socket, server_socket = socket.socketpair()
        try:
            server_socket.sendall(b"+$OK#9a")
            client = self.probe.RSPClient(client_socket)
            self.assertEqual("OK", client.receive(1.0))
        finally:
            client_socket.close()
            server_socket.close()

    def test_cemu_register_endianness_matches_stub_serialization(self):
        class FakeRegisterClient:
            def request(self, payload, timeout=5.0):
                values = {
                    "p3": "78563412",
                    "p40": "0219b6f0",
                    "p43": "f0debc9a",
                }
                return values[payload]

        client = self.probe.RSPClient.__new__(self.probe.RSPClient)
        client.request = FakeRegisterClient().request
        self.assertEqual(0x12345678, client.read_register(3))
        self.assertEqual(0x0219B6F0, client.read_register(self.probe.PPC_PC_REGISTER))
        self.assertEqual(0x9ABCDEF0, client.read_register(self.probe.PPC_LR_REGISTER))

    def test_trace_spec_pins_identity_preimages_and_snapshot_ranges(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self.probe.load_spec(self.write_spec(Path(tmp)))

        self.assertEqual("0005000010104D00", spec.target["title_id"])
        self.assertEqual(0x028C7B18, spec.breakpoints[0].address)
        self.assertEqual(0xC169E2D0, spec.breakpoints[0].expected_word)
        self.assertEqual(0x103144A0, spec.fixed_memory[0].address)
        self.assertEqual(31, spec.register_memory[0].register)
        self.assertEqual(-16, spec.register_memory[0].offset)

    def test_trace_spec_rejects_duplicate_or_unpinned_breakpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            duplicate = self.write_spec(
                root,
                breakpoints=[
                    {"label": "a", "address": "0x028c7b18", "expected_word": 1},
                    {"label": "b", "address": "0x028c7b18", "expected_word": 2},
                ],
            )
            with self.assertRaisesRegex(self.probe.ProbeError, "duplicate breakpoint address"):
                self.probe.load_spec(duplicate)

            missing = self.write_spec(
                root,
                breakpoints=[{"label": "a", "address": "0x028c7b18"}],
            )
            with self.assertRaisesRegex(self.probe.ProbeError, "expected_word"):
                self.probe.load_spec(missing)

    def test_trace_spec_rejects_incomplete_or_malformed_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            incomplete = self.write_spec(
                root,
                target={
                    "title_id": "0005000010104D00",
                    "module_checksum": "0x348600a0",
                    "rpx_sha256": "0" * 64,
                },
            )
            with self.assertRaisesRegex(self.probe.ProbeError, "cemu_rpx_hash"):
                self.probe.load_spec(incomplete)

            malformed = self.write_spec(
                root,
                target={
                    "title_id": "0005000010104D00",
                    "module_checksum": "0x348600a0",
                    "cemu_rpx_hash": "not-a-hash",
                    "rpx_sha256": "0" * 64,
                },
            )
            with self.assertRaisesRegex(self.probe.ProbeError, "invalid format"):
                self.probe.load_spec(malformed)

    def test_trace_spec_rejects_unsafe_snapshot_sizes_and_registers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            oversized = self.write_spec(
                root,
                fixed_memory=[{"label": "huge", "address": 0, "size": 4097}],
            )
            with self.assertRaisesRegex(self.probe.ProbeError, "size must be 1..4096"):
                self.probe.load_spec(oversized)

            bad_register = self.write_spec(
                root,
                register_memory=[
                    {"label": "bad", "register": "r32", "offset": 0, "size": 4}
                ],
            )
            with self.assertRaisesRegex(self.probe.ProbeError, "not an integer"):
                self.probe.load_spec(bad_register)

    def test_all_committed_trace_specs_are_accepted(self):
        paths = sorted(COMMITTED_TRACES.glob("*.json"))
        self.assertEqual(
            [
                "mh3g-dynamic-08-pouch-delta.json",
                "mh3g-dynamic-12-item-cap-return.json",
                "mh3g-dynamic-19-attack-derived.json",
                "mh3g-dynamic-20-defense-derived.json",
                "mh3g-dynamic-62-oxygen-delta.json",
            ],
            [path.name for path in paths],
        )
        specs = [self.probe.load_spec(path) for path in paths]
        self.assertEqual(
            [0x0219B6F0, 0x0203A2A0, 0x0286769C, 0x02867D14, 0x02863F0C],
            [s.breakpoints[0].address for s in specs],
        )
        self.assertEqual(
            [128, 20, 32, 32, 64],
            [s.register_memory[0].size for s in specs],
        )

    def test_keyboard_interrupt_removes_armed_breakpoints_and_resumes(self):
        class FakeSocket:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        class FakeClient:
            instance = None

            def __init__(self, sock):
                self.sock = sock
                self.receive_count = 0
                self.interrupt_count = 0
                self.continue_count = 0
                self.deleted = []
                self.requests = []
                FakeClient.instance = self

            def receive(self, timeout=None):
                self.receive_count += 1
                if self.receive_count == 1:
                    raise KeyboardInterrupt
                return "T05thread:00000001;"

            def request(self, payload, timeout=5.0):
                self.requests.append(payload)
                if payload == "?":
                    return "T05thread:00000001;"
                if payload.startswith("z0,"):
                    self.deleted.append(payload)
                return "OK"

            def read_memory(self, address, size):
                self.assert_address = address
                return bytes.fromhex("c169e2d0")

            def interrupt(self):
                self.interrupt_count += 1

            def continue_(self):
                self.continue_count += 1

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_spec = self.probe.load_spec(self.write_spec(root))
            output = root / "trace.jsonl"
            sock = FakeSocket()
            original_connect = self.probe._connect
            original_client = self.probe.RSPClient
            original_settle = self.probe.CEMU_GDB_SETTLE_SECONDS
            self.probe._connect = lambda host, port, timeout: sock
            self.probe.RSPClient = FakeClient
            self.probe.CEMU_GDB_SETTLE_SECONDS = 0
            try:
                with self.assertRaises(KeyboardInterrupt):
                    self.probe.run_trace(trace_spec, output, "127.0.0.1", 1337, 1.0)
            finally:
                self.probe._connect = original_connect
                self.probe.RSPClient = original_client
                self.probe.CEMU_GDB_SETTLE_SECONDS = original_settle
            events = [
                json.loads(line)["event"] for line in output.read_text().splitlines()
            ]

        client = FakeClient.instance
        self.assertIsNotNone(client)
        self.assertEqual(1, client.interrupt_count)
        self.assertEqual(["z0,28c7b18,4"], client.deleted)
        self.assertEqual(2, client.continue_count)
        self.assertEqual(
            [
                "?",
                "Hg0",
                "Hc-1",
                "Z0,28c7b18,4",
                "Hg0",
                "Hc-1",
                "z0,28c7b18,4",
            ],
            client.requests,
        )
        self.assertTrue(sock.closed)
        self.assertIn("cleanup_interrupt", events)
        self.assertIn("cleanup_breakpoint", events)
        self.assertEqual("resumed", events[-1])


if __name__ == "__main__":
    unittest.main()
