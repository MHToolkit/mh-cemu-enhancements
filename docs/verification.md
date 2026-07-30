# Local verification record (2026-07-30)

## Static gates passed

1. `python3 -m unittest discover -s tests -v` — ten tests passed: manifest/schema validation, negative validation gates, RPX SHA-256 + PPC preimages/anchors, standard and isolated idempotent installation, Experimental exclusion, isolated-profile inspection, isolated launch-command generation, legacy-path migration/uninstall, and reproducible asset-free archive construction.
2. `python3 scripts/mh-cemu-enhancements.py validate` — three manifests accepted.
3. `python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx <pinned MH3G_Cafe.rpx>` — accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and all declared PPC words.
4. A temporary harness linked against the locally built Cemu `PPCAssembler` accepted the lobby `b 0x021bbefc` instruction and both quest `addic r0, r0, 0x56f4` instructions. The Cemu app was not started.
5. `ruff check scripts tests` and `git diff --check` passed.

## Isolated installation

The default two non-Experimental packs are installed idempotently at the Cemu user-data path:

```text
.../nemessix-bundled-cemu-runtime-proof-20260721/home/Library/Application Support/Nemessix Dev/cemu/data/graphicPacks/mh-cemu-enhancements/
```

The receipt contains the two pack tree hashes and the verified RPX hash. The Experimental quest pack is not copied. The installer writes only that `graphicPacks/mh-cemu-enhancements` directory in the selected profile and never accesses MLC/save paths.

## Profile-path RCA (2026-07-30)

The initial isolated deployment was not loadable for two independently verified reasons: it had been placed at the outer root's `graphicPacks/` directory while the bundled Cemu source scans `<NEMESSIX_CEMU_DATA_ROOT>/data/graphicPacks/`; and the observed user launch used the standard macOS profile, where no `mh-cemu-enhancements` directory existed and `<GraphicPack/>` contained no entries. `inspect` and `isolated-launch-command` now make both states visible without launching Cemu or editing Cemu configuration. A receipted legacy isolated install migrates to the scanned `data/graphicPacks` location on reinstall and is also removed by uninstall.

## Outstanding runtime gate

No feature has been marked `Runtime Verified`. The next in-game test must use the exact JP v96 identity, enable one pack at a time, and record result plus restart behavior. Multiplayer validation is out of scope; the online recommendation remains the 30 FPS pack only.

## Distribution

`dist/mh-cemu-enhancements-0.1.0.zip` is deterministic, contains no game assets or tool cache, and is accompanied by its adjacent `.sha256` verification file.
