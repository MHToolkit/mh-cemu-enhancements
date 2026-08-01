# MH3G 全任务蓝色补给箱完整道具箱对照设计 / All-Quest Blue Supply-Box Full Item-Box Control Design

## 目标 / Goal

新增第四个、可独立启停的 Graphic Pack，将《Monster Hunter 3G HD Ver.》日版 v96 **所有任务中现有的蓝色补给箱**重定向到完整道具箱菜单，用作红色交纳箱失败原因的运行时对照。

Add a fourth independently selectable Graphic Pack that redirects the existing blue supply box in **every MH3G HD JP v96 quest** to the full item-box menu. This is a runtime control for isolating why the red delivery-box experiment still fails.

覆盖范围由全任务共享的蓝箱交互分支决定，不维护任务 ID 或地图白名单。存在蓝色补给箱的任务都会受影响；本来没有蓝箱的任务不会凭空新增箱子。

Coverage is defined by the shared quest blue-box interaction path, with no quest-ID or map whitelist. Every quest that already has a blue supply box is affected; quests without one do not gain a new box.

## 已证实的控制流 / Proven control flow

- `0x028C5E78` 以 `r4 = 0` 进入共享函数 `0x028C26F0`：蓝色补给箱路径。
- `0x028C5E80` 以 `r4 = 1` 进入同一函数：红色交纳箱路径。
- `0x028C2768` 根据保存的选择器分流；蓝箱从 `0x028C2770` 开始，红箱从 `0x028C27B4` 开始。
- 完整道具箱统一初始化器为 `0x021F0A8C`；当前玩家对象作为 `r4`，`r5 = 0` 选择完整菜单模式。
- 村庄/港口现有完整道具箱包已经通过实机验证，证明该初始化器和参数组合在已支持的据点场景可用。

- `0x028C5E78` enters shared function `0x028C26F0` with `r4 = 0`: the blue supply-box path.
- `0x028C5E80` enters the same function with `r4 = 1`: the red delivery-box path.
- `0x028C2768` dispatches on the saved selector; blue starts at `0x028C2770`, while red starts at `0x028C27B4`.
- `0x021F0A8C` is the shared full item-box initializer; the current player is passed in `r4`, and `r5 = 0` selects full-menu mode.
- The existing village/port full item-box pack has gameplay verification, proving this initializer and argument combination in the already-supported hub context.

## 独立包设计 / Independent pack design

新包 ID：

`mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control`

Cemu 叶子选项：

`MH Cemu Enhancements/MH3G HD JP v96/Quest Blue Supply Box -> Full Item Box (Control)`

该包默认不启用并标记为 `Runtime Experimental`。它与现有三个包并列安装，不替换或删除以下功能：

1. `30 FPS` 锁帧包；
2. 村庄/港口完整道具箱包；
3. 任务红色交纳箱实验包。

The pack is disabled by default and remains `Runtime Experimental`. It is installed alongside, rather than replacing or deleting, the existing 30 FPS lock, village/port full item-box, and quest red delivery-box experiment packs.

蓝箱对照包与红箱包写入不同地址，可以同时存在。为获得清晰结果，首次实测只需要启用蓝箱对照包；现有包的启用状态在安装时必须保留，不得因更新包目录而被重置。

The blue control and red experiment write different addresses and may coexist. For an unambiguous first test, only the new blue control needs to be enabled; installation must preserve the enable state of every existing pack.

## 补丁设计 / Patch design

只在蓝箱专属块 `0x028C2770..0x028C2784` 原地覆盖六条指令：

```asm
0x028c2770 = lis r3, 0x1031
0x028c2774 = lwz r3, 0x44a0(r3)
0x028c2778 = mr r4, r30
0x028c277c = li r5, 0
0x028c2780 = bl 0x021f0a8c
0x028c2784 = b 0x028c27f8
```

该重写读取完整道具箱所需的全局 UI 管理器，传入当前玩家 `r30`，以模式 `0` 调用 `0x021F0A8C`，再跳到共享收尾路径 `0x028C27F8`。不使用 code cave。

The six-instruction in-place rewrite loads the global UI manager, passes current player `r30`, calls `0x021F0A8C` in mode `0`, and rejoins common cleanup at `0x028C27F8`. No code cave is used.

实现时必须以精确 RPX 为基准验证原始指令 preimage：

| 地址 / Address | 预期原值 / Expected preimage |
| --- | --- |
| `0x028C2770` | `0x819E0E30` |
| `0x028C2774` | `0x3D601008` |
| `0x028C2778` | `0x39000001` |
| `0x028C277C` | `0xC00BE204` |
| `0x028C2780` | `0x38800000` |
| `0x028C2784` | `0x990C0BAE` |

## 明确不改的内容 / Explicit non-goals

- 不改蓝箱资源引用 `0x021B0E90`、红箱资源引用 `0x021B0F14`、蓝箱提示/交互编号 `14` 或红箱编号 `15`。
- 不改蓝箱外观、对象注册、任务数据、任务 ID、地图数据或红箱补丁。
- 不改 WUA、RPX 文件、Cemu 程序、MLC、存档或游戏镜像。
- 不让没有蓝箱的任务生成蓝箱。
- 不将其标记为多人游戏推荐功能。

- Do not change blue resource reference `0x021B0E90`, red resource reference `0x021B0F14`, blue prompt/action ID `14`, or red ID `15`.
- Do not change the blue model, object registration, quest data, quest IDs, map data, or red-box patch.
- Do not modify the WUA, RPX file, Cemu application, MLC, save data, or game image.
- Do not create a blue box in quests that lack one.
- Do not mark the experiment as recommended for multiplayer.

## 静态验证与打包 / Static verification and packaging

- 测试先行：先让 catalog/manifest/patch 测试因缺少第四包而失败，再添加生产文件。
- 锁定目标 RPX SHA-256、`moduleMatches = 0x348600A0` 与 Cemu RPX hash `8cb62099`。
- 校验六个 preimage、蓝/红分派锚点、完整道具箱初始化器锚点，以及返回共享收尾路径的分支目标。
- 使用真实 Cemu PPCAssembler 对六条补丁逐地址汇编，不能只依赖人工计算分支位移。
- 运行仓库完整测试、lint、`git diff --check`，并生成可复现的新版本 ZIP；预计版本为 `0.1.13`。
- 新 ZIP 必须同时包含四个包，尤其保留可安装但默认不启用的 `30 FPS` 包。

- Follow TDD: first make catalog/manifest/patch tests fail because the fourth pack is absent, then add production files.
- Pin the target RPX SHA-256, `moduleMatches = 0x348600A0`, and Cemu RPX hash `8cb62099`.
- Validate all six preimages, blue/red dispatch anchors, the full item-box initializer anchor, and the branch back to common cleanup.
- Assemble each patched address with the real Cemu PPCAssembler rather than relying only on manually calculated branch displacement.
- Run the full repository tests, lint, and `git diff --check`, then build a reproducible new ZIP, expected as version `0.1.13`.
- The ZIP must contain all four packs, including the installable but default-disabled `30 FPS` pack.

## 安装与运行时验收 / Installation and runtime acceptance

只有确认 Cemu 已退出后，才把第四包安装到当前标准 Cemu profile。安装前后保存文件清单、SHA-256 和 `settings.xml` 中的启用状态证据；不启动 Cemu，也不触碰游戏或存档文件。

Install the fourth pack into the current standard Cemu profile only after Cemu has exited. Capture file inventories, SHA-256 values, and enable-state evidence from `settings.xml` before and after installation. Do not launch Cemu or touch game/save files.

运行时验收由用户完成：

1. 在至少两个不同任务/地图中接近蓝色补给箱，仍显示原版可用的蓝箱交互提示；
2. 按 `A` 后打开完整道具箱菜单；
3. 菜单中可见并可进入装备变更、装备组合/套装变更、护石相关选项；
4. 关闭菜单后可再次打开；
5. 红箱表现单独记录，但不作为蓝箱对照通过与否的判定条件。

Runtime acceptance is user-performed:

1. In at least two different quests/maps, the blue supply box retains its normal usable interaction prompt.
2. Pressing `A` opens the full item-box menu.
3. Equipment change, equipment set/combination change, and talisman-related entries are visible and enterable.
4. The menu can be closed and opened again.
5. Red-box behavior is recorded separately and does not determine whether the blue control passes.

全任务覆盖由共享蓝箱路径的静态控制流保证；代表性多地图实测用于验证运行时行为，不要求逐一穷举游戏中的每个任务。

All-quest coverage is established statically by the shared blue-box path. Representative multi-map gameplay verifies runtime behavior without requiring an exhaustive playthrough of every quest.

## 结果判定 / Decision after the control

- **蓝箱成功、红箱失败：** 完整初始化器在任务 UI 上下文可用，问题集中在红箱对象/动作类型、注册或状态映射；下一步研究红箱的完整类型替换。
- **蓝箱也失败：** 据点完整道具箱初始化器不能在任务场景中直接构造可用菜单；停止继续猜测箱子编号，转向任务 UI 构造流程、上下文依赖和状态对象调查。

- **Blue succeeds while red fails:** the full initializer works in quest UI context, isolating the issue to red object/action type, registration, or state mapping; investigate a complete red type replacement next.
- **Blue also fails:** the hub full item-box initializer cannot directly construct a usable menu in quest context; stop guessing box IDs and investigate quest UI construction, context dependencies, and state objects.
