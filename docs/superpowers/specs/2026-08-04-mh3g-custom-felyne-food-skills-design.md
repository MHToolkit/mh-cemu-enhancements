# MH3G HD JP v96 猫饭技能自定义设计

**日期 / Date:** 2026-08-04  
**状态 / Status:** Approved for implementation / 已批准实现

## 目标 / Goal

把群友提供的 3DS「猫饭自定义 v1.2」语义转换为 Cemu Graphic Pack：用户可分别选择三个猫饭技能槽，下一次完成用餐时由游戏原生结算流程把所选技能写入菜单状态与任务运行状态。

Convert the community-provided 3DS “Custom Felyne Food Skills v1.2” behavior into a Cemu Graphic Pack. The user selects three skill slots, and the game's native meal finalizer writes those choices into both menu and runtime state when the next meal is completed.

## 已证实的 3DS 语义 / Confirmed 3DS semantics

原金手指不是单个固定地址写入，而是沿两条动态指针链把三个字节技能编号同步到两份状态：

- 菜单侧偏移：`+0x7D92/+0x7D94/+0x7D96`
- 任务运行侧偏移：`+0xE2E/+0xE30/+0xE32`
- 有效编号：`0x00..0x41`，其中 `0x00` 表示空槽

The original cheat follows two dynamic pointer chains and synchronizes three byte-sized IDs into menu-side and runtime-side state. Directly copying the 3DS addresses to Wii U would therefore be incorrect, and ARM little-endian byte writes cannot be transcribed as PPC big-endian writes.

## ARM → PPC 映射证据 / ARM-to-PPC mapping evidence

静态反汇编已经定位到结构和控制流均对应的原生用餐结算函数：

- 3DS ARM finalizer：`0x005C3054..0x005C3330`
- Wii U PPC finalizer：`0x021D8548..0x021D8790`
- PPC 唯一直接调用点：`0x021D9D9C`
- PPC 独立运行态读取器：`0x0285F224..0x0285F25C`

Wii U finalizer first clears three halfword slots, deduplicates up to three generated skills, then mirrors them into:

- menu destination `r30 + 0x83FE/0x8400/0x8402`
- runtime destination `[r31 + 0x140] + 0xE3E/0xE40/0xE42`

The independent reader loops over exactly three halfwords beginning at runtime offset `0xE3E`; its callers recognize IDs through `0x41`. This confirms that the JP-v96 Wii U build uses the same skill-ID domain as the 3DS source.

## 选定架构 / Selected architecture

新增一个默认关闭的独立实验包：

`MH3G HD JP v96 - Custom Felyne Food Skills`

### 1. 三个分类下拉框 / Three categorized dropdowns

Graphic Pack `rules.txt` 提供三个互不绑定的分类：

- `技能槽 1 / Skill Slot 1`
- `技能槽 2 / Skill Slot 2`
- `技能槽 3 / Skill Slot 3`

每个分类都完整列出 `00 无 / None` 与 `01..41` 的中英双语技能名。包内默认组合为 `06 / 36 / 00`（猫的特殊攻击术、猫的短期催眠术、空槽），但整个包默认不安装、不启用。

### 2. 原位覆盖结算尾段 / In-place finalizer rewrite

不使用 `.origin = codecave`。本机 Cemu 2.6 曾把 code cave 放到 guest `0x01800000` 并触发 PPC recompiler 崩溃。改为只覆盖 finalizer 尾部现有十条指令 `0x021D8740..0x021D8764`：

```asm
0x021d8740 = lwz r11, 0x140(r31)
0x021d8744 = li r0, $skill1
0x021d8748 = sth r0, 0x000a(r27)
0x021d874c = sth r0, 0x0e3e(r11)
0x021d8750 = li r0, $skill2
0x021d8754 = sth r0, 0x000c(r27)
0x021d8758 = sth r0, 0x0e40(r11)
0x021d875c = li r0, $skill3
0x021d8760 = sth r0, 0x000e(r27)
0x021d8764 = sth r0, 0x0e42(r11)
```

`r27` 在原函数中已经等于 `r30 + 0x83F4`，因此 `+0x0A/+0x0C/+0x0E` 精确对应菜单侧 `+0x83FE/+0x8400/+0x8402`。覆盖块同时更新 runtime state，然后原样落入 `0x021D8768` 的后续流程。后续代码会重新装载所需寄存器，不依赖被替换循环留下的 `r7/r9/r10/r12` 值。

### 3. 作用时机 / Activation timing

补丁只改变下一次原生用餐结算。修改预设后必须重新吃饭；对已经完成的猫饭不会追溯改写。餐前预览仍可能显示游戏原本生成的技能，实际任务状态与技能效果是实机验收重点。

## 安全边界 / Safety boundaries

- 仅匹配 Title ID `0005000010104D00`、JP update v96、RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`、module checksum `0x348600a0`。
- manifest 固定记录十个覆盖字的原始 preimage，并记录函数入口、寄存器构造、覆盖尾端与 fallthrough anchors。
- 不修改 Cemu、WUA、RPX、MLC 或存档；只安装仓库自有 Graphic Pack 文件。
- `41 + 1E` 已知不能共存；其他游戏原生互斥或非法组合也可能只生效其中一项。
- 没有真实吃饭并进入任务的游戏证据前，状态保持 `Runtime Experimental / Gameplay Pending`。

## 验证方案 / Verification

### 自动与静态验证 / Automated and static

1. 先添加目录、manifest、规则预设与精确补丁契约测试，并确认因包尚不存在而失败。
2. 校验每个槽恰好拥有 `0x00..0x41` 共 66 个双语选项。
3. 校验覆盖地址连续且仅为 `0x021D8740..0x021D8764`，补丁不含 `codecave`。
4. 针对固定 JP-v96 RPX 校验全部 preimage 与 anchors。
5. 运行完整单元测试、catalog validation、lint、`git diff --check` 与确定性打包。
6. 在不启动 Cemu 的前提下，保留大厅包与 30 FPS 包，并把本包安装到同一 Cemu Graphic Packs 根目录；核验 receipt 与源/安装文件哈希。

### 游戏验收 / Gameplay acceptance

1. 启用本包，分别选择三槽组合并重新吃饭。
2. 检查用餐后显示的技能，再进入任务确认技能状态与实际效果。
3. 至少覆盖常用组合 `06/36/00`、`06/05/00`、`12/41/00`、`05/41/00`。
4. 单独验证 `00` 空槽、三个不同技能、重复技能，以及一个已知互斥组合。

上述实机步骤由用户运行 Cemu 完成；仓库侧静态通过不得表述为 Runtime Verified。
