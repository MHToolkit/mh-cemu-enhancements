# MH3G HD JP v96 任务红蓝箱完整仓库条件调度设计

**日期 / Date:** 2026-08-02  
**状态 / Status:** Approved for implementation / 已批准实现

## 目标 / Goal

在所有任务中彻底放弃红色交纳箱与蓝色补给箱的原生功能，使两个箱子的交互都只请求完整家中仓库。大厅完整仓库与 30 FPS 继续作为独立包；30 FPS 默认关闭。

Replace the native red delivery-box and blue supply-box behavior in every quest so that both interactions request the full home item box only. The Lobby Full Item Box and 30 FPS packs remain independent; 30 FPS stays disabled by default.

## 已证实的问题 / Confirmed failure

上一版把 `0x02219DF0 = beq 0x02219E6C` 无条件改成 `nop`。用户实测显示该修改虽然在运行中成功热加载，但没有让红蓝箱打开完整仓库，并使任务看板对话框变成空白。原因是它在任务场景中对所有全局 UI 状态开放了大厅仓库调度器，而不是只处理由箱子初始化器提交的完整仓库状态 `6`。

The previous revision replaced `0x02219DF0 = beq 0x02219E6C` with an unconditional `nop`. Gameplay proved that the patch hot-loaded successfully, did not open the full item box from either quest box, and blanked the quest-board dialogue. It exposed the lobby item-box dispatcher to every global UI state in a quest instead of only state `6` submitted by the box initializer.

## 选定架构 / Selected architecture

新增一个统一的默认关闭实验包：

`MH3G HD JP v96 - Quest Red & Blue Boxes - Full Item Box (Experimental)`

旧红箱与旧蓝箱候选继续保留为 `runtime-blocked` 研究证据，不得与统一包同时安装。

The new combined pack is default-off and Runtime Experimental. The two older quest candidates remain runtime-blocked research evidence and cannot be installed alongside it.

### 1. 红蓝箱统一入口 / Unified red and blue entry

- 保留所有任务共用的蓝箱分派。
- 把红箱提示资格参数与提示编号改成补给箱语义，使红箱可以注册正常交互。
- 把红箱分派选择器从 `1` 改成 `0`，使红蓝箱都进入同一个蓝箱分支。
- 该共享分支调用 `0x021F0A8C(player, mode=0)`，请求完整仓库状态 `6`，随后回到原共享收尾路径。

- Keep the all-quest blue dispatch.
- Convert the red prompt eligibility and prompt resource to supply semantics so red can register a usable interaction.
- Change the red dispatch selector from `1` to `0` so both objects enter the same blue branch.
- That shared branch calls `0x021F0A8C(player, mode=0)` to request full-item-box state `6`, then rejoins the original common cleanup path.

### 2. 条件调度桥 / Conditional dispatcher bridge

不得再次无条件绕过 `0x02219DF0`，也不得使用 Cemu `.origin = codecave`；本机 Cemu 2.6 曾把该指令区分配到 guest `0x01800000` 并在 PPC recompiler 中崩溃。改为在原场景比较窗口 `0x02219DE0..0x02219DF4` 内联实现判定：

1. 保留 `0x02219DDC` 对场景管理器指针的原始读取。
2. 直接读取该对象 `+0x354` 的场景状态；等于据点值 `6` 时跳到原忙碌保护 `0x02219DF8`。
3. 场景状态不是 `6` 时读取全局 UI 管理器 `+0x5350`；仅当值为完整仓库状态 `6` 时落入同一忙碌保护。
4. 其他情况全部跳回原版跳过目标 `0x02219E6C`。
5. 保留 `+0x3D0/+0x20` 忙碌保护以及 `0x0215165C` 自身的状态分派。

The bridge must not bypass `0x02219DF0` unconditionally or use Cemu `.origin = codecave`; the local Cemu 2.6 build previously mapped such a cave to guest `0x01800000` and crashed in the PPC recompiler. The six-instruction window at `0x02219DE0..0x02219DF4` instead compares scene state directly at scene manager `+0x354`. Hub scene state `6` continues at the original busy guard. Outside the hub, only global UI state `+0x5350 == 6` may fall through; every other state returns to original skip target `0x02219E6C`. This preserves the original busy-state and dispatcher guards without a relocation.

## 安全边界 / Safety boundaries

- 仅支持 Title ID `0005000010104D00`、JP update v96、RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`、module checksum `0x348600a0`。
- 每个覆盖字都必须写入 manifest preimage；周边控制流写入 anchors，补丁中不得出现 `codecave`。
- 不修改 WUA、RPX 文件、Cemu 程序、MLC 或存档。
- 统一包仅限单人验证；没有游戏证据前不得标记 `Runtime Verified`。
- 安装器只暴露统一包；两个旧任务箱包保持 fail-closed。

## 验证 / Verification

### 自动与静态验证 / Automated and static

- 测试先失败，证明 catalog 尚无统一包且旧蓝箱仍可安装。
- manifest/schema/catalog、精确 patch 地址、preimage、anchor 与旧包阻断测试通过。
- 固定 RPX 的所有原始 PPC 字校验通过。
- Cemu 2.6 真实 `PPCAssembler` 接受全部内联分支指令，并确认补丁不生成 code cave。
- 完整测试、`validate`、`verify-reference`、`ruff`、`git diff --check` 与确定性打包通过。
- 安装后只启用大厅包和统一任务箱包；30 FPS 已安装但关闭；旧红/蓝包均不安装、不启用。

### 游戏验收 / Gameplay acceptance

1. 启用统一包后，从标题启动进入据点，任务看板文字与操作正常。
2. 进入至少两个不同任务，任务 HUD、暂停菜单和结算路径正常。
3. 红箱与蓝箱均显示可用提示，并打开完整仓库菜单。
4. 装备变更、装备组合、护石操作可进入；菜单可关闭并再次打开。
5. 红箱不再交纳、蓝箱不再发放补给品，符合已批准的功能取舍。

游戏验收必须由用户运行 Cemu 完成；仓库侧交付只能报告 `Gameplay Pending / 待实机验证`。
