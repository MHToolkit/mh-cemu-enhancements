# MH3G Quest Full Item-Box Dispatch Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the all-quest blue-box control with a guarded per-frame path to the existing full-item-box dispatcher and install it for user gameplay validation.

**Architecture:** Keep the existing blue confirmation rewrite at `0x028C2770..0x028C2784`. Replace only the early scene-gate exit at `0x02219DF0` with `nop`, preserving the following manager/busy guards and the dispatcher's own state switch. Keep red runtime-blocked.

**Tech Stack:** Python 3 `unittest`, JSON manifests, Cemu Graphic Pack v7 PPC ASM, immutable JP v96 RPX verification, Cemu `PPCAssembler`, deterministic ZIP packaging.

---

### Task 1: Lock the dispatch-bridge contract with a failing test

**Files:**
- Modify: `tests/test_catalog.py`

- [ ] Change the blue pack expectation to `availability = available` and require preimage `0x02219DF0 = 0x4182007C`.
- [ ] Require the patch line `0x02219df0 = nop` and anchors for `0x0214E084`, `0x02219DE8`, `0x02219E50`, `0x0215165C`, and `0x021F0D08`.
- [ ] Change default experimental selection to FPS plus blue; keep explicit red selection fail-closed.
- [ ] Run the targeted tests and confirm failure because the manifest and ASM do not yet expose the bridge.

### Task 2: Implement the minimal bridge

**Files:**
- Modify: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/manifest.json`
- Modify: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/rules.txt`
- Modify: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/patch_quest_blue_supply_full_item_box.asm`

- [ ] Add `0x02219df0 = nop` to the existing patch group.
- [ ] Record the exact original word and bilingual dispatch-chain anchors in the manifest.
- [ ] Restore only the blue candidate to `available`; retain `Runtime Experimental` and `default_install = false`.
- [ ] Run the targeted tests and confirm they pass.
- [ ] Run `verify-reference` against the pinned RPX.
- [ ] Assemble the new instruction at the exact address with Cemu's real `PPCAssembler` harness.

### Task 3: Synchronize evidence and package 0.1.15

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/research/mh3g-hd-jp-v96.md`
- Modify: `docs/verification.md`
- Create: `dist/mh-cemu-enhancements-0.1.15.zip`
- Create: `dist/mh-cemu-enhancements-0.1.15.zip.sha256`

- [ ] Document the bridge as gameplay-pending, single-player-only, and distinct from the blocked first blue revision.
- [ ] Run all tests, validation, reference verification, Ruff, and `git diff --check`.
- [ ] Build two archives, confirm byte identity, install the final archive and adjacent SHA-256.

### Task 4: Install the controlled runtime candidate

**Files:**
- Modify: `/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml`
- Install: `/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/`

- [ ] Confirm no Cemu process exists and back up `settings.xml`.
- [ ] Install FPS, Lobby, and blue with the immutable RPX gate; do not install red.
- [ ] Add exactly one enabled blue `GraphicPack/Entry`; preserve Lobby enabled and FPS disabled.
- [ ] Parse XML and run read-only `inspect` to prove Lobby/blue enabled, FPS disabled, and red absent.
- [ ] Do not launch Cemu and do not claim runtime success.

### Task 5: Final verification and commit

- [ ] Re-run the complete test, validation, reference, lint, XML, archive, installed-tree, and zero-Cemu-process checks.
- [ ] Stage only the documented source, tests, and `0.1.15` distribution files.
- [ ] Commit with `feat: add quest item-box dispatch bridge`.
