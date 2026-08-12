#!/usr/bin/env python3
"""Choose the next automatic release version for the current Git commit."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import Iterable


Version = tuple[int, int, int]
TAG_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
DIST_PATTERN = re.compile(r"^mh-cemu-enhancements-(\d+)\.(\d+)\.(\d+)\.zip$")


def _parse_versions(values: Iterable[str], pattern: re.Pattern[str]) -> set[Version]:
    versions: set[Version] = set()
    for value in values:
        match = pattern.fullmatch(value)
        if match:
            versions.add(tuple(int(part) for part in match.groups()))
    return versions


def choose_release_version(
    tags: Iterable[str],
    dist_names: Iterable[str],
    head_tags: Iterable[str],
) -> Version:
    """Return an idempotent version for HEAD, otherwise the next patch version."""
    parsed_tags = _parse_versions(tags, TAG_PATTERN)
    parsed_head_tags = _parse_versions(head_tags, TAG_PATTERN)
    if parsed_head_tags:
        return max(parsed_head_tags)

    parsed_dist = _parse_versions(dist_names, DIST_PATTERN)
    known_versions = parsed_tags | parsed_dist
    if not known_versions:
        return (0, 1, 0)

    latest = max(known_versions)
    # A manually prepared dist becomes the release version the first time it is seen.
    if latest in parsed_dist and latest not in parsed_tags:
        return latest
    return (latest[0], latest[1], latest[2] + 1)


def _git_lines(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    dist_names = [path.name for path in (repo_root / "dist").glob("*.zip")]
    version = choose_release_version(
        _git_lines(repo_root, "tag", "--list", "v[0-9]*"),
        dist_names,
        _git_lines(repo_root, "tag", "--points-at", "HEAD", "v[0-9]*"),
    )
    print(".".join(str(part) for part in version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
