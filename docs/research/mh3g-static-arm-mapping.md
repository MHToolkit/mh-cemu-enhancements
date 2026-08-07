# MH3G 43 项静态 ARM → Cemu PPC 映射 / 43 Static ARM → Cemu PPC Mappings

> 目标：`0005000010104D00`，JP v96；43 个包均默认关闭，状态为 **Runtime Experimental / Gameplay Pending**。静态原指令验证不等于实机功能验证。

| # | 中文 / English | 映射类型 | PPC 写入数 | 包 ID |
|---:|---|---|---:|---|
| 5 | 锋利度不减 / Sharpness Never Decreases | `exact-static` | 1 | `mh3g-hd-jp-v96-static-05-sharpness-never-decreases` |
| 6 | 会心不显示 / Critical Display Hidden | `shared-affinity-path` | 4 | `mh3g-hd-jp-v96-static-06-critical-display-hidden` |
| 7 | HP 无限 / Infinite HP | `exact-static` | 2 | `mh3g-hd-jp-v96-static-07-infinite-hp` |
| 11 | 里属性觉醒 / Awakening | `global-semantic` | 3 | `mh3g-hd-jp-v96-static-11-awakening` |
| 13 | 水下速度 2 倍 / Underwater Speed ×2 | `global-semantic-with-exact-scalars` | 23 | `mh3g-hd-jp-v96-static-13-underwater-speed-x2` |
| 14 | 金刚体 / Rock Steady | `global-semantic` | 7 | `mh3g-hd-jp-v96-static-14-rock-steady` |
| 15 | 铁镐和虫网不会损坏 / Unbreakable Pickaxes and Bug Nets | `mixed-exact-and-global-semantic` | 4 | `mh3g-hd-jp-v96-static-15-unbreakable-pickaxes-bug-nets` |
| 16 | 体力上限 150 / Maximum Health 150 | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-16-max-health-150` |
| 17 | 偷盗无效 / Theft Immunity | `global-semantic` | 3 | `mh3g-hd-jp-v96-static-17-theft-immunity` |
| 18 | 泥雪无效 / Mud and Snow Immunity | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-18-mud-snow-immunity` |
| 21 | 回避距离 UP / Evade Extender | `global-semantic` | 9 | `mh3g-hd-jp-v96-static-21-evade-extender` |
| 26 | 细菌感染无效 / Bio Status Immunity | `global-semantic` | 4 | `mh3g-hd-jp-v96-static-26-bio-status-immunity` |
| 27 | 属性异常无效 / Abnormal-Status Immunity | `global-semantic` | 1 | `mh3g-hd-jp-v96-static-27-status-immunity` |
| 29 | 任何地方可用电阻弹 / Power Coating Usable Anywhere | `exact-static` | 1 | `mh3g-hd-jp-v96-static-29-power-coating-anywhere` |
| 33 | 防御性能 +2 / Guard +2 | `exact-callsite-family` | 3 | `mh3g-hd-jp-v96-static-33-guard-plus-2` |
| 34 | 防御强化 / Guard Up | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-34-guard-up` |
| 35 | 燃鳞 / Flaming Aura | `global-semantic` | 1 | `mh3g-hd-jp-v96-static-35-flaming-aura` |
| 36 | 速食者 +2 / Speed Eating +2 | `global-semantic` | 3 | `mh3g-hd-jp-v96-static-36-speed-eating-plus-2` |
| 37 | 耐力无限 / Infinite Stamina | `exact-static` | 2 | `mh3g-hd-jp-v96-static-37-infinite-stamina` |
| 38 | 蓄力缩短 / Focus | `global-semantic` | 5 | `mh3g-hd-jp-v96-static-38-focus` |
| 39 | 调和成功率 100% / Combination Success 100% | `exact-static` | 1 | `mh3g-hd-jp-v96-static-39-combination-success-100` |
| 40 | 最大调和数 / Maximum Combination Yield | `exact-static` | 1 | `mh3g-hd-jp-v96-static-40-maximum-combination-yield` |
| 41 | 高级耳栓 / High-Grade Earplugs | `global-semantic` | 12 | `mh3g-hd-jp-v96-static-41-high-grade-earplugs` |
| 44 | 风压（大）无效 / Windproof (High) | `global-semantic` | 3 | `mh3g-hd-jp-v96-static-44-windproof-high` |
| 45 | 眩晕和气绝无效 / Stun Immunity | `global-semantic` | 1 | `mh3g-hd-jp-v96-static-45-stun-immunity` |
| 46 | 毒、麻痹、睡眠无效 / Poison, Paralysis, and Sleep Immunity | `global-semantic` | 5 | `mh3g-hd-jp-v96-static-46-poison-paralysis-sleep-immunity` |
| 47 | 耐震 / Tremor Resistance | `global-semantic` | 1 | `mh3g-hd-jp-v96-static-47-tremor-resistance` |
| 48 | 回避性能 +2 / Evasion +2 | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-48-evasion-plus-2` |
| 49 | 弩后坐力最小 / Minimum Bowgun Recoil | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-49-minimum-bowgun-recoil` |
| 50 | 弩无摇晃 / Bowgun Steadiness | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-50-bowgun-steadiness` |
| 51 | 近战不弹刀 / Mind's Eye | `global-semantic` | 2 | `mh3g-hd-jp-v96-static-51-minds-eye` |
| 52 | 弓箭自填 / Bow Auto-Reload | `global-semantic` | 5 | `mh3g-hd-jp-v96-static-52-bow-auto-reload` |
| 53 | 砥石高速化 / Speed Sharpening | `global-semantic` | 1 | `mh3g-hd-jp-v96-static-53-speed-sharpening` |
| 54 | 地图常显 / Map Always Visible | `global-semantic` | 1 | `mh3g-hd-jp-v96-static-54-map-always-visible` |
| 55 | 观察眼 / Capture Guru | `global-semantic` | 4 | `mh3g-hd-jp-v96-static-55-capture-guru` |
| 56 | 自动标记并标记当前区小怪 / Auto-Marker plus Current-Area Small Monsters | `partial-semantic` | 8 | `mh3g-hd-jp-v96-static-56-auto-marker-small-monsters` |
| 59 | 剥取、采集动作与获取加快 / Faster Carving, Gathering, and Acquisition | `exact-static` | 2 | `mh3g-hd-jp-v96-static-59-faster-carve-gather` |
| 60 | 高速收集 / Fast Gathering | `global-semantic` | 18 | `mh3g-hd-jp-v96-static-60-fast-gathering` |
| 61 | 高速设置 / Fast Placement | `global-semantic` | 7 | `mh3g-hd-jp-v96-static-61-fast-placement` |
| 63 | 气候温度适应 / Climate and Temperature Adaptation | `global-semantic` | 13 | `mh3g-hd-jp-v96-static-63-climate-temperature-adaptation` |
| 64 | 金刚身发动 / Rock Steady Activated | `exact-static` | 1 | `mh3g-hd-jp-v96-static-64-rock-steady-activated` |
| 65 | 战斗体验改善器 / Combat Experience Enhancer | `exact-static` | 1 | `mh3g-hd-jp-v96-static-65-combat-experience-enhancer` |
| 72 | 会心率 100% / Affinity 100% | `shared-affinity-path` | 4 | `mh3g-hd-jp-v96-static-72-affinity-100` |

## 验证边界 / Verification boundary

- 已验证：源 3DS `.code` 哈希、目标 RPX 哈希、每个 PPC 原指令、效果 ID/常量/函数结构映射、Cemu 补丁汇编语法。
- 待验证：真实任务/武器/状态下的行为、组合启用副作用，以及源编译器与 PPC 编译器路径复制差异。
- Verified: source 3DS `.code` hash, target RPX hash, every PPC preimage, effect-ID/constant/function-structure mapping, and Cemu patch assembly syntax.
- Pending: gameplay behavior across quests/weapons/statuses, combined-pack side effects, and source/PPC compiler path-duplication differences.
