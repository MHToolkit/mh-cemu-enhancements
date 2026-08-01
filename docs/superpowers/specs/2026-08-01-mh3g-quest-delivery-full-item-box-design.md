# MH3G 任务红色交纳箱全功能道具箱设计 / Quest Delivery Box Full Item Box Design

## 目标 / Goal

仅将《Monster Hunter 3G HD Ver.》日版 v96 任务内的红色交纳箱重定向到完整的家用道具箱菜单。蓝色补给箱必须保持原版行为与资源。

Redirect only the red quest delivery box in MH3G HD JP v96 to the full home item-box menu. The blue supply box must retain its original behavior and resources.

## 已证实的控制流 / Proven control flow

- `0x028C5E78` 以 `r4 = 0` 进入 `0x028C26F0`：蓝色补给箱路径。
- `0x028C5E80` 以 `r4 = 1` 进入 `0x028C26F0`：红色交纳箱路径。
- `0x028C2768` 对该标志作分支；只有红箱进入 `0x028C27B4`。
- 红箱原路径在 `0x028C27CC` / `0x028C27D4` 调用交纳清单构建与交纳菜单逻辑。
- 完整道具箱统一初始化器为 `0x021F0A8C`，且 `r5 = 0` 选择完整菜单模式。

- `0x028C5E78` enters `0x028C26F0` with `r4 = 0`: blue supply-box path.
- `0x028C5E80` enters it with `r4 = 1`: red delivery-box path.
- `0x028C2768` branches on that flag; only the red box reaches `0x028C27B4`.
- The original red path calls delivery-list and delivery-menu logic at `0x028C27CC` / `0x028C27D4`.
- `0x021F0A8C` is the shared item-box initializer; `r5 = 0` selects full-menu mode.

## 补丁设计 / Patch design

在红箱专属块 `0x028C27C4..0x028C27D8` 内原地写入六条指令：

1. 读取完整道具箱初始化器需要的全局 UI 管理器；
2. 将当前玩家对象 `r30` 作为第二参数；
3. 将模式设为 `0`；
4. 调用 `0x021F0A8C`；
5. 跳过原红箱的交纳状态标志写入，回到共同收尾路径 `0x028C27F8`。

The six-instruction in-place rewrite loads the UI manager, passes the current player (`r30`), selects mode `0`, calls `0x021F0A8C`, and skips delivery-only flag writes before rejoining the common cleanup path at `0x028C27F8`.

不使用 code cave，不改 `0x021B0E90`（蓝箱资源），也不改 `0x021B0F14`（红箱资源）。补丁只改变红箱确认交互后的运行时分派。

No code cave is used. Neither the blue resource word at `0x021B0E90` nor the red resource word at `0x021B0F14` is changed; only the red box's confirmation-time dispatch is redirected.

## 验证边界 / Verification boundary

- 静态验证：精确 RPX SHA、`moduleMatches`、六个 preimage、周边蓝/红分派锚点、PPCAssembler、仓库测试和可复现打包。
- 运行时状态：安装后仍标记 `Runtime Experimental`，直到用户在任务中实测红箱、蓝箱以及退出/返回流程。

- Static verification: exact RPX SHA, `moduleMatches`, six preimages, nearby blue/red dispatch anchors, PPCAssembler, repository tests, and reproducible packaging.
- Runtime status remains `Runtime Experimental` after installation until gameplay confirms the red box, blue box, and exit/re-entry flows.
