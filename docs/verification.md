# #13 full underwater-dispatch displacement candidate / #13 水下分派器完整位移候选（2026-08-07，0.1.21）

## Superseding runtime verdict / 覆盖性实测结论

The 0.1.20 candidate also did **not** pass the intended gameplay acceptance. In a same-route comparison, the underwater action presentation looked accelerated, but the character did not cover clearly more actual distance. This is a real negative runtime result, not an installation failure: the isolated profile loaded the exact JP-v96 title and the refreshed #13 pack, and the user compared movement in gameplay.

0.1.20 候选同样**没有通过目标功能验收**：同路线对照时能看到水下动作表现加速，但角色实际经过的距离没有明显增加。这是有效的运行时负向结果，不是安装失败；隔离配置确实载入了 JP v96 与当时最新的 #13 包，用户也已在游戏内完成移动对照。

因此，0.1.20 中“状态 6/7 的三条坐标积分已改为 1.0”只能保留为静态事实，不能再表述为“水下整体位移已经加倍”。当前 0.1.21 仍是新的 **Runtime Experimental** 候选，不是修复成功声明。

## RCA and expanded correction / 根因与扩展修正

1. The original 3DS entry forces effect ID `0xC7` and changes the `1.05/1.10` scalars corresponding to PPC field `state + 0x608`. PPC function `0x028A10F8..0x028A1190` loads that field at `0x028A1118` and copies it to eight animation slots at `+0x2AC`. This directly explains why the action presentation accelerates; it is not evidence that world displacement increased.
2. The PPC action dispatcher at `0x028CA170` reads the state ID from `state + 0x40` and dispatches 40 action states. The 0.1.20 correction touched only the three direct coordinate integrations in handler `0x028C7244` for states 6/7 (`0x028C7654`, `0x028C76DC`, `0x028C7744`). The negative route comparison shows that covering only this branch family is insufficient for ordinary swimming.
3. Static enumeration of that same dispatcher found four additional direct integrations that load `0.5` from pinned RPX constant `0x1007E224`, multiply the frame/action scalar, and write the resulting vector into `state + 0xE0/+0xE4/+0xE8`:
   - states 2/14: `0x028C6BDC`
   - states 16/17: `0x028C8C34`
   - state 29, two branches: `0x028C9BDC`, `0x028C9C9C`
4. 0.1.21 redirects those four loads plus the existing three state-6/7 loads to pinned `1.0` at `0x1007E1F4`. It therefore covers all seven direct `0.5 -> coordinate write-back` paths inside this 40-state dispatcher, while deliberately not touching similar-looking sites outside the dispatcher.
5. Which one of states 2/14, 16/17, or 29 was used by the user's ordinary-swim route is an inference until a live state trace is recorded. The expanded coverage is statically complete for this dispatcher, but gameplay timing and side-effect checks remain mandatory.

3DS 原项对 `0xC7` 与 `1.05/1.10` 的修改在 PPC 侧落到 `state + 0x608`；`0x028A1118` 会把该字段复制到八个动画槽，因此“动作加速”有明确数据流证据，但它不等于世界坐标位移加速。0.1.20 只修改了 40 状态动作分派器中状态 6/7 的三条坐标积分，覆盖面不足。0.1.21 补上状态 2/14、16/17、29 的另外四条直接积分，使该分派器内全部七条 `0.5 -> 坐标写回` 路径统一改为 `1.0`；分派器外的相似位置保持不动，以避免盲目扩大影响面。普通游泳实测具体经过哪一个新增状态，在拿到 live trace 前仍属于推断。

## Required gameplay acceptance / 必须完成的实机验收

- Disable #13 for the baseline, then enable only #13 for the candidate; keep #65 and every other static cheat disabled. / 基线关闭 #13，候选只启用 #13；#65 与其他静态金手指全部关闭。
- Keep FPS cap, weapon, full-stick magnitude, camera/direction, action, and start/end markers identical. / 固定 FPS、武器、满幅摇杆、镜头/方向、动作与起终点标记。
- Time the same underwater route at least three times in each mode and compare median elapsed time; animation appearance is not an acceptance metric. / 两种模式对同一路线各计时至少三次并比较中位耗时；动画观感不作为通过标准。
- Separately check ordinary forward swimming, dash, turning, ascent/descent, evasion, wall collision, stopping, and input recovery for overshoot or lock-up. / 另查普通前游、冲刺、转向、上浮/下潜、闪避、撞墙、停止与输入恢复是否过冲或锁死。

## 0.1.21 static and isolated-install gates / 0.1.21 静态与隔离安装门禁

1. `pytest tests/ -q` passes **29/29** executed tests; one optional immutable-reference test is skipped because its historical default fixture path is absent. The equivalent reference gate was run explicitly against the active extracted RPX.
2. `validate` accepts all **50** manifests. `verify-reference` accepts JP-v96 RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared preimage/anchor, including the four new words `C18AE224`, `C009E224`, `C1A9E224`, and `C1A9E224`.
3. Cemu's real `PPCAssembler` assembles all seven displacement instructions with zero relocations: `C18AE1F4`, `C18BE1F4` x3, `C009E1F4`, and `C1A9E1F4` x2.
4. Ruff and `git diff --check` pass. The static mapping ledger now totals **176** PPC writes; #13 contains **20** writes/preimages, of which seven are direct displacement integrations.
5. With no Cemu game process running, only #13 was refreshed in the isolated underwater-test profile. Inspection reports `installed=true` and preserves `enabled=true`. Repository and installed pack tree hashes both equal `bae8abb9e5d5f6cce880e64a4f6a7c195c3fb0dd554102a2e1f30e8085f79a12`.
6. The isolated `settings.xml` SHA-256 remains `229e0e06225027d07b2e1077596011445cb5f477d85835c7cfbb98631b8506ac`; no save/MLC path was modified, and no Cemu process was launched by this verification.
7. Two independent 0.1.21 package builds are byte-identical; the final archive digest is recorded in `dist/mh-cemu-enhancements-0.1.21.zip.sha256`.

These gates prove exact-binary targeting, assembler validity, dispatcher coverage, and installation integrity only. They do not prove that actual underwater travel is now 2x; the pack remains **Runtime Experimental / Gameplay Pending** until the timed gameplay comparison passes.

以上门禁只证明目标二进制、汇编器编码、分派器覆盖与安装完整性，**不证明实际水下路程已经达到 2 倍**。只有计时实测通过后，才能升级运行时结论。

# Runtime feedback correction / 实测反馈修正（2026-08-06，0.1.19）

## Root-cause result / 根因结论

1. **猫饭技能自定义 / Custom Felyne Food Skills:** the source ID is correct (`0x41 = 招财猫的厄运 / Unlucky Cat`), but the old patch replaced only the downstream mirror loop at `0x021D8740..0x021D8764`. Native temporary slots `r31 + 0x68/0x6A/0x6C` could therefore remain random and diverge from later meal processing/display. The corrected patch writes those three source slots after generator call `0x021D8658`, branches to native post-processing at `0x021D86B4`, and preserves the complete native menu/runtime mirror loop. This is a static/data-flow correction and still requires a real meal retest.
2. **#13/#21/#34/#50/#60:** re-disassembly with the correct RPX `.text` base `0x02000020` confirmed their effect IDs, call sites, branch consumers, and declared preimages. No replacement-address defect was found. The saved test profile enabled almost every static pack, including #65; #65 forces the normal-mode generic skill-slot comparison true and prevents a clean on/off comparison for these skill-based effects. #59 independently masks #60's collection timing.

猫饭源编号无误（`0x41 = 招财猫的厄运`），问题在首版补丁的数据流：只改最终镜像循环，没有先统一原生临时源槽。修正版改为写入 `r31 + 0x68/0x6A/0x6C`，再交回原生后处理和最终镜像循环。五个静态包没有发现地址或 PPC 指令错误；之前几乎全开的配置中，#65 会让通用技能查询恒真，#59 还会单独掩盖 #60，因此该次结果不能判定这五项不生效。

## Isolated retest / 隔离复测

Every comparison starts with all other static packs disabled. In particular, disable #65 for #13/#21/#34/#50/#60 and also disable #59 for #60. Keep the FPS cap identical between baseline and enabled runs.

每项都必须在其余静态包关闭的条件下单独对照；#13/#21/#34/#50/#60 一律关闭 #65，#60 还要关闭 #59。基线与启用后的 FPS 设置必须完全相同。

| Target / 项目 | Required comparison / 必须对照方式 |
| --- | --- |
| #13 水下速度 2 倍 | Same underwater route, action, start/end points, and FPS; record elapsed time rather than visual impression. / 固定同一路线、动作、起终点和 FPS，记录耗时。 |
| #21 回避距离 UP | Same weapon, flat start point, camera/direction, and one full roll; compare endpoints. / 固定武器、平地起点、镜头方向，比较一次完整翻滚终点。 |
| #34 防御强化 | Shielded weapon against a normally unblockable attack; an ordinary block proves nothing. / 用带盾武器格挡原本不可防御的攻击；普通攻击无验证价值。 |
| #50 弩无摇晃 | Bowgun with built-in left/right deviation, same ammo and long-range target; this is deviation, not #49 recoil. / 使用自带左右偏移的弩、相同弹药和远距离目标；该项不是 #49 后坐力。 |
| #60 高速收集 | Only #60 enabled, #59/#65 disabled; time a complete cycle at the same gathering point. / 只启用 #60，关闭 #59/#65，对同一采集点完整循环计时。 |
| 猫饭 / Felyne | Enable the pack, select `41/00/00`, fully restart/reload the title, eat a new meal, then check the post-meal result for `招财猫的厄运`; pre-meal preview may remain random. / 启用包并选 `41/00/00`，完整重启或重载标题后重新吃饭，用餐后核对“招财猫的厄运”；餐前预览仍可能随机。 |

## 2026-08-06 static and install gates / 静态与安装门禁

1. `pytest tests/ -q` passes **29/29** tests; `validate` accepts all **50** manifests.
2. The pinned JP-v96 RPX SHA-256 is `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`; every declared preimage and anchor passes against that immutable file.
3. Cemu's real `PPCAssembler` accepts the corrected seven-instruction Felyne block. With defaults `06/36/00`, the words are `38000006`, `B01F0068`, `38000036`, `B01F006A`, `38000000`, `B01F006C`, and `48000040`; the three selectors use `U32_MASKED_IMM` relocations and the final branch uses `BRANCH_S26`.
4. Ruff and `git diff --check` pass.
5. With no Cemu process running, the installer refreshes exactly **47 available packs** at `/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements`; all 47 installed tree hashes match their repository sources.
6. The receipt binds the install to the pinned RPX. `settings.xml` remains valid XML and its SHA-256 stays `90aff50f44231d06ae33f799e1136a0929da394958547259864216e5b1947a3f`; saved enable states are not edited.
7. Two independent `0.1.19` package builds are byte-identical; the final archive digest is stored in its adjacent `.sha256` sidecar.

These gates prove static correction and installation integrity only. The five subtle effects and the corrected Felyne meal path remain `Runtime Experimental / Gameplay Pending` until the isolated gameplay tests above pass.

以上门禁只证明静态修正与安装完整性。五个细微效果及修正版猫饭流程仍为 `Runtime Experimental / Gameplay Pending`，必须通过上面的隔离实测后才能升级结论。

# Runtime feedback correction / 实测反馈修正（2026-08-05，0.1.18 历史记录）

## Confirmed defects / 已确认缺陷

1. **#07 HP 无限 / Infinite HP**: the previous PPC conversion suppressed the normal write at `0x02865FF8` but left the lethal zero-clamp at `0x02866004`. This exactly explains surviving ordinary damage but dying to overkill damage. The corrected pack suppresses both writes. This PPC behavior is intentionally stronger than the source 3DS one-instruction patch; overkill survival on 3DS remains unverified.
2. **#65 战斗体验改善器 / Combat Experience Enhancer**: ARM `0x008A68BC` is in the normal-game-mode skill-slot branch. The previous PPC conversion incorrectly patched the special-mode branch at `0x02890AE4`; the corrected address is the normal branch at `0x02890B14`.
3. **猫饭技能自定义 / Custom Felyne Food Skills**: the latest `settings.xml` and `log.txt` showed that the pack was disabled and not loaded. Cemu resolves Graphic Pack variables while loading the title. After selecting and enabling presets, restart or reload the title, then eat a new meal; changing presets during a running title is not a valid test.

## Feedback classification / 反馈分类

| # | Feedback / 反馈 | Static conclusion / 静态结论 | Isolated retest / 隔离复测 |
| ---: | --- | --- | --- |
| 13 | 水下速度 2 倍不明显 | Eleven effect-ID checks plus the 1.05/1.10 to 2.0 scalar routes remain mapped correctly. / 11 条效果检查与两条倍率路径映射仍正确。 | Keep the same FPS/action and time the same underwater route. / 保持相同 FPS 与动作，对同一路线计时。 |
| 21 | 回距 UP 不明显 | All nine JP-v96 checks for effect ID `0xB8` are covered. / 已覆盖 `0xB8` 的 9 条检查。 | Use a fixed weapon, start point, and direction; compare one roll endpoint. / 固定武器、起点、方向并比较翻滚终点。 |
| 29 | 电阻弹可用 | User gameplay confirmed the intended availability behavior. / 用户已确认预期可用性行为。 | No corrective change. / 无需修正。 |
| 34 | 防强不明显 | Both JP-v96 checks for effect ID `0x25` are covered. / 已覆盖 `0x25` 的两条检查。 | Use a shielded weapon against a normally unblockable attack; ordinary blocks do not test Guard Up. / 用带盾武器格挡原本不可防御攻击。 |
| 35 | 燃鳞不明显 | Three ARM paths fold into one shared PPC check for effect ID `0xCF`; the mapping is structurally consistent. / 三条 ARM 路径在 PPC 合并为 `0xCF` 公共检查。 | Observe small-monster behavior in the same area, not a visible stat or large-monster aura. / 观察同区小怪行为。 |
| 44 | 对煌黑龙吹倒无效 | All three ordinary high-wind checks matching the 3DS source are covered. Special/scripted knockback may bypass them. / 与 3DS 源相同的三条普通大风压检查均已覆盖，特殊吹飞可能绕过。 | Test ordinary large wind pressure separately; Alatreon alone is not a mapping verdict. / 另测普通大风压。 |
| 48 | 未测 | No new failure evidence. / 暂无失败证据。 | Test invulnerability timing separately from #21 distance. / 与 #21 位移分开测试无敌帧。 |
| 50 | 弩无摇晃不明显 | Both JP-v96 checks for effect ID `0xAE` are covered. / 已覆盖 `0xAE` 的两条检查。 | Use a bowgun with built-in left/right deviation and compare long-range trajectories; this is not recoil. / 使用自带左右偏移的弩远距离对比弹道。 |
| 60 | 高速收集不明显 | All 18 JP-v96 checks for effect ID `0x8D` are covered. / 已覆盖 `0x8D` 的 18 条检查。 | Disable #59 and time a full cycle at the same gathering point. / 关闭 #59 后对同一采集点完整循环计时。 |

The reported run enabled almost every static pack at once, including both #59/#60 and #6/#72. Cemu logged every selected pack as applied and no patch parser errors, but that combined run cannot isolate subtle effects. After the corrections above, all packs remain `Runtime Experimental / Gameplay Pending` until a focused gameplay retest is recorded.

该次反馈运行几乎同时启用了全部静态包，包括 #59/#60 与 #6/#72。Cemu 日志显示所选包均已应用且没有补丁解析错误，但该组合无法隔离判断细微效果。本轮修正后，各项仍保持 `Runtime Experimental / Gameplay Pending`，等待逐项实测。

## 2026-08-05 static and install gates / 静态与安装门禁

1. `pytest tests/ -q` passed **27/27** tests; `validate` accepted all **50** manifests.
2. The pinned JP-v96 RPX passed every declared preimage and anchor check.
3. Cemu's real `PPCAssembler` encoded the corrected instructions as `02865FF8 -> 60000000`, `02866004 -> 60000000`, and `02890B14 -> 7C084040`.
4. Ruff and `git diff --check` passed.
5. With no Cemu process running, the installer refreshed the same **47-pack** receipt at `/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements`.
6. Installed #07, #65, and Felyne-food trees exactly match their source trees. `settings.xml` remained valid XML and its SHA-256 stayed `90aff50f44231d06ae33f799e1136a0929da394958547259864216e5b1947a3f`; saved enable states were not edited.
7. Two independent `0.1.18` builds were byte-identical; the final archive digest is stored in its adjacent `.sha256` sidecar.

# Local verification record / 本地验证记录（2026-08-04，0.1.17）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — **25/25 tests passed**. Coverage includes 50 catalog manifests, 43 independent static ARM conversions, the 44-FPS control conversion, the three-slot Felyne-food contract, fail-closed quest candidates, pinned RPX assertions, idempotent standard/isolated installation, inspection, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — **50 manifests accepted**, of which 47 are available leaves and three quest-box research candidates are `runtime-blocked`.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor, including all ten Felyne-food overwrite words.
4. The Felyne-food rules contract contains exactly three categories and exactly 66 bilingual values (`0x00..0x41`) per category. Defaults inside the disabled pack are `0x06/0x36/0x00`.
5. Cemu 2.6's real `PPCAssembler` accepted all ten fixed-address instructions and produced the expected default words. The three `$skill*` expressions produced `U32_MASKED_IMM` relocations over the 16-bit immediate field, matching Graphic Pack variable resolution:

```text
021d8740 817f0140 lwz r11, 0x140(r31)
021d8744 38000006 li r0, $skill1
021d8748 b01b000a sth r0, 0x000a(r27)
021d874c b00b0e3e sth r0, 0x0e3e(r11)
021d8750 38000036 li r0, $skill2
021d8754 b01b000c sth r0, 0x000c(r27)
021d8758 b00b0e40 sth r0, 0x0e40(r11)
021d875c 38000000 li r0, $skill3
021d8760 b01b000e sth r0, 0x000e(r27)
021d8764 b00b0e42 sth r0, 0x0e42(r11)
```

6. `ruff check scripts tests` and `git diff --check` passed.
7. Two independent `0.1.17` package builds were byte-identical. The archive contains the complete catalog and no RPX, WUA, save, MLC, Cemu binary, game asset, `.idea`, or tool cache; the final SHA-256 is stored in the adjacent sidecar.

These gates establish static correctness and installation integrity only. They do not promote a pack to `Runtime Verified` without gameplay evidence.

以上门槛只证明静态正确性与安装完整性；没有游戏内证据时，不得把包升级为 `Runtime Verified`。

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It remains opt-in `Runtime Verified`.
- **30 FPS：** User testing was unstable; hunting behavior was not completed. It remains default-off `Runtime Experimental`.
- **Quest boxes / 任务箱：** Red stayed crossed; blue and later combined candidates either opened no menu, caused crashes/stuck input, or damaged unrelated quest UI. All three candidates are retained as negative research evidence and are `runtime-blocked`.
- **43 static conversions / 43 项静态转换：** Static mapping and installation tooling pass; gameplay is still pending for each independent default-off pack.
- **Custom Felyne Food Skills / 猫饭技能自定义：** ARM/PPC semantic mapping, rules, preimages, real assembler, and installation pass. No real meal/quest-effect test exists yet, so it remains **Runtime Experimental / Gameplay Pending**.

The food pack changes the next native meal finalization only. Cemu resolves Graphic Pack parameters when loading the title, so after selecting presets the user must restart or reload the title and then eat again. Pre-meal preview may remain game-generated, and native incompatible combinations such as `0x41 + 0x1E` may apply only one effect.

猫饭包只改变下一次原生用餐结算。Cemu 在标题加载时解析 Graphic Pack 参数，因此修改预设后必须重启或重新载入游戏，再重新吃饭。餐前预览可能仍是原版随机结果，`0x41 + 0x1E` 等原生互斥组合也可能只生效其中一项。

## Installed isolated profile / 已安装隔离配置

After confirming zero Cemu processes, the installer wrote only its owned directory:

```text
/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/.build/nemessix-bundled-cemu-runtime-proof-20260721/home/Library/Application Support/Nemessix Dev/cemu/data/graphicPacks/mh-cemu-enhancements/
```

The receipt contains exactly:

```text
mh3g-hd-jp-v96-lobby-full-item-box
mh3g-hd-jp-v96-fps-lock-30
mh3g-hd-jp-v96-custom-felyne-food-skills
```

The installer intentionally did not edit `config/settings.xml`. Its existing saved states were preserved and the XML parses successfully:

| Pack | Installed | Saved enabled state |
| --- | --- | --- |
| Lobby Full Item Box | yes | enabled |
| Lock 30 FPS | yes | enabled |
| Custom Felyne Food Skills | yes | disabled |
| Lock 44 FPS | no | disabled |
| All three quest-box candidates | no | disabled |

Receipt tree hashes:

```text
Lobby       76225166f133acfa0ea11b8773a5f2d1fe2317c24529c01e54378fb221c33580
30 FPS      c9b1b6639576486560ecfc7c9ea94ad183ba75d4e12a5cf12b6af7444e18a42d
Felyne food 15bdce2c9c8f61907a381d7d5b166d8e5c87a725c15106143ceb9011bb304246
```

The installed Felyne-food tree equals the source tree. Per-file SHA-256 values match source and destination:

```text
manifest.json                         0e37d063d266882e3bbae5338a90cc50b8e90d366423f24fd6048fc3a3ed287f
rules.txt                             294ac52965496822a986242cc294755cf5a1459ffba25fb12a2585dc0108c76a
patch_custom_felyne_food_skills.asm   499ba021caf506aceacf71b0855f5f21bd5fcdf6b85eb9b2d4363239a4fa75ef
```

No Cemu process was launched, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.17.zip` is the deterministic distribution archive; `dist/mh-cemu-enhancements-0.1.17.zip.sha256` is its adjacent digest. The Felyne-food pack requires explicit selection plus `--include-experimental`; it is not auto-installed merely because experimental packs are allowed.
