# MH3G JP v96 #28 斩斧能量槽 PPC 定位手册

## 当前结论 / Current conclusion

- 3DS 金手指读取运行时堆指针 `0x083F50C4`，持续把对象 `+0x64` 的 **8 位**值写为
  `100`。这个地址不是可直接移植到 Wii U 的静态全局。
- 已精确映射的同类玩家内层字段（例如 #24/#30 的 `+0x452/+0x453`）在 Wii U
  一致后移 8 字节，因此 `+0x6C` 是比直接照抄 `+0x64` 更值得先验证的**布局假设**；
  它仍不是已确认字段。
- 对 JP v96 固定 `.text` 的 D-form 扫描中，非栈 byte/halfword 访问在 `+0x64`
  有 260 处、`+0x6C` 有 181 处；只看 byte 访问则分别为 84 与 149 处。静态数量
  不能建立对象身份或能量语义。
- 在常见玩家/武器逻辑区间 `0x02800000..0x02900000`，`+0x6C` 的直接 byte
  访问只剩 `0x02860690`（`lbz`）、`0x028606A4`（`stb`）和 `0x02860B98`
  （`stb`），但三处同属 `0x02860558` 的复杂动作/效果路径，尚无斩斧身份、
  0..100 标度或生命周期证据，不能直接拿来做 Pack。
- 当前 Apple Silicon Cemu 的 GDB stub 虽接受 `Z2/Z3/Z4`，底层 read/write
  breakpoint 只在 x86-64 Windows/Linux 实现；非 x86 会记录“不支持”。因此本机
  不能依赖内存 watchpoint，必须先做同对象快照差分，再对缩小后的 PPC store 地址
  逐一使用**执行断点**。

The only current target-layout lead is `+0x6C`, inferred from an independently
observed +8 shift in related inner-player fields. It is not a mapping. Static
access counts and the three nearby instructions above are only search-space
reduction, never writer proof.

## 第一阶段：五个同生命周期快照 / Five same-lifecycle snapshots

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

## 第二阶段：从字段缩到唯一 writer / Narrow to the unique writer

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

在以上证据闭环之前，#28 仍保持 `source-decoded / not-traced / not-created`，不发布猜测
Graphic Pack。
