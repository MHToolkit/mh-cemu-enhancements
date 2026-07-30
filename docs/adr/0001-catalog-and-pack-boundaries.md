# ADR 0001: Generic catalog with independently selectable Cemu packs

**Status:** Accepted

## Context

The repository begins with Monster Hunter 3G HD Ver. (Wii U, Japan, update v96), but it must continue to store independently versioned Cemu cheats, Graphic Packs, PPC patches, and installation tooling for other Monster Hunter and Wii U titles.

## Decision

Use these boundaries:

```text
catalog/                              catalog index and pack manifests
schemas/                              stable manifest and catalog schemas
packs/<platform>/<title>/<region-version>/<feature>/
scripts/                              generic catalog validation, installation, removal, packaging
tests/                                tests for the generic scripts and catalog contract
docs/research/                        reproducible reverse-engineering evidence
```

Each `<feature>` directory is one Cemu-selectable Graphic Pack. A shared Cemu UI switch is deliberately not used: 30 FPS, lobby storage, and quest storage must be independently enabled and independently removable.

Every pack manifest records platform, canonical title, title ID, region, update, reference RPX SHA-256, Cemu module checksum, source/provenance, license, status, default enablement, original preimage, and replacement action. The catalog accepts future titles without a root-schema rename.

## Consequences

- No game binary, save, key, MLC content, or dumped asset is committed or distributed.
- Cemu `moduleMatches` is the runtime module gate; the installer/verifier adds a reference-RPX and original-byte gate before installation.
- Status values are constrained to `Static Verified`, `Runtime Experimental`, and `Runtime Verified`.
- The first Cemu v96 packs remain region/version-scoped rather than being presented as compatible with other MH3G builds.
