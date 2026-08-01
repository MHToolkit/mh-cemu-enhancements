# mh-cemu-enhancements

Local-first catalog for independently selectable **Cemu Graphic Packs**, PPC patches, and installer tooling. The repository is deliberately multi-title: packs live under `packs/<platform>/<title>/<region-version>/<feature>/`, while the catalog and scripts remain title-neutral.

It distributes no RPX, RPL, WUA, save, MLC, key, texture dump, or other game asset. It does not start Cemu, change its binary, or mutate global Cemu configuration.

## Initial catalog: MH3G HD JP v96

| Pack | Status | Availability | Default installation |
| --- | --- | --- | --- |
| Lock 30 FPS | `Runtime Experimental` | `available` | no |
| Lobby full item box | `Runtime Verified` | `available` | no |
| Quest red delivery box -> full item box | `Runtime Experimental` | `runtime-blocked` | no |
| Quest blue supply box -> full item box (dispatch-bridge control) | `Runtime Experimental` | `available` | no |

Target identity: Wii U title `0005000010104D00`, Japan update v96, RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`, Cemu patch module checksum `0x348600a0`.

`Static Verified` means the pack structure, Cemu grammar, module gate, RPX hash, and declared big-endian PPC preimages passed locally. It is not an in-game success claim. User gameplay verified the lobby menu and its equipment, equipment-set, and talisman actions. The 30 FPS result was unstable. Repeated red-box tests remained unusable. The first blue control accepted input without opening a menu; static tracing found its missing per-frame dispatch behind the hub scene-state gate. The revised blue control now adds that dispatch bridge and is available only as a gameplay-pending single-player experiment. Red remains `runtime-blocked`.

## Validate and install

```bash
python3 scripts/mh-cemu-enhancements.py validate
python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx /absolute/path/to/MH3G_Cafe.rpx

# There are currently no default packs; no Cemu launch or config edit.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx

# Explicitly install the gameplay-verified Lobby pack.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-lobby-full-item-box

# Install the revised blue dispatch-bridge control; Experimental must be explicit.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-quest-blue-supply-box-full-item-box-control \
  --include-experimental

# Red remains runtime-blocked. Install 30 FPS explicitly with
# --include-experimental if desired.

python3 scripts/mh-cemu-enhancements.py uninstall --cemu-root /absolute/path/to/cemu-data-root
python3 scripts/mh-cemu-enhancements.py inspect --cemu-root /absolute/path/to/cemu-data-root
python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-0.1.15.zip
```

Install writes only its owned Graphic Pack directory with a receipt. For a standard Cemu macOS data root that is `<cemu-root>/graphicPacks/mh-cemu-enhancements/`; for the supplied Nemessix-isolated outer root (`.../Library/Application Support/Nemessix Dev/cemu`) it is `<cemu-root>/data/graphicPacks/mh-cemu-enhancements/`, which is the Cemu user-data path scanned by the bundled build. Re-running install replaces only that owned directory; uninstall is idempotent and removes only that directory. If that directory has no receipt, it is renamed to a local backup before replacement. A receipted installation made by the pre-fix isolated layout is migrated from `<cemu-root>/graphicPacks/mh-cemu-enhancements/` on the next install, or removed by uninstall.

`inspect` is read-only: it reports the resolved Graphic Pack directory, the applicable settings file, each catalog entry's installation status, and its saved Cemu enable state. After installation, enable only the desired available packs in Cemu's Graphic Packs UI. The installer never changes Cemu's saved enable/disable choices.

### macOS isolated profile launch

The supplied Cemu build uses the isolated profile **only** when `NEMESSIX_CEMU_DATA_ROOT` is present. `-m` selects an MLC directory only; it does not change the Cemu user-data/Graphic Packs profile. Starting the `.app` normally (including with only `-m`) uses the standard `~/Library/Application Support/Cemu` profile and cannot see packs installed in the isolated root. To avoid mixing profiles, print the exact command without launching Cemu:

```bash
python3 scripts/mh-cemu-enhancements.py isolated-launch-command \
  --cemu-root "/absolute/path/Library/Application Support/Nemessix Dev/cemu" \
  --cemu-app /absolute/path/Cemu.app
```

Run the printed command manually, then open **Graphic Packs**, select the desired available switches, and restart/reload the title. The red experiment remains blocked. The blue dispatch bridge is single-player and gameplay-pending; leave 30 FPS disabled until its instability is understood.

## Compatibility and online use

- The 30 FPS pack uses per-pack `vsyncFrequency = 30`, not a global Cemu setting. User testing was unstable, so it is default-off `Runtime Experimental`.
- The lobby pack changes one Port Tanzia interaction instruction from restricted mode `r5 = 1` to full mode `r5 = 0` at shared initializer `0x021F0A8C`. It redirects no object and uses no branch or code cave. User gameplay verified the complete menu plus equipment, equipment-set, and talisman actions, so it is `Runtime Verified` while remaining opt-in.
- The red candidate changes only the **red delivery box**, but gameplay continued to show an unusable crossed prompt. It is retained for static history and is `runtime-blocked` from installation.
- The first blue control reached the shared selector-0 branch and retained the normal prompt, but pressing the interaction button opened no menu. `0x021F0A8C` only stores state `6`; the sole dispatcher for that state was skipped by the hub scene-state check. The revised control keeps its six-instruction trigger and changes original `0x02219DF0 = beq 0x02219E6C` to `nop`, retaining the following manager and busy-state guards before `0x0215165C`. It is `Runtime Experimental`, available only for isolated single-player validation, and not a runtime-success claim.
- Available Cemu leaves are `MH Cemu Enhancements > MH3G HD JP v96 > Lock 30 FPS`, `Lobby Full Item Box`, and `Quest Blue Supply Box -> Full Item Box (Control)`. The catalog keeps red as non-installable negative evidence.
- Leave all item-box modification packs disabled for multiplayer. The 30 FPS pack is also not recommended until its instability is resolved.
- Never enable this JP v96 catalog against another title, region, update, RPX hash, or module checksum.

## Evidence and format

- [Architecture and status vocabulary](docs/architecture.md)
- [Catalog boundary decision](docs/adr/0001-catalog-and-pack-boundaries.md)
- [MH3G HD JP v96 PPC ledger](docs/research/mh3g-hd-jp-v96.md)
- [Pack manifest schema](schemas/pack-manifest.schema.json)

The per-pack `patch_*.asm` syntax and `[Control] vsyncFrequency` behavior are based on the Cemu Graphic Pack parser. The user-supplied Bilibili page was not relied upon: its short links were unavailable, and all mappings here are backed by the local 3DS ARM semantic evidence plus Wii U PPC/static-resource analysis.

Future GitHub destination: `MHToolkit/mh-cemu-enhancements`. This local repository intentionally has no remote configured or published by this project.
