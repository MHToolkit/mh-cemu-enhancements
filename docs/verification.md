# Local verification record / 本地验证记录（2026-08-01）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — 18 tests passed. The suite covers manifest/schema validation, catalog identities, negative fail-closed gates, the lobby mode contract, the blocked red-only quest contract, the revised all-quest blue selector-0 dispatch-bridge contract, refusal of the `runtime-blocked` red candidate, pinned RPX preimages/anchors, standard and isolated idempotent installation, explicit Experimental selection, profile inspection, legacy migration/uninstall, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — all four manifests accepted.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor.
4. Cemu 2.6's real `PPCAssembler` accepted all eight retained red-box instructions and all seven revised blue-control instructions without launching Cemu. The revised blue words are `60000000` (`nop` at `0x02219DF0`), `3c601031`, `806344a0`, `7fc4f378`, `38a00000`, `4b92e30d` (`bl 0x021F0A8C` from `0x028C2780`), and `48000074` (`b 0x028C27F8` from `0x028C2784`). The prior red branch words remain `38800000`, `38a0000e`, `3c601031`, `806344a0`, `7fc4f378`, `38a00000`, `4b92e2b9`, and `48000020`.
5. `ruff check scripts tests` and `git diff --check` passed.
6. Two independent `0.1.15` package builds produced identical SHA-256 values. The source archive retains all four catalog entries, including the blocked red negative-evidence directory and the revised blue experimental candidate, and contains no game asset or tool cache. The final digest is kept in the adjacent `.sha256` file to avoid embedding a self-referential archive hash in a packaged document.

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The current one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It is `Runtime Verified` while remaining default-off.
- **30 FPS：** User testing was unstable. The pack is downgraded to default-off `Runtime Experimental`; hunting behavior was not tested.
- **Quest red box / 任务红箱：** The first gameplay run showed a crossed prompt and no red-box interaction. Later runs proved both the eligibility-only revision and the red-local supply-prompt revision were loaded, but the red box still displayed the crossed unusable interaction. This is a recorded runtime failure, not a verified redirect; the candidate is now `runtime-blocked`.
- **Quest blue control / 任务蓝箱对照：** The first revision retained the native usable prompt, but pressing the interaction button produced no menu. Static follow-up showed that initializer `0x021F0A8C` only stores menu state while the per-frame path `0x0214E084 -> 0x02219D10 -> 0x0215165C` exits early outside hub scene-state `6`. The revised candidate removes only that early exit at `0x02219DF0`; it preserves the following manager-validity and busy-state guards, while state `6` in `0x0215165C` still routes to `0x021F0D08`. Static evidence and assembly verification pass, but whether the dispatcher can request the lobby resource during a quest is still **Gameplay Pending / 待实机验证**.

Earlier lobby selector/resource/code-cave/accessor attempts are retained only as negative research history. They either left the restricted menu unchanged or, for the code-cave candidate, crashed in the PPC recompiler. None is part of the current installed or packaged source.

## Installed standard profile / 已安装标准配置

The user's launch command supplies `-m` but no `NEMESSIX_CEMU_DATA_ROOT`, so Cemu scans the standard macOS profile rather than the isolated outer root. After two fresh zero-process checks, the installer wrote only:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

Installed and enabled / 已安装并启用：

- `MH3G HD JP v96 - Lobby Full Item Box`
- `MH3G HD JP v96 - Quest Blue Supply Box - Full Item Box (Control)`

Installed but disabled / 已安装但未启用：

- `MH3G HD JP v96 - Lock 30 FPS`

After a fresh zero-process check, the installer replaced only its receipted owned directory with the three selectable packs: Lobby, 30 FPS, and the revised blue dispatch bridge. It used the immutable reference RPX and recorded SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`. The blocked red directory is absent from the installed tree. `settings.xml` contains enabled entries only for Lobby and the revised blue candidate; 30 FPS remains installed without an enabled entry, and the red candidate has no entry. The pre-edit settings backup is:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/settings.xml.backup-mh3g-dispatch-bridge-20260801T143611Z
```

The backup SHA-256 is `f25be1ff360b19abccdfb040ea173ed023f749ce147326ded20d34760eb0e900`; the post-edit XML parses successfully and has SHA-256 `74326d8bdd41c7ba9149d3b20d8f8060dd5ef9feb7627b514ce711dda165f500`. Final read-only inspection reports Lobby installed/enabled, 30 FPS installed/disabled, red installed=false/enabled=false, and revised blue installed/enabled. The installed blue ASM matches the source with SHA-256 `61ec085abb34423a62a5afa6e87f4d6a462dfd325bd0b6ed432a8f3a81a94971`. No Cemu process was launched, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.15.zip` is deterministic, retains all four catalog entries as source evidence, contains no game asset or tool cache, and has adjacent SHA-256 file `dist/mh-cemu-enhancements-0.1.15.zip.sha256` containing the final digest. Runtime selection fails closed for the blocked red candidate; the revised blue candidate still requires explicit Experimental selection.
