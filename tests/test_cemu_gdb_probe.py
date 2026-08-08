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
                    "p3": "12345678",
                    "p40": "0219b6f0",
                    "p43": "9abcdef0",
                    "p1f": "2d8914b0",
                }
                return values[payload]

        client = self.probe.RSPClient.__new__(self.probe.RSPClient)
        client.request = FakeRegisterClient().request
        self.assertEqual(0x12345678, client.read_register(3))
        self.assertEqual(0x0219B6F0, client.read_register(self.probe.PPC_PC_REGISTER))
        self.assertEqual(0x9ABCDEF0, client.read_register(self.probe.PPC_LR_REGISTER))
        self.assertEqual(0x2D8914B0, client.read_register(31))

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
                "mh3g-dynamic-01-03-speed-state.json",
                "mh3g-dynamic-04-sharpness-state.json",
                "mh3g-dynamic-08-pouch-delta.json",
                "mh3g-dynamic-09-pouch-slot-one.json",
                "mh3g-dynamic-12-item-cap-return.json",
                "mh3g-dynamic-19-attack-derived.json",
                "mh3g-dynamic-20-defense-derived.json",
                "mh3g-dynamic-23-item-box-slot-one.json",
                "mh3g-dynamic-24-gunlance-counts.json",
                "mh3g-dynamic-30-bowgun-counts.json",
                "mh3g-dynamic-31-hp-state.json",
                "mh3g-dynamic-32-drink-timers.json",
                "mh3g-dynamic-57-placed-object-threshold.json",
                "mh3g-dynamic-58-placed-count-three-limit.json",
                "mh3g-dynamic-58-placed-count-two-limit.json",
                "mh3g-dynamic-58-placed-count-zero-limit.json",
                "mh3g-dynamic-62-oxygen-delta.json",
                "mh3g-dynamic-controller-normalized-input.json",
            ],
            [path.name for path in paths],
        )
        specs = [self.probe.load_spec(path) for path in paths]
        self.assertEqual(
            [
                0x028924AC,
                0x0285F0F4,
                0x0219B6F0,
                0x0219B830,
                0x0203A2A0,
                0x0286769C,
                0x02867D14,
                0x021F1900,
                0x02856CEC,
                0x02856D7C,
                0x02865FEC,
                0x02893154,
                0x0218A394,
                0x0289A618,
                0x0289A738,
                0x0289A018,
                0x02863F0C,
                0x02BCB9CC,
            ],
            [s.breakpoints[0].address for s in specs],
        )
        self.assertEqual(
            [32, 32, 128, 4, 20, 32, 32, 16, 32, 32, 32, 32, 12, 32, 32, 32, 64, 32],
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

    def test_wait_register_nonzero_skips_zero_hit_then_captures(self):
        class FakeSocket:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        class FakeClient:
            instance = None

            def __init__(self, sock):
                self.sock = sock
                self.condition_reads = 0
                self.continue_count = 0
                FakeClient.instance = self

            def receive(self, timeout=None):
                return "T05thread:00000001;core:01;swbreak:;"

            def request(self, payload, timeout=5.0):
                return "OK"

            def read_memory(self, address, size):
                if address == 0x028C7B18 and size == 4:
                    return bytes.fromhex("c169e2d0")
                return bytes(size)

            def read_register(self, register):
                if register == self.probe.PPC_PC_REGISTER:
                    return 0x028C7B18
                if register == 29:
                    self.condition_reads += 1
                    return 0 if self.condition_reads == 1 else 0x2000
                if register == 31:
                    return 0x10000010
                return 0

            def continue_(self):
                self.continue_count += 1

        FakeClient.probe = self.probe
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
                self.probe.run_trace(
                    trace_spec,
                    output,
                    "127.0.0.1",
                    1337,
                    1.0,
                    wait_register_nonzero=29,
                    max_skipped_hits=2,
                )
            finally:
                self.probe._connect = original_connect
                self.probe.RSPClient = original_client
                self.probe.CEMU_GDB_SETTLE_SECONDS = original_settle
            rows = [json.loads(line) for line in output.read_text().splitlines()]

        self.assertEqual(1, sum(row["event"] == "condition_miss" for row in rows))
        met = next(row for row in rows if row["event"] == "condition_met")
        self.assertEqual("0x00002000", met["value"])
        self.assertEqual("0x00000000", met["excluded_value"])
        self.assertNotIn("required_mask", met)
        hit = next(row for row in rows if row["event"] == "hit")
        self.assertEqual("0x00002000", hit["snapshot"]["gpr"]["r29"])
        self.assertEqual(3, FakeClient.instance.continue_count)
        self.assertTrue(sock.closed)

    def test_wait_register_not_value_skips_baseline_then_captures_change(self):
        class FakeSocket:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        class FakeClient:
            instance = None

            def __init__(self, sock):
                self.sock = sock
                self.condition_reads = 0
                self.continue_count = 0
                FakeClient.instance = self

            def receive(self, timeout=None):
                return "T05thread:00000001;core:01;swbreak:;"

            def request(self, payload, timeout=5.0):
                return "OK"

            def read_memory(self, address, size):
                if address == 0x028C7B18 and size == 4:
                    return bytes.fromhex("c169e2d0")
                return bytes(size)

            def read_register(self, register):
                if register == self.probe.PPC_PC_REGISTER:
                    return 0x028C7B18
                if register == 29:
                    self.condition_reads += 1
                    return 0x80080000 if self.condition_reads == 1 else 0xA0080000
                if register == 31:
                    return 0x10000010
                return 0

            def continue_(self):
                self.continue_count += 1

        FakeClient.probe = self.probe
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
                self.probe.run_trace(
                    trace_spec,
                    output,
                    "127.0.0.1",
                    1337,
                    1.0,
                    wait_register_not_value=(29, 0x80080000),
                    max_skipped_hits=2,
                )
            finally:
                self.probe._connect = original_connect
                self.probe.RSPClient = original_client
                self.probe.CEMU_GDB_SETTLE_SECONDS = original_settle
            rows = [json.loads(line) for line in output.read_text().splitlines()]

        miss = next(row for row in rows if row["event"] == "condition_miss")
        self.assertEqual("not_value", miss["condition"])
        self.assertEqual("0x80080000", miss["excluded_value"])
        met = next(row for row in rows if row["event"] == "condition_met")
        self.assertEqual("0xa0080000", met["value"])
        self.assertEqual("0x80080000", met["excluded_value"])
        self.assertNotIn("required_mask", met)
        hit = next(row for row in rows if row["event"] == "hit")
        self.assertEqual("0xa0080000", hit["snapshot"]["gpr"]["r29"])
        self.assertEqual(3, FakeClient.instance.continue_count)
        self.assertTrue(sock.closed)

    def test_wait_register_mask_ignores_unrelated_high_bits(self):
        class FakeSocket:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        class FakeClient:
            instance = None

            def __init__(self, sock):
                self.sock = sock
                self.condition_reads = 0
                self.continue_count = 0
                FakeClient.instance = self

            def receive(self, timeout=None):
                return "T05thread:00000001;core:01;swbreak:;"

            def request(self, payload, timeout=5.0):
                return "OK"

            def read_memory(self, address, size):
                if address == 0x028C7B18 and size == 4:
                    return bytes.fromhex("c169e2d0")
                return bytes(size)

            def read_register(self, register):
                if register == self.probe.PPC_PC_REGISTER:
                    return 0x028C7B18
                if register == 29:
                    self.condition_reads += 1
                    if self.condition_reads == 1:
                        return 0x80080000
                    return 0x80082000
                if register == 31:
                    return 0x10000010
                return 0

            def continue_(self):
                self.continue_count += 1

        FakeClient.probe = self.probe
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
                self.probe.run_trace(
                    trace_spec,
                    output,
                    "127.0.0.1",
                    1337,
                    1.0,
                    wait_register_mask=(29, 0x2000),
                    max_skipped_hits=2,
                )
            finally:
                self.probe._connect = original_connect
                self.probe.RSPClient = original_client
                self.probe.CEMU_GDB_SETTLE_SECONDS = original_settle
            rows = [json.loads(line) for line in output.read_text().splitlines()]

        miss = next(row for row in rows if row["event"] == "condition_miss")
        self.assertEqual("mask_set", miss["condition"])
        self.assertEqual("0x00002000", miss["required_mask"])
        met = next(row for row in rows if row["event"] == "condition_met")
        self.assertEqual("0x80082000", met["value"])
        self.assertEqual("0x00002000", met["required_mask"])
        self.assertNotIn("excluded_value", met)
        hit = next(row for row in rows if row["event"] == "hit")
        self.assertEqual("0x80082000", hit["snapshot"]["gpr"]["r29"])
        self.assertEqual(3, FakeClient.instance.continue_count)
        self.assertTrue(sock.closed)


if __name__ == "__main__":
    unittest.main()
