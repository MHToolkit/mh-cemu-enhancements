# mh-cemu-enhancements

Local-first catalog for independently selectable **Cemu Graphic Packs**, PPC patches, and installer tooling. The repository is deliberately multi-title: packs live under `packs/<platform>/<title>/<region-version>/<feature>/`, while the catalog and scripts remain title-neutral.

It distributes no RPX, RPL, WUA, save, MLC, key, texture dump, or other game asset. It does not start Cemu, change its binary, or mutate global Cemu configuration.

## Initial catalog: MH3G HD JP v96

| Pack | Status | Default installation | Cemu UI switch |
| --- | --- | --- | --- |
| Lock 30 FPS | `Static Verified` | yes | independent |
| Lobby full item box | `Static Verified` | yes | independent |
| Quest supply/delivery full item box | `Runtime Experimental` | no | independent |

Target identity: Wii U title `0005000010104D00`, Japan update v96, RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`, Cemu patch module checksum `0x348600a0`.

`Static Verified` means the pack structure, Cemu grammar, module gate, RPX hash, and declared big-endian PPC preimages passed locally. It is not an in-game success claim. The quest pack is intentionally experimental and omitted unless explicitly requested.

## Validate and install

```bash
python3 scripts/mh-cemu-enhancements.py validate
python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx /absolute/path/to/MH3G_Cafe.rpx

# Default: install only non-experimental packs; no Cemu launch or config edit.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx

# Explicitly include the default-off quest experiment.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-quest-full-item-box-experimental \
  --include-experimental

python3 scripts/mh-cemu-enhancements.py uninstall --cemu-root /absolute/path/to/cemu-data-root
python3 scripts/mh-cemu-enhancements.py inspect --cemu-root /absolute/path/to/cemu-data-root
python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-0.1.0.zip
```

Install writes only its owned Graphic Pack directory with a receipt. For a standard Cemu macOS data root that is `<cemu-root>/graphicPacks/mh-cemu-enhancements/`; for the supplied Nemessix-isolated outer root (`.../Library/Application Support/Nemessix Dev/cemu`) it is `<cemu-root>/data/graphicPacks/mh-cemu-enhancements/`, which is the Cemu user-data path scanned by the bundled build. Re-running install replaces only that owned directory; uninstall is idempotent and removes only that directory. If that directory has no receipt, it is renamed to a local backup before replacement. A receipted installation made by the pre-fix isolated layout is migrated from `<cemu-root>/graphicPacks/mh-cemu-enhancements/` on the next install, or removed by uninstall.

`inspect` is read-only: it reports the resolved Graphic Pack directory, the applicable settings file, each pack's installation status, and its saved Cemu enable state. After installation, enable each desired pack in Cemu's Graphic Packs UI. The installer never changes Cemu's saved enable/disable choices, which keeps all three switches independent.

### macOS isolated profile launch

The supplied Cemu build uses the isolated profile **only** when `NEMESSIX_CEMU_DATA_ROOT` is present. Starting the `.app` normally (for example, from Finder) uses the standard `~/Library/Application Support/Cemu` profile and cannot see packs installed in the isolated root. To avoid mixing profiles, print the exact command without launching Cemu:

```bash
python3 scripts/mh-cemu-enhancements.py isolated-launch-command \
  --cemu-root "/absolute/path/Library/Application Support/Nemessix Dev/cemu" \
  --cemu-app /absolute/path/Cemu.app
```

Run the printed command manually, then open **Graphic Packs**, select the desired independent switches, and restart/reload the title. Do not use the Experimental quest pack for normal or multiplayer play.

## Compatibility and online use

- The 30 FPS pack uses per-pack `vsyncFrequency = 30`, not a global Cemu setting.
- The lobby patch jumps from the restricted lobby dispatch to the game’s existing full-home-box flow. Its exact source/target words are checked before installation.
- The quest patch substitutes the supply and delivery menu-resource dispatches with the existing home-box resource. It remains `Runtime Experimental` until isolated gameplay tests prove all actions and quest-state safety.
- For multiplayer, enable **only Lock 30 FPS**. Leave both box packs disabled.
- Never enable this JP v96 catalog against another title, region, update, RPX hash, or module checksum.

## Evidence and format

- [Architecture and status vocabulary](docs/architecture.md)
- [Catalog boundary decision](docs/adr/0001-catalog-and-pack-boundaries.md)
- [MH3G HD JP v96 PPC ledger](docs/research/mh3g-hd-jp-v96.md)
- [Pack manifest schema](schemas/pack-manifest.schema.json)

The per-pack `patch_*.asm` syntax and `[Control] vsyncFrequency` behavior are based on the Cemu Graphic Pack parser. The user-supplied Bilibili page was not relied upon: its short links were unavailable, and all mappings here are backed by the local 3DS ARM semantic evidence plus Wii U PPC/static-resource analysis.

Future GitHub destination: `MHToolkit/mh-cemu-enhancements`. This local repository intentionally has no remote configured or published by this project.
