# MH3G 外部装备金手指 → Cemu PPC 映射 / External Equipment Cheats → Cemu PPC Mapping

> 目标 / Target：MH3G HD JP v96，Title ID `0005000010104D00`，`moduleMatches = 0x348600A0`。  
> 源 3DS `.code` SHA-256：`3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77`。  
> 目标 RPX SHA-256：`7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`。

这三项不是把 3DS 地址机械改写成 Cemu 地址。源侧 Gateway/ARM 语义先在匹配哈希的 3DS 代码上解码，再按函数结构、对象布局、调用者和原始 PPC 指令映射到 JP v96。所有 Pack 都默认关闭。生产全解锁、无需材料与无需金钱 V7 均已获得实机结果，现为 **Runtime Verified**；静态映射、前像与汇编通过本身仍不等于游戏内功能已经验证。

These packs do not mechanically reuse 3DS addresses. Gateway/ARM semantics are decoded against the hash-matching 3DS code, then mapped to JP v96 through function structure, object layout, callers, and pinned PPC preimages. Every pack is default-off. Production Unlock, No Materials, and No Money V7 now have gameplay results and are **Runtime Verified**; static mapping, preimage, and assembly proof alone are still not gameplay proof.

## 1. 装备生产全解锁 / Unlock All Equipment Production

Gateway 源代码先读取 `*0x00C394C8`，以对象首字 `0x00B5E934` 做身份保护，再循环把对象 `+0x65DC` 起的 49 个 32 位字写成 `0xFFFFFFFF`。本机 Citra Gateway 实现对 `C0000000 00000030` 与 `D2000000` 的组合实际执行 49 次，因此覆盖 1568 个解锁位，足以覆盖原生有效装备 ID `0x0000..0x05FC`。

3DS 原生检查从角色子对象 `root+0x18` 加 `0x65C4`，即 `root+0x65DC`；PPC 包装器 `0x02198FDC` 从 `root+0x38` 加同一 `0x65C4`，即 `root+0x65FC`。核心 PPC 检查 `0x02198FA8` 先排除 `0xFFFF` 和 `>=0x5FD`，再读取单个解锁位。因此 Cemu Pack 不写角色对象或存档，而只把 `0x02198FC8: beq false` 改为 `nop`；无效 ID 边界仍完整保留。

| Source semantic | JP-v96 PPC | Conversion |
|---|---:|---|
| 49-word unlock table fill | `0x02198FC8 = 0x4182000C` | `nop` after valid-ID bounds |
| 3DS `root+0x18+0x65C4` | PPC `root+0x38+0x65C4` | exact layout shift `+0x20` |

## 2. 装备制造与强化无需材料 / Craft and Upgrade Without Materials

ARM code cave 把 `0x00992BE8` 的“主背包 + 备用背包 + 仓库合计数量”返回值改为 99，但读取保存的返回地址并保留 `0x005EC3A0` 这一名调用者的真实数量。PPC 等价函数是 `0x0219B624`；全 text 共有 26 个直接调用，`0x021F74AC` 精确对应 ARM 的豁免调用，因此只替换其余 25 项为 `li r3, 99`。

ARM `0x0042A848` 的单条仓库数量调用在 PPC 优化后复制为 `0x02182C30` 与 `0x02182C90`，两处都替换为 99。ARM `0x00990F9C` 的附带生产解锁映射到同一 `0x02198FC8 = nop`。总计 **28 条 PPC 写入**，不使用 code cave：

- 25 个 `0x0219B624` 非豁免调用者 → `li r3, 99`；
- 2 个 `0x0219B564` 编译器展开调用者 → `li r3, 99`；
- 1 个生产解锁位失败分支 → `nop`；
- `0x021F74AC` 保持真实数量，未被补丁覆盖。

这严格复现“伪装查询数量”的源语义，并不生成真实物品，也不自动证明已有部分材料不会被扣除。

### 2026-08-11 JP-v96 实机结果

- 零材料时，生产与强化均可完成；核心“无需材料”功能通过。
- 更正后的实测确认：即使实际持有材料，生产与强化也不会扣除；本包对 JP-v96 的调用族覆盖同时使需求检查和材料消耗路径完整忽略材料。
- 3DS 铁匠铺会因为共享 ARM 数量钩子覆盖显示路径而把材料全部显示为 99；JP-v96 PPC 实测中铁匠铺及相关界面保持正常数量，没有 99、空白或错误显示。
- 关闭本包并完整重启后恢复原材料要求，无崩溃或其他异常。该差异按更窄的功能等价接受，不为复制 3DS 的全 99 显示副作用而扩大核心补丁。

## 3. 装备制造与强化无需金钱 / Craft and Upgrade Without Money

ARM `0x005CC70C` 与 PPC `0x0221B530` 的结构一致：解析装备类别、计算费用、读取角色子对象 `+0x20` 的当前金钱，再设置不足标志 `0x4`。源补丁 `0x005CC880 E3500000` 使有效非负费用不再触发不足标志；PPC 在 `0x0221B6A0` 改为无条件跳到 `0x0221B6A8`，只绕过该标志写入。

ARM `0x00889AF8` 与 PPC `0x0215A84C` 都会先清零两个输出，再按装备类别返回对应指针或默认 `-1`。源补丁从 `0x00889B14` 直接跳到默认路径；PPC 对应把 `0x0215A86C` 改为跳到 `0x0215A8E0`。下游费用函数在两个零输出与 `-1` 返回下得到费用 0。总计 **2 条 PPC 写入**。

| ARM source | ARM preimage | JP-v96 PPC | PPC preimage | Replacement |
|---:|---:|---:|---:|---|
| `0x005CC880` | `0xE1510000` | `0x0221B6A0` | `0x40810008` | `b 0x0221B6A8` |
| `0x00889B14` | `0x379FF101` | `0x0215A86C` | `0x40800028` | `b 0x0215A8E0` |

### V1-V6 实机否定与 V7 运行时闭环定位 / V1-V6 gameplay rejection and V7 runtime-closed targeting

- **V1** 直接复刻 3DS 的全局类别分派与不足金钱旁路；生产、强化均可免费，但所有武器攻击力和人物面板显示归零，因此被否定。
- **V2** 删除全局副作用，只在生产费用包装器 `0x0221B468` 的两个直接调用点 `0x02206ECC`、`0x0221B694` 返回 0；低余额生产、价格 0、钱包不减和面板正常均已通过实测。
- **V3/V4** 顺着两条旧强化记录路径补入 `0x021CDC7C` 与 `0x0220B584`。静态数据流分别把费用写入 8 字节候选 `+0x04`，或经栈 `+0x0C` 写入详细记录 `+0x31C`；但小白鼠与本机复测仍显示强化原价。
- **V5/V6** 误把共享装备价值函数 `0x0221D224` 在两套通用详情控制器中的四个调用当成当前加工价格渲染。2026-08-12 冷启动日志与运行中客机内存读取确认 V6 八个声明地址全部已写成 `38 60 00 00`，材料充足的加工界面仍显示 `75000z`。这正式排除了安装、勾选和加载问题，也否定了四个显示层猜测点。

V7 不再根据相似 UI 调用猜测，而是从当前画面的真实数值反查：

1. 在客机堆中搜索屏幕价格的 big-endian 32 位值，定位到所选加工对象的价格字；切换条目后该字段随画面从 `75000` 变化为 `25000`。
2. 对该字段设置硬件**读**监视点，命中 Cemu PPC JIT；恢复出的客机 PC 为 `0x026A74E4`，对应静态指令 `0x026A74F4: lwz r5,0x31C(r9)`，证明当前价格渲染器直接读取所选对象 `+0x31C`。
3. 同一对象 `+0x27C` 是强化候选记录；实测铳枪记录首字节类别为 `0x0B`。`0x02159D14` 对类别 `1..6` 返回映射 0，对 `7..11` 及 `13..19` 返回映射 1，因此该铳枪明确走映射 1。
4. 当前加工控制器在 `0x0220C9F0` 把对象 `+0x31C` 作为价格数组、在 `0x0220C9F4` 把 `+0x27C` 作为候选数组，并于 `0x0220C9FC` 调用生成器 `0x0221C730`。
5. `0x0221C730` 先循环把十个价格字清零（`0x0221C754` / `0x0221C784`），再按上述类别映射从两条互斥分支重新填入价格：

| Category map | Price call | Immediate store | Covered equipment |
|---:|---:|---:|---|
| 0 | `0x0221C850 -> 0x0221BE94` | `0x0221C854: stw r3,0(r21)` | 类别 `1..6` |
| 1 | `0x0221C96C -> 0x0221C4D4 -> 0x0221B364` | `0x0221C970: stw r3,0(r21)` | 类别 `7..11,13..19`；本次铳枪 `0x0B` 命中 |

完整 `.text` 扫描得到 `0x0221C730` 的七个直接调用者：`0x0220C9FC`、`0x0220EC68`、`0x02221AA8`、`0x026FDEEC`、`0x026FDF24`、`0x026FE20C`、`0x026FE250`；各调用都显式传入候选记录与价格输出数组。V7 因此只把生成器内部这两个价格调用改为 `li r3,0`，让原生后续 store 把 0 写入统一价格字段。它同时保留已通过的两个生产点和两条旧强化记录兼容点，共六条写入：

| Purpose | JP-v96 site | Preimage | V7 |
|---|---:|---:|---:|
| 生产候选费用 | `0x02206ECC` | `0x4801459D` | `li r3,0` |
| 生产可用性费用 | `0x0221B694` | `0x4BFFFDD5` | `li r3,0` |
| 旧强化 8 字节记录 | `0x021CDC7C` | `0x4804F69D` | `li r3,0` |
| 旧强化详细记录 | `0x0220B584` | `0x48011D95` | `li r3,0` |
| 真实候选类别映射 0 | `0x0221C850` | `0x4BFFF645` | `li r3,0` |
| 真实候选类别映射 1 | `0x0221C96C` | `0x4BFFFB69` | `li r3,0` |

V7 **删除** V5/V6 的 `0x026FEBEC`、`0x026FEC14`、`0x02709644`、`0x02709668` 四个通用详情补丁，并保持共享装备价值函数 `0x0221D224`、攻击力敏感分派 `0x0215A86C`、钱包比较、钱包调整器及出售/退款调用者原样。上述运行时证据已经闭环到真实价格字段和唯一两类生成分支。2026-08-12 用户本机冷启动复测确认此前“生产 0z、强化仍为原价”的故障已修复，强化路径正常生效，因此 V7 现为 `Runtime Verified / Gameplay Passed`；该结论不冒充独立测试者或全部装备类别穷举。

V7 abandons UI-similarity guesses and traces the displayed value itself. A live heap search located the selected object's big-endian price; a hardware read watchpoint recovered renderer instruction `0x026A74F4`, which loads object `+0x31C`. The active controller passes that exact `+0x31C` array and candidate records at `+0x27C` to builder `0x0221C730`. The builder clears ten prices, then repopulates them through only two category branches at `0x0221C850` and `0x0221C96C`; the tested gunlance category `0x0B` takes the latter. V7 zeros those two builder-local calls, retains two gameplay-passed production sites and two narrow legacy upgrade-record sites, and removes all four disproven generic-detail patches. Static and runtime targeting is closed. On 2026-08-12 the user cold-started V7 locally and confirmed that the formerly failing upgrade path now works, promoting it to `Runtime Verified / Gameplay Passed`; this does not claim an independent retest or exhaustive category coverage.

## 互斥和组合 / Conflicts and combinations

- “装备生产全解锁”与“无需材料”共享 `0x02198FC8`，而后者已包含前者语义；两者属于同一 `exclusive_group`，不要同时启用。
- “无需钱”可与其中任意一个组合，但首轮验收必须逐项单开，避免无法判断是哪条补丁生效或产生副作用。
- 三项都要求完全重启游戏后验证；Cemu 的已加载 PPC 补丁不能用菜单勾选状态代替冷启动验收。
