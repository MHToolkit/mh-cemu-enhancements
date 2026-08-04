#!/usr/bin/env python3
"""Validate, install, remove, and package portable Cemu enhancement packs.

This tool deliberately manages only its owned ``graphicPacks/mh-cemu-enhancements`` directory.
It never launches Cemu and never reads or writes save/MLC data.
"""

from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime, timezone
import hashlib
import json
import re
import shlex
import shutil
import struct
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree


CATALOG_PATH = Path("catalog/packs.json")
MANIFEST_SCHEMA_PATH = Path("schemas/pack-manifest.schema.json")
INSTALL_DIRECTORY = Path("mh-cemu-enhancements")
NEMESSIX_ISOLATED_ROOT_SUFFIX = (
    "Library",
    "Application Support",
    "Nemessix Dev",
    "cemu",
)
FORBIDDEN_ASSET_SUFFIXES = {".rpx", ".rpl", ".wua", ".wux", ".wud", ".cci", ".arc"}


@dataclasses.dataclass
class ValidationResult:
    packs: list[dict[str, Any]]
    errors: list[str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalized_root(path: Path) -> Path:
    # Cemu validates the lexical environment value; resolving /tmp and other
    # macOS symlinks would produce a different value than the caller supplied.
    return path.expanduser().absolute()


def _is_nemessix_isolated_root(cemu_root: Path) -> bool:
    return _normalized_root(cemu_root).parts[-len(NEMESSIX_ISOLATED_ROOT_SUFFIX):] == NEMESSIX_ISOLATED_ROOT_SUFFIX


def graphic_packs_root(cemu_root: Path) -> Path:
    """Return the user-data graphicPacks directory for either supported root layout."""
    root = _normalized_root(cemu_root)
    if _is_nemessix_isolated_root(root):
        return root / "data" / "graphicPacks"
    return root / "graphicPacks"


def install_root(cemu_root: Path) -> Path:
    return graphic_packs_root(cemu_root) / INSTALL_DIRECTORY


def _legacy_isolated_install_root(cemu_root: Path) -> Path | None:
    root = _normalized_root(cemu_root)
    if _is_nemessix_isolated_root(root):
        return root / "graphicPacks" / INSTALL_DIRECTORY
    return None


def _settings_path(cemu_root: Path) -> tuple[Path, str]:
    root = _normalized_root(cemu_root)
    if _is_nemessix_isolated_root(root):
        return root / "config" / "settings.xml", "isolated"
    return root / "settings.xml", "standard"


def isolated_launch_command(cemu_app: Path, cemu_root: Path) -> str:
    """Build, but never execute, the command for the supplied isolated Cemu build."""
    root = _normalized_root(cemu_root)
    if not root.is_absolute() or not _is_nemessix_isolated_root(root):
        suffix = "/".join(NEMESSIX_ISOLATED_ROOT_SUFFIX)
        raise ValueError(f"isolated Cemu root must end with /{suffix}")
    binary = _normalized_root(cemu_app) / "Contents" / "MacOS" / "Cemu_release"
    return f"env NEMESSIX_CEMU_DATA_ROOT={shlex.quote(str(root))} {shlex.quote(str(binary))}"


def inspect_cemu_root(cemu_root: Path, packs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Report installation and Cemu saved-enable state without mutating any Cemu file."""
    root = _normalized_root(cemu_root)
    user_data_root = root / "data" if _is_nemessix_isolated_root(root) else root
    target = install_root(root)
    config_path, config_layout = _settings_path(root)
    enabled_rules: set[Path] = set()
    config_error: str | None = None
    if config_path.is_file():
        try:
            document = ElementTree.parse(config_path)
            for entry in document.findall("./GraphicPack/Entry"):
                if entry.get("disabled", "false").lower() == "true":
                    continue
                filename = entry.get("filename")
                if filename:
                    path = Path(filename)
                    enabled_rules.add(_normalized_root(path if path.is_absolute() else user_data_root / path))
        except (ElementTree.ParseError, OSError) as exc:
            config_error = str(exc)
    pack_reports = []
    for pack in packs:
        rules = target / pack["install_folder"] / pack["rules"]
        pack_reports.append(
            {
                "id": pack["id"],
                "installed": rules.is_file(),
                "enabled": _normalized_root(rules) in enabled_rules,
                "rules_path": rules,
            }
        )
    return {
        "cemu_root": root,
        "user_data_root": user_data_root,
        "graphic_packs_root": graphic_packs_root(root),
        "install_root": target,
        "config_path": config_path,
        "config_layout": config_layout,
        "config_exists": config_path.is_file(),
        "config_error": config_error,
        "packs": pack_reports,
    }


def _number(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise ValueError(f"not an integer: {value!r}")


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def _rules_has_required_syntax(path: Path, title_id: str) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "[Definition]" not in text:
        errors.append(f"{path}: missing [Definition]")
    if f"titleIds = {title_id}" not in text:
        errors.append(f"{path}: titleIds does not pin {title_id}")
    if "version = 7" not in text:
        errors.append(f"{path}: missing Graphic Pack version = 7")
    return errors


def _asm_has_required_syntax(path: Path, module_checksum: str, patch_addresses: set[int]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "[MH3G HD JP v96]" not in text:
        errors.append(f"{path}: missing patch group")
    if f"moduleMatches = {module_checksum}" not in text:
        errors.append(f"{path}: module checksum is not pinned")
    for address in patch_addresses:
        if f"0x{address:08x} =" not in text.lower():
            errors.append(f"{path}: missing patch instruction at 0x{address:08x}")
    return errors


def validate_repository(repo_root: Path) -> ValidationResult:
    repo_root = repo_root.resolve()
    errors: list[str] = []
    schema_file = repo_root / MANIFEST_SCHEMA_PATH
    try:
        schema = _load_json(schema_file)
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationResult([], [f"cannot parse manifest schema {schema_file}: {exc}"])
    status_enum = schema.get("properties", {}).get("status", {}).get("enum")
    if status_enum != ["Static Verified", "Runtime Experimental", "Runtime Verified"]:
        errors.append("manifest schema must declare the three supported status values")
    catalog_file = repo_root / CATALOG_PATH
    if not catalog_file.is_file():
        return ValidationResult([], [f"missing catalog: {catalog_file}"])
    try:
        catalog = _load_json(catalog_file)
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationResult([], [f"cannot parse {catalog_file}: {exc}"])
    if catalog.get("schema_version") != 1:
        errors.append("catalog schema_version must be 1")
    raw_packs = catalog.get("packs")
    if not isinstance(raw_packs, list) or not raw_packs:
        return ValidationResult([], errors + ["catalog packs must be a non-empty list"])

    packs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for entry in raw_packs:
        if not isinstance(entry, dict):
            errors.append("catalog contains a non-object entry")
            continue
        manifest_rel = entry.get("manifest")
        if not isinstance(manifest_rel, str):
            errors.append("catalog entry missing manifest")
            continue
        manifest_path = repo_root / manifest_rel
        try:
            pack = _load_json(manifest_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot parse manifest {manifest_rel}: {exc}")
            continue
        packs.append(pack)
        required = {
            "id", "platform", "title", "title_id", "title_slug", "region", "update", "status",
            "default_install", "availability", "pack_dir", "install_folder", "rules", "source", "license",
        }
        missing = sorted(required - pack.keys())
        if missing:
            errors.append(f"{manifest_rel}: missing fields: {', '.join(missing)}")
            continue
        pack_id = pack["id"]
        if not isinstance(pack_id, str) or pack_id in seen_ids:
            errors.append(f"{manifest_rel}: duplicate or invalid id {pack_id!r}")
        seen_ids.add(pack_id)
        if pack["platform"] != "wiiu" or pack["title_id"] != "0005000010104D00":
            errors.append(f"{manifest_rel}: target must pin Wii U title 0005000010104D00")
        path_parts = Path(pack["pack_dir"]).parts
        expected_version_dir = f"{pack['region'].lower()}-{pack['update'].lower()}"
        if (
            len(path_parts) < 5
            or path_parts[0] != "packs"
            or path_parts[1] != pack["platform"]
            or path_parts[2] != pack["title_slug"]
            or path_parts[3] != expected_version_dir
        ):
            errors.append(f"{manifest_rel}: pack_dir does not match platform/title/region/update identity")
        if pack["status"] not in {"Static Verified", "Runtime Experimental", "Runtime Verified"}:
            errors.append(f"{manifest_rel}: unknown status {pack['status']!r}")
        if not isinstance(pack["default_install"], bool):
            errors.append(f"{manifest_rel}: default_install must be boolean")
        auto_experimental_install = pack.get("auto_experimental_install", False)
        if not isinstance(auto_experimental_install, bool):
            errors.append(f"{manifest_rel}: auto_experimental_install must be boolean")
        if auto_experimental_install and pack["status"] != "Runtime Experimental":
            errors.append(f"{manifest_rel}: auto_experimental_install requires Runtime Experimental")
        if pack["availability"] not in {"available", "runtime-blocked"}:
            errors.append(f"{manifest_rel}: unknown availability {pack['availability']!r}")
        if pack["status"] == "Runtime Experimental" and pack["default_install"]:
            errors.append(f"{manifest_rel}: experimental pack must default_install=false")

        exclusive_group = pack.get("exclusive_group")
        if exclusive_group is not None and (
            not isinstance(exclusive_group, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9-]+", exclusive_group) is None
        ):
            errors.append(f"{manifest_rel}: exclusive_group must be a lowercase hyphenated identifier")
        source_cheat_entries = pack.get("source_cheat_entries")
        if source_cheat_entries is not None and (
            not isinstance(source_cheat_entries, list)
            or any(not isinstance(entry, int) or entry < 1 for entry in source_cheat_entries)
            or len(set(source_cheat_entries)) != len(source_cheat_entries)
        ):
            errors.append(f"{manifest_rel}: source_cheat_entries must be unique positive integers")

        if pack.get("conversion_kind") == "3ds-arm-static-to-wiiu-ppc":
            static_required = {
                "auto_experimental_install",
                "conversion_confidence",
                "name_bilingual",
                "source_arm_patches",
                "source_cheat_entries",
                "known_risks",
                "patch",
                "preimages",
            }
            missing_static = sorted(static_required - pack.keys())
            if missing_static:
                errors.append(
                    f"{manifest_rel}: static ARM conversion missing fields: "
                    + ", ".join(missing_static)
                )
            if pack["status"] != "Runtime Experimental" or pack["default_install"]:
                errors.append(f"{manifest_rel}: static ARM conversion must be default-off Runtime Experimental")
            if auto_experimental_install:
                errors.append(f"{manifest_rel}: static ARM conversion must require explicit selection")
            if not isinstance(source_cheat_entries, list) or len(source_cheat_entries) != 1:
                errors.append(f"{manifest_rel}: static ARM conversion must reference exactly one source cheat")
            if not isinstance(pack.get("name_bilingual"), str) or " / " not in pack.get("name_bilingual", ""):
                errors.append(f"{manifest_rel}: static ARM conversion needs a bilingual name")
            if not isinstance(pack.get("known_risks"), list) or not pack.get("known_risks"):
                errors.append(f"{manifest_rel}: static ARM conversion needs explicit known_risks")
            for source_patch in pack.get("source_arm_patches", []):
                try:
                    _number(source_patch["address"])
                    _number(source_patch["word"])
                except (KeyError, TypeError, ValueError) as exc:
                    errors.append(f"{manifest_rel}: invalid source ARM patch: {exc}")

        package_dir = repo_root / pack["pack_dir"]
        rules_file = package_dir / pack["rules"]
        if not rules_file.is_file():
            errors.append(f"{manifest_rel}: missing rules file {rules_file}")
        else:
            errors.extend(_rules_has_required_syntax(rules_file, pack["title_id"]))
        if not (package_dir / "manifest.json").is_file():
            errors.append(f"{manifest_rel}: package directory must include manifest.json")
        for file in package_dir.rglob("*") if package_dir.exists() else []:
            if file.is_file() and file.suffix.lower() in FORBIDDEN_ASSET_SUFFIXES:
                errors.append(f"{manifest_rel}: prohibited game asset {file.relative_to(repo_root)}")

        preimages = pack.get("preimages", [])
        anchors = pack.get("anchors", [])
        if not isinstance(preimages, list) or not isinstance(anchors, list):
            errors.append(f"{manifest_rel}: preimages and anchors must be lists")
            continue
        patch_addresses: set[int] = set()
        for preimage in preimages:
            try:
                address = _number(preimage["address"])
                _number(preimage["word"])
                patch_addresses.add(address)
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"{manifest_rel}: invalid preimage: {exc}")
        for anchor in anchors:
            try:
                _number(anchor["address"])
                _number(anchor["word"])
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"{manifest_rel}: invalid anchor: {exc}")
        patch_file = pack.get("patch")
        if preimages and not isinstance(patch_file, str):
            errors.append(f"{manifest_rel}: PPC preimages require patch file")
        if isinstance(patch_file, str):
            asm_file = package_dir / patch_file
            if not asm_file.is_file():
                errors.append(f"{manifest_rel}: missing patch file {asm_file}")
            else:
                checksum = pack.get("source", {}).get("module_checksum")
                if not isinstance(checksum, str):
                    errors.append(f"{manifest_rel}: PPC pack needs source.module_checksum")
                else:
                    errors.extend(_asm_has_required_syntax(asm_file, checksum, patch_addresses))
    return ValidationResult(packs, errors)


def _decompress_rpx_text(rpx: Path) -> tuple[int, bytes]:
    data = rpx.read_bytes()
    if data[:4] != b"\x7fELF":
        raise ValueError("reference is not an ELF/RPX")
    elf_header = struct.unpack_from(">16sHHIIIIIHHHHHH", data, 0)
    section_offset = elf_header[6]
    section_count = elf_header[12]
    for index in range(section_count):
        offset = section_offset + index * 40
        (_, _, flags, virtual_address, file_offset, file_size, _, _, _, _) = struct.unpack_from(
            ">IIIIIIIIII", data, offset
        )
        if virtual_address != 0x02000020:
            continue
        raw = data[file_offset:file_offset + file_size]
        if flags & 0x08000000:
            expected_size = struct.unpack_from(">I", raw, 0)[0]
            result = zlib.decompress(raw[4:])
            if len(result) != expected_size:
                raise ValueError("compressed text section has an unexpected size")
            return virtual_address, result
        return virtual_address, raw
    raise ValueError("RPX text section at 0x02000020 not found")


def verify_reference(reference_rpx: Path, packs: Iterable[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not reference_rpx.is_file():
        return [f"reference RPX not found: {reference_rpx}"]
    pack_list = list(packs)
    expected_hashes = {
        pack.get("source", {}).get("rpx_sha256")
        for pack in pack_list
        if pack.get("preimages")
    }
    expected_hashes.discard(None)
    actual_hash = sha256_file(reference_rpx)
    if len(expected_hashes) != 1:
        errors.append("PPC packs must share exactly one RPX SHA-256")
    elif actual_hash != next(iter(expected_hashes)):
        errors.append(f"RPX SHA-256 mismatch: expected {next(iter(expected_hashes))}, got {actual_hash}")
    try:
        text_base, text = _decompress_rpx_text(reference_rpx)
    except (OSError, ValueError, struct.error, zlib.error) as exc:
        return errors + [f"cannot read RPX text section: {exc}"]
    for pack in pack_list:
        for assertion in [*pack.get("preimages", []), *pack.get("anchors", [])]:
            address = _number(assertion["address"])
            expected = _number(assertion["word"])
            relative = address - text_base
            if relative < 0 or relative + 4 > len(text):
                errors.append(f"{pack['id']}: preimage address 0x{address:08x} outside text")
                continue
            actual = struct.unpack_from(">I", text, relative)[0]
            if actual != expected:
                errors.append(
                    f"{pack['id']}: preimage mismatch at 0x{address:08x}: "
                    f"expected 0x{expected:08x}, got 0x{actual:08x}"
                )
    return errors


def select_packs(packs: Iterable[dict[str, Any]], selected_ids: list[str], include_experimental: bool) -> list[dict[str, Any]]:
    catalog = {pack["id"]: pack for pack in packs}
    if selected_ids:
        unknown = sorted(set(selected_ids) - catalog.keys())
        if unknown:
            raise ValueError(f"unknown pack id(s): {', '.join(unknown)}")
        chosen = [catalog[pack_id] for pack_id in selected_ids]
    else:
        chosen = [pack for pack in packs if pack["default_install"]]
        if include_experimental:
            chosen.extend(
                pack
                for pack in packs
                if pack["status"] == "Runtime Experimental"
                and pack["availability"] == "available"
                and pack.get("auto_experimental_install", False)
            )
    experimental = [pack["id"] for pack in chosen if pack["status"] == "Runtime Experimental"]
    if experimental and not include_experimental:
        raise ValueError("experimental pack requires --include-experimental: " + ", ".join(experimental))
    blocked = [pack["id"] for pack in chosen if pack["availability"] != "available"]
    if blocked:
        raise ValueError("pack is runtime-blocked pending further evidence: " + ", ".join(blocked))
    return chosen


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def install(repo_root: Path, cemu_root: Path, packs: list[dict[str, Any]], reference_rpx: Path | None, verify: bool = True) -> Path:
    if verify and any(pack.get("preimages") for pack in packs):
        if reference_rpx is None:
            raise ValueError("PPC pack installation requires --reference-rpx for preimage verification")
        errors = verify_reference(reference_rpx, packs)
        if errors:
            raise ValueError("reference verification failed:\n" + "\n".join(errors))
    target = install_root(cemu_root)
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mh-cemu-enhancements-", dir=parent) as temp:
        staged = Path(temp) / "mh-cemu-enhancements"
        staged.mkdir()
        receipt_packs = []
        for pack in packs:
            source = repo_root / pack["pack_dir"]
            destination = staged / pack["install_folder"]
            shutil.copytree(source, destination)
            receipt_packs.append({"id": pack["id"], "tree_sha256": _tree_hash(source)})
        receipt = {
            "schema_version": 1,
            "project": "mh-cemu-enhancements",
            "packs": receipt_packs,
            "reference_rpx_sha256": sha256_file(reference_rpx) if reference_rpx else None,
        }
        (staged / ".install-receipt.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if target.exists():
            if not (target / ".install-receipt.json").is_file():
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                backup = target.with_name(target.name + ".backup-" + stamp)
                sequence = 1
                while backup.exists():
                    backup = target.with_name(target.name + f".backup-{stamp}-{sequence}")
                    sequence += 1
                target.rename(backup)
            else:
                shutil.rmtree(target)
        shutil.move(str(staged), str(target))
    legacy_target = _legacy_isolated_install_root(cemu_root)
    if (
        legacy_target is not None
        and legacy_target != target
        and (legacy_target / ".install-receipt.json").is_file()
    ):
        shutil.rmtree(legacy_target)
    return target


def uninstall(cemu_root: Path) -> None:
    target = install_root(cemu_root)
    if target.exists():
        shutil.rmtree(target)
    legacy_target = _legacy_isolated_install_root(cemu_root)
    if legacy_target is not None and (legacy_target / ".install-receipt.json").is_file():
        shutil.rmtree(legacy_target)


def _distribution_files(repo_root: Path) -> list[Path]:
    ignored_top = {".git", ".idea", "dist", "__pycache__", ".ruff_cache", ".pytest_cache"}
    result = []
    for path in repo_root.rglob("*"):
        relative = path.relative_to(repo_root)
        if not path.is_file() or relative.parts[0] in ignored_top or "__pycache__" in relative.parts:
            continue
        if path.name == ".DS_Store" or path.suffix.lower() in FORBIDDEN_ASSET_SUFFIXES:
            continue
        result.append(path)
    return sorted(result, key=lambda item: item.relative_to(repo_root).as_posix())


def package_repository(repo_root: Path, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in _distribution_files(repo_root):
            relative = source.relative_to(repo_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output


def zip_member_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    verify = commands.add_parser("verify-reference")
    verify.add_argument("--reference-rpx", type=Path, required=True)
    install_parser = commands.add_parser("install")
    install_parser.add_argument("--cemu-root", type=Path, required=True)
    install_parser.add_argument("--reference-rpx", type=Path)
    install_parser.add_argument("--pack", action="append", default=[])
    install_parser.add_argument("--include-experimental", action="store_true")
    remove = commands.add_parser("uninstall")
    remove.add_argument("--cemu-root", type=Path, required=True)
    inspect_parser = commands.add_parser("inspect", help="read-only installation and saved-enable-state report")
    inspect_parser.add_argument("--cemu-root", type=Path, required=True)
    launch = commands.add_parser("isolated-launch-command", help="print, but do not execute, the isolated Cemu launch command")
    launch.add_argument("--cemu-root", type=Path, required=True)
    launch.add_argument("--cemu-app", type=Path, required=True)
    package = commands.add_parser("package")
    package.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = validate_repository(args.repo_root)
    if result.errors:
        print("VALIDATION FAILED", file=sys.stderr)
        print("\n".join(result.errors), file=sys.stderr)
        return 1
    if args.command == "validate":
        print(f"OK: {len(result.packs)} pack manifests")
    elif args.command == "verify-reference":
        errors = verify_reference(args.reference_rpx, result.packs)
        if errors:
            print("REFERENCE VERIFICATION FAILED", file=sys.stderr)
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(f"OK: {args.reference_rpx}")
    elif args.command == "install":
        try:
            packs = select_packs(result.packs, args.pack, args.include_experimental)
            target = install(args.repo_root, args.cemu_root, packs, args.reference_rpx)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"installed {len(packs)} pack(s) at {target}")
    elif args.command == "uninstall":
        uninstall(args.cemu_root)
        print(f"removed {install_root(args.cemu_root)}")
    elif args.command == "inspect":
        report = inspect_cemu_root(args.cemu_root, result.packs)
        print(json.dumps(report, default=str, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.command == "isolated-launch-command":
        try:
            print(isolated_launch_command(args.cemu_app, args.cemu_root))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif args.command == "package":
        output = package_repository(args.repo_root, args.output)
        print(f"created {output} {sha256_file(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
