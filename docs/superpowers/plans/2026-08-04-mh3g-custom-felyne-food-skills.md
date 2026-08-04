# MH3G Custom Felyne Food Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add a default-off Cemu Graphic Pack with three complete bilingual Felyne-food skill selectors and apply them through the native JP-v96 meal finalizer.

**Architecture:** Replace only the ten-instruction writeback tail at `0x021D8740..0x021D8764`. The inline block writes all three selected halfword IDs to the menu and runtime structures, then falls through to untouched game code. No code cave, game asset, save, or emulator binary is modified.

**Tech Stack:** Cemu Graphic Pack v7, Cemu PPC patch assembler variables, Python 3 `unittest`, JSON manifests, immutable JP-v96 RPX preimage verification.

---

### Task 1: Define the pack contract with failing tests

**Files:**
- Modify: `tests/test_catalog.py`

- [x] Add `mh3g-hd-jp-v96-custom-felyne-food-skills` to the exact available catalog set.
- [x] Assert `Runtime Experimental`, `available`, default-install false, and auto-experimental-install false.
- [x] Assert all ten exact preimages at `0x021D8740..0x021D8764` and surrounding function anchors.
- [x] Parse `rules.txt`; require three categories, each containing every integer value `0x00..0x41` exactly once and a bilingual name.
- [x] Require defaults `$skill1=0x06`, `$skill2=0x36`, `$skill3=0x00`.
- [x] Require exactly ten fixed-address patch assignments, menu offsets `0x0A/0x0C/0x0E`, runtime offsets `0xE3E/0xE40/0xE42`, and no `codecave`.
- [x] Add an explicit installer-selection test proving the experimental flag and exact pack ID are required.
- [x] Run the focused tests and observe failure because the catalog/pack does not yet exist.

### Task 2: Implement the bilingual Graphic Pack

**Files:**
- Create: `packs/wiiu/mh3g-hd/jp-v96/custom-felyne-food-skills/manifest.json`
- Create: `packs/wiiu/mh3g-hd/jp-v96/custom-felyne-food-skills/rules.txt`
- Create: `packs/wiiu/mh3g-hd/jp-v96/custom-felyne-food-skills/patch_custom_felyne_food_skills.asm`
- Modify: `catalog/packs.json`

- [x] Create the module-gated ten-instruction patch using `$skill1`, `$skill2`, and `$skill3`.
- [x] Create all 198 bilingual presets (66 values for each of three categories).
- [x] Record pinned target identity, preimages, anchors, source provenance, activation timing, and known invalid-combination risk in the manifest.
- [x] Append the manifest path to the catalog without changing unrelated pack entries.
- [x] Run focused tests and confirm green.

### Task 3: Update user-facing inventory and usage documentation

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/research/mh3g-hd-jp-v96.md`

- [x] Increase the available leaf count from 46 to 47 and add the new pack to status tables/lists.
- [x] Explain the three selectors, `00..41` domain, default `06/36/00`, re-eat requirement, preview limitation, and incompatible-combination risk bilingually.
- [x] Keep status as `Runtime Experimental / Gameplay Pending`; do not imply runtime success.

### Task 4: Verify and package

**Files:**
- Create: `dist/mh-cemu-enhancements-0.1.17.zip`
- Create: `dist/mh-cemu-enhancements-0.1.17.zip.sha256`

- [x] Run focused tests, then all tests.
- [x] Run `validate`, `verify-reference` against the pinned JP-v96 RPX, `ruff`, and `git diff --check`.
- [x] Build two archives and byte-compare them for deterministic output.
- [x] Place the verified archive and SHA-256 sidecar in `dist/` without deleting older or unrelated artifacts.

### Task 5: Install without launching Cemu

**Files:**
- Install under the resolved owned root: `.../cemu/data/graphicPacks/mh-cemu-enhancements`

- [x] Confirm no Cemu process is running.
- [x] Select Lobby Full Item Box, Lock 30 FPS, and Custom Felyne Food Skills explicitly; include experimental packs and provide the pinned RPX.
- [x] Verify the receipt contains exactly those three installed packs, leaving runtime enable/disable choices to Cemu configuration.
- [x] Compare installed new-pack files against the repository and confirm Cemu remains stopped.
- [x] Report static verification and installation separately from gameplay validation.
