# Runtime feedback correction / 实测反馈修正（2026-08-05）

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
