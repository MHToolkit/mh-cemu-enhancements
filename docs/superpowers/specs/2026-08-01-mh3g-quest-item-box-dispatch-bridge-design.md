# MH3G 任务完整仓库调度桥设计 / Quest Full Item-Box Dispatch Bridge Design

## 目标 / Goal

在不修改 WUA、RPX 文件、Cemu 二进制、MLC 或存档的前提下，为现有任务蓝箱对照补齐据点完整仓库状态机的逐帧分派，验证任务场景能否复用游戏内已有的完整仓库生命周期。

Without modifying the WUA, RPX file, Cemu binary, MLC, or save data, extend the existing quest blue-box control with the missing per-frame dispatch for the game's existing hub full-item-box state machine.

## 已证实根因 / Proven root cause

- 蓝箱确认路径能够调用 `0x021F0A8C`，该初始化器写入完整仓库全局状态 `6`，但不会直接构造菜单。
- 全局 UI 管理器每帧经 `0x0214DFC8 -> 0x02219D10` 更新。
- `0x02219DE8` 调用 `0x021B7E08` 检查场景状态 `6`；任务场景失败后，原指令 `0x02219DF0 = beq 0x02219E6C` 绕过 `0x0215165C`。
- `0x0215165C` 是状态 `6` 到 `0x021F0D08` 的唯一直接分派路径。

- The blue confirmation path reaches `0x021F0A8C`, which stores global full-item-box state `6` but does not construct the menu immediately.
- The global UI manager updates every frame through `0x0214DFC8 -> 0x02219D10`.
- `0x02219DE8` checks hub scene state `6` through `0x021B7E08`; on failure, original instruction `0x02219DF0 = beq 0x02219E6C` skips `0x0215165C` in a quest.
- `0x0215165C` is the only direct dispatcher from state `6` to `0x021F0D08`.

## 最小候选 / Minimal candidate

保留现有蓝箱六指令触发器，并增加：

```asm
0x02219df0 = nop
```

这只移除场景检查失败后的提前退出。后续保护仍保留：管理器 `0x10314278` 必须有效，`+0x3D0/+0x20` 忙碌标志必须为零；状态调度器自身对 `manager+0x5350` 做范围分派，状态 `0` 直接返回。候选不修改红箱、任务数据、箱子资源或模型。

Keep the existing six-instruction blue trigger and add `0x02219DF0 = nop`. This removes only the early exit after the scene-state check. The following manager and busy-state guards remain intact, and dispatcher state `0` returns immediately. Red, quest data, resources, and models remain unchanged.

## 风险与验收 / Risk and acceptance

该指令会让全局菜单调度器在非据点场景也到达自身状态分派，因此只作为单人运行时实验。若蓝箱按键后出现完整菜单、可以关闭并再次打开，说明现有资源构造链足够；若无菜单或崩溃，则恢复配置并停止该候选，下一阶段必须显式构造 `uIDLobbyMyhBox` 生命周期。

This lets the global menu dispatcher reach its own state switch outside the hub and is therefore single-player experimental. Success requires the full menu to open, close, and reopen from the blue box. No menu or a crash fails the candidate and requires explicit `uIDLobbyMyhBox` lifecycle construction in a later design.

安装时只部署并启用蓝箱对照；大厅完整仓库保持启用，30 FPS 保持已安装但禁用，红箱继续不安装。任何静态或安装证据均不得标记为 `Runtime Verified`。

Installation deploys and enables only the blue control in addition to the enabled Lobby pack; 30 FPS remains installed/disabled and red remains absent. Static or installation evidence must not be reported as `Runtime Verified`.
