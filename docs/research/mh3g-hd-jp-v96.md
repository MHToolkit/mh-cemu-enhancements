# MH3G HD JP v96 static-research ledger

## Scope

Target: **Monster Hunter 3G HD Ver.**, Wii U Japan, title ID `0005000010104D00`, update v96. This ledger is static evidence only; Cemu is not launched by this project.

## Immutable reference

| Field | Value |
| --- | --- |
| RPX SHA-256 | `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` |
| Cemu RPX hash | `8cb62099` |
| Cemu patch module checksum | `0x348600a0` |
| PPC text load address | `0x02000020` |
| PPC data load address | `0x10000000` |

The RPX is not copied into this repository. The verifier accepts an explicit local reference path.

## 3DS control evidence (semantic reference only)

The local Japanese 3DS title is `0004000000048100` / `CTR-P-AMHJ`. Its extracted `code.bin` SHA-256 is `3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77`.

The existing 3DS force-30-FPS cheat follows `60C9E728 -> B0C9E728 -> +0x30` and writes float `0x41F00000`. This proves a 3DS runtime-pointer semantic only; it is ARM data and is never reused as a Wii U PPC address or patch.

## Menu-class mapping

Both the 3DS ARM code and the decompressed Wii U PPC data expose the same UI-class families. This separates menu/interaction handling from a world-model/chest visual:

| Intent | Class | JP v96 PPC evidence |
| --- | --- | --- |
| Full home item box | `uIDLobbyMyhBox` | RTTI at `0x100684d8`; resource `GUI\\lobby\\myh_box2_n` at `0x100256f4` |
| Restricted lobby/pub item box | `uIDLobbyShoItemGet` | RTTI at `0x10060ad0`; resource `GUI\\lobby\\sho_item` at `0x10025664` |
| Quest supply box | `uIDCockpitBox` | RTTI at `0x10052244`; resource `GUI\\quest\\box` at `0x100243f4` |
| Quest delivery box | `uIDCockpitShareBox` | RTTI at `0x10054680`; resource `GUI\\quest\\cockpit\\que_delibox` at `0x10024404` |

The Japanese gameplay reference independently describes village/port boxes as fuller storage, the pub box as item-only, and base-camp boxes as supply-only. The class/resource evidence confirms that the requested target is interaction/UI dispatch, not save data or a chest model.

## Cemu pack evidence

The local Cemu source parser reads `[Control] vsyncFrequency` from `rules.txt` and applies `.asm` patch groups only when `moduleMatches` contains the loaded module checksum. Cemu's documented `patch_*.asm` format supports PPC instruction replacement and code caves.

## Public-research boundary

The supplied Bilibili URL (`BV1XC4y1q74u`) could not be retrieved by the static web client and its three b23 download links were already known to return 404. It is not treated as source evidence. The project records public links in the README and proceeds from the local ARM/PPC assets above.

## Exact PPC dispatches and fail-closed assertions

All instruction words below are big-endian words from the immutable RPX text section. The installer verifies the RPX SHA-256 and every source/anchor word before copying a PPC pack; Cemu additionally gates the patch group with `moduleMatches = 0x348600a0`.

### Lobby restricted-mode override (Runtime Verified / 运行时已验证)

The earlier branch, six-site substitution, full-home code-cave, 3DS-register-position `r9`, and resident-object accessor candidates all loaded in Cemu while the restricted three-option menu remained. They are superseded and are not gameplay success. The latest accessor run is especially conclusive: Cemu's log records module checksum `0x348600a0`, application of patch group `MH3G HD JP v96`, and activation of the Lobby leaf, while the screenshot still shows only deposit, withdrawal, and combine/sell.

The valid 3DS reference supplied for Port Tanzia changes `0x008EA6D0` from ARM `0xE3A02001` (`MOV r2, #1`) to `0xE3A02000` (`MOV r2, #0`). The complete extracted 3DS `.code` was reverse-LZSS decompressed to SHA-256 `3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77`. Disassembly proves that this is the third argument to ARM function `0x005DEC70`, not a menu count or UI factory selector. That function stores the argument as a mode byte and selects state value `3` when the mode equals `1`, otherwise value `6`.

The Wii U semantic counterpart is PPC function `0x021F0A8C`. It stores its third PPC argument (`r5`) at object offset `+0x6E12`, performs the same `mode == 1` comparison, and writes the same `3` versus `6` state values. There are exactly two direct PPC callers. The sibling complete-box path at `0x027995F8` passes `r5 = 0`; the Port Tanzia restricted path at `0x02799678` passes `r5 = 1`; both immediately call `0x021F0A8C`. This argument/data-flow match is the cross-architecture mapping that the old register-position guess lacked.

| Role | Address | Original big-endian word | Evidence |
| --- | --- | --- | --- |
| Store mode | `0x021f0ad0` | `0x9bfc6e12` | `stb r31, 0x6e12(r28)` stores the third argument |
| Mode test | `0x021f0af0` | `0x2c1f0001` | `cmpwi r31, 1` |
| Unrestricted value | `0x021f0af4` | `0x38000006` | Defaults to state value `6` |
| Restricted override | `0x021f0af8`, `0x021f0afc` | `bne +8`; `li r0, 3` | Mode `1` changes the state value to `3` |
| State store | `0x021f0b00` | `0xb01d000c` | Stores the selected state into the shared box state |
| Complete caller | `0x027995f8`, `0x02799600` | `li r5, 0`; `bl 0x021f0a8c` | Existing unrestricted call |
| Port caller | `0x02799678`, `0x02799680` | `li r5, 1`; `bl 0x021f0a8c` | Patch the mode argument only |

```asm
0x02799678 = li r5, 0
```

This does not replace a UI object, construct a different object, alter the physical chest model, or touch save data. It changes one existing Port interaction argument from restricted mode to the game's own unrestricted mode. The user verified the complete menu plus equipment, equipment-set, and talisman actions in gameplay, so the pack is **Runtime Verified / 运行时已验证**. It remains default-off as an explicit opt-in.

### Quest red delivery box -> full item box (Experimental / 实验)

The earlier two-resource substitution was a false design: changing `0x021B0E90` and `0x021B0F14` swaps UI resource names but leaves the supply/delivery classes and interaction logic unchanged. It also violates the final scope because `0x021B0E90` belongs to the blue supply box. That candidate is removed.

旧的双资源替换是错误设计：`0x021B0E90` 与 `0x021B0F14` 只改变 UI 资源名，不会改变补给/交纳类的交互逻辑，而且 `0x021B0E90` 属于明确不应修改的蓝色补给箱。该候选已移除。

Static cross-references expose two tail-dispatch stubs into shared interaction function `0x028C26F0`: `0x028C5E78` passes selector `r4 = 0` for the blue supply box, while `0x028C5E80` passes `r4 = 1` for the red delivery box. The shared function compares that saved selector at `0x028C2768`; only the nonzero/red path reaches `0x028C27B4`, where calls at `0x028C27CC` and `0x028C27D4` prepare the delivery list and open the delivery menu.

静态交叉引用证明，共用交互函数 `0x028C26F0` 有两个尾分派入口：`0x028C5E78` 为蓝箱传 `r4 = 0`，`0x028C5E80` 为红箱传 `r4 = 1`。函数在 `0x028C2768` 比较该标志；只有非零的红箱路径进入 `0x028C27B4`，并在 `0x028C27CC` / `0x028C27D4` 构建交纳清单和交纳菜单。

首次运行时测试显示红箱上方为带叉提示且无法进入上述确认分支，证明仅修改确认回调仍然太晚。向前回溯到 `0x028C5824`：红箱提示生成先以 `r4 = 1` 调用共用资格函数 `0x0216B3FC`。该函数在任务进行状态 `5/7` 比较这个参数；`1` 返回 `-1` 并让 `0x028C5830` 跳过提示注册，而补给语义参数 `0` 返回允许值 `0`。首个修订候选据此把 `0x028C5824` 改为 `li r4, 0`。

The first runtime test showed a crossed red-box prompt and never reached the patched confirmation block, proving that confirmation-time redirection alone was too late. Backward tracing reaches `0x028C5824`, where red prompt generation calls shared eligibility function `0x0216B3FC` with `r4 = 1`. In active quest states `5/7`, selector `1` returns `-1`, causing `0x028C5830` to skip prompt registration; supply selector `0` returns allowed value `0`. The first revised candidate therefore changed `0x028C5824` to `li r4, 0`.

第二次运行时测试确认该修订补丁已由 Cemu 加载，但红箱仍显示红叉。这否定了“资格参数同时决定提示内容”的假设：资格参数只让代码到达 `0x028C5838`，而该处仍明确传入交纳提示编号 `15`。继续追入 `0x020F060C` 可见，参数 `r5` 仅在 `0x020F0698..0x020F06A0` 用于查询提示图文；从 `0x020F06B8` 起，注册器只接收查询结果，不再保留原始编号。因此新候选只在红箱自己的调用点把 `0x028C5838` 改为补给提示编号 `14`；这会替换红叉提示，却不会把蓝箱对象、蓝箱调用点或红箱后续确认分支改掉。

The second runtime test confirmed that Cemu loaded that revision, yet red still displayed the crossed prompt. This disproves the assumption that the eligibility selector also controls prompt content: it only allows execution to reach `0x028C5838`, which still explicitly passes delivery prompt selector `15`. Tracing into `0x020F060C` shows that argument `r5` is used only at `0x020F0698..0x020F06A0` to resolve prompt visual/text; from `0x020F06B8` onward, registration receives only the resolved result and does not retain the original selector. The new candidate therefore changes only the red-local `0x028C5838` to supply prompt selector `14`. This replaces the crossed prompt without modifying the blue object, the blue call site, or the red confirmation branch.

| Role / 作用 | Address | Original word | Replacement / 目标 |
| --- | --- | --- | --- |
| Red eligibility selector / 红箱资格参数 | `0x028c5824` | `0x38800001` | `li r4, 0` |
| Red-local prompt selector / 红箱局部提示编号 | `0x028c5838` | `0x38a0000f` | `li r5, 0xe` |
| UI manager high / UI 管理器高位 | `0x028c27c4` | `0x3fe01031` | `lis r3, 0x1031` |
| UI manager load / UI 管理器读取 | `0x028c27c8` | `0x807f507c` | `lwz r3, 0x44a0(r3)` |
| Delivery prepare call / 原交纳准备调用 | `0x028c27cc` | `0x4b8b75f1` | `mr r4, r30` |
| Delivery manager reload / 原交纳管理器重读 | `0x028c27d0` | `0x807f507c` | `li r5, 0` |
| Delivery menu call / 原交纳菜单调用 | `0x028c27d4` | `0x4b8b742d` | `bl 0x021f0a8c` |
| Delivery result test / 原交纳结果检查 | `0x028c27d8` | `0x2c030000` | `b 0x028c27f8` |

The eligibility and prompt rewrites are both inside the red-only world-object function. The in-place confirmation rewrite then calls the already-proven full item-box initializer with the current player in `r4` and full mode `r5 = 0`, skips delivery-only flag writes, and rejoins common cleanup. It uses no code cave and writes neither `0x021B0E90` nor `0x021B0F14`. The pack remains **Runtime Experimental / 运行时实验** and default-off until gameplay proves the red box, the unchanged blue box, menu exit/re-entry, and quest completion flow.

### All-quest blue supply-box control (Experimental / 全任务蓝箱对照实验)

Repeated gameplay still showed the crossed, unusable prompt on the patched red box. The next candidate is therefore a separate control on the already-usable blue supply box. Every quest blue box reaches the same selector-0 dispatch at `0x028C5E78` and falls through the shared interaction function into `0x028C2770`; there is no quest-ID or map-specific branch in this route. The control consequently covers every quest that already contains a blue supply box, while quests without one remain unchanged.

红箱补丁经过多次实测仍显示带叉且不可用的提示，因此下一个候选改为独立的蓝箱对照。所有任务蓝箱统一从 `0x028C5E78` 以选择器 `0` 进入共享交互函数，并落入 `0x028C2770`；该路径没有任务 ID 或地图白名单。因此，对照包覆盖所有本来存在蓝色补给箱的任务，但不会向没有蓝箱的任务新增对象。

| Role / 作用 | Address | Original word | Replacement / 目标 |
| --- | --- | --- | --- |
| Blue object state load / 蓝箱对象状态读取 | `0x028c2770` | `0x819e0e30` | `lis r3, 0x1031` |
| Quest-global high / 原任务全局地址高位 | `0x028c2774` | `0x3d601008` | `lwz r3, 0x44a0(r3)` |
| Supply state value / 原补给状态值 | `0x028c2778` | `0x39000001` | `mr r4, r30` |
| Supply float state / 原补给浮点状态 | `0x028c277c` | `0xc00be204` | `li r5, 0` |
| Supply mode argument / 原补给模式参数 | `0x028c2780` | `0x38800000` | `bl 0x021f0a8c` |
| Supply state-byte store / 原补给状态字节写入 | `0x028c2784` | `0x990c0bae` | `b 0x028c27f8` |

```asm
0x028c2770 = lis r3, 0x1031
0x028c2774 = lwz r3, 0x44a0(r3)
0x028c2778 = mr r4, r30
0x028c277c = li r5, 0
0x028c2780 = bl 0x021f0a8c
0x028c2784 = b 0x028c27f8
```

The rewrite calls the gameplay-proven item-box initializer with current player `r30` and full mode `0`, then rejoins common cleanup at `0x028C27F8`. The red branch starts separately at `0x028C27B4`, so both packs write disjoint addresses. The control uses no code cave and does not touch resource words `0x021B0E90`/`0x021B0F14`, prompt IDs `14`/`15`, object registration, models, maps, quest data, WUA, RPX, MLC, or save data.

If blue opens the full menu, the initializer is viable inside quest UI context and the red failure is isolated to red object/action registration or state mapping. If blue also fails, further box-ID substitution is not justified; the next investigation must trace quest UI construction, owning state objects, and context dependencies. Until gameplay decides that control, this fourth pack remains default-off **Runtime Experimental / 运行时实验** and is not recommended for multiplayer.

## Runtime validation gate

No Cemu process was launched by the repository verification workflow. The lobby pack has separate user gameplay evidence and is `Runtime Verified`; the quest red-box pack still requires the exact manifest identity, Cemu version, title update, RPX SHA-256, module checksum, enabled-pack set, red/blue box results, exit/re-entry, and quest completion outcome. Do not test the Experimental quest pack in multiplayer. The 30 FPS pack is also experimental after unstable user testing.
