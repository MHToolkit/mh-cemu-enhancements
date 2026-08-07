# MH3G 动态 3DS → Wii U PPC/GDB 转换 / Dynamic Mapping

## 结论 / Verdict

静态转换结束后，剩余的不是模糊的“二三十项”，而是矩阵中精确的 **21 项**：

- 10 项 `arm-runtime-pointer`
- 6 项 `arm-hotkey-routine`
- 5 项 `arm-code-cave`

After the static phase, the conversion matrix contains exactly **21** remaining entries:
10 runtime-pointer programs, 6 hotkey routines, and 5 ARM code caves.

这些 3DS 地址和偏移只作为源语义证据，**绝不直接写入 Wii U**。每个 Cemu
Graphic Pack 都必须先取得 JP v96 PPC hook、原指令前像和至少一次对应游戏动作的
GDB trace；在此之前只允许推进到 `ppc-candidate / not-traced / not-created`，不得
创建可安装 pack。

The 3DS addresses and offsets are source-side semantic evidence only and must
never be written into Wii U memory. Every Cemu Graphic Pack requires a proven
JP-v96 PPC hook, an original-word preimage, and at least one GDB trace of the
matching gameplay action. Before that evidence exists, an entry may advance to
`ppc-candidate / not-traced / not-created`, but no installable pack may be made.

机器可读的逐项语义、源位置、目标策略和批次见
[`mh3g-dynamic-ppc-mapping.json`](mh3g-dynamic-ppc-mapping.json)。

## 实施顺序 / Execution Order

| 优先级 | 批次 | 条目 | 目标 |
| ---: | --- | --- | --- |
| 1 | `direct-native-hooks` | #8、#12、#19、#20、#62 | 先找等价 PPC 原生函数、参数和写回；最有机会转为窄范围静态 PPC hook。 |
| 2 | `player-inventory-roots` | #4、#9、#10、#23、#32、#58 | 用大厅/任务/装备切换快照确定对象归属和生命周期。 |
| 3 | `weapon-runtime-state` | #24、#25、#28、#30 | 用铳枪、轻/重弩、斩斧的受控动作定位弹药、装填与能量 writer。 |
| 4 | `controller-action-hooks` | #1、#2、#3、#31、#57 | 先证明 Wii U 输入位，再建立共用 PPC 输入门。 |
| 5 | `monster-runtime-state` | #66 | 最后定位怪物生命/捕获字段，避免污染任务结算。 |

## GDB 取证工具 / GDB Evidence Tool

仓库新增 `scripts/cemu-gdb-probe.py`。它不会启动 Cemu；只连接用户已经以
`--enable-gdbstub` 启动的实例。每次 trace 都必须使用 JSON spec：

1. 固定 `title_id`、`module_checksum`、Cemu RPX hash 与 RPX SHA-256。
2. 每个 breakpoint 都声明 `expected_word`；任何前像不符立即停止，绝不继续下断点。
3. 命中时记录 32 个 GPR、PC、LR、固定内存和寄存器相对内存到 JSONL。
4. breakpoint 为一次性；结束或失败时清理仍在使用的断点并恢复游戏运行。
   即使 tracer 收到 `Ctrl-C`，也会先中断目标、撤销已下断点并恢复运行后再退出。
5. 工具不读取或修改 RPX/WUA、MLC、存档、Graphic Pack 配置。

The repository now includes `scripts/cemu-gdb-probe.py`. It never launches
Cemu; it only attaches to an instance already started with `--enable-gdbstub`.
Every trace spec pins title ID, module checksum, Cemu RPX hash, and full RPX
SHA-256, and supplies an expected PPC word for every one-shot breakpoint. A
mismatch fails closed before any breakpoint is armed. Hits are emitted as JSONL
with GPR/PC/LR and bounded memory snapshots; remaining breakpoints are removed
and the title is resumed on exit.

只检查 spec，不连接 Cemu：

```bash
python3 scripts/cemu-gdb-probe.py check-spec --spec /path/to/trace-spec.json
```

连接已经运行的 Cemu 并记录：

```bash
python3 scripts/cemu-gdb-probe.py trace \
  --spec /path/to/trace-spec.json \
  --output /path/to/trace.jsonl
```

## 每项升级门槛 / Promotion Gates

一个动态条目只有同时满足以下条件，才能从研究清单升级为默认关闭的
`Runtime Experimental` pack：

1. **Source decoded**：Gateway 条件、指针、字段宽度和 code-cave 算法已经解释。
2. **PPC mapped**：目标函数、参数/对象字段、控制流和副作用已经用静态反汇编证明。
3. **Fail-closed**：manifest 固定 JP v96 RPX SHA、`moduleMatches = 0x348600a0`，并为每个 PPC 写入记录原指令。
4. **GDB traced**：真实对应动作命中目标 hook，寄存器/对象变化符合假设。
5. **Assembler verified**：Cemu 真实 PPCAssembler 接受全部指令和 relocation。
6. **Gameplay pending**：安装和 trace 仍不等于玩法通过；实机对照完成前不得写 `Runtime Verified`。

## 当前状态 / Current State

- 21/21 源 Gateway 程序已解码并按真实依赖分批。
- 2/21 已有静态 PPC **候选**，均仍需受控 GDB trace，尚未声明
  `ppc-mapped`：
  - #8 道具袋不减：数量变更函数 `0x0219B6E4`，入口 `r5` 为候选有符号
    delta，`r6` 为 4 字节槽数组；目标结构与 3DS 函数逐段一致。
  - #12 携带道具上限：道具记录 getter `0x0203A284`、返回点
    `0x0203A2A0`、记录步长 `0x14`、携带上限偏移 `+3`。
- 0/21 已完成 PPC 映射；当前没有为动态项创建任何可安装 pack。
- 0/21 有本分支的新 GDB gameplay trace。
- 已为 #8 与 #12 分别提交只读一次性 trace spec：
  `traces/mh3g-dynamic-08-pouch-delta.json`、
  `traces/mh3g-dynamic-12-item-cap-return.json`。
- 第一批为 #8、#12、#19、#20、#62；候选地址可以随静态证据进入研究清单，
  但只有反汇编与 trace 同时支持时才可进入 manifest。

This is intentionally a research baseline, not a gameplay-success claim.
