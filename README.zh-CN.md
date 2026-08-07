# mh-cemu-enhancements

面向 Cemu 的本地优先增强资源目录：收纳可独立启用的 **Graphic Pack**、PPC patch、清单、校验和安装工具。根目录不绑定 MH3G；资源统一按 `packs/<platform>/<title>/<region-version>/<feature>/` 落盘，可持续增加其他 Monster Hunter/Wii U 游戏和地区版本。

仓库不收纳 RPX/RPL/WUA、存档、MLC、密钥、纹理 dump 或任何游戏资产；不会启动 Cemu、改 Cemu 二进制、改全局 Cemu 配置，也不会写入存档或 MLC。

## 首批：MH3G HD 日版 v96

| 开关 | 状态 | 可用性 | 默认安装 |
| --- | --- | --- | --- |
| 锁定 30 FPS | `Runtime Experimental` | `available` | 否 |
| 锁定 44 FPS（3DS 转换） | `Runtime Experimental` | `available` | 否 |
| 43 个 3DS 静态 ARM 转换包 | `Runtime Experimental` | `available` | 否（逐项显式选择） |
| 集会所/酒场完整家中箱子 | `Runtime Verified` | `available` | 否 |
| 猫饭技能自定义（三槽、`00..41`） | `Runtime Experimental` | `available` | 否（显式选择） |
| 任务红色交纳箱 -> 完整家中箱子 | `Runtime Experimental` | `runtime-blocked` | 否 |
| 任务蓝色补给箱 -> 完整家中箱子（无条件调度桥对照） | `Runtime Experimental` | `runtime-blocked` | 否 |
| 任务红蓝箱 -> 完整家中箱子（条件调度桥） | `Runtime Experimental` | `runtime-blocked`（暂停） | 否 |

适用身份：Wii U Title ID `0005000010104D00`、JP update v96、RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`、Cemu patch module checksum `0x348600a0`。

`Static Verified` 仅表示 Graphic Pack 结构、Cemu 语法、模块门槛、RPX hash 与声明的 PPC 原始字校验已经通过；**不等于游戏内已验证**。大厅包已由用户实测完整菜单、换装、装备组合与护石功能；30 FPS 因实测不稳定降为实验状态。任务箱多次实测仍不可用，蓝箱调度桥还会使任务看板对话框空白，因此所有任务箱实验现已暂停并阻止安装。活动 3DS 金手指已完整盘点：44 FPS 使用 Cemu 原生控制项；另有 43 条静态 ARM 项已根据哈希一致的 3DS `.code` 与 JP-v96 PPC 语义/前像映射为独立实验包，共 172 条 PPC 写入。另行提供的 3DS 猫饭金手指已按语义映射到 JP-v96 原生用餐结算函数，并提供三个完整双语 `00..41` 下拉槽；当前仍待实机验证。其他动态指针、热键与注入例程仍只记录为待独立映射。

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

python3 scripts/mh-cemu-enhancements.py uninstall --cemu-root /绝对路径/cemu-data-root
python3 scripts/mh-cemu-enhancements.py inspect --cemu-root /绝对路径/cemu-data-root
python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-0.1.20.zip
```

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
- 当前共有 47 个可用 Cemu 叶子：30/44 FPS、大厅完整箱子、猫饭技能自定义，以及 `3DS Static Cheats` 下 43 个独立静态转换项。所有任务箱候选均作为不可安装的失败证据保留。
- 43 个静态转换包均默认关闭并保持 `Runtime Experimental / Gameplay Pending`。#6 与 #72 共用会心路径且互斥；#56 为部分语义映射；#65 强制常规游戏模式的通用技能比较，测试风险最高。隔离复测 #13/#21/#34/#50/#60 时必须关闭 #65；复测 #60 时还必须关闭 #59。
- 联机时关闭全部道具箱修改包；30 FPS 包在稳定性结论出来前也不作为联机推荐。
- 不得对不同 Title ID、地区、更新、RPX hash 或 module checksum 使用本 JP v96 目录。

## 证据与格式

- [架构、状态语义与安全边界](docs/architecture.md)
- [通用目录决策](docs/adr/0001-catalog-and-pack-boundaries.md)
- [MH3G HD JP v96 PPC 静态证据账本](docs/research/mh3g-hd-jp-v96.md)
- [完整 3DS → Cemu 金手指转换矩阵](docs/research/mh3g-3ds-cheat-conversion.md)
- [43 项静态 ARM → PPC 映射与包 ID 清单](docs/research/mh3g-static-arm-mapping.md)
- [pack manifest schema](schemas/pack-manifest.schema.json)

用户给出的 Bilibili 页面没有作为实现证据：其中 b23 短链不可用。本目录只依据本机 3DS ARM 语义对照、Wii U PPC/静态资源分析，以及 Cemu Graphic Pack parser 的规则实现。

未来建议远端：`MHToolkit/mh-cemu-enhancements`。当前只创建本地仓库，不创建、不发布远端。
