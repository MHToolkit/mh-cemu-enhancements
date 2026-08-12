# mh-cemu-enhancements

面向 Cemu 的本地优先增强资源目录：收纳可独立启用的 **Graphic Pack**、PPC patch、清单、校验和安装工具。根目录不绑定 MH3G；资源统一按 `packs/<platform>/<title>/<region-version>/<feature>/` 落盘，可持续增加其他 Monster Hunter/Wii U 游戏和地区版本。

仓库不收纳 RPX/RPL/WUA、存档、MLC、密钥、纹理 dump 或任何游戏资产；不会启动 Cemu、改 Cemu 二进制、改全局 Cemu 配置，也不会写入存档或 MLC。

## 首批：MH3G HD 日版 v96

| 开关 | 状态 | 可用性 | 默认安装 |
| --- | --- | --- | --- |
| 锁定 30 FPS | `Runtime Experimental` | `available` | 否 |
| 锁定 44 FPS（3DS 转换） | `Runtime Experimental` | `available` | 否 |
| 3 个 60 FPS 行为修复 | `Runtime Experimental` | `available` | 否（逐项显式选择） |
| 43 个 3DS 静态 ARM 转换包 | `Runtime Experimental` | `available` | 否（逐项显式选择） |
| 集会所/酒场完整家中箱子 | `Runtime Verified` | `available` | 否 |
| 猫饭技能自定义（三槽、`00..41`） | `Runtime Experimental` | `available` | 否（显式选择） |
| 3 个外部装备金手指（生产解锁 / 无需材料 / 无需钱） | `3 项 Runtime Verified` | `available` | 否（逐项显式选择） |
| 任务红色交纳箱 -> 完整家中箱子 | `Runtime Experimental` | `runtime-blocked` | 否 |
| 任务蓝色补给箱 -> 完整家中箱子（无条件调度桥对照） | `Runtime Experimental` | `runtime-blocked` | 否 |
| 任务红蓝箱 -> 完整家中箱子（条件调度桥） | `Runtime Experimental` | `runtime-blocked`（暂停） | 否 |

适用身份：Wii U Title ID `0005000010104D00`、JP update v96、RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`、Cemu patch module checksum `0x348600a0`。

`Static Verified` 仅表示 Graphic Pack 结构、Cemu 语法、模块门槛、RPX hash 与声明的 PPC 原始字校验已经通过；**不等于游戏内已验证**。大厅包已由用户实测完整菜单、换装、装备组合与护石功能；30 FPS 因实测不稳定降为实验状态。任务箱多次实测仍不可用，蓝箱调度桥还会使任务看板对话框空白，因此所有任务箱实验现已暂停并阻止安装。活动 3DS 金手指已完整盘点：44 FPS 使用 Cemu 原生控制项；另有 43 条静态 ARM 项已根据哈希一致的 3DS `.code` 与 JP-v96 PPC 语义/前像映射为独立实验包，共 179 条 PPC 写入。另行提供的 3DS 猫饭金手指已按语义映射到 JP-v96 原生用餐结算函数，并提供三个完整双语 `00..41` 下拉槽；当前仍待实机验证。本次新增的三个外部装备金手指也已独立映射。生产全解锁与无需材料已实机通过；更正后的无需材料结果是生产与强化会完整无视材料需求、实际持有的材料也不会被扣除，Cemu 界面保持正常数量而没有复刻 3DS 铁匠铺的全 99 显示。无需金钱 V1 虽能免费加工，却会把攻击力和人物面板归零；V2 通过生产，V3/V4 只覆盖旧强化记录。V5/V6 已由冷启动日志和客机内存证明完整加载，但连续误把通用详情值调用当成加工价格路径；材料充足的强化仍显示 `75000z`。V7 改为从运行时真实价格反查：硬件读监视点证明当前画面读取所选对象 `+0x31C`，实际候选生成器 `0x0221C730` 再通过 `0x0221C850` 与 `0x0221C96C` 两个互斥类别分支写入该字段。V7 删除四个已证伪的通用详情补丁，只修改这两个真实价格生成点，同时保留共享装备价值、攻击力敏感分派、出售/退款与钱包调整逻辑；2026-08-12 用户本机冷启动复测确认此前失败的强化路径已正常生效，因此 V7 升级为 Runtime Verified；该结论不冒充独立测试者或全部装备类别穷举。剩余动态集合现已精确收敛为 21 项（10 个运行时指针、6 个热键例程、5 个 ARM code-cave），全部已解码源语义并拆成 fail-closed PPC/GDB 取证批次；在目标映射和真实 trace 齐全前不会伪装成可安装 pack。

## 校验、安装、卸载、分发

```bash
python3 scripts/mh-cemu-enhancements.py validate
python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx /绝对路径/MH3G_Cafe.rpx

# 当前没有默认安装项；不启动 Cemu，也不改 Cemu 的启用状态。
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /绝对路径/cemu-data-root \
  --reference-rpx /绝对路径/MH3G_Cafe.rpx

# 安装基础人工实测集合：已验证大厅包、两个可选 FPS 上限包，
# 以及显式选择的猫饭技能自定义包。
# 不启动 Cemu，也不改 Cemu 已保存的启用/禁用状态。
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /绝对路径/cemu-data-root \
  --reference-rpx /绝对路径/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-lobby-full-item-box \
  --pack mh3g-hd-jp-v96-fps-lock-30 \
  --pack mh3g-hd-jp-v96-fps-lock-44 \
  --pack mh3g-hd-jp-v96-custom-felyne-food-skills \
  --include-experimental

# 全部任务箱候选均暂停且 runtime-blocked，不能安装。
# 43 个静态转换包均需按映射清单中的包 ID 重复传入 --pack 显式安装；
# 即使使用 --include-experimental，也不会把这 43 项自动加入安装集合。
# 三个外部装备包同样只接受显式选择；请先阅读各自的隔离验收条件。

python3 scripts/mh-cemu-enhancements.py uninstall --cemu-root /绝对路径/cemu-data-root
python3 scripts/mh-cemu-enhancements.py inspect --cemu-root /绝对路径/cemu-data-root
python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-preview.zip
```

### `main` 自动发布

`.github/workflows/release-on-main-pr-merge.yml` 只在目标分支为 `main` 的 PR **确实合并**后运行：先校验目录并执行完整单测，再独立构建两次 ZIP 并要求字节完全一致，随后创建带注释的 `vX.Y.Z` Tag，并把 ZIP 与 SHA-256 sidecar 发布为最新 GitHub Release。仅关闭但未合并的 PR、普通分支 push 都不会触发发布。同一合并提交重跑时会复用已有 Tag；后续合并默认递增 patch 版本，除非维护者已在仓库中准备了版本更高但尚未打 Tag 的 dist。

Release ZIP 使用固定顶层目录 `mh-cemu-enhancements/`，并把插件按 `01-frame-rate`、`02-speed-and-actions`、`03-skills-and-immunities`、`04-combat-and-weapons`、`05-balance-breaking`、`06-quality-of-life`、`07-item-box-and-interface` 七类存放。源码仓库仍保留通用的扁平 pack 路径，只有打包成品会确定性重写 catalog、manifest 和文件路径。每个 Pack 都提供“效果、边界、验证、来源/状态”四段式中英双语说明；ZIP 根目录生成的 `PACK-INDEX.md` 会同时列出每项摘要和完整说明，`catalog/distribution-index.json` 也向工具暴露相同字段。解压后的成品会再次通过同一套 `validate`。完整规则见 [Release ZIP 目录与分类规则](docs/release-layout.md)。

ZIP 不包含 `.github`、`tests`、`dist`、编辑器缓存等仓库专用内容，也不会包含任何游戏资产。分类只影响发行包的可读性；安装器仍用稳定的 `install_folder` 写入 Cemu 自有目录，因此不会仅因 ZIP 重构而改变既有 Cemu 启用路径。推荐在解压后的 `mh-cemu-enhancements/` 根目录运行安装命令，不要手工整类复制。

安装器只写入自有的 Graphic Pack 目录及其中 receipt：标准 Cemu macOS 数据根是 `<cemu-root>/graphicPacks/mh-cemu-enhancements/`；提供的 Nemessix 隔离外层根（`.../Library/Application Support/Nemessix Dev/cemu`）则必须写入 `<cemu-root>/data/graphicPacks/mh-cemu-enhancements/`，这是 bundled Cemu 实际扫描的 user-data 路径。重复安装只替换该自有目录；卸载也只移除该目录，重复卸载成功返回。若目录原先不存在 receipt，会先原地改名备份。此前错误写入隔离根 `<cemu-root>/graphicPacks/mh-cemu-enhancements/` 的旧版 receipt 安装会在下一次安装时自动迁移；直接卸载也会移除该自有旧目录。

`inspect` 为只读诊断：它输出解析后的 Graphic Pack 目录、对应 settings 文件、每个 catalog 条目的安装状态以及 Cemu 保存的启用状态。安装完成后，只在 Cemu 的 **Graphic Packs** UI 启用需要的可用包；安装器不会自行改变 Cemu 保存的启用状态。

### macOS 隔离 profile 启动

提供的 Cemu build 只有在设置 `NEMESSIX_CEMU_DATA_ROOT` 时才会使用隔离 profile。`-m` 只指定 MLC 目录，不会切换 Cemu 的用户数据/Graphic Packs profile；仅带 `-m` 启动时仍会落入标准 `~/Library/Application Support/Cemu` profile，因此看不到安装在隔离根的包。为避免混用 profile，先仅打印正确启动命令（不会启动 Cemu）：

```bash
python3 scripts/mh-cemu-enhancements.py isolated-launch-command \
  --cemu-root "/绝对路径/Library/Application Support/Nemessix Dev/cemu" \
  --cemu-app /绝对路径/Cemu.app
```

手动执行打印出的命令后，在 **Graphic Packs** 中分别勾选所需的可用开关，并重新载入/重启游戏。全部任务箱实验继续阻断；两个 FPS 包在测试前保持关闭，且 30 FPS 与 44 FPS 不能同时启用。

## 补丁语义、兼容与联机

- 30 FPS 与 44 FPS 都使用 Graphic Pack 的 `[Control] vsyncFrequency`，不写 Cemu 全局帧率配置；两者均保持 `Runtime Experimental`、默认关闭，且只能二选一，因为 Cemu 同时只能接受一个自定义 VSync 频率。44 FPS 包是两条重复 3DS 44 FPS 条目的语义转换。
- 大厅包只改一条 Port Tanzia 交互指令：把传给共享箱子初始化函数 `0x021F0A8C` 的受限模式参数由 `r5 = 1` 改为完整模式 `r5 = 0`。它不替换对象、不使用分支或 code cave，完整菜单、换装、装备组合与护石功能已经实测通过，标记为 `Runtime Verified`，但仍默认关闭。
- 红箱候选只改**红色交纳箱**，但实机仍持续显示不可用红叉。该候选保留作静态失败历史，并以 `runtime-blocked` 阻止安装。
- 无条件蓝箱桥把 `0x02219DF0` 改成 `nop`。Cemu 已证明它在运行中成功热加载，但它仍不弹仓库菜单，并把无关任务 UI 状态送入大厅调度器，导致任务看板对话框空白；现已 `runtime-blocked`。
- 红蓝统一候选保留为源码历史，但现与其他任务箱实验一起标为 `runtime-blocked` 暂停；在拥有可复现的正确任务场景生命周期前，安装器不会选择它。
- 猫饭技能自定义包提供三个互相独立的双语 `00..41` 下拉槽，包内默认组合为 `06/36/00`。修正版在随机生成结束后覆盖原生临时槽 `r31 + 0x68/0x6A/0x6C`，并保留游戏原生的菜单/任务状态最终镜像循环。Cemu 在标题加载时解析 Graphic Pack 参数；修改预设后必须重启或重新载入游戏，再重新吃饭。餐前预览仍可能显示原版随机技能，游戏原生互斥组合（已知例：`41 + 1E`）也可能只生效其中一项。该包默认关闭，状态为 `Runtime Experimental / Gameplay Pending`。
- 三个外部装备包是 `Equipment Cheats` 下相互独立且默认关闭的叶子：生产全解锁只旁路合法 ID 的解锁位失败；无需材料已包含生产解锁，并把精确的非豁免材料数量调用族伪装为 99；无需金钱 V7 保留两个生产费用单点与两个旧强化记录点，并覆盖运行时追踪闭环的两类候选价格生成调用。生产全解锁与无需材料互斥，因为后者已经包含前者。前两项已实测通过；无需金钱 V1 因攻击力/人物面板归零被否定，V2 只通过生产、遗漏强化，V3 只覆盖一条强化记录路径，V4 覆盖两条记录路径但仍显示原价，V5/V6 已证明加载却连续误判通用详情显示点；V7 已改为真实 +0x31C 候选价格源；2026-08-12 用户本机冷启动确认此前失败的强化路径已正常生效，现为 `Runtime Verified / Gameplay Passed`，且故意保留共享价值函数和真实出售/退款计算。
- 当前共有 53 个可用 Cemu 叶子：30/44 FPS、三个默认关闭的 60 FPS 行为修复（视角速度、锤子正本垒、风压吹飞距离）、大厅完整箱子、猫饭技能自定义、`3DS Static Cheats` 下 43 个独立静态转换项，以及三个外部装备项。所有任务箱候选均作为不可安装的失败证据保留。三个新增 60 FPS 修复继续保持 `Runtime Experimental / Gameplay Pending`，必须逐项隔离实测。
- 43 个静态转换包均默认关闭并保持 `Runtime Experimental / Gameplay Pending`。每个 Cemu 描述现都先讲真实游戏效果，再用中英双语列明作用边界、隔离验收方法与 3DS/PPC 来源状态，不再只显示“由 3DS ASM 转换”的样板说明。#6 与 #72 共用会心路径且互斥；#56 为部分语义映射；#65 强制常规游戏模式的通用技能比较，测试风险最高。隔离复测 #13/#21/#34/#50/#60 时必须关闭 #65；复测 #60 时还必须关闭 #59。2026-08-07 本机实测已确认 #13 0.1.22 不再只是动画加速，水下实际位移也明显翻倍；皮皮鸟独立复测仍待回报，因此暂时保持实验状态。
- 联机时关闭全部道具箱修改包；30 FPS 包在稳定性结论出来前也不作为联机推荐。
- 不得对不同 Title ID、地区、更新、RPX hash 或 module checksum 使用本 JP v96 目录。

## 证据与格式

- [架构、状态语义与安全边界](docs/architecture.md)
- [通用目录决策](docs/adr/0001-catalog-and-pack-boundaries.md)
- [Release ZIP 目录与分类规则](docs/release-layout.md)
- [MH3G HD JP v96 PPC 静态证据账本](docs/research/mh3g-hd-jp-v96.md)
- [完整 3DS → Cemu 金手指转换矩阵](docs/research/mh3g-3ds-cheat-conversion.md)
- [43 项静态 ARM → PPC 映射与包 ID 清单](docs/research/mh3g-static-arm-mapping.md)
- [外部装备金手指 Gateway/ARM → PPC 映射](docs/research/mh3g-equipment-gateway-cheat-mapping.md)
- [21 项动态 PPC/GDB 映射与取证批次](docs/research/mh3g-dynamic-ppc-mapping.md)
- [pack manifest schema](schemas/pack-manifest.schema.json)

用户给出的 Bilibili 页面没有作为实现证据：其中 b23 短链不可用。本目录只依据本机 3DS ARM 语义对照、Wii U PPC/静态资源分析，以及 Cemu Graphic Pack parser 的规则实现。

远端仓库：`MHToolkit/mh-cemu-enhancements`。功能分支不会自动打 Tag 或创建 Release；只有合并到 `main` 的 PR 会触发上述发布工作流。
