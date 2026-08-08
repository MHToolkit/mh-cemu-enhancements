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
创建可安装 pack。若只观察到相关字段、输入位或候选 hook，而完整动作、状态桥和恢复路径
尚未闭环，则单独记录为 `partial-runtime-evidence`；它不会放宽 pack 门槛。

The 3DS addresses and offsets are source-side semantic evidence only and must
never be written into Wii U memory. Every Cemu Graphic Pack requires a proven
JP-v96 PPC hook, an original-word preimage, and at least one GDB trace of the
matching gameplay action. Before that evidence exists, an entry may advance to
`ppc-candidate / not-traced / not-created`, but no installable pack may be made.
A real but incomplete field, input, or hook observation is recorded separately
as `partial-runtime-evidence`; it does not relax the pack promotion gates.

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
4. 每个 breakpoint 最终只产出一次 `hit`；若指定寄存器等待条件，工具会让同一 software
   breakpoint 在未匹配时持续恢复/重装，直到匹配或达到 fail-closed 上限。结束或失败时清理
   仍在使用的断点并恢复游戏运行；即使 tracer 收到 `Ctrl-C`，也会先中断目标、撤销断点并
   恢复运行后再退出。
5. 工具不读取或修改 RPX/WUA、MLC、存档、Graphic Pack 配置。

Cemu 2.6 的 GDB stub 在客户端连接时不会主动发送 stop packet。工具使用已由
Cemu 实现和实测确认的 `?` → `Hg0` → `Hc-1` 握手：`?` 只获取默认线程状态，
不会暂停游戏；只有真实 breakpoint 命中后才会选择返回的具体线程 ID。初始连接
阶段不得用 `Ctrl-C` 代替握手，也不得把 `?` 返回的线程直接传给 `Hg`，否则可能
让 stub 和游戏进入等待状态。

Cemu 2.6 does not emit an unsolicited stop packet when a debugger connects.
The probe therefore uses the verified `?` → `Hg0` → `Hc-1` handshake. The
status query does not pause the title, and a concrete thread ID is selected
only after a real breakpoint stop. Sending Ctrl-C during initial attach, or
using the status-query thread as a stopped context, can stall the stub.

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

等待某个当前帧按键位真实出现后再保存完整 snapshot：

```bash
python3 scripts/cemu-gdb-probe.py trace \
  --spec docs/research/traces/mh3g-dynamic-controller-normalized-input.json \
  --output /path/to/controller-a.jsonl \
  --wait-register-mask r29=0x2000 \
  --max-skipped-hits 1000
```

`--wait-register-nonzero`、`--wait-register-not-value REGISTER=VALUE` 和
`--wait-register-mask REGISTER=MASK` 互斥。输入归一化对象存在固定高位/摇杆位，不能把
“r29 非零”当作按键条件；已知按键应优先使用精确 mask。

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
- 17/21 已推进到静态 PPC **候选**。这表示目标原生函数、字段或输入消费点已有
  可复核的跨架构证据，**不表示**完整补丁已经成立：
  - #1/#2/#3 速度倍率：玩家每帧更新函数 `0x02892294` 在
    `0x028924AC` 消费 `+0x608` 浮点倍率；归一化输入在 `0x02BCB9CC`
    写入，L/R 掩码分别为 `0x0100/0x0200`。跨函数安全状态桥和松键恢复仍需证明。
  - #4 斩味常紫：斩味更新函数 `0x0285F01C`，玩家状态
    `+0xAFC/+0xAFE/+0xAFB` 分别为当前值、上限和档位缓存；普通扣减、归零、
    上限钳制和档位刷新必须一起 trace。
  - #8 道具袋不减：数量变更函数 `0x0219B6E4`，入口 `r5` 为有符号 delta，
    `r6` 为 4 字节槽数组，数量写回点为 `0x0219B830`。
  - #9 背包第一格×99：选择器 `0x0219A6E4` 返回主背包 `+0xA8` 或备用背包
    `+0x108`；主背包第一条记录位于全局根 `0x10315C50` 所指对象的 `+0xE0`，
    记录步长 4、数量偏移 `+2`，原生数量 writer 同为 `0x0219B6E4`。
  - #12 携带道具上限：道具记录 getter `0x0203A284`、返回点
    `0x0203A2A0`、记录步长 `0x14`、携带上限偏移 `+3`。
  - #19 攻击倍率：攻击派生函数 `0x02867648` 在 `0x02867694` 写玩家状态
    `+0x6E8` 的 16 位攻击值，并保留原版 700 上限与 `+0x6EC` 显示值更新。
  - #20 防御倍率：防御派生函数 `0x02867CB4` 在 `0x02867D04` 写玩家状态
    `+0x6EA` 的 16 位防御值，并保留最低值处理与 `+0x6F0` 显示值更新。
  - #23 道具箱第一格×99：道具箱全局根同为 `0x10315C50`，首条记录位于
    `+0x1C0`，记录步长 4、数量偏移 `+2`、原生记录数为 101；候选更新路径入口
    为 `0x021F18BC`。
  - #24 铳枪弹药自填：共享武器状态函数 `0x02856C0C` 在
    `0x02856CEC/0x02856D00` 把 `+0x45B` 来源弹数复制到 `+0x45A` 当前弹数，
    并保留 `+0x462` 原生上限钳制。
  - #30 弩系自动装填：与 #24 共用函数和字段，备用类型/状态分支在
    `0x02856D7C/0x02856D90` 执行相同复制；轻弩与重弩仍需分别 trace。
  - #31 按 A 回血：HP 变更函数 `0x02865D08` 使用 `+0x640/+0x642` 作为当前/
    最大 HP，`r31` 保存有符号变化量；A 的归一化掩码为 `0x2000`，但输入轮询与
    HP writer 不在同一寄存器生命周期内。
  - #32 冷热饮效果：每帧更新函数 `0x02892294` 的两组浮点计时器为
    `+0x974/+0x978` 与 `+0x980/+0x984`；静态证据尚不能判定哪组对应热饮或冷饮。
  - #57 L/R+左方向键切换设置物判定：`0x02189FF4` 遍历 64 个 12 字节槽，
    ID 在 `+0`、阈值/状态字节在 `+7`；`0x0218A394` 执行阈值比较。左方向键掩码、
    真实调用类别、跨 hook 状态和恢复路径尚待 trace。
  - #58 多个炸弹/陷阱/肉：三个计数映射到玩家状态
    `+0x572/+0x573/+0x574`，原生准入 helper 为 `0x0289A014`、
    `0x0289A608`、`0x0289A728`，阈值分别为 0、3、2；三类身份仍需分别确认。
  - #62 氧气无限：氧气增减函数 `0x02863EEC`，有符号 delta 位于 `r4`，
    玩家状态 `+0x65C/+0x65E` 分别为当前值/上限，HUD 读取相同字段对。
- 余下 4/21 保持 `source-decoded`，没有把弱证据冒充映射：
  - #10 任务中背包第一格：已精确映射任务管理器访问器 `0x0270E63C`、全局根
    `0x1030BE28` 及 `0x1A4/0x8C` 两级步长，但尚未追到源
    `+0xAA0C/+0x2CE2` 背包镜像和 8 位数量 writer。
  - #25 子弹不减：依据已证实的 `+8` 布局偏移，仅得到八个缓存槽
    `+0x12A6..+0x12C2` 的假设窗口；尚无 PPC 弹药递减 writer 或对象根证据。
  - #28 斩斧能量槽最大：源 `0x083F50C4` 是 Citra 运行时堆指针；PPC `+0x64`
    字节访问误报过多，尚无斩斧控制流、0..100 标度或 writer 可建立候选。
  - #66 当前区域怪物一击必杀/直接捕获：源管理器链和 `+0x1558 = 0x18`
    已解码，但常量与字段语义都不唯一，必须排除怪物生命周期和任务结算状态。
- 0/21 已完成 PPC 映射；当前没有为动态项创建任何可安装 pack。
- 12/21 已取得 `partial-runtime-evidence`，9/21 仍为 `not-traced`；0/21 达到
  `gameplay-traced`。逐项原始路径、SHA-256、观测值和限制见
  [`mh3g-dynamic-runtime-evidence.json`](mh3g-dynamic-runtime-evidence.json) 与
  [`mh3g-dynamic-runtime-evidence-20260808.md`](mh3g-dynamic-runtime-evidence-20260808.md)。
- 最新 Nemessix/Cemu 调试提交 `1dcbefc1564f5dfed55dbdbfb7903f3470f15579`
  已在同一 MH3G JP v96 进程真实验证 persistent breakpoint：A 条件命中前连续重装
  833 次，随后不重启 Cemu 独立 reconnect，L/R/左方向键分别连续重装 108/157/170 次后
  命中。当前帧归一化掩码确定为 A=`0x2000`、L=`0x0100`、R=`0x0200`、
  左=`0x0080`。
- #1/#2/#3 的 `0x028924AC` 已在村庄移动输入期间真实命中，现场
  `r7=0x2FF7D610`、`r7+0x608=0x3F800000`（float 1.0）；该证据证明倍率消费点，
  仍未证明安全输入桥和 2x/3x gameplay 效果。
- #9/#23 的 live 根 `*0x10315C50=0x2E622A80` 与首记录 `+0xE0/+0x1C0`
  已和静态布局一致；#19/#20/#31/#58/#62 的候选玩家字段也能读出合理现场值。
  这些都是被动字段观察，不替代对应 writer 和受控动作 trace。
- #32 的 `0x02893154/0x028932B4` 已在村庄基线分别命中，两组计时器全零；
  热饮/冷饮身份仍需高温与低温任务各一次受控 trace。
- 早期 attach/preimage 门禁仍有效：#8 的 `0x0219B6F0 = 0x7CBA2B78` 与 #12 的
  `0x0203A2A0 = 0x4E800020` 在运行中匹配并成功下断点，但尚未捕获相应 gameplay
  动作，因此两项仍是 `not-traced`。
- 已为 17 个候选准备 17 份动作 trace spec，并另有 1 份共用的归一化输入 spec。
  #1/#2/#3 共用同一倍率 spec；#58 的三个阈值 helper 拆成三份独立 spec，避免在
  错误断点读取无效寄存器。候选地址可以随静态证据进入研究清单，但只有反汇编与
  对应 gameplay trace 同时支持时才可进入 manifest。

This is intentionally a research baseline, not a gameplay-success claim.
