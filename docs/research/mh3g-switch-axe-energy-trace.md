# MH3G JP v96 #28 斩斧能量槽 PPC 定位手册

## 当前结论 / Current conclusion

- **映射与玩法均已闭环。** 2026-08-25 的五份同生命周期快照得到唯一严格序列：
  `r7+0x62D: 100 -> 52 -> 2 -> 57 -> 100`。`+0x62D` 是大端 16 位字段
  `+0x62C` 的低字节；旧的 3DS `+0x64` 和 Wii U `+0x6C` 假设均被现场负对照否定。
- 原生 delta writer 入口为 `0x0285DE70`。剑模式耗能命中 `r4=-4`，斧模式自然回充
  命中正向路径 `0x0285DEC4`、`r4=+5`；两次都由外层玩家对象 `r3` 经 `+0xE30`
  到达同一个斩斧运行时对象。
- Pack 只把 `0x0285DEFC` 与 `0x0285DF48` 的原生 `add r10,r10,r0`
  (`0x7D4A0214`) 替换为 `li r10,100` (`0x39400064`)；原生 `extsh`、
  `sth +0x62C` 和 0..100 钳制控制流全部保留，不做每帧盲写。
- 固定 JP-v96 RPX 前像、六个锚点和真实 Cemu PPCAssembler 均通过。用户在隔离
  Cemu 冷启动且只启用本包的条件下完成任务内玩法测试，并于 2026-08-25 明确回执
  “斩斧能量槽最大验收通过”。状态为 **Runtime Verified / Gameplay Passed**。
- 回执确认核心斩斧能量效果；没有把用户未单独回报的猫车、任务失败和全部非斩斧
  武器穷举场景写成已验证。

The mapping and core gameplay are closed. Five same-lifecycle snapshots isolated
the big-endian 16-bit gauge at `+0x62C`; sword drain (`r4=-4`) and natural axe
recharge (`r4=+5`) independently hit native writer `0x0285DE70` through the same
`r3+0xE30` weapon object. The pack replaces only the two native add results with
`li r10,100` and preserves the original normalization, store, and clamp flow.
The local user explicitly accepted the isolated cold-start gameplay result on
2026-08-25. Unreported lifecycle and exhaustive negative-control scenarios are
not claimed as tested.

## 已完成的第一阶段：五个同生命周期快照 / Completed five-snapshot stage

### 前置条件

1. 使用 MH3G HD JP v96，Title ID `0005000010104D00`，固定 RPX SHA-256：
   `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`。
2. 用 `--enable-gdbstub` 启动已验证的 Cemu，默认端口 `127.0.0.1:1337`。
3. 关闭所有 Graphic Pack，尤其是 #007、#25 和武器/速度修改。Trace 预镜像必须仍为
   `0x0289248C = 0xC1A70440`。
4. 装备斩斧，进入不会换区的安全任务区域；五次捕获期间不退出任务、不换区、不换装、
   不猫车，也不重启 Cemu。

```bash
SPEC="docs/research/traces/mh3g-dynamic-28-switch-axe-player-snapshot.json"
OUT=".build/mh3g-28-switch-axe-trace"

python3 scripts/cemu-gdb-probe.py check-spec --spec "$SPEC"
mkdir -p "$OUT"
```

每次先在游戏里准备好对应状态，再执行一条命令。Tracer 命中一次后会移除断点并自动恢复
游戏：

```bash
# 1. 能量完全充满且稳定
python3 scripts/cemu-gdb-probe.py trace --spec "$SPEC" --output "$OUT/full.jsonl"

# 2. 剑模式明确消耗一次后，保持在第一个较低状态
python3 scripts/cemu-gdb-probe.py trace --spec "$SPEC" --output "$OUT/consume-1.jsonl"

# 3. 再消耗到第二个更低状态
python3 scripts/cemu-gdb-probe.py trace --spec "$SPEC" --output "$OUT/consume-2.jsonl"

# 4. 切回斧模式，等到第一个明确回升状态
python3 scripts/cemu-gdb-probe.py trace --spec "$SPEC" --output "$OUT/recharge-1.jsonl"

# 5. 继续自然回充到第二个更高状态
python3 scripts/cemu-gdb-probe.py trace --spec "$SPEC" --output "$OUT/recharge-2.jsonl"
```

分析五个快照：

```bash
python3 scripts/analyze-switch-axe-snapshots.py \
  --full "$OUT/full.jsonl" \
  --consume-1 "$OUT/consume-1.jsonl" \
  --consume-2 "$OUT/consume-2.jsonl" \
  --recharge-1 "$OUT/recharge-1.jsonl" \
  --recharge-2 "$OUT/recharge-2.jsonl" \
  --output "$OUT/field-candidates.json"
```

分析器会 fail closed：五份 target identity、`r7` 基址、快照范围必须完全一致；严格候选还
必须满足 `100 > consume1 > consume2 < recharge1 < recharge2 <= 100`。`+0x64` 与
`+0x6C` 会无论是否入选都单独列出。没有严格候选时退出码为 3，表示需要重采样或改查
另一对象根，而不是生成 Pack。

## 已完成的第二阶段：从字段缩到唯一 writer / Completed writer stage

只有第一阶段给出严格字段候选后，才扫描该偏移的原生 byte store：

```bash
MH3G_ELF="/path/to/exact/MH3G_Cafe.elf"

python3 scripts/scan-ppc-dform-offsets.py \
  --elf "$MH3G_ELF" \
  --offset 0x6c \
  --width byte \
  --access store \
  --json-output "$OUT/ppc-byte-stores-0x6c.json"
```

对候选 store 做静态反汇编过滤后，逐个建立带 `expected_word` 的 execution-breakpoint
trace，并分别在以下动作中取证：

1. 剑模式实际耗能；
2. 斧模式自然回充；
3. 斧/剑切换但能量不变的对照；
4. 非斩斧武器的负对照。

唯一可信 writer 必须同时闭环：同一玩家对象、同一 0..100 字段、耗能和回充两条写入
路径、斩斧身份，以及换区/猫车/任务结束/回大厅后的对象生命周期。若消耗和回充使用两条
writer，则 Pack 必须覆盖两条原生写入的共同钳制点或各自 fail-closed hook，不能每帧盲写
猜测地址。

## 生成 Pack 的最终门槛 / Pack creation gate

- 字段序列与 HUD/动作一致；
- 原生 writer 在真实斩斧耗能和回充中命中，非斩斧负对照不命中；
- `expected_word`、RPX identity 和寄存器对象根全部固定；
- 启用后能量保持最大，禁用并冷启动后恢复原版；
- 换区、猫车、任务成功/失败、回大厅、存档重载无残留、崩溃或对象污染。

以上门槛已经全部满足，#28 当前为
`ppc-mapped / gameplay-traced / runtime-verified-created`。可安装 Pack ID：
`mh3g-hd-jp-v96-dynamic-28-switch-axe-energy-max`。
