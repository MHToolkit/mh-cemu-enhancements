# MH3G 动态 PPC 运行时证据（2026-08-08）

## 2026-08-25 增量：#28 已闭环

#28 斩斧能量槽最大新增三组可复核证据：同生命周期五快照唯一严格字段、剑模式负 delta
writer、斧模式正 delta writer。字段为斩斧运行时对象大端 16 位 `+0x62C`，原生 writer
为 `0x0285DE70`；生成 Pack 的两处固定指令、真实 Cemu PPCAssembler 和本机隔离冷启动
玩法均通过。当前总计为：12 项 `partial-runtime-evidence`、8 项 `not-traced`、1 项
`gameplay-traced / ppc-mapped`，1 个动态 Runtime Verified Pack。

This ledger now includes #28's same-lifecycle field sequence, negative sword-drain
writer, positive axe-recharge writer, and explicit local gameplay acceptance.
Current totals are twelve partial-runtime entries, eight not-traced entries, one
gameplay-traced/PPC-mapped entry, and one Runtime Verified dynamic pack.

## 结论

这轮已经从“只有静态候选”推进到 **12/21 项存在局部运行时证据**，但仍然是研究态：

- 12 项：`partial-runtime-evidence`
- 9 项：`not-traced`
- 0 项：`gameplay-traced`
- 0 项：`ppc-mapped`
- 0 个动态 Graphic Pack 可安装

`partial-runtime-evidence` 只表示真实 Cemu/MH3G 进程中观察到了相关 hook、字段或输入位，
不表示源金手指的完整效果、安全状态桥、恢复路径和玩法副作用已经闭环。机器可读原始路径、
SHA-256、事件计数、观测值和每项限制见
[`mh3g-dynamic-runtime-evidence.json`](mh3g-dynamic-runtime-evidence.json)。

## 最新调试运行时

- Nemessix/Cemu 修复提交：`1dcbefc1564f5dfed55dbdbfb7903f3470f15579`
- Nemessix PR：[`MHToolkit/nemessix#19`](https://github.com/MHToolkit/nemessix/pull/19)
- 修复内容：GDB software breakpoint 命中后恢复原指令，在下一条安全指令处重新装回；
  客户端退出后仍可在同一 Cemu 进程重新连接。
- 原 artifact 可执行文件 SHA-256：
  `e4c9502e4f9d052ef43c09dd4dcb3ad88f90078593053789ce8304b9eb562356`
- 隔离重签名运行副本 SHA-256：
  `159c33cf5a3c3603840230c426e570444d69ae85175f6953ff653e49b97803d3`
- 隔离 Bundle ID：`info.cemu.Cemu.GDBPersistentProbe`
- 同一实测进程：PID `73948`
- CPU：recompiler；Graphic Packs：全部关闭；GDB：`127.0.0.1:1337`
- HOME、Cemu data root、MLC、存档、输入和 settings 全部使用 copy-only 隔离副本。
- Persistent breakpoint 证据索引 SHA-256：
  `28a63e16ce6d9c776169909dbc4427bf8e287dc108cc4db2d43cb99c32f38e77`

## 已完成的真实门禁

在同一个 MH3G JP v96 村庄进程中，`0x02BCB9CC` 的 persistent breakpoint 完成：

| 独立连接 | 操作 | 未匹配后再次装回 | r29 命中值 | 已证实掩码 |
| ---: | --- | ---: | --- | --- |
| 1 | A（键盘 U） | 833 次 | `0x80082000` | `0x2000` |
| 2 | L（键盘 Q） | 108 次 | `0x80080100` | `0x0100` |
| 3 | R（键盘 E） | 157 次 | `0x80080200` | `0x0200` |
| 4 | 左方向键（键盘 J） | 170 次 | `0x80080080` | `0x0080` |

每次完成后 tracer 都删除断点、恢复游戏并关闭连接；后三次均在不重启 Cemu 的情况下重新
attach。这同时验证了：

1. persistent breakpoint 不再只命中一次；
2. 断点恢复/重装至少连续通过 834 次；
3. 同一进程 detach/reconnect 可继续设置、命中和删除断点；
4. `cemu-gdb-probe.py` 的寄存器值使用逻辑 PPC 十六进制解释后，`r31` 等 guest 指针可读。

## 逐项推进

### #1/#2/#3 速度倍率

- `0x028924AC` 在村庄移动输入期间真实命中，`r7=0x2FF7D610`。
- `r7+0x608` 为 `0x3F800000`（float `1.0`），与静态倍率消费点一致。
- L/R 当前帧掩码分别真实确认成 `0x0100/0x0200`。
- **仍缺**：输入 hook 与玩家倍率 hook 之间生命周期安全的共享状态、L 松开恢复、
  L/R 优先级，以及 2x/3x 真实位移/动作对照。因此不能创建 pack。

### #9/#23 背包与道具箱第一格

- `*0x10315C50 = 0x2E622A80`。
- 主背包首记录为根 `+0xE0`，现场首条为道具 ID `2`、数量 `1`。
- 道具箱首记录为根 `+0x1C0`，现场首条为道具 ID `9`、数量 `99`。
- **仍缺**：受控 1→2→3 数量变化及原生 writer 命中，空槽、备用数组、存档同步和对象
  重建边界均未验证。

### #19/#20 攻击与防御倍率

- 同一玩家对象 `+0x6E8/+0x6EA` 现场值为 `305/633`。
- `+0x6EC/+0x6F0` 的显示浮点值为 `3.05/633.0`。
- **仍缺**：换装前后在派生 writer 上的受控 trace，以及原生 700 上限、最低值和防止
  重复累乘的实现证明。

### #31 按 A 回血

- A 当前帧归一化掩码真实确认成 `0x2000`。
- 同一玩家对象 `+0x640/+0x642` 现场为当前/最大 HP `100/100`。
- **仍缺**：受伤状态下 A 输入和 HP writer 的共同动作 trace，以及跨函数状态桥、按住/边沿
  触发和原生治疗副作用。

### #32 冷热饮效果

- `0x02893154` 和 `0x028932B4` 在同一帧路径中分别命中，同一 `r7` 玩家对象。
- 村庄无效果基线下 `+0x974/+0x978/+0x980/+0x984` 全为 `0.0`。
- **仍缺**：高温任务饮用冷饮、低温任务饮用热饮两组受控 trace；当前仍不能给两组字段
  标注热/冷身份。

### #57 L/R+左方向键切换设置物判定

- L、R、左方向键的当前帧掩码分别真实确认成 `0x0100/0x0200/0x0080`。
- **仍缺**：放置、重复放置、回收时 `0x0218A394` 的真实调用类别与 `+7` 阈值变化；
  跨 hook 可恢复状态和任务结算影响也未验证。

### #58 多个炸弹、陷阱和肉

- 玩家对象 `+0x572/+0x573/+0x574` 村庄快照为 `[0, 0, 1]`，地址可读且值域合理。
- **仍缺**：炸弹、陷阱、肉分别连续放置时三个 helper 的独立命中和物品身份对应关系；
  回收、销毁、任务结束的回落路径未验证。

### #62 氧气无限

- 玩家对象 `+0x65C/+0x65E` 村庄快照为当前/上限 `100/100`。
- **仍缺**：水下自然耗氧时 `0x02863F0C` 的真实负 `r4` delta；补氧、离水、初始化和 HUD
  更新必须保留，不能用无条件常量写入替代。

## 下一批受控动作

优先级保持 fail-closed：

1. #9：第一格数量 1→2→3，命中 `0x0219B830`；
2. #19/#20：只换一件装备，分别命中 `0x0286769C/0x02867D14`；
3. #62：进入水下并捕获一次自然负 delta；
4. #32：高温/低温各一次饮料前后 trace；
5. #57/#58：分别对真实放置、拒绝、回收动作取证；
6. 最后才设计共享输入状态桥并开始 PPCAssembler 实现。

任何后续 pack 仍必须同时满足：原指令前像、完整动作 trace、生命周期安全、Assembler 通过、
默认关闭和独立 gameplay 验收；本轮证据不改变该门槛。
