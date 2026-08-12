# mh-cemu-enhancements

Local-first catalog for independently selectable **Cemu Graphic Packs**, PPC patches, and installer tooling. The repository is deliberately multi-title: packs live under `packs/<platform>/<title>/<region-version>/<feature>/`, while the catalog and scripts remain title-neutral.

It distributes no RPX, RPL, WUA, save, MLC, key, texture dump, or other game asset. It does not start Cemu, change its binary, or mutate global Cemu configuration.

## Initial catalog: MH3G HD JP v96

| Pack | Status | Availability | Default installation |
| --- | --- | --- | --- |
| Lock 30 FPS | `Runtime Experimental` | `available` | no |
| Lock 44 FPS (3DS conversion) | `Runtime Experimental` | `available` | no |
| 43 static ARM-to-PPC conversion packs | `Runtime Experimental` | `available` | no (explicit per-pack selection) |
| Lobby full item box | `Runtime Verified` | `available` | no |
| Custom Felyne food skills (three slots, `00..41`) | `Runtime Experimental` | `available` | no (explicit selection) |
| 3 external equipment cheats (production unlock / no materials / no money) | `3 Runtime Verified` | `available` | no (explicit per-pack selection) |
| Quest red delivery box -> full item box | `Runtime Experimental` | `runtime-blocked` | no |
| Quest blue supply box -> full item box (unconditional bridge control) | `Runtime Experimental` | `runtime-blocked` | no |
| Quest red & blue boxes -> full item box (conditional bridge) | `Runtime Experimental` | `runtime-blocked` (paused) | no |

Target identity: Wii U title `0005000010104D00`, Japan update v96, RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`, Cemu patch module checksum `0x348600a0`.

`Static Verified` means the pack structure, Cemu grammar, module gate, RPX hash, and declared big-endian PPC preimages passed locally. It is not an in-game success claim. User gameplay verified the lobby menu and its equipment, equipment-set, and talisman actions. The 30 FPS result was unstable. Repeated quest-box tests remained unusable; the blue bridge also blanked quest-board dialogue. All quest-box experiments are therefore paused and blocked from installation. The active 3DS cheat source was fully inventoried: 44 FPS has a native Cemu control conversion, and 43 static ARM entries were mapped from the hash-matching 3DS `.code` to independent JP-v96 PPC experimental packs with 179 fixed-address writes. A separately supplied 3DS Felyne-food cheat was semantically mapped to the native JP-v96 meal finalizer and exposed as three complete bilingual `00..41` selectors; it remains Gameplay Pending. Three additional user-supplied equipment cheats are mapped independently. Production Unlock and No Materials are gameplay verified; corrected No Materials evidence confirms that production and upgrade fully ignore material requirements without deducting owned materials, while Cemu UI counts remain normal instead of reproducing the 3DS all-99 display. No Money V1 made processing free but zeroed attack/status displays; V2 passed free production; V3/V4 covered only legacy upgrade records. V5/V6 were proven loaded but repeatedly misidentified generic detail-value calls, and a sufficient-material upgrade still displayed `75000z`. V7 now follows a live hardware-read-watchpoint trace from the selected object `+0x31C` price field to actual candidate builder `0x0221C730`, zeroing its two mutually exclusive category price generators at `0x0221C850` and `0x0221C96C`. It removes all four disproven generic-detail patches while preserving shared equipment value, attack-sensitive dispatch, sale/refund callers, and wallet adjustment. On 2026-08-12 the user cold-started the installed V7 and confirmed that the formerly failing upgrade route now works, promoting it to Runtime Verified; this does not claim an independent retest or exhaustive category coverage. The remaining dynamic set is now pinned to exactly 21 source-decoded entries (10 runtime pointers, 6 hotkey routines, and 5 ARM code caves) with fail-closed PPC/GDB trace batches; none is presented as an installable pack before its target mapping and runtime trace exist.

## Validate and install

```bash
python3 scripts/mh-cemu-enhancements.py validate
python3 scripts/mh-cemu-enhancements.py verify-reference --reference-rpx /absolute/path/to/MH3G_Cafe.rpx

# There are currently no default packs; no Cemu launch or config edit.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx

# Install the base manual-test set: verified Lobby, both optional FPS caps,
# and the explicitly selected Felyne-food customizer.
# The installer does not launch Cemu or change saved enable/disable choices.
python3 scripts/mh-cemu-enhancements.py install \
  --cemu-root /absolute/path/to/cemu-data-root \
  --reference-rpx /absolute/path/to/MH3G_Cafe.rpx \
  --pack mh3g-hd-jp-v96-lobby-full-item-box \
  --pack mh3g-hd-jp-v96-fps-lock-30 \
  --pack mh3g-hd-jp-v96-fps-lock-44 \
  --pack mh3g-hd-jp-v96-custom-felyne-food-skills \
  --include-experimental

# All quest-box candidates are paused and runtime-blocked; they cannot be installed.
# Each of the 43 static conversions must be explicitly selected with a repeated
# --pack ID from the mapping ledger. --include-experimental alone does not add them.
# The three external equipment packs are also explicit-only; select one or more
# by ID after reading their isolated gameplay test conditions.

python3 scripts/mh-cemu-enhancements.py uninstall --cemu-root /absolute/path/to/cemu-data-root
python3 scripts/mh-cemu-enhancements.py inspect --cemu-root /absolute/path/to/cemu-data-root
python3 scripts/mh-cemu-enhancements.py package --output dist/mh-cemu-enhancements-0.1.23.zip
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

Run the printed command manually, then open **Graphic Packs**, select the desired available switches, and restart/reload the title. All quest-box experiments remain blocked. Leave both FPS caps disabled until testing, and never enable 30 FPS and 44 FPS together.

## Compatibility and online use

- The 30 FPS and 44 FPS packs use per-pack `[Control] vsyncFrequency`, not a global Cemu setting. Both are default-off `Runtime Experimental`; they are mutually exclusive because Cemu accepts only one custom VSync frequency at a time. The 44-FPS pack is a semantic conversion of the two duplicate 3DS 44-FPS entries.
- The lobby pack changes one Port Tanzia interaction instruction from restricted mode `r5 = 1` to full mode `r5 = 0` at shared initializer `0x021F0A8C`. It redirects no object and uses no branch or code cave. User gameplay verified the complete menu plus equipment, equipment-set, and talisman actions, so it is `Runtime Verified` while remaining opt-in.
- The red candidate changes only the **red delivery box**, but gameplay continued to show an unusable crossed prompt. It is retained for static history and is `runtime-blocked` from installation.
- The unconditional blue bridge changed `0x02219DF0` to `nop`. Cemu proved it hot-loaded, but it still opened no item-box menu and blanked quest-board dialogue by exposing unrelated quest UI states to the lobby dispatcher. It is now `runtime-blocked`.
- The combined candidate is retained as source history, but is now `runtime-blocked` and paused with the other task-box experiments. It is excluded from the installer selection until a reproducible correct quest-scene lifecycle exists.
- Custom Felyne Food Skills exposes three independent bilingual selectors covering IDs `00..41`, defaulting inside the pack to `06/36/00`. The corrected patch replaces native temporary slots `r31 + 0x68/0x6A/0x6C` after random generation and leaves the game's final menu/runtime mirroring loop intact. Cemu resolves Graphic Pack parameters when loading the title: after changing presets, restart or reload the title and then eat again. Pre-meal preview may remain game-generated, and native incompatible combinations (known example: `41 + 1E`) may apply only one effect. The pack is default-off `Runtime Experimental / Gameplay Pending`.
- The three external equipment packs are independent default-off leaves under `Equipment Cheats`: Production Unlock bypasses only the valid-ID unlock-bit failure; No Materials includes that unlock and spoofs the exact non-exempt material-count call family as 99; No Money V7 keeps two production-local cost zeros and two legacy upgrade-record zeros, then covers the two runtime-traced category price generators inside the active candidate builder. Production Unlock and No Materials are mutually exclusive because the latter already includes the former. The first two are gameplay verified. No Money V1's global dispatcher patch was disproven by zero attack/status displays; V2 passed production but missed upgrades; V3 covered one upgrade record path; V4 covered both record paths but still displayed the native price; V5/V6 were proven loaded but repeatedly targeted the wrong generic detail calls. On 2026-08-12 the user cold-started V7 and confirmed that the formerly failing upgrade route now works; all three equipment packs are therefore `Runtime Verified`. V7 deliberately leaves the shared value function plus real sale/refund calculations native.
- There are 50 available Cemu leaves: 30/44 FPS, Lobby Full Item Box, Custom Felyne Food Skills, 43 independent entries under `3DS Static Cheats`, and the three external equipment entries. The catalog keeps all task-box candidates as non-installable negative evidence.
- All 43 static conversions are default-off `Runtime Experimental / Gameplay Pending`. Every Cemu description now leads with the real gameplay effect, then states its boundaries, an isolated verification method, and the 3DS/PPC source status in both Chinese and English instead of showing conversion boilerplate alone. #6 and #72 share an affinity path and are mutually exclusive; #56 is a partial semantic mapping; #65 forces the normal-game-mode generic skill comparison and has the broadest test risk. Isolated tests for #13/#21/#34/#50/#60 must disable #65; #60 must also disable #59. Local gameplay on 2026-08-07 confirmed that #13 0.1.22 visibly doubles actual underwater travel rather than animation alone; an independent Pipi retest remains pending, so the pack stays experimental for now.
- Leave all item-box modification packs disabled for multiplayer. The 30 FPS pack is also not recommended until its instability is resolved.
- Never enable this JP v96 catalog against another title, region, update, RPX hash, or module checksum.

## Evidence and format

- [Architecture and status vocabulary](docs/architecture.md)
- [Catalog boundary decision](docs/adr/0001-catalog-and-pack-boundaries.md)
- [MH3G HD JP v96 PPC ledger](docs/research/mh3g-hd-jp-v96.md)
- [Complete 3DS-to-Cemu cheat conversion matrix](docs/research/mh3g-3ds-cheat-conversion.md)
- [43 static ARM-to-PPC mappings and pack IDs](docs/research/mh3g-static-arm-mapping.md)
- [External equipment-cheat Gateway/ARM-to-PPC mappings](docs/research/mh3g-equipment-gateway-cheat-mapping.md)
- [21 dynamic PPC/GDB mapping entries and probe batches](docs/research/mh3g-dynamic-ppc-mapping.md)
- [Pack manifest schema](schemas/pack-manifest.schema.json)

The per-pack `patch_*.asm` syntax and `[Control] vsyncFrequency` behavior are based on the Cemu Graphic Pack parser. The user-supplied Bilibili page was not relied upon: its short links were unavailable, and all mappings here are backed by the local 3DS ARM semantic evidence plus Wii U PPC/static-resource analysis.

Future GitHub destination: `MHToolkit/mh-cemu-enhancements`. This local repository intentionally has no remote configured or published by this project.
