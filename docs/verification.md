# Local verification record / 本地验证记录（2026-08-01）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — 17 tests passed. The suite covers manifest/schema validation, four independent Cemu leaves, negative fail-closed gates, the lobby mode contract, the red-only quest contract, the all-quest blue selector-0 control contract, pinned RPX preimages/anchors, standard and isolated idempotent installation, explicit Experimental selection, profile inspection, legacy migration/uninstall, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — all four manifests accepted.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor.
4. Cemu 2.6's real `PPCAssembler` accepted all eight red-box instructions and all six new blue-control instructions without launching Cemu. The blue words are `3c601031`, `806344a0`, `7fc4f378`, `38a00000`, `4b92e30d` (`bl 0x021F0A8C` from `0x028C2780`), and `48000074` (`b 0x028C27F8` from `0x028C2784`). The prior red branch words remain `38800000`, `38a0000e`, `3c601031`, `806344a0`, `7fc4f378`, `38a00000`, `4b92e2b9`, and `48000020`.
5. `ruff check scripts tests` and `git diff --check` passed.
6. Two independent `0.1.13` package builds produced identical SHA-256 values. The archive has 29 files, includes all four packs, and contains no game asset or tool cache; the final post-documentation digest is kept in the adjacent `.sha256` file to avoid embedding a self-referential archive hash in a packaged document.

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The current one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It is `Runtime Verified` while remaining default-off.
- **30 FPS：** User testing was unstable. The pack is downgraded to default-off `Runtime Experimental`; hunting behavior was not tested.
- **Quest red box / 任务红箱：** The first gameplay run showed a crossed prompt and no red-box interaction. Later runs proved both the eligibility-only revision and the red-local supply-prompt revision were loaded, but the red box still displayed the crossed unusable interaction. This is a recorded runtime failure, not a verified redirect. The separate red pack remains installed for comparison and stays default-off `Runtime Experimental`.
- **Quest blue control / 任务蓝箱对照：** The fourth pack targets the selector-0 branch shared by every quest that already has a blue supply box. It is statically isolated from the red branch and remains default-off `Runtime Experimental / gameplay pending`. Blue success will isolate the red fault to object/action registration or state mapping; blue failure will redirect research to quest UI construction context.

Earlier lobby selector/resource/code-cave/accessor attempts are retained only as negative research history. They either left the restricted menu unchanged or, for the code-cave candidate, crashed in the PPC recompiler. None is part of the current installed or packaged source.

## Installed standard profile / 已安装标准配置

The user's launch command supplies `-m` but no `NEMESSIX_CEMU_DATA_ROOT`, so Cemu scans the standard macOS profile rather than the isolated outer root. After two fresh zero-process checks, the installer wrote only:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

Installed and enabled / 已安装并启用：

- `MH3G HD JP v96 - Lobby Full Item Box`
- `MH3G HD JP v96 - Quest Red Delivery Box - Full Item Box (Experimental)`
- `MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)`

Installed but disabled / 已安装但未启用：

- `MH3G HD JP v96 - Lock 30 FPS`

After fresh zero-process checks before installation and settings mutation, the installer deployed all four catalog packs. It preserved the existing Lobby/Red enabled states and the disabled 30 FPS state; one exact `GraphicPack/Entry` was then added to enable only the new blue control. Repository and installed blue ASM both have SHA-256 `b021fc787469709ce696a5641c19255d161d24da0868243ef8f82923f54d073d`. The receipt records all four pack IDs and reference RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`. The pre-edit settings backup is:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml.backup-mh3g-blue-box-20260801T202514
```

The backup SHA-256 is `91d1152275911cc15f09e37f13147de830f0337ff30abb06d29c6eecdc6e6a53`; the post-edit XML parses successfully and has SHA-256 `4d3358a3b6011e558bc5da64310147a7de066d3dca2013cb0332bf50a7b1ba0a`. Final read-only inspection reports all four packs installed, Lobby/Red/Blue enabled, and 30 FPS disabled. No Cemu process was launched, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.13.zip` is deterministic, contains all four catalog packs and no game asset or tool cache, and has adjacent SHA-256 file `dist/mh-cemu-enhancements-0.1.13.zip.sha256` containing the final digest.
