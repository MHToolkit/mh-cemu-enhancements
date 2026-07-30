# Local verification record (2026-07-30)

## Current static gates

1. `python3 -m unittest discover -s tests -v` — fourteen tests passed: manifest/schema validation, negative validation gates, the six-site lobby construction-path contract, RPX SHA-256 + PPC preimages/anchors, standard and isolated idempotent installation, exact Experimental selection/exclusion, isolated-profile inspection, isolated launch-command generation, legacy-path migration/uninstall, and reproducible asset-free archive construction.
2. `python3 scripts/mh-cemu-enhancements.py validate` — three manifests accepted.
3. `python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx <pinned MH3G_Cafe.rpx>` — accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and all declared PPC words.
4. A temporary harness linked against the locally built Cemu `PPCAssembler` accepted all six lobby candidate instructions. Its `BRANCH_S26` relocation resolved the two calls to final PPC words `0x48541481` and `0x48541661`. The Cemu app was not started.
5. `ruff check scripts tests` and `git diff --check` passed.

## Runtime evidence and current standard-profile installation

The user confirmed that the 30 FPS switch took effect with the JP v96 title, so the FPS manifest is now `Runtime Verified`. The first lobby run established the opposite result: Cemu loaded and applied the old one-branch pack but the menu remained restricted. That failed candidate is replaced by the six-site construction-path candidate, which remains `Runtime Experimental` and default-off.

After a zero-Cemu-process check, the installer copied exactly the runtime-verified FPS pack and the explicitly selected lobby candidate to the user's normal Cemu profile:

```text
/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements/
```

The receipt contains the two pack tree hashes and the verified RPX hash. Read-only inspection confirmed both installed packs remain enabled in Cemu's existing `settings.xml`; the quest experiment is neither installed nor enabled. The installer writes only that `graphicPacks/mh-cemu-enhancements` directory and never accesses MLC/save paths.

## Profile-path RCA (2026-07-30)

The initial isolated deployment was not loadable for two independently verified reasons: it had been placed at the outer root's `graphicPacks/` directory while the bundled Cemu source scans `<NEMESSIX_CEMU_DATA_ROOT>/data/graphicPacks/`; and the observed user launch used the standard macOS profile, where no `mh-cemu-enhancements` directory existed and `<GraphicPack/>` contained no entries. `inspect` and `isolated-launch-command` now make both states visible without launching Cemu or editing Cemu configuration. A receipted legacy isolated install migrates to the scanned `data/graphicPacks` location on reinstall and is also removed by uninstall.

## Outstanding runtime gate

The lobby and quest box packs are not `Runtime Verified`. The next lobby test must use the exact JP v96 identity with only Lock 30 FPS and Lobby Full Item Box enabled, then verify equipment, talismans, item deposit/withdrawal and sell/combine actions, followed by a clean title restart. Multiplayer validation is out of scope; the online recommendation remains the 30 FPS pack only.

## Distribution

`dist/mh-cemu-enhancements-0.1.2.zip` is deterministic, contains no game assets or tool cache, and is accompanied by its adjacent `.sha256` verification file.
