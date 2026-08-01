# MH3G Quest Red and Blue Conditional Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one default-off experimental Graphic Pack that replaces both quest boxes with the full item-box request while keeping unrelated task UI states behind the original dispatch gate.

**Architecture:** Red prompt registration and dispatch are converted to the blue shared path; that path calls the existing full-item-box initializer in mode `0`. A six-instruction inline gate permits the original hub scene or global full-item-box state `6`, while all other quest UI states retain the original skip behavior. No Cemu code cave or game asset is used.

**Tech Stack:** Cemu Graphic Pack v7, Cemu PPC patch assembler, Python 3 `unittest`, JSON manifests, immutable JP v96 RPX preimage verification.

---

### Task 1: Specify the combined pack contract first

**Files:**
- Modify: `tests/test_catalog.py`

- [ ] **Step 1: Add the combined catalog and rules expectations**

Add ID `mh3g-hd-jp-v96-quest-red-blue-full-item-box-experimental` to `test_catalog_and_manifests_validate`, and add rules leaf:

```python
"quest-red-blue-full-item-box-experimental": (
    "MH Cemu Enhancements/MH3G HD JP v96/"
    "Quest Red & Blue Boxes -> Full Item Box (Experimental)"
),
```

- [ ] **Step 2: Make selection fail closed for both old candidates**

Replace the prior blue-available assertion so both legacy IDs raise `ValueError("runtime-blocked")`. Require `include_experimental=True` to select only FPS plus the new combined pack.

- [ ] **Step 3: Add the exact combined-pack contract test**

Require:

```python
self.assertEqual("Runtime Experimental", combined["status"])
self.assertFalse(combined["default_install"])
self.assertEqual("available", combined["availability"])
```

Require preimages at `0x02219DE0..0x02219DF4`, `0x028C2770..0x028C2784`, `0x028C5824`, `0x028C5838`, and `0x028C5E80`. Require bilingual manifest text and these patch lines:

```asm
0x02219de0 = lwz r0, 0x354(r12)
0x02219de4 = cmpwi r0, 6
0x02219de8 = beq 0x02219df8
0x02219dec = lbz r0, 0x5350(r31)
0x02219df0 = cmpwi r0, 6
0x02219df4 = bne 0x02219e6c
0x028c2770 = lis r3, 0x1031
0x028c2774 = lwz r3, 0x44a0(r3)
0x028c2778 = mr r4, r30
0x028c277c = li r5, 0
0x028c2780 = bl 0x021f0a8c
0x028c2784 = b 0x028c27f8
0x028c5824 = li r4, 0
0x028c5838 = li r5, 0xe
0x028c5e80 = li r4, 0
```

Also assert that the combined patch contains neither `nop` at `0x02219DF0` nor `codecave`.

- [ ] **Step 4: Run the focused tests and observe the expected failure**

Run:

```bash
rtk python3 -m unittest \
  tests.test_catalog.CatalogTests.test_catalog_and_manifests_validate \
  tests.test_catalog.CatalogTests.test_include_experimental_adds_fps_and_combined_quest_pack \
  tests.test_catalog.CatalogTests.test_old_quest_candidates_are_runtime_blocked \
  tests.test_catalog.CatalogTests.test_quest_red_blue_combined_pack_is_conditionally_gated -v
```

Expected: failures because the combined manifest/files do not exist and the old blue candidate is still available.

### Task 2: Implement the unified red/blue pack

**Files:**
- Create: `packs/wiiu/mh3g-hd/jp-v96/quest-red-blue-full-item-box-experimental/rules.txt`
- Create: `packs/wiiu/mh3g-hd/jp-v96/quest-red-blue-full-item-box-experimental/patch_quest_red_blue_full_item_box.asm`
- Create: `packs/wiiu/mh3g-hd/jp-v96/quest-red-blue-full-item-box-experimental/manifest.json`
- Modify: `catalog/packs.json`
- Modify: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/manifest.json`

- [ ] **Step 1: Create the independent Cemu leaf**

Use Graphic Pack version `7`, title ID `0005000010104D00`, default `false`, and path:

```text
MH Cemu Enhancements/MH3G HD JP v96/Quest Red & Blue Boxes -> Full Item Box (Experimental)
```

- [ ] **Step 2: Add the exact PPC replacement block**

Create the patch with module gate `0x348600a0` and exactly the fifteen instructions listed in Task 1. The six inline gate instructions replace the helper call window without touching `0x02219DF8..0x02219E08` busy guards.

- [ ] **Step 3: Add fail-closed manifest evidence**

Use RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`. Record the exact original words:

```text
02219DE0 38800006    02219DE4 386C0340
02219DE8 4BF9E021    02219DEC 2C030000
02219DF0 4182007C    02219DF4 819D0000
028C2770 819E0E30    028C2774 3D601008
028C2778 39000001    028C277C C00BE204
028C2780 38800000    028C2784 990C0BAE
028C5824 38800001    028C5838 38A0000F
028C5E80 38800001
```

Add anchors for helper purity at `0x021B7E14..0x021B7E28`, original pointer load `0x02219DD8..0x02219DDC`, original busy guards `0x02219DF8..0x02219E08`, dispatcher `0x0215165C`, state-6 route `0x02151698/0x0215174C`, handler `0x021F0D08`, and both box wrappers `0x028C5E78..0x028C5E84`.

- [ ] **Step 4: Block the superseded blue candidate and add the combined catalog entry**

Set old blue `availability` to `runtime-blocked` with bilingual runtime-failure reason. Append the combined manifest to `catalog/packs.json`.

- [ ] **Step 5: Run the focused tests and confirm green**

Run the four focused tests from Task 1. Expected: all pass.

- [ ] **Step 6: Commit implementation**

Stage only the test, catalog, old-blue manifest, and new combined directory. Commit:

```bash
rtk git commit -m "feat: conditionally bridge both quest boxes"
```

### Task 3: Verify PPC control flow with the pinned binary and real assembler

**Files:**
- Modify only if a verified encoding defect is found: `packs/wiiu/mh3g-hd/jp-v96/quest-red-blue-full-item-box-experimental/patch_quest_red_blue_full_item_box.asm`

- [ ] **Step 1: Validate every RPX preimage and anchor**

Run:

```bash
rtk python3 scripts/mh-cemu-enhancements.py verify-reference \
  --reference-rpx /Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/.build/mh3g-offline-hunter-debug-20260725T132604Z/mh3g_cafe.rpx
```

Expected: `OK`.

- [ ] **Step 2: Assemble every replacement with Cemu 2.6 PPCAssembler**

Use the existing local Cemu source/build harness and require these properties in its output:

```text
02219de8 -> beq 0x02219df8
02219df4 -> bne 0x02219e6c
028c2780 -> bl 0x021f0a8c
028c2784 -> b 0x028c27f8
```

The output must list only fixed module addresses; `Codecave:` must not appear.

- [ ] **Step 3: Run all static gates**

```bash
rtk python3 -m unittest discover -s tests -v
rtk python3 scripts/mh-cemu-enhancements.py validate
rtk ruff check scripts tests
rtk git diff --check
```

Expected: all tests and checks pass.

### Task 4: Document, package, install, and preserve runtime boundaries

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/research/mh3g-hd-jp-v96.md`
- Modify: `docs/verification.md`
- Create: `dist/mh-cemu-enhancements-0.1.16.zip`
- Create: `dist/mh-cemu-enhancements-0.1.16.zip.sha256`

- [ ] **Step 1: Record the failed unconditional bridge and new conditional candidate**

State bilingually that the prior blue hot-load failed and blanked the quest board. Describe the combined pack as `Gameplay Pending`, never `Runtime Verified`.

- [ ] **Step 2: Build twice and compare deterministic archives**

```bash
rtk python3 scripts/mh-cemu-enhancements.py package --output /tmp/mh-cemu-enhancements-0.1.16-a.zip
rtk python3 scripts/mh-cemu-enhancements.py package --output /tmp/mh-cemu-enhancements-0.1.16-b.zip
rtk proxy cmp -s /tmp/mh-cemu-enhancements-0.1.16-a.zip /tmp/mh-cemu-enhancements-0.1.16-b.zip
```

Copy the first archive to `dist/` and write its adjacent SHA-256 file.

- [ ] **Step 3: Install only the intended four-state profile after proving Cemu is stopped**

Install Lobby, 30 FPS, and the new combined pack into the standard Cemu root with the immutable RPX. Remove enabled entries for both old quest candidates. Save and enable only Lobby plus the new combined pack; leave 30 FPS installed but disabled.

- [ ] **Step 4: Inspect final state without launching Cemu**

Require:

```text
Lobby: installed=true enabled=true
30 FPS: installed=true enabled=false
old red: installed=false enabled=false
old blue: installed=false enabled=false
combined red+blue: installed=true enabled=true
```

Verify XML parsing, source/installed patch SHA equality, receipt hashes, package hash, and zero Cemu processes.

- [ ] **Step 5: Run final gates and commit evidence**

Run the complete test, validation, RPX, lint, diff, inspect, and deterministic-package checks again. Stage only the five documentation files and `0.1.16` artifacts. Commit:

```bash
rtk git commit -m "docs: record combined quest box deployment"
```

