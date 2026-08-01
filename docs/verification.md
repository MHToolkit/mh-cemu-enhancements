# Local verification record (2026-08-01)

## Current static gates

1. `python3 -m unittest discover -s tests -v` — fourteen tests passed: manifest/schema validation, negative validation gates, the lobby resident-object accessor contract, RPX SHA-256 + PPC preimages/anchors, standard and isolated idempotent installation, exact Experimental selection/exclusion, isolated-profile inspection, isolated launch-command generation, legacy-path migration/uninstall, and reproducible asset-free archive construction.
2. `python3 scripts/mh-cemu-enhancements.py validate` — three manifests accepted.
3. `python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx <pinned MH3G_Cafe.rpx>` — accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and all declared PPC words.
4. Cemu's real PPCAssembler encodes `lwz r3, 0x00a8(r3)` as `0x806300a8`; the pack has no code cave or relocation. This static verification run did not start the Cemu app.
5. `ruff check scripts tests` and `git diff --check` passed.

## Runtime evidence and current standard-profile installation

The user confirmed that the 30 FPS switch took effect with the JP v96 title, so the FPS manifest is now `Runtime Verified`. The lobby runs established the opposite result for the branch, six-site substitution, full-home code-cave, and 3DS-informed `li r9, 0` candidates: the standard-profile Cemu log records JP v96, `Set vsync frequency to 30`, and `Applying patch group 'MH3G HD JP v96'`, but the restricted three-option menu remained. The dual-selector replacement was worse: Cemu 2.6 macOS logged `Codecave: 01800000-01800008` and resolved `lobby_full_box_entry`, then crashed before gameplay with `SIGBUS` / `EXC_BAD_ACCESS` at guest `0x017ffffc`; macOS identifies the triggering thread as `PPCRecompiler`. That code-cave candidate remains retracted and is not gameplay success.

Static follow-up corrected the temporary disassembly base from `0x02000000` to the RPX text section's actual `0x02000020`. It identified `sID::IDLobby` vtable entry `+0x4c` at `0x021baf70` as the resident-object accessor. The new candidate patches only `0x021baff4`, changing logical UI ID `0x17` from slot `+0xb4` (restricted selector `0x08`) to slot `+0xa8` (already-created complete-home selector `0x0e`). Slot `+0xc4` is the alternate restricted selector `0x07` and is not part of this return path. No code cave or branch is used.

After a zero-Cemu-process check, the installer restored the user's normal Cemu profile to the runtime-verified FPS pack only:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

The receipt contains the FPS pack tree hash. The Lobby `<Entry>` was removed and the Lock 30 FPS `<Entry>` restored in the same standard profile after the emulator exited. XML parsing and catalog inspection confirm that only FPS is installed and enabled. The quest experiment is neither installed nor enabled. The installer itself writes only that `graphicPacks/mh-cemu-enhancements` directory and never accesses MLC/save paths.

## Profile-path RCA (2026-07-30)

The initial isolated deployment was not loadable for two independently verified reasons: it had been placed at the outer root's `graphicPacks/` directory while the bundled Cemu source scans `<NEMESSIX_CEMU_DATA_ROOT>/data/graphicPacks/`; and the observed user launch used the standard macOS profile, where no `mh-cemu-enhancements` directory existed and `<GraphicPack/>` contained no entries. `inspect` and `isolated-launch-command` now make both states visible without launching Cemu or editing Cemu configuration. A receipted legacy isolated install migrates to the scanned `data/graphicPacks` location on reinstall and is also removed by uninstall.

## Outstanding runtime gate

The lobby and quest box packs are not `Runtime Verified`. The next lobby step is an isolated in-game run with only Lock 30 FPS and the new no-code-cave Lobby pack enabled. It must verify equipment, talismans, item deposit/withdrawal, combine/sell, closing and reopening the menu, and a clean title restart. Multiplayer validation is out of scope; the online recommendation remains the 30 FPS pack only.

## Distribution

`dist/mh-cemu-enhancements-0.1.7.zip` is deterministic, contains no game assets or tool cache, and is accompanied by its adjacent `.sha256` verification file.
