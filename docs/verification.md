# Local verification record (2026-07-31)

## Current static gates

1. `python3 -m unittest discover -s tests -v` — fourteen tests passed: manifest/schema validation, negative validation gates, the lobby mode-argument contract, RPX SHA-256 + PPC preimages/anchors, standard and isolated idempotent installation, exact Experimental selection/exclusion, isolated-profile inspection, isolated launch-command generation, legacy-path migration/uninstall, and reproducible asset-free archive construction.
2. `python3 scripts/mh-cemu-enhancements.py validate` — three manifests accepted.
3. `python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx <pinned MH3G_Cafe.rpx>` — accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and all declared PPC words.
4. A PPC assembly smoke check encodes `li r9, 0` as `0x39200000`; the pack has no code cave or relocation. The Cemu app was not started by this project.
5. `ruff check scripts tests` and `git diff --check` passed.

## Runtime evidence and current standard-profile installation

The user confirmed that the 30 FPS switch took effect with the JP v96 title, so the FPS manifest is now `Runtime Verified`. The lobby runs established the opposite result for the branch, six-site substitution, full-home code-cave, and 3DS-informed `li r9, 0` candidates: the standard-profile Cemu log records JP v96, `Set vsync frequency to 30`, and `Applying patch group 'MH3G HD JP v96'`, but the restricted three-option menu remained. The latest screenshot is direct gameplay evidence of that failure. The dual-selector redirect is its static-verified replacement and remains `Runtime Experimental`, default-off, and is now installed only after a clean Cemu shutdown.

After a zero-Cemu-process check, the installer copied exactly the runtime-verified FPS pack and the dual-selector lobby candidate to the user's normal Cemu profile:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

The receipt contains the two pack tree hashes and the verified RPX hash. The lobby entry was already enabled in Cemu's existing `settings.xml`; the missing Lock 30 FPS `<Entry>` was restored in that same standard profile after the emulator exited. XML parsing and catalog inspection confirm that both installed packs are enabled. The quest experiment is neither installed nor enabled. The installer itself writes only that `graphicPacks/mh-cemu-enhancements` directory and never accesses MLC/save paths.

## Profile-path RCA (2026-07-30)

The initial isolated deployment was not loadable for two independently verified reasons: it had been placed at the outer root's `graphicPacks/` directory while the bundled Cemu source scans `<NEMESSIX_CEMU_DATA_ROOT>/data/graphicPacks/`; and the observed user launch used the standard macOS profile, where no `mh-cemu-enhancements` directory existed and `<GraphicPack/>` contained no entries. `inspect` and `isolated-launch-command` now make both states visible without launching Cemu or editing Cemu configuration. A receipted legacy isolated install migrates to the scanned `data/graphicPacks` location on reinstall and is also removed by uninstall.

## Outstanding runtime gate

The lobby and quest box packs are not `Runtime Verified`. After the dual-selector replacement is installed, the next lobby test must use the exact JP v96 identity with only Lock 30 FPS and Lobby Full Item Box enabled, then verify equipment, talismans, item deposit/withdrawal and sell/combine actions, followed by a clean title restart. Multiplayer validation is out of scope; the online recommendation remains the 30 FPS pack only.

## Distribution

`dist/mh-cemu-enhancements-0.1.5.zip` is deterministic, contains no game assets or tool cache, and is accompanied by its adjacent `.sha256` verification file.
