# Local verification record (2026-07-30)

## Static gates passed

1. `python3 -m unittest discover -s tests -v` — six tests passed: manifest/schema validation, negative validation gates, RPX SHA-256 + PPC preimages/anchors, idempotent install/uninstall, Experimental exclusion, and reproducible asset-free archive construction.
2. `python3 scripts/mh-cemu-enhancements.py validate` — three manifests accepted.
3. `python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx <pinned MH3G_Cafe.rpx>` — accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and all declared PPC words.
4. A temporary harness linked against the locally built Cemu `PPCAssembler` accepted the lobby `b 0x021bbefc` instruction and both quest `addic r0, r0, 0x56f4` instructions. The Cemu app was not started.
5. `ruff check scripts tests` and `git diff --check` passed.

## Isolated installation

The default two non-Experimental packs were installed twice, idempotently, at:

```text
.../nemessix-bundled-cemu-runtime-proof-20260721/home/Library/Application Support/Nemessix Dev/cemu/graphicPacks/mh-cemu-enhancements/
```

The receipt contains the two pack tree hashes and the verified RPX hash. The Experimental quest pack was not copied. No Cemu process was launched; the installer writes only that `graphicPacks/mh-cemu-enhancements` directory and never accesses MLC/save paths.

## Outstanding runtime gate

No feature has been marked `Runtime Verified`. The next in-game test must use the exact JP v96 identity, enable one pack at a time, and record result plus restart behavior. Multiplayer validation is out of scope; the online recommendation remains the 30 FPS pack only.

## Distribution

`dist/mh-cemu-enhancements-0.1.0.zip` is deterministic, contains no game assets or tool cache, and is accompanied by its adjacent `.sha256` verification file.
