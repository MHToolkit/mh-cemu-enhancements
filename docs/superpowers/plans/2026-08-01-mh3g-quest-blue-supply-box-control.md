# MH3G 全任务蓝色补给箱对照包 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增、验证、打包并安装一个覆盖所有现有任务蓝色补给箱的独立完整道具箱对照包，同时保留当前三个包及其启用状态。

**Architecture:** 在共享任务箱交互函数的蓝箱专属块 `0x028C2770..0x028C2784` 内原地重写六条 PPC 指令，调用已验证的完整道具箱初始化器 `0x021F0A8C` 后回到共同收尾路径。包通过独立 manifest/rules/ASM 接入通用 catalog，默认关闭并保持 `Runtime Experimental`；安装器只更新自身拥有的 Graphic Pack 目录，不改游戏、Cemu 二进制、MLC 或存档。

**Tech Stack:** Python 3 `unittest`, JSON manifest/schema, Cemu Graphic Pack v7 rules/PPC ASM, Cemu `PPCAssembler`, deterministic ZIP tooling, Git.

---

## 文件结构 / File structure

- `tests/test_catalog.py`：先定义第四包身份、全任务共享蓝箱控制流、preimage/anchor、安装与压缩包合同。
- `catalog/packs.json`：注册第四个独立 manifest。
- `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/manifest.json`：记录包身份、兼容性、六个 preimage、控制流 anchors 与不可变 RPX 身份。
- `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/rules.txt`：提供独立 Cemu UI 叶子和目标 Title ID。
- `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/patch_quest_blue_supply_full_item_box.asm`：只改蓝箱专属确认块。
- `README.md`、`README.zh-CN.md`：增加第四包、安装命令、对照结论与 `0.1.13` 打包命令。
- `docs/architecture.md`：把蓝箱对照加入目录、运行时边界和联机限制。
- `docs/research/mh3g-hd-jp-v96.md`：记录蓝箱共享分派、六指令候选及对照结果判定。
- `docs/verification.md`：记录新测试、PPCAssembler、包哈希和实际标准 profile 安装证据。
- `dist/mh-cemu-enhancements-0.1.13.zip` 与 `.sha256`：包含全部四包的可复现分发产物。

### Task 1: 用失败测试锁定第四包合同 / Lock the fourth-pack contract with a failing test

**Files:**
- Modify: `tests/test_catalog.py`

- [ ] **Step 1: 更新 catalog 身份集合和独立 UI 路径期望**

在 `test_catalog_and_manifests_validate` 的期望集合中加入：

```python
"mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control",
```

在 `test_rules_paths_expose_each_pack_as_an_independent_cemu_leaf` 的 `expected_paths` 中加入：

```python
"quest-blue-supply-box-full-item-box-control": (
    "MH Cemu Enhancements/MH3G HD JP v96/"
    "Quest Blue Supply Box -> Full Item Box (Control)"
),
```

- [ ] **Step 2: 添加蓝箱专属控制流合同测试**

```python
def test_quest_blue_supply_box_control_is_global_and_isolated(self):
    result = self.tool.validate_repository(REPO)
    blue = next(
        pack
        for pack in result.packs
        if pack["id"] == "mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control"
    )

    self.assertEqual("Runtime Experimental", blue["status"])
    self.assertFalse(blue["default_install"])
    self.assertEqual("available", blue["availability"])
    self.assertEqual(
        {
            0x028C2770: 0x819E0E30,
            0x028C2774: 0x3D601008,
            0x028C2778: 0x39000001,
            0x028C277C: 0xC00BE204,
            0x028C2780: 0x38800000,
            0x028C2784: 0x990C0BAE,
        },
        {
            self.tool._number(item["address"]): self.tool._number(item["word"])
            for item in blue["preimages"]
        },
    )
    self.assertEqual(
        {
            0x021F0AD0: 0x9BFC6E12,
            0x021F0AF0: 0x2C1F0001,
            0x021F0AF4: 0x38000006,
            0x021F0AFC: 0x38000003,
            0x028C2768: 0x2C1F0000,
            0x028C276C: 0x40820048,
            0x028C27B4: 0x7FC3F378,
            0x028C27F8: 0x3D201008,
            0x028C5E78: 0x38800000,
            0x028C5E7C: 0x4BFFC874,
            0x028C5E80: 0x38800001,
            0x028C5E84: 0x4BFFC86C,
        },
        {
            self.tool._number(item["address"]): self.tool._number(item["word"])
            for item in blue["anchors"]
        },
    )
    patch = (REPO / blue["pack_dir"] / blue["patch"]).read_text()
    self.assertIn("0x028c2770 = lis r3, 0x1031", patch)
    self.assertIn("0x028c2774 = lwz r3, 0x44a0(r3)", patch)
    self.assertIn("0x028c2778 = mr r4, r30", patch)
    self.assertIn("0x028c277c = li r5, 0", patch)
    self.assertIn("0x028c2780 = bl 0x021f0a8c", patch)
    self.assertIn("0x028c2784 = b 0x028c27f8", patch)
    self.assertNotIn("0x021b0e90", patch.lower())
    self.assertNotIn("0x021b0f14", patch.lower())
    self.assertNotIn("0x028c27c4", patch.lower())
    self.assertNotIn("quest id", patch.lower())
    self.assertNotIn("codecave", patch.lower())
```

- [ ] **Step 3: 运行目标测试并确认是“第四包不存在”导致失败**

Run:

```bash
rtk python3 -m unittest tests.test_catalog.CatalogTests.test_catalog_and_manifests_validate tests.test_catalog.CatalogTests.test_rules_paths_expose_each_pack_as_an_independent_cemu_leaf tests.test_catalog.CatalogTests.test_quest_blue_supply_box_control_is_global_and_isolated -v
```

Expected: `FAIL`/`ERROR` because catalog contains only three pack IDs and the new blue manifest cannot be selected; no syntax/import failure.

- [ ] **Step 4: 提交失败测试**

```bash
rtk git add tests/test_catalog.py
rtk git commit -m "test: define all-quest blue box control"
```

### Task 2: 添加最小第四包实现 / Add the minimal fourth-pack implementation

**Files:**
- Modify: `catalog/packs.json`
- Create: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/manifest.json`
- Create: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/rules.txt`
- Create: `packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/patch_quest_blue_supply_full_item_box.asm`
- Test: `tests/test_catalog.py`

- [ ] **Step 1: 在 catalog 注册第四个 manifest**

在 `catalog/packs.json` 的 `packs` 数组末尾加入：

```json
{
  "manifest": "packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control/manifest.json"
}
```

- [ ] **Step 2: 创建独立 rules 和 ASM**

`rules.txt`：

```ini
[Definition]
titleIds = 0005000010104D00
name = MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)
path = MH Cemu Enhancements/MH3G HD JP v96/Quest Blue Supply Box -> Full Item Box (Control)
description = 全任务蓝色补给箱完整道具箱对照；不改红箱。 / All-quest blue supply-box full item-box control; red is untouched.
version = 7
```

`patch_quest_blue_supply_full_item_box.asm`：

```asm
[MH3G HD JP v96]
moduleMatches = 0x348600a0
0x028c2770 = lis r3, 0x1031
0x028c2774 = lwz r3, 0x44a0(r3)
0x028c2778 = mr r4, r30
0x028c277c = li r5, 0
0x028c2780 = bl 0x021f0a8c
0x028c2784 = b 0x028c27f8
```

- [ ] **Step 3: 创建 manifest**

Manifest 必须使用：

```json
{
  "id": "mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control",
  "platform": "wiiu",
  "title": "Monster Hunter 3G HD Ver.",
  "title_id": "0005000010104D00",
  "title_slug": "mh3g-hd",
  "region": "JP",
  "update": "v96",
  "status": "Runtime Experimental",
  "default_install": false,
  "availability": "available",
  "pack_dir": "packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control",
  "install_folder": "MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)",
  "rules": "rules.txt",
  "patch": "patch_quest_blue_supply_full_item_box.asm"
}
```

并补齐设计文档中六个 `preimages`、十二个 `anchors`、双语 `meaning`、`source` 身份、MIT metadata license 与“全任务共享蓝箱路径、红箱不变”的双语 summary。

- [ ] **Step 4: 运行目标测试并确认转绿**

```bash
rtk python3 -m unittest tests.test_catalog.CatalogTests.test_catalog_and_manifests_validate tests.test_catalog.CatalogTests.test_rules_paths_expose_each_pack_as_an_independent_cemu_leaf tests.test_catalog.CatalogTests.test_quest_blue_supply_box_control_is_global_and_isolated -v
```

Expected: `Ran 3 tests ... OK`.

- [ ] **Step 5: 用固定 RPX 验证 preimage 和 anchor**

```bash
rtk python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx "/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/.build/mh3g-offline-hunter-debug-20260725T132604Z/mh3g_cafe.rpx"
```

Expected: all four packs accepted; SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every word match.

- [ ] **Step 6: 提交最小实现**

```bash
rtk git add catalog/packs.json packs/wiiu/mh3g-hd/jp-v96/quest-blue-supply-box-full-item-box-control
rtk git commit -m "feat: add all-quest blue box control"
```

### Task 3: 同步双语文档和分发版本 / Synchronize bilingual docs and distribution version

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/research/mh3g-hd-jp-v96.md`
- Modify: `docs/verification.md`

- [ ] **Step 1: 更新 README 英文与中文清单**

两份 README 都必须记录：

```text
Quest blue supply box -> full item box (control) | Runtime Experimental | no | independent
```

并提供显式安装 ID：

```bash
--pack mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control --include-experimental
```

把打包命令更新为：

```bash
rtk python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-0.1.13.zip
```

说明它覆盖所有“本来存在蓝箱”的任务、默认关闭、只供单机对照；不把静态覆盖写成运行时通过。

- [ ] **Step 2: 更新架构、研究和验证账本**

`docs/architecture.md` 增加第四目录和以下边界：

```text
The blue quest control is Experimental and default-off; it replaces only the shared blue confirmation block while enabled.
```

`docs/research/mh3g-hd-jp-v96.md` 增加六个原始字与六条目标指令表，并写清：蓝成功定位红箱类型/注册；蓝失败则调查任务 UI 构造上下文。

`docs/verification.md` 暂时将运行时状态记录为 `Runtime Experimental / gameplay pending`，安装完成后再填入精确测试数、ZIP SHA 和 profile 文件哈希。

- [ ] **Step 3: 文档自检并提交**

```bash
rtk proxy rg -n 'all three|全部三个|currently no.*three|0\.1\.12' README.md README.zh-CN.md docs/architecture.md docs/research/mh3g-hd-jp-v96.md docs/verification.md
rtk git diff --check
rtk git add README.md README.zh-CN.md docs/architecture.md docs/research/mh3g-hd-jp-v96.md docs/verification.md
rtk git commit -m "docs: document blue box control experiment"
```

Expected: obsolete three-pack and `0.1.12` statements are either removed or explicitly historical; `git diff --check` is silent.

### Task 4: 真实汇编、完整验证与可复现打包 / Real assembly, full verification, and reproducible package

**Files:**
- Create: `dist/mh-cemu-enhancements-0.1.13.zip`
- Create: `dist/mh-cemu-enhancements-0.1.13.zip.sha256`
- Modify: `docs/verification.md`

- [ ] **Step 1: 用真实 Cemu PPCAssembler 验证六条指令**

将 `/tmp/mh3g_ppcassembler_smoke.cpp` 的 cases 替换为：

```cpp
const std::array<Case, 6> cases{{
    {0x028c2770, "lis r3, 0x1031", 0x3c601031},
    {0x028c2774, "lwz r3, 0x44a0(r3)", 0x806344a0},
    {0x028c2778, "mr r4, r30", 0x7fc4f378},
    {0x028c277c, "li r5, 0", 0x38a00000},
    {0x028c2780, "bl 0x021f0a8c", 0x4b92e30d},
    {0x028c2784, "b 0x028c27f8", 0x48000074},
}};
```

使用同一 Cemu 源码树重新编译并运行：

```bash
rtk proxy clang++ -std=c++20 -I"/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/externals/cemu/src/src" /tmp/mh3g_ppcassembler_smoke.cpp "/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/externals/cemu/src/src/Cemu/PPCAssembler/ppcAssembler.cpp" -o /tmp/mh3g_ppcassembler_smoke
rtk proxy /tmp/mh3g_ppcassembler_smoke
```

Expected: six lines with the expected words and exit 0.

- [ ] **Step 2: 运行完整静态门禁**

```bash
rtk python3 -m unittest discover -s tests -v
rtk python3 scripts/mh-cemu-enhancements.py validate
rtk python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx "/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/.build/mh3g-offline-hunter-debug-20260725T132604Z/mh3g_cafe.rpx"
rtk ruff check scripts tests
rtk git diff --check
```

Expected: 17 tests, four valid manifests, exact RPX match, Ruff clean, no whitespace errors.

- [ ] **Step 3: 构建两次并比较可复现 ZIP**

```bash
rtk python3 scripts/mh-cemu-enhancements.py package --output /tmp/mh-cemu-enhancements-0.1.13-a.zip
rtk python3 scripts/mh-cemu-enhancements.py package --output /tmp/mh-cemu-enhancements-0.1.13-b.zip
rtk proxy shasum -a 256 /tmp/mh-cemu-enhancements-0.1.13-a.zip /tmp/mh-cemu-enhancements-0.1.13-b.zip
rtk proxy cp /tmp/mh-cemu-enhancements-0.1.13-a.zip dist/mh-cemu-enhancements-0.1.13.zip
rtk proxy shasum -a 256 dist/mh-cemu-enhancements-0.1.13.zip > dist/mh-cemu-enhancements-0.1.13.zip.sha256
rtk proxy unzip -l dist/mh-cemu-enhancements-0.1.13.zip
```

Expected: both temporary hashes identical; archive contains all four manifests/rules and contains no RPX, WUA, save, MLC, `.idea`, `.DS_Store`, or cache.

- [ ] **Step 4: 更新最终静态证据并提交跟踪文件**

在 `docs/verification.md` 写入实际测试数、六个汇编字、最终 ZIP SHA-256。只暂存 Git 跟踪的源码/文档；如果 `dist/` 被忽略，则保留本地产物但不强制提交。

```bash
rtk git add docs/verification.md
rtk git commit -m "docs: record blue box static verification"
```

### Task 5: 安装全部四包并保留启用状态 / Install all four packs and preserve enable state

**Files:**
- Read/Write owned directory: `/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/`
- Read/backup only: `/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml`
- Modify: `docs/verification.md`

- [ ] **Step 1: 再次确认 Cemu 零进程并记录安装前状态**

```bash
rtk proxy pgrep -x Cemu_release
rtk python3 scripts/mh-cemu-enhancements.py inspect --cemu-root "/Users/vincentadamnemessis/Library/Application Support/Cemu"
rtk proxy shasum -a 256 "/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml"
```

Expected: `pgrep` returns no PID. If a PID appears, stop before any install or settings write.

- [ ] **Step 2: 安装全部四个显式包**

```bash
rtk python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root "/Users/vincentadamnemessis/Library/Application Support/Cemu" \
  --reference-rpx "/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/.build/mh3g-offline-hunter-debug-20260725T132604Z/mh3g_cafe.rpx" \
  --pack mh3g-hd-jp-v96-fps-lock-30 \
  --pack mh3g-hd-jp-v96-lobby-full-item-box \
  --pack mh3g-hd-jp-v96-quest-delivery-full-item-box-experimental \
  --pack mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control \
  --include-experimental
```

Expected: receipt and four pack folders exist. The installer does not edit `settings.xml`, so 30 FPS stays disabled and existing enabled states remain unchanged; the new blue control remains disabled until explicitly selected.

- [ ] **Step 3: 在用户要求的测试配置中仅新增启用蓝箱对照**

创建时间戳备份后，仅在 `settings.xml` Graphic Pack 列表中加入蓝箱叶子；不得改变现有三项的布尔状态。先用 XML parser 读取并确认确切节点结构，再做最小写入；写后解析 XML 并比较其余节点。

Expected enabled set:

```text
Lobby Full Item Box = enabled
Quest Red Delivery Box -> Full Item Box (Experimental) = enabled
Quest Blue Supply Box -> Full Item Box (Control) = enabled
Lock 30 FPS = disabled
```

- [ ] **Step 4: 检查文件、哈希、receipt 和启用状态**

```bash
rtk python3 scripts/mh-cemu-enhancements.py inspect --cemu-root "/Users/vincentadamnemessis/Library/Application Support/Cemu"
rtk proxy find "/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements" -type f -maxdepth 3 -print
rtk proxy shasum -a 256 "/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)/patch_quest_blue_supply_full_item_box.asm"
rtk proxy pgrep -x Cemu_release
```

Expected: four installed, exactly three box-related leaves enabled as above, FPS installed but disabled, repository and installed blue ASM hashes equal, and Cemu still has no PID.

- [ ] **Step 5: 记录安装证据并提交**

在 `docs/verification.md` 记录标准 profile 路径、四包安装清单、新蓝箱 ASM SHA、settings 备份路径、启用状态，以及未启动 Cemu/未改 WUA、RPX、MLC、save 的边界。

```bash
rtk git add docs/verification.md
rtk git commit -m "docs: record four-pack deployment"
```

## 最终验收 / Final acceptance

- 仓库测试和固定 RPX 静态验证只能支持 `Runtime Experimental`，不能宣称蓝箱实机成功。
- 用户在至少两个不同任务/地图测试：蓝箱正常提示、按 `A` 打开完整菜单、装备/套装/护石选项可用、关闭后可再次进入。
- 蓝箱成功且红箱失败时，下一阶段处理红箱对象/动作类型；蓝箱也失败时，下一阶段研究任务 UI 构造上下文。
