# Local verification record / 本地验证记录（2026-08-02）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — 19 tests passed. The suite covers five catalog identities, schema validation, fail-closed legacy quest candidates, the combined red+blue conditional-gate contract, pinned RPX preimages/anchors, standard and isolated idempotent installation, explicit Experimental selection, inspection, migration/uninstall, and reproducible asset-free packaging.
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
7. Two independent `0.1.16` package builds produced identical SHA-256 values. The archive retains all five catalog entries, including both runtime-blocked negative-evidence directories, and contains no game asset or tool cache. The final digest is kept in the adjacent `.sha256` file.

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It remains `Runtime Verified` and opt-in.
- **30 FPS：** User testing was unstable; hunting behavior was not tested. It remains default-off `Runtime Experimental`.
- **Old red candidate / 旧红箱候选：** Repeated gameplay retained a crossed unusable prompt despite verified eligibility, prompt-ID, and confirmation rewrites. It remains `runtime-blocked`.
- **Unconditional blue bridge / 无条件蓝箱桥：** The title initially loaded with only Lobby active. Later log entries proved that Cemu hot-applied the blue patch during the running title. Neither box opened the full menu, and the quest-board dialogue became blank. Since the six box-trigger instructions cannot run from the quest board, unconditional `0x02219DF0 = nop` is the direct cross-UI corruption source. The candidate is now `runtime-blocked`.
- **Combined conditional bridge / 红蓝统一条件桥：** Static, assembler, install, and configuration evidence pass. It converts red prompt/dispatch semantics to the shared blue path, sends both boxes to mode `0`, and dispatches outside the hub only when global UI state is exactly full-item-box state `6`. It is **Gameplay Pending / 待实机验证**, not `Runtime Verified`.

Earlier lobby selector/resource/code-cave/accessor attempts remain negative research history. The Cemu `.origin = codecave` candidate mapped to guest `0x01800000` and crashed in the PPC recompiler; the new combined pack contains no relocation or code cave.

## Installed standard profile / 已安装标准配置

The user's launch command supplies `-m` but no `NEMESSIX_CEMU_DATA_ROOT`, so Cemu scans the standard macOS profile. After confirming zero Cemu processes, the installer wrote only:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

Installed and enabled / 已安装并启用：

- `MH3G HD JP v96 - Lobby Full Item Box`
- `MH3G HD JP v96 - Quest Red & Blue Boxes - Full Item Box (Experimental)`

Installed but disabled / 已安装但未启用：

- `MH3G HD JP v96 - Lock 30 FPS`

Absent and disabled / 未安装且未启用：

- `MH3G HD JP v96 - Quest Red Delivery Box - Full Item Box (Experimental)`
- `MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)`

The installer used the immutable reference RPX and recorded SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`. The pre-edit settings backup is:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml.backup-mh3g-combined-conditional-20260801T183643Z
```

The backup SHA-256 is `b716b1c4549e91bbdea2c6d7c0bffc20b2e2a7c0ace5182043258261d02efed6`; the post-edit XML parses successfully and has SHA-256 `3504dc3a6d63c5e75d0e47719de806b80e8aaca648a07eb8c493916176e6bc78`. The installed combined ASM matches its source with SHA-256 `5b17b4784261ad558b074ca2066af29990a7a1f245b1772856255a8eef47583e`. Receipt tree hashes are:

```text
Lobby      76225166f133acfa0ea11b8773a5f2d1fe2317c24529c01e54378fb221c33580
30 FPS     1bb04434c49729455ab155494689338f4894b7e0946f7f899bde7c437508a257
Combined   c9e6052708bed8bdd684bfa757afe52f17b33e1fe274def1a1bc6bd378f4d95d
```

No Cemu process was launched by the repository workflow, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.16.zip` is deterministic, retains all five catalog entries as source evidence, contains no game asset or tool cache, and has adjacent SHA-256 file `dist/mh-cemu-enhancements-0.1.16.zip.sha256`. Runtime selection fails closed for both older quest candidates; the combined conditional bridge requires explicit Experimental selection.
