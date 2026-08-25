#!/usr/bin/env python3
"""Enumerate direct PPC D-form memory accesses to selected object offsets.

The scanner reads the big-endian PowerPC ``.text`` section from an ELF32 file
without external disassembly dependencies.  It is intended for narrowing native
writers after a runtime snapshot proves a field offset; it does not establish an
object identity or gameplay meaning by itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
from typing import Any


DFORM_OPS = {
    32: ("lwz", "load", "word"),
    33: ("lwzu", "load", "word"),
    34: ("lbz", "load", "byte"),
    35: ("lbzu", "load", "byte"),
    36: ("stw", "store", "word"),
    37: ("stwu", "store", "word"),
    38: ("stb", "store", "byte"),
    39: ("stbu", "store", "byte"),
    40: ("lhz", "load", "halfword"),
    41: ("lhzu", "load", "halfword"),
    42: ("lha", "load", "halfword"),
    43: ("lhau", "load", "halfword"),
    44: ("sth", "store", "halfword"),
    45: ("sthu", "store", "halfword"),
    48: ("lfs", "load", "float"),
    49: ("lfsu", "load", "float"),
    50: ("lfd", "load", "float"),
    51: ("lfdu", "load", "float"),
    52: ("stfs", "store", "float"),
    53: ("stfsu", "store", "float"),
    54: ("stfd", "store", "float"),
    55: ("stfdu", "store", "float"),
}


class ScanError(RuntimeError):
    """Raised when the input is not the expected ELF32 big-endian form."""


def _c_string(data: bytes, offset: int) -> str:
    if not 0 <= offset < len(data):
        raise ScanError("section-name offset is outside the string table")
    end = data.find(b"\0", offset)
    if end < 0:
        raise ScanError("unterminated section name")
    return data[offset:end].decode("ascii", "strict")


def load_text(path: Path) -> tuple[int, bytes]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ScanError(f"cannot read ELF {path}: {exc}") from exc
    if len(data) < 52 or data[:4] != b"\x7fELF":
        raise ScanError("input is not an ELF file")
    if data[4] != 1 or data[5] != 2:
        raise ScanError("input must be ELF32 big-endian")
    try:
        section_offset = struct.unpack_from(">I", data, 0x20)[0]
        entry_size = struct.unpack_from(">H", data, 0x2E)[0]
        section_count = struct.unpack_from(">H", data, 0x30)[0]
        names_index = struct.unpack_from(">H", data, 0x32)[0]
    except struct.error as exc:
        raise ScanError("truncated ELF header") from exc
    if entry_size < 40 or section_count < 1 or names_index >= section_count:
        raise ScanError("invalid ELF section table")
    if section_offset + entry_size * section_count > len(data):
        raise ScanError("ELF section table is truncated")

    sections = [
        struct.unpack_from(">IIIIIIIIII", data, section_offset + index * entry_size)
        for index in range(section_count)
    ]
    names_header = sections[names_index]
    names_start, names_size = names_header[4], names_header[5]
    if names_start + names_size > len(data):
        raise ScanError("ELF section-name table is truncated")
    names = data[names_start : names_start + names_size]
    text = None
    for section in sections:
        if _c_string(names, section[0]) == ".text":
            text = section
            break
    if text is None:
        raise ScanError("ELF has no .text section")
    text_address, text_offset, text_size = text[3], text[4], text[5]
    if text_offset + text_size > len(data) or text_size % 4:
        raise ScanError("ELF .text section is truncated or unaligned")
    return text_address, data[text_offset : text_offset + text_size]


def _signed16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def scan(
    text_address: int,
    text: bytes,
    offsets: set[int],
    access: str = "all",
    width: str = "all",
    include_stack: bool = False,
    start_address: int | None = None,
    end_address: int | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in range(0, len(text), 4):
        address = text_address + index
        if start_address is not None and address < start_address:
            continue
        if end_address is not None and address >= end_address:
            continue
        word = int.from_bytes(text[index : index + 4], "big")
        decoded = DFORM_OPS.get(word >> 26)
        if decoded is None:
            continue
        mnemonic, operation, operand_width = decoded
        register = (word >> 21) & 0x1F
        base_register = (word >> 16) & 0x1F
        displacement = _signed16(word & 0xFFFF)
        if displacement not in offsets:
            continue
        if not include_stack and base_register == 1:
            continue
        if access != "all" and operation != access:
            continue
        if width != "all" and operand_width != width:
            continue
        register_name = f"f{register}" if operand_width == "float" else f"r{register}"
        rows.append(
            {
                "address": f"0x{address:08x}",
                "word": f"0x{word:08x}",
                "mnemonic": mnemonic,
                "access": operation,
                "width": operand_width,
                "register": register_name,
                "base_register": f"r{base_register}",
                "displacement": f"{displacement:+#x}",
                "assembly": (
                    f"{mnemonic} {register_name}, {displacement:#x}(r{base_register})"
                ),
            }
        )
    return rows


def _number(value: str) -> int:
    return int(value, 0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--offset", type=_number, action="append", required=True)
    parser.add_argument("--access", choices=("all", "load", "store"), default="all")
    parser.add_argument(
        "--width",
        choices=("all", "byte", "halfword", "word", "float"),
        default="all",
    )
    parser.add_argument("--include-stack", action="store_true")
    parser.add_argument("--start-address", type=_number)
    parser.add_argument("--end-address", type=_number)
    parser.add_argument("--json-output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.start_address is not None and args.end_address is not None:
        if args.start_address >= args.end_address:
            print("ERROR: --start-address must be lower than --end-address")
            return 2
    try:
        text_address, text = load_text(args.elf)
        rows = scan(
            text_address,
            text,
            set(args.offset),
            access=args.access,
            width=args.width,
            include_stack=args.include_stack,
            start_address=args.start_address,
            end_address=args.end_address,
        )
        report = {
            "schema_version": 1,
            "scope": "static-dform-accesses-only-not-object-proof",
            "elf": str(args.elf),
            "text_address": f"0x{text_address:08x}",
            "text_size": len(text),
            "offsets": [f"{value:+#x}" for value in sorted(set(args.offset))],
            "access": args.access,
            "width": args.width,
            "include_stack": args.include_stack,
            "start_address": (
                f"0x{args.start_address:08x}" if args.start_address is not None else None
            ),
            "end_address": (
                f"0x{args.end_address:08x}" if args.end_address is not None else None
            ),
            "hit_count": len(rows),
            "hits": rows,
        }
        if args.json_output:
            if args.json_output.exists():
                raise ScanError(f"refusing to overwrite report: {args.json_output}")
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(
            f".text {report['text_address']} size={report['text_size']}; "
            f"hits={report['hit_count']}"
        )
        for row in rows:
            print(f"{row['address']} {row['word']}  {row['assembly']}")
        return 0
    except (ScanError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
