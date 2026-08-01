# Local verification record / 本地验证记录（2026-08-01）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — 16 tests passed. The suite covers manifest/schema validation, independent Cemu leaves, negative fail-closed gates, the lobby mode contract, the red-only quest control-flow contract, pinned RPX preimages/anchors, standard and isolated idempotent installation, explicit Experimental selection, profile inspection, legacy migration/uninstall, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — all three manifests accepted.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor.
4. Cemu 2.6's real `PPCAssembler` accepted all eight red-box instructions without launching Cemu. The six direct words are `38800000` (red eligibility uses supply selector), `38a0000e` (red-local prompt uses supply selector 14), `3c601031`, `806344a0`, `7fc4f378`, and `38a00000`; branch relocations resolve to `4b92e2b9` (`bl 0x021F0A8C`) and `48000020` (`b 0x028C27F8`).
5. `ruff check scripts tests` and `git diff --check` passed.
6. Two independent package builds produced the same SHA-256; the current value is recorded in the adjacent distribution `.sha256` file.

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The current one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It is `Runtime Verified` while remaining default-off.
- **30 FPS：** User testing was unstable. The pack is downgraded to default-off `Runtime Experimental`; hunting behavior was not tested.
- **Quest red box / 任务红箱：** The first gameplay run showed a crossed prompt and no red-box interaction. The second run proved that the eligibility-only revision was loaded but still displayed the cross. Static tracing now separates the two inputs: `0x028C5824` controls whether red registers a prompt, while `0x028C5838` supplies delivery prompt selector `15`; `0x020F060C` resolves that selector only to prompt visual/text and does not retain it as the confirmation action. The new candidate locally uses supply selector `14` at the red call site while retaining the red-only full-box callback. It remains default-off `Runtime Experimental` until a new gameplay run covers the red box opening the full menu, the blue supply box retaining its original menu, closing/reopening, and quest completion.

Earlier lobby selector/resource/code-cave/accessor attempts are retained only as negative research history. They either left the restricted menu unchanged or, for the code-cave candidate, crashed in the PPC recompiler. None is part of the current installed or packaged source.

## Installed standard profile / 已安装标准配置

The user's launch command supplies `-m` but no `NEMESSIX_CEMU_DATA_ROOT`, so Cemu scans the standard macOS profile rather than the isolated outer root. After two fresh zero-process checks, the installer wrote only:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

Installed and enabled:

- `MH3G HD JP v96 - Lobby Full Item Box`
- `MH3G HD JP v96 - Quest Red Delivery Box - Full Item Box (Experimental)`

The unstable 30 FPS pack is not installed and is not enabled. The installed eligibility-only red-box patch has SHA-256 `2adfe52d19c47e625640da9c6b638f07a4da3c9dc06a86f4ab97bd9beb50c227` and was rejected by the second gameplay run. The new repository candidate has SHA-256 `a377c2047623494c7bf9fab67d5a3eefc6860b0add9a74cca779c04a497a8dac`; it has deliberately not replaced the installed file while Cemu is running. The installed Lobby patch remains SHA-256 `86acd8733dab5aa5ccccc1cf767055a61751da8b7426aaa28502a30849a647e5`. A pre-edit settings backup exists at:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml.backup-mh3g-red-box-20260801T170000
```

No Cemu process was launched, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.12.zip` is deterministic, contains no game asset or tool cache, and has an adjacent `.sha256` verification file containing the final digest.
