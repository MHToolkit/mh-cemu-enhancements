#!/usr/bin/env python3
"""Fail-closed tracer for Cemu's GDB remote stub.

The probe never launches Cemu and never edits game, MLC, save, or Graphic Pack
files.  It connects to an already running ``--enable-gdbstub`` instance, checks
every declared PPC preimage before arming software breakpoints, records one
matching hit per checkpoint as JSON Lines, removes its breakpoints, and resumes
the title.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import socket
import time
from typing import Any


STOP_THREAD_RE = re.compile(r"thread:([0-9A-Fa-f]+);")
HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")
PPC_GPR_COUNT = 32
PPC_PC_REGISTER = 64
PPC_LR_REGISTER = 67
CEMU_GDB_SETTLE_SECONDS = 1.0


class ProbeError(RuntimeError):
    """Raised when a trace cannot remain fail-closed."""


def _number(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ProbeError(f"{field} must be an integer, not bool")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError as exc:
            raise ProbeError(f"{field} is not an integer: {value!r}") from exc
    raise ProbeError(f"{field} is not an integer: {value!r}")


def _hex32(value: int) -> str:
    return f"0x{value:08x}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def encode_packet(payload: str) -> bytes:
    raw = payload.encode("ascii")
    checksum = sum(raw) & 0xFF
    return b"$" + raw + f"#{checksum:02x}".encode("ascii")


def decode_packet(packet: bytes) -> str:
    if not packet.startswith(b"$") or len(packet) < 4 or packet[-3:-2] != b"#":
        raise ProbeError(f"malformed GDB packet: {packet!r}")
    payload = packet[1:-3]
    checksum_raw = packet[-2:]
    if not HEX_RE.fullmatch(checksum_raw.decode("ascii", "strict")):
        raise ProbeError(f"malformed GDB checksum: {checksum_raw!r}")
    expected = int(checksum_raw, 16)
    observed = sum(payload) & 0xFF
    if observed != expected:
        raise ProbeError(
            f"GDB checksum mismatch: expected {expected:02x}, observed {observed:02x}"
        )
    decoded = bytearray()
    escaped = False
    for byte in payload:
        if escaped:
            decoded.append(byte ^ 0x20)
            escaped = False
        elif byte == ord("}"):
            escaped = True
        else:
            decoded.append(byte)
    if escaped:
        raise ProbeError("malformed trailing GDB escape")
    return decoded.decode("ascii")


@dataclass(frozen=True)
class Breakpoint:
    label: str
    address: int
    expected_word: int


@dataclass(frozen=True)
class FixedMemory:
    label: str
    address: int
    size: int


@dataclass(frozen=True)
class RegisterMemory:
    label: str
    register: int
    offset: int
    size: int


@dataclass(frozen=True)
class TraceSpec:
    name: str
    target: dict[str, str]
    breakpoints: tuple[Breakpoint, ...]
    fixed_memory: tuple[FixedMemory, ...]
    register_memory: tuple[RegisterMemory, ...]


def load_spec(path: Path) -> TraceSpec:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProbeError(f"cannot parse trace spec {path}: {exc}") from exc
    if raw.get("schema_version") != 1:
        raise ProbeError("trace spec schema_version must be 1")
    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ProbeError("trace spec name must be a non-empty string")
    target = raw.get("target")
    if not isinstance(target, dict):
        raise ProbeError("trace spec target must be an object")
    for required in ("title_id", "module_checksum", "cemu_rpx_hash", "rpx_sha256"):
        value = target.get(required)
        if not isinstance(value, str) or not value:
            raise ProbeError(f"trace spec target.{required} must be a non-empty string")
    identity_patterns = {
        "title_id": r"[0-9A-Fa-f]{16}",
        "module_checksum": r"0x[0-9A-Fa-f]{8}",
        "cemu_rpx_hash": r"[0-9A-Fa-f]{8}",
        "rpx_sha256": r"[0-9A-Fa-f]{64}",
    }
    for field, pattern in identity_patterns.items():
        if re.fullmatch(pattern, target[field]) is None:
            raise ProbeError(f"trace spec target.{field} has an invalid format")

    breakpoints_raw = raw.get("breakpoints")
    if not isinstance(breakpoints_raw, list) or not breakpoints_raw:
        raise ProbeError("trace spec must declare at least one breakpoint")
    breakpoints: list[Breakpoint] = []
    labels: set[str] = set()
    addresses: set[int] = set()
    for index, item in enumerate(breakpoints_raw):
        if not isinstance(item, dict):
            raise ProbeError(f"breakpoints[{index}] must be an object")
        label = item.get("label")
        if not isinstance(label, str) or not label:
            raise ProbeError(f"breakpoints[{index}].label must be non-empty")
        address = _number(item.get("address"), f"breakpoints[{index}].address")
        expected = _number(
            item.get("expected_word"), f"breakpoints[{index}].expected_word"
        )
        if address % 4:
            raise ProbeError(f"breakpoint {label!r} address must be 4-byte aligned")
        if not 0 <= expected <= 0xFFFFFFFF:
            raise ProbeError(f"breakpoint {label!r} expected_word is outside u32")
        if label in labels:
            raise ProbeError(f"duplicate breakpoint label: {label}")
        if address in addresses:
            raise ProbeError(f"duplicate breakpoint address: {_hex32(address)}")
        labels.add(label)
        addresses.add(address)
        breakpoints.append(Breakpoint(label, address, expected))

    fixed_memory = _load_fixed_memory(raw.get("fixed_memory", []))
    register_memory = _load_register_memory(raw.get("register_memory", []))
    return TraceSpec(
        name=name,
        target={key: str(value) for key, value in target.items()},
        breakpoints=tuple(breakpoints),
        fixed_memory=tuple(fixed_memory),
        register_memory=tuple(register_memory),
    )


def _load_fixed_memory(raw: Any) -> list[FixedMemory]:
    if not isinstance(raw, list):
        raise ProbeError("fixed_memory must be an array")
    result: list[FixedMemory] = []
    labels: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ProbeError(f"fixed_memory[{index}] must be an object")
        label = item.get("label")
        if not isinstance(label, str) or not label or label in labels:
            raise ProbeError(f"fixed_memory[{index}].label must be unique and non-empty")
        address = _number(item.get("address"), f"fixed_memory[{index}].address")
        size = _number(item.get("size"), f"fixed_memory[{index}].size")
        if not 1 <= size <= 4096:
            raise ProbeError(f"fixed_memory[{index}].size must be 1..4096")
        labels.add(label)
        result.append(FixedMemory(label, address, size))
    return result


def _register_number(value: Any, field: str) -> int:
    if isinstance(value, str) and re.fullmatch(r"r(?:[0-9]|[12][0-9]|3[01])", value):
        return int(value[1:])
    register = _number(value, field)
    if not 0 <= register < PPC_GPR_COUNT:
        raise ProbeError(f"{field} must identify PPC r0..r31")
    return register


def _load_register_memory(raw: Any) -> list[RegisterMemory]:
    if not isinstance(raw, list):
        raise ProbeError("register_memory must be an array")
    result: list[RegisterMemory] = []
    labels: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ProbeError(f"register_memory[{index}] must be an object")
        label = item.get("label")
        if not isinstance(label, str) or not label or label in labels:
            raise ProbeError(
                f"register_memory[{index}].label must be unique and non-empty"
            )
        register = _register_number(
            item.get("register"), f"register_memory[{index}].register"
        )
        offset = _number(item.get("offset", 0), f"register_memory[{index}].offset")
        size = _number(item.get("size"), f"register_memory[{index}].size")
        if not -(1 << 31) <= offset < (1 << 31):
            raise ProbeError(f"register_memory[{index}].offset is outside s32")
        if not 1 <= size <= 4096:
            raise ProbeError(f"register_memory[{index}].size must be 1..4096")
        labels.add(label)
        result.append(RegisterMemory(label, register, offset, size))
    return result


class RSPClient:
    def __init__(self, sock: socket.socket):
        self.sock = sock

    def _read_byte(self, timeout: float | None) -> bytes:
        self.sock.settimeout(timeout)
        value = self.sock.recv(1)
        if not value:
            raise ProbeError("Cemu GDB connection closed")
        return value

    def receive(self, timeout: float | None = None) -> str:
        while True:
            byte = self._read_byte(timeout)
            if byte in (b"+", b"-"):
                continue
            if byte == b"\x03":
                continue
            if byte != b"$":
                raise ProbeError(f"unexpected GDB byte: {byte!r}")
            packet = bytearray(byte)
            while packet[-1:] != b"#":
                packet.extend(self._read_byte(timeout))
            packet.extend(self._read_byte(timeout))
            packet.extend(self._read_byte(timeout))
            try:
                payload = decode_packet(bytes(packet))
            except ProbeError:
                self.sock.sendall(b"-")
                raise
            self.sock.sendall(b"+")
            # RSP console-output packets are ``O`` followed by hex-encoded
            # bytes.  Do not confuse the ordinary command response ``OK`` for
            # console output, or every successful Cemu command will time out.
            console_hex = payload[1:]
            if (
                payload.startswith("O")
                and len(console_hex) % 2 == 0
                and bool(console_hex)
                and HEX_RE.fullmatch(console_hex) is not None
            ):
                continue
            return payload

    def request(self, payload: str, timeout: float = 5.0) -> str:
        self.sock.sendall(encode_packet(payload))
        response = self.receive(timeout)
        if response.startswith("E"):
            raise ProbeError(f"GDB request {payload!r} failed: {response}")
        return response

    def interrupt(self) -> None:
        self.sock.sendall(b"\x03")

    def continue_(self) -> None:
        self.sock.sendall(encode_packet("c"))

    def read_memory(self, address: int, size: int) -> bytes:
        response = self.request(f"m{address:x},{size:x}")
        if len(response) != size * 2 or not HEX_RE.fullmatch(response):
            raise ProbeError(
                f"invalid memory response at {_hex32(address)} size {size}: {response!r}"
            )
        return bytes.fromhex(response)

    def read_register(self, register: int) -> int:
        response = self.request(f"p{register:x}")
        if not response or not HEX_RE.fullmatch(response):
            raise ProbeError(f"invalid register r{register} response: {response!r}")
        # Cemu's stub swaps its internally byte-reversed OSContext GPR/LR
        # storage before formatting the RSP response.  The resulting hex text
        # is therefore already the logical big-endian PPC value, just like PC
        # and the remaining special registers.  Reversing it again turns valid
        # guest pointers such as 0x2d8914b0 into inaccessible 0xb014892d.
        return int(response, 16)


def _select_thread(client: RSPClient, stop: str) -> str:
    match = STOP_THREAD_RE.search(stop)
    thread = match.group(1) if match else "0"
    client.request(f"Hg{thread}")
    client.request("Hc-1")
    return thread


def _select_default_threads(client: RSPClient) -> None:
    """Select Cemu's default register thread and all continue threads.

    Cemu 2.6 accepts ``Hg0`` while the emulated title is running.  Selecting
    the concrete thread reported by ``?`` is not equivalent: that thread is a
    status hint rather than a guaranteed stopped-thread context and can leave
    the stub waiting forever.  Concrete IDs are selected only after a real
    breakpoint stop.
    """

    client.request("Hg0")
    client.request("Hc-1")


def _snapshot(client: RSPClient, spec: TraceSpec) -> dict[str, Any]:
    registers = [client.read_register(index) for index in range(PPC_GPR_COUNT)]
    pc = client.read_register(PPC_PC_REGISTER)
    lr = client.read_register(PPC_LR_REGISTER)
    fixed = {
        item.label: {
            "address": _hex32(item.address),
            "size": item.size,
            "hex": client.read_memory(item.address, item.size).hex(),
        }
        for item in spec.fixed_memory
    }
    register_memory: dict[str, Any] = {}
    for item in spec.register_memory:
        address = (registers[item.register] + item.offset) & 0xFFFFFFFF
        register_memory[item.label] = {
            "base_register": f"r{item.register}",
            "base_value": _hex32(registers[item.register]),
            "offset": item.offset,
            "address": _hex32(address),
            "size": item.size,
            "hex": client.read_memory(address, item.size).hex(),
        }
    return {
        "pc": _hex32(pc),
        "lr": _hex32(lr),
        "gpr": {f"r{index}": _hex32(value) for index, value in enumerate(registers)},
        "fixed_memory": fixed,
        "register_memory": register_memory,
    }


def _connect(host: str, port: int, timeout: float) -> socket.socket:
    deadline = time.monotonic() + timeout
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            return socket.create_connection((host, port), timeout=min(1.0, timeout))
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    raise ProbeError(f"cannot connect to Cemu GDB at {host}:{port}: {last_error}")


def run_trace(
    spec: TraceSpec,
    output: Path,
    host: str,
    port: int,
    connect_timeout: float,
    wait_register_nonzero: int | None = None,
    wait_register_not_value: tuple[int, int] | None = None,
    wait_register_mask: tuple[int, int] | None = None,
    max_skipped_hits: int = 120,
) -> None:
    wait_condition_count = sum(
        condition is not None
        for condition in (
            wait_register_nonzero,
            wait_register_not_value,
            wait_register_mask,
        )
    )
    if wait_condition_count > 1:
        raise ProbeError(
            "register wait conditions are mutually exclusive"
        )
    if wait_register_nonzero is not None and not 0 <= wait_register_nonzero < PPC_GPR_COUNT:
        raise ProbeError("wait_register_nonzero must identify PPC r0..r31")
    if wait_register_not_value is not None:
        wait_register, excluded_value = wait_register_not_value
        if not 0 <= wait_register < PPC_GPR_COUNT:
            raise ProbeError("wait_register_not_value must identify PPC r0..r31")
        if not 0 <= excluded_value <= 0xFFFFFFFF:
            raise ProbeError("wait_register_not_value comparison is outside u32")
    if wait_register_mask is not None:
        wait_register, required_mask = wait_register_mask
        if not 0 <= wait_register < PPC_GPR_COUNT:
            raise ProbeError("wait_register_mask must identify PPC r0..r31")
        if not 1 <= required_mask <= 0xFFFFFFFF:
            raise ProbeError("wait_register_mask mask must be a nonzero u32")
    if max_skipped_hits < 1:
        raise ProbeError("max_skipped_hits must be at least 1")
    if output.exists():
        raise ProbeError(f"refusing to overwrite trace output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    def emit(event: str, **fields: Any) -> None:
        row = {"ts": _utc_now(), "event": event, **fields}
        with output.open("a", encoding="utf-8") as target:
            target.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        print(json.dumps(row, ensure_ascii=False, sort_keys=True), flush=True)

    sock = _connect(host, port, connect_timeout)
    client = RSPClient(sock)
    active: dict[int, Breakpoint] = {}
    skipped_hits: dict[int, int] = {}
    paused = False
    try:
        # Cemu 2.6 does not send an unsolicited stop packet when a client
        # attaches.  Querying '?' is its non-blocking session handshake; it
        # returns a default-thread status without pausing the title.  Do not
        # send Ctrl-C here: doing so turns a read-only attach into a disruptive
        # pause and selecting that status thread with Hg<tid> can deadlock.
        time.sleep(CEMU_GDB_SETTLE_SECONDS)
        stop = client.request("?")
        match = STOP_THREAD_RE.search(stop)
        thread = match.group(1) if match else "0"
        emit(
            "status",
            trace=spec.name,
            target=spec.target,
            thread=thread,
            stop=stop,
            target_running=True,
        )
        _select_default_threads(client)
        emit("session_ready", register_thread="default", continue_threads="all")

        observed: dict[str, str] = {}
        for breakpoint in spec.breakpoints:
            raw = client.read_memory(breakpoint.address, 4)
            word = int.from_bytes(raw, "big")
            observed[breakpoint.label] = _hex32(word)
            if word != breakpoint.expected_word:
                raise ProbeError(
                    f"preimage mismatch for {breakpoint.label}: "
                    f"expected {_hex32(breakpoint.expected_word)}, observed {_hex32(word)}"
                )
        emit(
            "connected",
            trace=spec.name,
            target=spec.target,
            thread=thread,
            stop=stop,
            observed_preimages=observed,
        )

        for breakpoint in spec.breakpoints:
            response = client.request(f"Z0,{breakpoint.address:x},4")
            if response != "OK":
                raise ProbeError(
                    f"cannot arm {breakpoint.label} at {_hex32(breakpoint.address)}: "
                    f"{response!r}"
                )
            active[breakpoint.address] = breakpoint
            emit(
                "armed",
                label=breakpoint.label,
                address=_hex32(breakpoint.address),
                expected_word=_hex32(breakpoint.expected_word),
            )

        while active:
            paused = False
            client.continue_()
            stop = client.receive(None)
            paused = True
            thread = _select_thread(client, stop)
            pc = client.read_register(PPC_PC_REGISTER)
            breakpoint = active.get(pc)
            if breakpoint is None:
                emit("unexpected_stop", thread=thread, stop=stop, snapshot=_snapshot(client, spec))
                raise ProbeError(f"unexpected stop at {_hex32(pc)}")
            condition_register = wait_register_nonzero
            condition_kind = "nonzero"
            condition_excluded_value = 0
            if wait_register_not_value is not None:
                condition_register, condition_excluded_value = wait_register_not_value
                condition_kind = "not_value"
            if wait_register_mask is not None:
                condition_register, condition_required_mask = wait_register_mask
                condition_kind = "mask_set"
            if condition_register is not None:
                condition_value = client.read_register(condition_register)
                condition_matches = condition_value != condition_excluded_value
                condition_details: dict[str, str] = {}
                if condition_kind == "mask_set":
                    condition_matches = (
                        condition_value & condition_required_mask
                    ) == condition_required_mask
                    condition_details["required_mask"] = _hex32(condition_required_mask)
                else:
                    condition_details["excluded_value"] = _hex32(
                        condition_excluded_value
                    )
                if not condition_matches:
                    count = skipped_hits.get(pc, 0) + 1
                    skipped_hits[pc] = count
                    emit(
                        "condition_miss",
                        label=breakpoint.label,
                        address=_hex32(breakpoint.address),
                        thread=thread,
                        register=f"r{condition_register}",
                        condition=condition_kind,
                        value=_hex32(condition_value),
                        skipped_hits=count,
                        **condition_details,
                    )
                    if count >= max_skipped_hits:
                        raise ProbeError(
                            f"wait condition {condition_kind} did not match for "
                            f"r{condition_register} after {count} hit(s)"
                        )
                    continue
                emit(
                    "condition_met",
                    label=breakpoint.label,
                    address=_hex32(breakpoint.address),
                    thread=thread,
                    register=f"r{condition_register}",
                    condition=condition_kind,
                    value=_hex32(condition_value),
                    skipped_hits=skipped_hits.get(pc, 0),
                    **condition_details,
                )
            snapshot = _snapshot(client, spec)
            emit(
                "hit",
                label=breakpoint.label,
                address=_hex32(breakpoint.address),
                thread=thread,
                stop=stop,
                snapshot=snapshot,
            )
            response = client.request(f"z0,{breakpoint.address:x},4")
            if response != "OK":
                raise ProbeError(f"cannot remove breakpoint {breakpoint.label}: {response!r}")
            del active[breakpoint.address]
            emit("consumed", label=breakpoint.label, address=_hex32(breakpoint.address))

        emit("complete", trace=spec.name)
    except BaseException as exc:
        emit("fatal", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        if active and not paused:
            try:
                client.interrupt()
                stop = client.receive(5.0)
                paused = True
                _select_default_threads(client)
                match = STOP_THREAD_RE.search(stop)
                thread = match.group(1) if match else "0"
                emit("cleanup_interrupt", thread=thread, stop=stop)
            except BaseException as exc:
                emit(
                    "cleanup_interrupt_error",
                    error=f"{type(exc).__name__}: {exc}",
                )
        if paused:
            for address, breakpoint in tuple(active.items()):
                try:
                    response = client.request(f"z0,{address:x},4", timeout=1.0)
                    emit(
                        "cleanup_breakpoint",
                        label=breakpoint.label,
                        address=_hex32(address),
                        response=response,
                    )
                except BaseException as exc:
                    emit(
                        "cleanup_error",
                        label=breakpoint.label,
                        address=_hex32(address),
                        error=f"{type(exc).__name__}: {exc}",
                    )
            try:
                client.continue_()
                emit("resumed")
            except BaseException as exc:
                emit("resume_error", error=f"{type(exc).__name__}: {exc}")
        sock.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check-spec", help="validate a trace spec without Cemu")
    check.add_argument("--spec", type=Path, required=True)
    trace = subparsers.add_parser("trace", help="run a fail-closed trace")
    trace.add_argument("--spec", type=Path, required=True)
    trace.add_argument("--output", type=Path, required=True)
    trace.add_argument("--host", default="127.0.0.1")
    trace.add_argument("--port", type=int, default=1337)
    trace.add_argument("--connect-timeout", type=float, default=180.0)
    trace.add_argument(
        "--wait-register-nonzero",
        help="ignore breakpoint hits until the selected PPC GPR is nonzero (for example r29)",
    )
    trace.add_argument(
        "--wait-register-not-value",
        metavar="REGISTER=VALUE",
        help=(
            "ignore breakpoint hits while the selected PPC GPR equals VALUE "
            "(for example r29=0x80080000)"
        ),
    )
    trace.add_argument(
        "--wait-register-mask",
        metavar="REGISTER=MASK",
        help=(
            "ignore breakpoint hits until all MASK bits are set in the selected "
            "PPC GPR (for example r29=0x2000)"
        ),
    )
    trace.add_argument(
        "--max-skipped-hits",
        type=int,
        default=120,
        help="fail closed after this many non-matching hits while waiting (default: 120)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        spec = load_spec(args.spec)
        if args.command == "check-spec":
            print(
                f"OK: {spec.name}: {len(spec.breakpoints)} breakpoint(s), "
                f"{len(spec.fixed_memory)} fixed snapshot(s), "
                f"{len(spec.register_memory)} register snapshot(s)"
            )
            return 0
        wait_register = None
        if args.wait_register_nonzero is not None:
            wait_register = _register_number(
                args.wait_register_nonzero, "--wait-register-nonzero"
            )
        wait_register_not_value = None
        if args.wait_register_not_value is not None:
            register_raw, separator, value_raw = args.wait_register_not_value.partition("=")
            if not separator:
                raise ProbeError(
                    "--wait-register-not-value must use REGISTER=VALUE syntax"
                )
            wait_register_not_value = (
                _register_number(register_raw, "--wait-register-not-value"),
                _number(value_raw, "--wait-register-not-value"),
            )
        wait_register_mask = None
        if args.wait_register_mask is not None:
            register_raw, separator, mask_raw = args.wait_register_mask.partition("=")
            if not separator:
                raise ProbeError("--wait-register-mask must use REGISTER=MASK syntax")
            wait_register_mask = (
                _register_number(register_raw, "--wait-register-mask"),
                _number(mask_raw, "--wait-register-mask"),
            )
        run_trace(
            spec,
            args.output,
            args.host,
            args.port,
            args.connect_timeout,
            wait_register_nonzero=wait_register,
            wait_register_not_value=wait_register_not_value,
            wait_register_mask=wait_register_mask,
            max_skipped_hits=args.max_skipped_hits,
        )
        return 0
    except ProbeError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
