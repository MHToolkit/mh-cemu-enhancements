# MH3G HD JP v96 Initial Packs Implementation Plan

> Executed in the primary session only. Steps use checkbox (`- [x]`) syntax so the checked state is evidence of the implemented static deliverable, not a claim of in-game verification.

**Goal:** Build a generic Cemu enhancement catalog and three independently selectable MH3G HD JP v96 feature packs with fail-closed static verification.

**Architecture:** Generic JSON schemas and Python standard-library tooling own catalog validation, pack installation/removal, reference-byte verification, and archive creation. Each feature is a self-contained Cemu Graphic Pack underneath the platform/title/region-version hierarchy, while the catalog manifest carries compatibility and verification state.

**Tech Stack:** Cemu `rules.txt`/`patch_*.asm`, Python 3 standard library, JSON Schema Draft 2020-12 metadata, `unittest`, `zip`, Git.

---

### Task 1: Establish the generic catalog contract

**Files:**
- Create: `schemas/pack-manifest.schema.json`
- Test: `tests/test_catalog.py`

- [x] Write tests that reject unknown status, a title/path mismatch, a mismatched PPC checksum, and a default-enabled experimental pack.
- [x] Run the test suite red before the installer/validator existed.
- [x] Implement standard-library schema-aware validation and catalog manifests for the three JP v96 features.
- [x] Re-run the tests and verify all catalog contract cases pass.

### Task 2: Implement pack and PPC-preimage validators

**Files:**
- Create: `scripts/mh-cemu-enhancements.py`
- Create: `packs/wiiu/mh3g-hd/jp-v96/*/rules.txt`
- Create: `packs/wiiu/mh3g-hd/jp-v96/*/patch_*.asm`

- [x] Add grammar, `moduleMatches`, manifest, and reference-RPX SHA/preimage checks.
- [x] Implement `validate` and `verify-reference`; it decompresses the RPX text section at `0x02000020` and compares every declared original word and target anchor.
- [x] Exercise Cemu's built `PPCAssembler` in an external static harness: it accepted the lobby branch and both `addic` quest instructions without launching Cemu.
- [x] Verify the pinned local RPX and fail closed on identity/checksum/preimage mismatches.

### Task 3: Finish the exact box-dispatch mapping

**Files:**
- Modify: `docs/research/mh3g-hd-jp-v96.md`
- Modify: box-pack manifests and `patch_*.asm`
- Test: `tests/test_verify.py`

- [x] Identify the menu-resource dispatches for full-home, lobby-restricted, supply, and delivery UI handlers; do not target chest models or save data.
- [x] Record the exact code address, original big-endian word, replacement PPC instruction/branch, checksum, and rationale in the ledger.
- [x] Add original-word and destination-anchor assertions to each PPC manifest and verify them against the local RPX.
- [x] Mark the lobby pack `Static Verified` after source/target words passed; retain the quest pack as `Runtime Experimental` and default-off.

### Task 4: Implement idempotent distribution lifecycle

**Files:**
- Modify: `scripts/mh-cemu-enhancements.py`
- Create: `README.md`
- Create: `README.zh-CN.md`

- [x] Write install/uninstall tests for repeated installation, default exclusion of Experimental content, receipt creation, and exact owned-directory removal.
- [x] Implement `install`, `uninstall`, and `package` using staging, a receipt, collision backup, and default-off behavior for Experimental packs.
- [x] Re-run the install path in a temporary root and twice in the isolated Cemu root.

### Task 5: Complete local evidence and delivery

**Files:**
- Create: `dist/mh-cemu-enhancements-<version>.zip`
- Modify: `docs/research/mh3g-hd-jp-v96.md`

- [x] Run syntax, schema, manifest, original-byte, install/uninstall, archive-content, and `git diff --check` gates.
- [x] Install only the non-Experimental packs to the supplied isolated Cemu `graphicPacks` root after static gates; do not launch Cemu or mutate MLC/save data.
- [x] Build the deterministic archive and record its SHA-256. The commit identifier is recorded after the final Git gate.
- [ ] Perform in-game validation. This is intentionally outstanding: no Cemu process was launched, so no pack is promoted to `Runtime Verified`.
