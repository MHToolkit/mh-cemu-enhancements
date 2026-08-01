# Local verification record / 本地验证记录（2026-08-01）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — 16 tests passed. The suite covers manifest/schema validation, independent Cemu leaves, negative fail-closed gates, the lobby mode contract, the red-only quest control-flow contract, pinned RPX preimages/anchors, standard and isolated idempotent installation, explicit Experimental selection, profile inspection, legacy migration/uninstall, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — all three manifests accepted.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor.
4. Cemu 2.6's real `PPCAssembler` accepted all seven red-box instructions without launching Cemu. The five direct words are `38800000` (red eligibility uses supply selector), `3c601031`, `806344a0`, `7fc4f378`, and `38a00000`; branch relocations resolve to `4b92e2b9` (`bl 0x021F0A8C`) and `48000020` (`b 0x028C27F8`).
5. `ruff check scripts tests` and `git diff --check` passed.
6. Two independent package builds produced the same SHA-256; the current value is recorded in the adjacent distribution `.sha256` file.

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The current one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It is `Runtime Verified` while remaining default-off.
- **30 FPS：** User testing was unstable. The pack is downgraded to default-off `Runtime Experimental`; hunting behavior was not tested.
- **Quest red box / 任务红箱：** The first gameplay run showed a crossed prompt and no red-box interaction. Static backward tracing identified the earlier delivery-only eligibility selector at `0x028C5824`; the new candidate changes only that selector to supply semantics while retaining red interaction ID `15` and the red-only full-box callback. The revised candidate remains default-off `Runtime Experimental` until a new gameplay run covers the red box opening the full menu, the blue supply box retaining its original menu, closing/reopening, and quest completion.

Earlier lobby selector/resource/code-cave/accessor attempts are retained only as negative research history. They either left the restricted menu unchanged or, for the code-cave candidate, crashed in the PPC recompiler. None is part of the current installed or packaged source.

## Installed standard profile / 已安装标准配置

The user's launch command supplies `-m` but no `NEMESSIX_CEMU_DATA_ROOT`, so Cemu scans the standard macOS profile rather than the isolated outer root. After two fresh zero-process checks, the installer wrote only:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

Installed and enabled:

- `MH3G HD JP v96 - Lobby Full Item Box`
- `MH3G HD JP v96 - Quest Red Delivery Box - Full Item Box (Experimental)`

The unstable 30 FPS pack is not installed and is not enabled. XML parsing plus catalog `inspect` confirm both installed box packs are enabled. The currently installed first red-box candidate has SHA-256 `5cd41f7973d1b0c92a6a57d5f1347952db36a899498953ec8182f212f3f8c972`; it is superseded by repository source `2adfe52d19c47e625640da9c6b638f07a4da3c9dc06a86f4ab97bd9beb50c227` and must not be replaced until Cemu is fully exited. A pre-edit settings backup exists at:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml.backup-mh3g-red-box-20260801T170000
```

No Cemu process was launched, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.11.zip` is deterministic, contains no game asset or tool cache, and has an adjacent `.sha256` verification file containing the final digest.
