# Release ZIP layout and category policy / Release ZIP 目录与分类规则

The Git repository keeps the generic, stable source layout
`packs/<platform>/<title>/<region-update>/<pack>/`. A release ZIP is a user-facing
distribution, so packaging inserts one explicit category directory without moving the
canonical source tree:

Git 仓库继续使用稳定且通用的源码布局
`packs/<platform>/<title>/<region-update>/<pack>/`。Release ZIP 面向实际使用者，打包时会在
不移动仓库源码的前提下插入一级明确分类：

```text
mh-cemu-enhancements/
├── README.md
├── README.zh-CN.md
├── LICENSE
├── PACK-INDEX.md
├── catalog/
│   ├── categories.json
│   ├── distribution-index.json
│   └── packs.json
├── docs/
├── schemas/
├── scripts/
└── packs/
    └── wiiu/mh3g-hd/jp-v96/
        ├── 01-frame-rate/
        ├── 02-speed-and-actions/
        ├── 03-skills-and-immunities/
        ├── 04-combat-and-weapons/
        ├── 05-balance-breaking/
        ├── 06-quality-of-life/
        └── 07-item-box-and-interface/
```

## Categories / 分类

| Order | ID | 中文 | English | Current packs |
| ---: | --- | --- | --- | ---: |
| 01 | `frame-rate` | 帧率相关 | Frame Rate | 5 |
| 02 | `speed` | 加速与动作 | Speed and Actions | 6 |
| 03 | `skills-immunities` | 技能与免疫 | Skills and Immunities | 21 |
| 04 | `combat-weapons` | 战斗与武器 | Combat and Weapons | 7 |
| 05 | `balance-breaking` | 破坏平衡 | Balance Breaking | 10 |
| 06 | `quality-of-life` | 便利功能 | Quality of Life | 3 |
| 07 | `item-box-interface` | 道具箱与界面 | Item Box and Interface | 4 |

Every manifest must declare exactly one primary `distribution_category`. Category is
independent of `status` and `availability`: for example, the item-box category contains
one available lobby pack and three `runtime-blocked` task-box evidence packs. A pack is
not promoted, hidden, or made installable merely by being assigned a category.

每个 manifest 必须声明且只能声明一个主分类 `distribution_category`。分类与 `status`、
`availability` 相互独立：例如“道具箱与界面”当前包含一个可用大厅包和三个
`runtime-blocked` 任务箱证据包。归类不会自动提升验证状态、隐藏风险，也不会让阻塞包变得可安装。

## Deterministic rewrite / 确定性重写

During packaging, `catalog/packs.json`, every packaged manifest `pack_dir`, and all pack
file paths are rewritten to the categorized release location. The extracted release is
then validated again as a self-contained repository. `PACK-INDEX.md` is the bilingual
human index and includes every pack's concise summary plus its full effect/scope/verify/
source-status description. `catalog/distribution-index.json` contains the same summary,
description, category, status, availability, count, and path data for tools. Neither file
contains a timestamp, so two builds of the same commit remain byte-identical.

打包时会同步重写 ZIP 内的 `catalog/packs.json`、每个 manifest 的 `pack_dir` 以及全部包文件
路径，随后对解压后的成品再次执行完整目录校验。`PACK-INDEX.md` 是中英双语人工索引，会列出
每个 Pack 的精简摘要和“效果、边界、验证、来源/状态”完整说明；
`catalog/distribution-index.json` 则为工具提供同一套摘要、完整说明、分类、状态、可用性、数量
和路径数据。两者都不写入时间戳，因此同一提交连续构建两次仍可保持逐字节一致。

## Per-pack description contract / 单包说明契约

Every `rules.txt` `[Definition]` must contain exactly one non-empty `name`, `path`, and
`description`. The description must be at least 500 characters and use the fixed
bilingual sections `中文：效果：…边界：…验证：…来源/状态：… / English: Effect: …
Scope: … Verify: … Source/status: …`. The manifest `summary` must lead with the same
Chinese and English effect text and state the real runtime status. A blocked pack must
also say `runtime-blocked` explicitly. Repository validation, unit tests, and validation
of the extracted release all enforce this contract.

每个 `rules.txt` 的 `[Definition]` 必须各有且仅有一个非空 `name`、`path` 与 `description`。
说明不得少于 500 字符，并固定采用“`中文：效果：…边界：…验证：…来源/状态：… /
English: Effect: … Scope: … Verify: … Source/status: …`”双语结构。manifest 的 `summary`
必须以相同的中英文实际效果开头并写明真实运行状态；阻塞包还必须明确标注
`runtime-blocked`。源码校验、单元测试以及解压后发行树复验都会执行该契约。

The release ZIP excludes repository-only CI/tests/editor metadata and every prohibited
game-asset suffix. GitHub's source archive remains available for development history and
tests. The release keeps documentation and research evidence so every experimental or
blocked verdict remains auditable.

Release ZIP 不包含仅供仓库使用的 CI、测试和编辑器元数据，也继续排除全部受禁游戏资产后缀。
开发历史和测试仍可通过 GitHub source archive 获取；发行包保留文档与研究证据，确保实验项和
阻塞项的结论仍可审计。

## Installation compatibility / 安装兼容

The categorized path is a release-storage concern. The installer still copies selected
packs by their stable `install_folder` into its owned Cemu directory. This deliberately
avoids changing existing Cemu saved-enable paths merely because the release archive was
made easier to browse. Use the installer from the extracted root rather than manually
copying every category, because it enforces selection, runtime-blocked gates, RPX
preimage verification, backup, and receipt behavior.

分类路径只影响发行包的存储结构。安装器仍按稳定的 `install_folder` 把已选插件复制到其自有
Cemu 目录，避免仅因 ZIP 更易浏览就破坏 Cemu 已保存的启用路径。应从解压根目录运行安装器，
不要手工整类复制；只有安装器会执行显式选择、`runtime-blocked` 阻断、RPX 前像校验、备份和
receipt 管理。

The merged-PR workflow on `main` validates and builds the ZIP twice before creating a tag
or GitHub Release. Feature-branch pushes never publish this layout prematurely.

`main` 的已合并 PR 工作流会先校验并连续构建两次 ZIP，再创建 Tag 和 GitHub Release；功能
分支 push 不会提前发布这套目录。
