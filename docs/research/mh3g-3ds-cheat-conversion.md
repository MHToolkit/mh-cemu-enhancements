# MH3G 3DS → Cemu 金手指转换矩阵 / Cheat Conversion Matrix

## 范围与证据 / Scope and Evidence

本矩阵完整盘点活动 3DS Gateway/Citra 金手指文件的 73 条条目。源文件只用于本机只读分析，未复制到仓库或安装目录。目标固定为 MH3G HD JP v96（`0005000010104D00`）。

This matrix inventories all 73 entries in the active 3DS Gateway/Citra cheat file. The source file is read-only analysis input and is not copied into this repository or the installation directory. The target is pinned to MH3G HD JP v96 (`0005000010104D00`).

- 3DS source list SHA-256 / 金手指源文件：`6add19f3237edcefd05d3bd9cdbf96662e82452c32b51ca7883135b19279711a`
- Matching 3DS `.code` SHA-256 / 匹配的 3DS 程序：`3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77`，基址 `0x00100000`，大小 12255232 字节
- Wii U RPX SHA-256 / 目标 RPX：`7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`
- Target PPC text / 目标 PPC text：基址 `0x02000020`，大小 18439328 字节
- 修正反向 LZSS 末字节边界后，本机 3DS `.code` 与既有 JP 对照哈希完全一致，因此 43 条 `arm-static-patch` 具备可复现的源侧前像。
- Cemu 2.6 原生解析 `[Control] vsyncFrequency`，因此 44 FPS 使用原生 Graphic Pack 控制项；PPC 静态转换则使用固定地址 `.asm` 并钉住每个原指令。

## 已实现 / Implemented

- **43 个独立静态 ARM 转换包**：共 168 条 JP-v96 PPC 固定地址写入；每包双语、默认关闭、`Runtime Experimental / Gameplay Pending`，必须显式选择安装。
- **#71 锁定 44 FPS / Lock 44 FPS**：`mh3g-hd-jp-v96-fps-lock-44`，使用 `vsyncFrequency = 44`；#73 为重复项，不另建包。
- 43 项完整映射、PPC 写入数和包 ID 见 [mh3g-static-arm-mapping.md](mh3g-static-arm-mapping.md)。
- 静态门禁已覆盖：3DS 源 hash、目标 RPX hash、PPC 原指令/锚点、manifest/schema、真实 Cemu PPC 汇编器语法；**这些不等于游戏内已验证**。

## 已知重点风险 / Focused Risks

- **#6 与 #72** 共用会心计算路径，已设置互斥组；不要同时启用。#6 虽标作“会心不显示”，但其 ARM 指令实际同样把两条会心加成路径改为 100，因此当前 PPC 转换与 #72 等效。
- **#56 自动标记并标记当前区域小怪**为 `partial-semantic`：PPC 侧覆盖已找到的效果检查和小怪标记路径，但 3DS 的一个 UI 虚调用没有一对一静态 PPC 落点。
- **#65 战斗体验改善器**只有模糊源名称，且补丁作用于通用技能比较路径，影响面最大，优先单独测试。
- #7 会冻结 HP 扣减路径；#13、#59 等倍率/动作时间类转换可能因不同动作分支产生局部差异。
- 多包叠加可能覆盖同一通用技能查询路径；首轮应逐项启用并记录武器、任务、动作和异常。

## 尚未实现项的边界 / Remaining Boundaries

- `requires-ppc-mapping`：动态指针、热键、注入例程或运行时内存布局不能从 3DS ARM 地址直接照搬到 Wii U PPC，仍需独立定位。
- `not-supported`：Cemu Graphic Pack 没有对应的逐标题原生控制项（本例为关闭 dithering）。
- `not-applicable`：Wii U/Cemu 没有 3DS 裸眼 3D，对应功能天然无需实现。
- 60 FPS 条目按用户要求排除；重复条目不重复建包。

## 全量条目 / Complete Entry List

| # | 3DS 名称 | English | 结论 / Disposition | Cemu 状态 |
|---:|---|---|---|---|
| 1 | 速度变更L键3倍 | L held: game speed ×3 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 2 | 速度变更L键2倍 | L held: game speed ×2 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 3 | 速度变更R键1倍 | R held: restore game speed ×1 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 4 | 斩味常紫 | Sharpness always purple | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 5 | 锋利度不减MH3G_v1.0 | Sharpness never decreases | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-05-sharpness-never-decreases (Runtime Experimental) |
| 6 | 会心不显示 | Critical-hit display hidden | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-06-critical-display-hidden (Runtime Experimental) |
| 7 | HP无限 | Infinite HP | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-07-infinite-hp (Runtime Experimental) |
| 8 | 道具袋不减 | Item-pouch quantities do not decrease | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 9 | 背包第一格×99 | Pouch slot 1 ×99 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 10 | 任务中背包第一格 | Quest pouch slot 1 ×99 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 11 | 里属性觉醒 | Awakening: unlock hidden element | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-11-awakening (Runtime Experimental) |
| 12 | 携带道具上限提升至 99 | Carry-item cap raised to 99 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 13 | 水下速度 2倍 | Underwater movement speed ×2 | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-13-underwater-speed-x2 (Runtime Experimental) |
| 14 | 金刚体 | Super Armor / Rock Steady | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-14-rock-steady (Runtime Experimental) |
| 15 | 铁镐和虫网不会损坏 | Pickaxes and bug nets do not break | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-15-unbreakable-pickaxes-bug-nets (Runtime Experimental) |
| 16 | 体力上限150 | Maximum health 150 | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-16-max-health-150 (Runtime Experimental) |
| 17 | 偷盗无效 | Theft immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-17-theft-immunity (Runtime Experimental) |
| 18 | 泥雪无效 | Mud and snow immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-18-mud-snow-immunity (Runtime Experimental) |
| 19 | 攻击倍率 | Attack multiplier | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 20 | 防御倍率 | Defense multiplier | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 21 | 3G回避距离UP效果 | Evade Extender effect | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-21-evade-extender (Runtime Experimental) |
| 22 | 背包第一格×99 | Pouch slot 1 ×99 | 重复，跳过 / Duplicate skipped | Duplicate of #9 |
| 23 | 道具箱第一格×99 | Item-box slot 1 ×99 | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 24 | 铳枪弹药自填 | Gunlance ammunition auto-refill | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 25 | 子弹不减 | Bowgun ammunition does not decrease | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 26 | 细菌感染无效 | Bio status immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-26-bio-status-immunity (Runtime Experimental) |
| 27 | 属性异常无效 | Abnormal-status immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-27-status-immunity (Runtime Experimental) |
| 28 | 斩斧能量槽max | Switch Axe energy gauge maximum | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 29 | 任何地方都可以使用电阻弹 | Power Coating usable everywhere | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-29-power-coating-anywhere (Runtime Experimental) |
| 30 | MH3G_v1.0弩系自动装填 | Bowgun auto reload | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 31 | 按a回血 | Press A to heal | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 32 | 冷热饮效果 | Hot and cold drink effect | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 33 | 防御性能+2 | Guard +2 | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-33-guard-plus-2 (Runtime Experimental) |
| 34 | 防御强化 | Guard Up | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-34-guard-up (Runtime Experimental) |
| 35 | 燃鳞 | Burning Scale (literal source label; exact effect unverified) | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-35-flaming-aura (Runtime Experimental) |
| 36 | 速食者+2 | Speed Eating +2 | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-36-speed-eating-plus-2 (Runtime Experimental) |
| 37 | 耐力无限 | Infinite stamina | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-37-infinite-stamina (Runtime Experimental) |
| 38 | 蓄力缩短 | Focus / shorter charge time | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-38-focus (Runtime Experimental) |
| 39 | 调和100%成功 | 100% combine success | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-39-combination-success-100 (Runtime Experimental) |
| 40 | 最大调和数 | Maximum combine quantity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-40-maximum-combination-yield (Runtime Experimental) |
| 41 | 高级耳栓 | High Grade Earplugs | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-41-high-grade-earplugs (Runtime Experimental) |
| 42 | 泥雪无效 | Mud and snow immunity | 重复，跳过 / Duplicate skipped | Duplicate of #18 |
| 43 | 水下速度2倍 | Underwater movement speed ×2 | 重复，跳过 / Duplicate skipped | Duplicate of #13 |
| 44 | 风压(大)无效 | Wind Pressure (Large) immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-44-windproof-high (Runtime Experimental) |
| 45 | 眩晕和气绝无效 | Stun and faint immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-45-stun-immunity (Runtime Experimental) |
| 46 | MH3G毒 麻痹 睡眠无效 | Poison, paralysis, and sleep immunity | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-46-poison-paralysis-sleep-immunity (Runtime Experimental) |
| 47 | 耐震 | Tremor resistance | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-47-tremor-resistance (Runtime Experimental) |
| 48 | 3G回避性能+2效果 | Evade Window +2 | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-48-evasion-plus-2 (Runtime Experimental) |
| 49 | 弩系武器后坐力最小(不显示) | Bowgun recoil minimum (hidden) | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-49-minimum-bowgun-recoil (Runtime Experimental) |
| 50 | 弩系武器无摇晃(不显示) | Bowgun deviation none (hidden) | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-50-bowgun-steadiness (Runtime Experimental) |
| 51 | 近战攻击不弹刀 | Melee Mind’s Eye | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-51-minds-eye (Runtime Experimental) |
| 52 | 弓箭自填 | Bow auto reload | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-52-bow-auto-reload (Runtime Experimental) |
| 53 | 砥石使用高速化 | Speed Sharpening | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-53-speed-sharpening (Runtime Experimental) |
| 54 | 地图 | Map effect | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-54-map-always-visible (Runtime Experimental) |
| 55 | 观察眼效果 | Psychic / observation-eye effect | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-55-capture-guru (Runtime Experimental) |
| 56 | 自动标记且标记当前区域小怪 | Auto-marker plus current-area small-monster marking | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-56-auto-marker-small-monsters (Runtime Experimental) |
| 57 | L+←破坏所有设置物/R+←恢复正常 | L+Left destroys placed objects; R+Left restores them | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 58 | 可以设置多个炸弹、陷阱和肉 | Allow multiple bombs, traps, and meat | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 59 | 4g3g通用剥取采集动作加快且获取加快X | Faster carve/gather actions and acquisition | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-59-faster-carve-gather (Runtime Experimental) |
| 60 | 高速收集效果 | Fast gathering effect | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-60-fast-gathering (Runtime Experimental) |
| 61 | 高速设置 | Fast placement effect | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-61-fast-placement (Runtime Experimental) |
| 62 | 氧气无限 | Infinite oxygen | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 63 | 气候温度适应X | Climate and temperature adaptation | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-63-climate-temperature-adaptation (Runtime Experimental) |
| 64 | 金刚身发动 | Rock Steady activated | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-64-rock-steady-activated (Runtime Experimental) |
| 65 | 战斗体验改善器 | Combat experience enhancer (literal source label; exact effect unverified) | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-65-combat-experience-enhancer (Runtime Experimental) |
| 66 | 当前区域怪物一击必杀 大怪可直接捕获 | One-hit KO for current-area monsters; large monsters immediately capturable | 需独立 PPC 映射 / Requires PPC mapping | Requires independent Wii U PPC research |
| 67 | 60 FPS v1.0 | 60 FPS v1.0 | 按要求排除 / User-excluded | N/A |
| 68 | No Dithering v1.0 | No Dithering v1.0 | 当前不支持 / Not supported | No safe Cemu Graphic Pack control |
| 69 | Render Settings, Disable 3D v1.0 | Render Settings: Disable 3D v1.0 | 无需实现 / Not applicable | Inherent on Wii U / Cemu |
| 70 | FPS Rate 60 v1.0 | FPS Rate 60 v1.0 | 按要求排除 / User-excluded | N/A |
| 71 | 帧数 44帧 | Lock 44 FPS | 已实现 / Implemented | Pack: mh3g-hd-jp-v96-fps-lock-44 |
| 72 | 会心率100% | 100% critical-hit rate | 已实现（实验） / Implemented (experimental) | Pack: mh3g-hd-jp-v96-static-72-affinity-100 (Runtime Experimental) |
| 73 | 44贞 | Lock 44 FPS | 重复，跳过 / Duplicate skipped | Duplicate of #71 |

## 实测建议 / Manual Test Guidance

1. 保持 30 FPS 关闭，只启用 **Lock 44 FPS**，先验证任务、过场、菜单、加载、水下场景的速度与音画同步。
2. 43 个静态包首轮逐项测试，不要一次全开；每项记录是否生效、武器/任务条件、崩溃/卡死/副作用。
3. #6 与 #72 二选一；#56、#65 作为高风险/部分映射项最后单独测。
4. 本轮不安装任何任务内红/蓝箱实验包；它们仍为 `runtime-blocked`。

1. Keep 30 FPS disabled and test **Lock 44 FPS** alone across quests, cutscenes, menus, loading, underwater movement, and A/V synchronization.
2. Test the 43 static packs one at a time first; record effect, weapon/quest conditions, crashes, hangs, and side effects.
3. Choose only one of #6 and #72; test partial/high-risk #56 and #65 separately and last.
4. No quest red/blue-box experiment is installed in this iteration; those remain `runtime-blocked`.
