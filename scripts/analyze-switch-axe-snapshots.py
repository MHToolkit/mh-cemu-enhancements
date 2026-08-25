#!/usr/bin/env python3
"""Rank byte fields from five controlled MH3G Switch Axe snapshots.

This helper is deliberately fail-closed.  It accepts only complete JSONL traces
from ``cemu-gdb-probe.py``, requires the same target identity and player-object
base for every capture, and reports a strict candidate only when one byte follows
the full -> two consumptions -> two recharge samples expected of the 0..100
Switch Axe gauge.  Finding a candidate does not prove its PPC writer.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any


TARGET_FIELDS = ("title_id", "module_checksum", "cemu_rpx_hash", "rpx_sha256")
ROLE_NAMES = ("full", "consume_1", "consume_2", "recharge_1", "recharge_2")
EXPECTED_OFFSETS = (0x64, 0x6C)


class AnalysisError(RuntimeError):
    """Raised when the evidence bundle cannot remain fail-closed."""


@dataclass(frozen=True)
class Snapshot:
    role: str
    path: Path
    target: tuple[str, ...]
    base_value: int
    memory_offset: int
    data: bytes


def _read_rows(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AnalysisError(f"cannot read trace {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AnalysisError(
                f"invalid JSON in {path}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(row, dict):
            raise AnalysisError(f"trace row {path}:{line_number} must be an object")
        rows.append(row)
    if not rows:
        raise AnalysisError(f"trace is empty: {path}")
    return rows


def load_snapshot(role: str, path: Path, memory_label: str) -> Snapshot:
    rows = _read_rows(path)
    fatal = [row for row in rows if row.get("event") == "fatal"]
    if fatal:
        raise AnalysisError(f"trace contains a fatal event: {path}")
    if sum(row.get("event") == "complete" for row in rows) != 1:
        raise AnalysisError(f"trace must contain exactly one complete event: {path}")
    hits = [row for row in rows if row.get("event") == "hit"]
    if len(hits) != 1:
        raise AnalysisError(f"trace must contain exactly one hit event: {path}")

    status_rows = [row for row in rows if row.get("event") == "status"]
    if len(status_rows) != 1 or not isinstance(status_rows[0].get("target"), dict):
        raise AnalysisError(f"trace must contain exactly one target-bearing status: {path}")
    target_raw = status_rows[0]["target"]
    target: list[str] = []
    for field in TARGET_FIELDS:
        value = target_raw.get(field)
        if not isinstance(value, str) or not value:
            raise AnalysisError(f"trace target.{field} is missing in {path}")
        target.append(value.lower())

    snapshot = hits[0].get("snapshot")
    if not isinstance(snapshot, dict):
        raise AnalysisError(f"hit snapshot is missing in {path}")
    register_memory = snapshot.get("register_memory")
    if not isinstance(register_memory, dict):
        raise AnalysisError(f"hit register_memory is missing in {path}")
    region = register_memory.get(memory_label)
    if not isinstance(region, dict):
        raise AnalysisError(f"snapshot label {memory_label!r} is missing in {path}")

    base_raw = region.get("base_value")
    offset_raw = region.get("offset")
    size_raw = region.get("size")
    hex_raw = region.get("hex")
    if not isinstance(base_raw, str):
        raise AnalysisError(f"snapshot base_value is invalid in {path}")
    if not isinstance(offset_raw, int) or isinstance(offset_raw, bool):
        raise AnalysisError(f"snapshot offset is invalid in {path}")
    if not isinstance(size_raw, int) or isinstance(size_raw, bool) or size_raw <= 0:
        raise AnalysisError(f"snapshot size is invalid in {path}")
    if not isinstance(hex_raw, str):
        raise AnalysisError(f"snapshot hex payload is invalid in {path}")
    try:
        base_value = int(base_raw, 0)
        data = bytes.fromhex(hex_raw)
    except ValueError as exc:
        raise AnalysisError(f"snapshot encoding is invalid in {path}: {exc}") from exc
    if len(data) != size_raw:
        raise AnalysisError(
            f"snapshot size mismatch in {path}: declared {size_raw}, decoded {len(data)}"
        )
    return Snapshot(
        role=role,
        path=path,
        target=tuple(target),
        base_value=base_value,
        memory_offset=offset_raw,
        data=data,
    )


def _candidate(offset: int, values: tuple[int, ...]) -> dict[str, Any]:
    full, consume_1, consume_2, recharge_1, recharge_2 = values
    bounded = all(0 <= value <= 100 for value in values)
    strict = (
        bounded
        and full == 100
        and full > consume_1 > consume_2
        and consume_2 < recharge_1 < recharge_2 <= full
    )
    relaxed = (
        bounded
        and full >= consume_1 >= consume_2
        and full > consume_2
        and consume_2 < recharge_1 <= recharge_2 <= full
        and recharge_2 > consume_2
    )
    transition_count = sum(
        (
            full > consume_1,
            consume_1 > consume_2,
            recharge_1 > consume_2,
            recharge_2 > recharge_1,
        )
    )
    return {
        "offset": f"0x{offset:04x}",
        "values": dict(zip(ROLE_NAMES, values, strict=True)),
        "strict": strict,
        "relaxed": relaxed,
        "score": transition_count + (4 if full == 100 else 0),
        "matches_source_offset": offset == 0x64,
        "matches_plus_8_layout_hypothesis": offset == 0x6C,
    }


def analyze(snapshots: list[Snapshot], top: int = 32) -> dict[str, Any]:
    if [snapshot.role for snapshot in snapshots] != list(ROLE_NAMES):
        raise AnalysisError(f"snapshot roles must be exactly: {', '.join(ROLE_NAMES)}")
    targets = {snapshot.target for snapshot in snapshots}
    if len(targets) != 1:
        raise AnalysisError("all snapshots must use the same pinned MH3G target identity")
    bases = {snapshot.base_value for snapshot in snapshots}
    if len(bases) != 1:
        raise AnalysisError(
            "player-object base changed between snapshots; repeat all five captures "
            "in one Cemu process, quest, area, and equipment lifecycle"
        )
    memory_offsets = {snapshot.memory_offset for snapshot in snapshots}
    sizes = {len(snapshot.data) for snapshot in snapshots}
    if len(memory_offsets) != 1 or len(sizes) != 1:
        raise AnalysisError("all snapshots must cover the same register-relative memory range")

    memory_offset = next(iter(memory_offsets))
    size = next(iter(sizes))
    candidates = [
        _candidate(
            memory_offset + index,
            tuple(snapshot.data[index] for snapshot in snapshots),
        )
        for index in range(size)
    ]
    strict = [item for item in candidates if item["strict"]]
    relaxed = [item for item in candidates if item["relaxed"] and not item["strict"]]
    strict.sort(key=lambda item: (-item["score"], int(item["offset"], 0)))
    relaxed.sort(key=lambda item: (-item["score"], int(item["offset"], 0)))

    by_offset = {int(item["offset"], 0): item for item in candidates}
    expected = {
        f"0x{offset:04x}": by_offset.get(offset)
        for offset in EXPECTED_OFFSETS
    }
    status = "strict-candidates-found" if strict else "relaxed-only" if relaxed else "no-candidate"
    target_tuple = next(iter(targets))
    return {
        "schema_version": 1,
        "status": status,
        "scope": "field-candidate-only-not-writer-proof",
        "target": dict(zip(TARGET_FIELDS, target_tuple, strict=True)),
        "player_base": f"0x{next(iter(bases)):08x}",
        "snapshot_offset": memory_offset,
        "snapshot_size": size,
        "expected_offsets": expected,
        "strict_candidate_count": len(strict),
        "relaxed_candidate_count": len(relaxed),
        "strict_candidates": strict[:top],
        "relaxed_candidates": relaxed[:top],
        "next_gate": (
            "Use the winning byte offset to enumerate native PPC byte stores, then "
            "execution-breakpoint every narrowed writer during consumption and recharge."
        ),
    }


def _print_report(report: dict[str, Any]) -> None:
    print(f"status: {report['status']}")
    print(f"player base: {report['player_base']}")
    print(
        "candidate counts: "
        f"strict={report['strict_candidate_count']} "
        f"relaxed={report['relaxed_candidate_count']}"
    )
    for offset, candidate in report["expected_offsets"].items():
        if candidate is None:
            print(f"expected {offset}: outside snapshot")
        else:
            values = candidate["values"]
            sequence = " -> ".join(str(values[role]) for role in ROLE_NAMES)
            print(
                f"expected {offset}: {sequence}; "
                f"strict={candidate['strict']} relaxed={candidate['relaxed']}"
            )
    rows = report["strict_candidates"] or report["relaxed_candidates"]
    for candidate in rows:
        values = candidate["values"]
        sequence = " -> ".join(str(values[role]) for role in ROLE_NAMES)
        grade = "strict" if candidate["strict"] else "relaxed"
        print(f"{grade} {candidate['offset']}: {sequence}")
    print(f"next gate: {report['next_gate']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    for role in ROLE_NAMES:
        parser.add_argument(f"--{role.replace('_', '-')}", type=Path, required=True)
    parser.add_argument("--memory-label", default="player_state")
    parser.add_argument("--top", type=int, default=32)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.top < 1:
        print("ERROR: --top must be at least 1")
        return 2
    try:
        paths = {
            role: getattr(args, role)
            for role in ROLE_NAMES
        }
        snapshots = [
            load_snapshot(role, paths[role], args.memory_label) for role in ROLE_NAMES
        ]
        report = analyze(snapshots, args.top)
        if args.output:
            if args.output.exists():
                raise AnalysisError(f"refusing to overwrite report: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        _print_report(report)
        return 0 if report["status"] == "strict-candidates-found" else 3
    except AnalysisError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
