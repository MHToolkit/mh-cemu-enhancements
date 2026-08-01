# Local verification record / 本地验证记录（2026-08-02）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — 19 tests passed. The suite covers five catalog identities, schema validation, fail-closed handling for all three quest candidates, the retained combined red+blue conditional-gate evidence, pinned RPX preimages/anchors, standard and isolated idempotent installation, explicit Experimental selection, inspection, migration/uninstall, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — all five manifests accepted.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor.
4. Cemu 2.6's real `PPCAssembler` accepted all fifteen fixed-address combined-pack instructions without launching Cemu or allocating a code cave:

```text
02219de0 800c0354 lwz r0, 0x354(r12)
02219de4 2c000006 cmpwi r0, 6
02219de8 41820010 beq 0x02219df8
02219dec 881f5350 lbz r0, 0x5350(r31)
02219df0 2c000006 cmpwi r0, 6
02219df4 40820078 bne 0x02219e6c
028c2770 3c601031 lis r3, 0x1031
028c2774 806344a0 lwz r3, 0x44a0(r3)
028c2778 7fc4f378 mr r4, r30
028c277c 38a00000 li r5, 0
028c2780 4b92e30d bl 0x021f0a8c
028c2784 48000074 b 0x028c27f8
028c5824 38800000 li r4, 0
028c5838 38a0000e li r5, 0xe
028c5e80 38800000 li r4, 0
```

5. The original helper at `0x021B7E08` was disassembled from the immutable RPX. Its body reads scene-object field `+0x14`, compares it with the request, returns a Boolean, and has no side effect. Because original `0x02219DDC` already loads the enclosing scene manager, direct `+0x354` is equivalent to the original `+0x340` object plus `+0x14` state field.
6. `ruff check scripts tests` and `git diff --check` passed.
7. Two independent `0.1.17` package builds produced identical SHA-256 values. The archive retains all five catalog entries, including all three runtime-blocked negative-evidence directories, and contains no game asset or tool cache. The final digest is kept in the adjacent `.sha256` file.

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It remains `Runtime Verified` and opt-in.
- **30 FPS：** User testing was unstable; hunting behavior was not tested. It remains default-off `Runtime Experimental`.
- **Old red candidate / 旧红箱候选：** Repeated gameplay retained a crossed unusable prompt despite verified eligibility, prompt-ID, and confirmation rewrites. It remains `runtime-blocked`.
- **Unconditional blue bridge / 无条件蓝箱桥：** The title initially loaded with only Lobby active. Later log entries proved that Cemu hot-applied the blue patch during the running title. Neither box opened the full menu, and the quest-board dialogue became blank. Since the six box-trigger instructions cannot run from the quest board, unconditional `0x02219DF0 = nop` is the direct cross-UI corruption source. The candidate is now `runtime-blocked`.
- **Combined conditional bridge / 红蓝统一条件桥：** Asynchronous GDB proved the box trigger, mode-0 initializer, direct handler, native scene-slot-6 helper `0x02141B8C`, virtual initializer `0x021BA8E8`, object setup, scene request, and next-frame update all execute. The quest scene then crashes at `0x0268AB84` after a lobby GUI layout lookup returns null. The remaining dependency is the missing lobby resource/lifecycle graph, not a box selector or state gate. The candidate is `runtime-blocked`.
- **Clean deployment acceptance / 清理后部署验收：** After reinstalling only Lobby plus the disabled 30 FPS files, the supplied Cemu build was launched with the user's exact `-m`/`-g` command. It loaded title `00050000-10104d00` v96 at the existing quest scene with normal HUD and no crash. Fresh `log.txt` contains only `Activate graphic pack: .../Lobby Full Item Box`; no FPS or quest patch group was active. The requested Cemu process was then closed cleanly. This validates the cleaned selection, not quest full-item-box behavior.

Earlier lobby selector/resource/code-cave/accessor attempts remain negative research history. The Cemu `.origin = codecave` candidate mapped to guest `0x01800000` and crashed in the PPC recompiler; the new combined pack contains no relocation or code cave.

## Installed standard profile / 已安装标准配置

The user's launch command supplies `-m` but no `NEMESSIX_CEMU_DATA_ROOT`, so Cemu scans the standard macOS profile. After confirming that the requested bundled Cemu process had exited, the installer wrote only the owned directory below. An unrelated `/Applications/Cemu.app` process was not terminated or modified.

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

Installed and enabled / 已安装并启用：

- `MH3G HD JP v96 - Lobby Full Item Box`

Installed but disabled / 已安装但未启用：

- `MH3G HD JP v96 - Lock 30 FPS`

Absent and disabled / 未安装且未启用：

- `MH3G HD JP v96 - Quest Red Delivery Box - Full Item Box (Experimental)`
- `MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)`
- `MH3G HD JP v96 - Quest Red & Blue Boxes - Full Item Box (Experimental)`

The installer used the immutable reference RPX and recorded SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`. Before removing the stale enabled entry for the retired combined pack, the settings backup was written to:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml.backup-mh3g-quest-retired-20260802T040901
```

The backup SHA-256 is `e5be1a062fd8f583acca32073991ceafb8e31f3e21831b46c2c43243d2d16f4a`; after clean launch/exit, the XML still parses, contains no quest-pack entry, and has SHA-256 `f25be1ff360b19abccdfb040ea173ed023f749ce147326ded20d34760eb0e900`. Receipt tree hashes are:

```text
Lobby      76225166f133acfa0ea11b8773a5f2d1fe2317c24529c01e54378fb221c33580
30 FPS     1bb04434c49729455ab155494689338f4894b7e0946f7f899bde7c437508a257
```

The static repository gates did not launch Cemu; the separate post-install acceptance launch is recorded above. No WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.17.zip` is deterministic, retains all five catalog entries as source evidence, contains no game asset or tool cache, and has an adjacent SHA-256 file. Runtime selection fails closed for all three quest candidates; only Lobby and the explicitly selected Experimental 30 FPS pack remain installable.
