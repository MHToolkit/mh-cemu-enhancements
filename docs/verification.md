# Local verification record / 本地验证记录（2026-08-04）

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

The food pack changes the next native meal finalization only. After selecting presets, the user must eat again. Pre-meal preview may remain game-generated, and native incompatible combinations such as `0x41 + 0x1E` may apply only one effect.

猫饭包只改变下一次原生用餐结算；修改预设后必须重新吃饭。餐前预览可能仍是原版随机结果，`0x41 + 0x1E` 等原生互斥组合也可能只生效其中一项。

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
