# Local verification record (2026-08-01)

## Current static gates

1. `python3 -m unittest discover -s tests -v` — fifteen tests passed: manifest/schema validation, independent Cemu tree paths, negative validation gates, the lobby restricted-mode contract, RPX SHA-256 + PPC preimages/anchors, standard and isolated idempotent installation, exact Experimental selection/exclusion, isolated-profile inspection, isolated launch-command generation, legacy-path migration/uninstall, and reproducible asset-free archive construction.
2. `python3 scripts/mh-cemu-enhancements.py validate` — three manifests accepted.
3. `python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx <pinned MH3G_Cafe.rpx>` — accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and all declared PPC words.
4. Cemu's real PPCAssembler encodes `li r5, 0` as `0x38a00000`; the pack has no code cave or relocation. This static verification run did not start the Cemu app.
5. `ruff check scripts tests` and `git diff --check` passed.

## Runtime evidence and current standard-profile installation

The user confirmed that the 30 FPS switch took effect with the JP v96 title, so the FPS manifest is now `Runtime Verified`. The lobby runs established the opposite result for the branch, six-site substitution, full-home code-cave, and 3DS-informed `li r9, 0` candidates: the standard-profile Cemu log records JP v96, `Set vsync frequency to 30`, and `Applying patch group 'MH3G HD JP v96'`, but the restricted three-option menu remained. The dual-selector replacement was worse: Cemu 2.6 macOS logged `Codecave: 01800000-01800008` and resolved `lobby_full_box_entry`, then crashed before gameplay with `SIGBUS` / `EXC_BAD_ACCESS` at guest `0x017ffffc`; macOS identifies the triggering thread as `PPCRecompiler`. That code-cave candidate remains retracted and is not gameplay success.

The later accessor candidate also failed in gameplay: the live log proved the Lobby leaf was enabled and applied, but the screenshot still showed the restricted three-option menu. Cross-architecture follow-up decompressed the complete 3DS `.code` to the pinned expected SHA-256, mapped ARM initializer `0x005DEC70` to PPC initializer `0x021F0A8C` by matching mode storage and the `mode == 1 ? 3 : 6` state transition, and found the exact sibling PPC callers. The complete path passes `r5 = 0` at `0x027995F8`; the Port restricted path passes `r5 = 1` at `0x02799678`. The new one-word candidate changes only the latter to `li r5, 0`; no object redirect, code cave, or branch is used.

After a zero-Cemu-process check, the installer placed the FPS and lobby packs into the user's normal Cemu profile used by an `-m`-only launch:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

The receipt contains both pack tree hashes. XML parsing and catalog inspection confirm that FPS and Lobby are installed but retain their existing disabled settings entries; the quest experiment is neither installed nor enabled. The installer writes only `graphicPacks/mh-cemu-enhancements` and never accesses MLC/save paths.

## Profile-path RCA (2026-07-30)

The initial isolated deployment was not loadable for two independently verified reasons: it had been placed at the outer root's `graphicPacks/` directory while the bundled Cemu source scans `<NEMESSIX_CEMU_DATA_ROOT>/data/graphicPacks/`; and an `-m`-only launch still uses the standard macOS profile, because `-m` changes MLC rather than the Cemu user-data root. `inspect` and `isolated-launch-command` now make both states visible without launching Cemu or editing Cemu configuration. A receipted legacy isolated install migrates to the scanned `data/graphicPacks` location on reinstall and is also removed by uninstall.

## Outstanding runtime gate

The lobby and quest box packs are not `Runtime Verified`. The next lobby step is an in-game run with the new mode-override Lobby pack enabled and the unrelated Quest pack disabled. It must first prove the missing equipment/set/talisman menu entries appear, then verify those actions, item deposit/withdrawal, combine/sell, closing and reopening the menu, and a clean title restart. Multiplayer validation is out of scope; the online recommendation remains the 30 FPS pack only.

## Distribution

`dist/mh-cemu-enhancements-0.1.9.zip` is deterministic across independent builds, contains no game assets or tool cache, and is accompanied by its adjacent `.sha256` verification file. Prior archives remain historical only and are not evidence for this candidate.
