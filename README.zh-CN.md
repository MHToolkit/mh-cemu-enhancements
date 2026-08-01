# mh-cemu-enhancements

面向 Cemu 的本地优先增强资源目录：收纳可独立启用的 **Graphic Pack**、PPC patch、清单、校验和安装工具。根目录不绑定 MH3G；资源统一按 `packs/<platform>/<title>/<region-version>/<feature>/` 落盘，可持续增加其他 Monster Hunter/Wii U 游戏和地区版本。

仓库不收纳 RPX/RPL/WUA、存档、MLC、密钥、纹理 dump 或任何游戏资产；不会启动 Cemu、改 Cemu 二进制、改全局 Cemu 配置，也不会写入存档或 MLC。

## 首批：MH3G HD 日版 v96

| 开关 | 状态 | 可用性 | 默认安装 |
| --- | --- | --- | --- |
| 锁定 30 FPS | `Runtime Experimental` | `available` | 否 |
| 集会所/酒场完整家中箱子 | `Runtime Verified` | `available` | 否 |
| 任务红色交纳箱 -> 完整家中箱子 | `Runtime Experimental` | `runtime-blocked` | 否 |
| 任务蓝色补给箱 -> 完整家中箱子（调度桥对照） | `Runtime Experimental` | `available` | 否 |

适用身份：Wii U Title ID `0005000010104D00`、JP update v96、RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`、Cemu patch module checksum `0x348600a0`。

`Static Verified` 仅表示 Graphic Pack 结构、Cemu 语法、模块门槛、RPX hash 与声明的 PPC 原始字校验已经通过；**不等于游戏内已验证**。大厅包已由用户实测完整菜单、换装、装备组合与护石功能；30 FPS 因实测不稳定降为实验状态。任务红箱多次实测仍不可用。第一版蓝箱对照按键后没有菜单；静态追踪定位到被据点场景门槛拦截的逐帧调度。修订版蓝箱现在加入调度桥，只作为等待实测的单人实验重新开放；红箱继续 `runtime-blocked`。

## 校验、安装、卸载、分发

```bash
python3 scripts/mh-cemu-enhancements.py validate
python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx /绝对路径/MH3G_Cafe.rpx

# 当前没有默认安装项；不启动 Cemu，也不改 Cemu 的启用状态。
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /绝对路径/cemu-data-root \
  --reference-rpx /绝对路径/MH3G_Cafe.rpx

# 显式安装已实测通过的大厅包。
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /绝对路径/cemu-data-root \
  --reference-rpx /绝对路径/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-lobby-full-item-box

# 显式安装修订后的蓝箱调度桥对照；Experimental 必须显式解锁。
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /绝对路径/cemu-data-root \
  --reference-rpx /绝对路径/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control \
  --include-experimental

# 红箱继续 runtime-blocked；如仍需安装 30 FPS，也须显式选择并加
# --include-experimental。

python3 scripts/mh-cemu-enhancements.py uninstall --cemu-root /绝对路径/cemu-data-root
python3 scripts/mh-cemu-enhancements.py inspect --cemu-root /绝对路径/cemu-data-root
python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-0.1.15.zip
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

手动执行打印出的命令后，在 **Graphic Packs** 中分别勾选所需的可用开关，并重新载入/重启游戏。红箱继续阻断；蓝箱调度桥仅限单人且仍等待实测；30 FPS 包在稳定性结论出来前保持关闭。

## 补丁语义、兼容与联机

- 30 FPS 使用 Graphic Pack 的 `[Control] vsyncFrequency = 30`，不写 Cemu 全局帧率配置；用户实测不稳定，因此保持 `Runtime Experimental`、默认关闭。
- 大厅包只改一条 Port Tanzia 交互指令：把传给共享箱子初始化函数 `0x021F0A8C` 的受限模式参数由 `r5 = 1` 改为完整模式 `r5 = 0`。它不替换对象、不使用分支或 code cave，完整菜单、换装、装备组合与护石功能已经实测通过，标记为 `Runtime Verified`，但仍默认关闭。
- 红箱候选只改**红色交纳箱**，但实机仍持续显示不可用红叉。该候选保留作静态失败历史，并以 `runtime-blocked` 阻止安装。
- 第一版蓝箱对照进入了全任务共用的选择器 `0` 分支并保留正常提示，但按交互键后没有菜单。`0x021F0A8C` 只写入状态 `6`，其唯一后续调度被据点场景检查绕过。修订版保留六指令触发器，把原指令 `0x02219DF0 = beq 0x02219E6C` 改为 `nop`，并保留 `0x0215165C` 前面的管理器有效性和忙碌状态保护。该版本仍是 `Runtime Experimental`，只开放单人隔离实测，不代表运行时成功。
- 当前可用 Cemu 叶子为：`MH Cemu Enhancements > MH3G HD JP v96 > Lock 30 FPS`、`Lobby Full Item Box` 与 `Quest Blue Supply Box -> Full Item Box (Control)`。红箱继续作为不可安装的失败证据保留。
- 联机时关闭全部道具箱修改包；30 FPS 包在稳定性结论出来前也不作为联机推荐。
- 不得对不同 Title ID、地区、更新、RPX hash 或 module checksum 使用本 JP v96 目录。

## 证据与格式

- [架构、状态语义与安全边界](docs/architecture.md)
- [通用目录决策](docs/adr/0001-catalog-and-pack-boundaries.md)
- [MH3G HD JP v96 PPC 静态证据账本](docs/research/mh3g-hd-jp-v96.md)
- [pack manifest schema](schemas/pack-manifest.schema.json)

用户给出的 Bilibili 页面没有作为实现证据：其中 b23 短链不可用。本目录只依据本机 3DS ARM 语义对照、Wii U PPC/静态资源分析，以及 Cemu Graphic Pack parser 的规则实现。

未来建议远端：`MHToolkit/mh-cemu-enhancements`。当前只创建本地仓库，不创建、不发布远端。
