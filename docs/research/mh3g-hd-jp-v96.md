# MH3G HD JP v96 static-research ledger

## Scope

Target: **Monster Hunter 3G HD Ver.**, Wii U Japan, title ID `0005000010104D00`, update v96. This ledger is static evidence only; Cemu is not launched by this project.

## Immutable reference

| Field | Value |
| --- | --- |
| RPX SHA-256 | `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` |
| Cemu RPX hash | `8cb62099` |
| Cemu patch module checksum | `0x348600a0` |
| PPC text load address | `0x02000020` |
| PPC data load address | `0x10000000` |

The RPX is not copied into this repository. The verifier accepts an explicit local reference path.

## 3DS control evidence (semantic reference only)

The local Japanese 3DS title is `0004000000048100` / `CTR-P-AMHJ`. Its extracted `code.bin` SHA-256 is `3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77`.

The existing 3DS force-30-FPS cheat follows `60C9E728 -> B0C9E728 -> +0x30` and writes float `0x41F00000`. This proves a 3DS runtime-pointer semantic only; it is ARM data and is never reused as a Wii U PPC address or patch.

## Menu-class mapping

Both the 3DS ARM code and the decompressed Wii U PPC data expose the same UI-class families. This separates menu/interaction handling from a world-model/chest visual:

| Intent | Class | JP v96 PPC evidence |
| --- | --- | --- |
| Full home item box | `uIDLobbyMyhBox` | RTTI at `0x100684d8`; resource `GUI\\lobby\\myh_box2_n` at `0x100256f4` |
| Restricted lobby/pub item box | `uIDLobbyShoItemGet` | RTTI at `0x10060ad0`; resource `GUI\\lobby\\sho_item` at `0x10025664` |
| Quest supply box | `uIDCockpitBox` | RTTI at `0x10052244`; resource `GUI\\quest\\box` at `0x100243f4` |
| Quest delivery box | `uIDCockpitShareBox` | RTTI at `0x10054680`; resource `GUI\\quest\\cockpit\\que_delibox` at `0x10024404` |

The Japanese gameplay reference independently describes village/port boxes as fuller storage, the pub box as item-only, and base-camp boxes as supply-only. The class/resource evidence confirms that the requested target is interaction/UI dispatch, not save data or a chest model.

## Cemu pack evidence

The local Cemu source parser reads `[Control] vsyncFrequency` from `rules.txt` and applies `.asm` patch groups only when `moduleMatches` contains the loaded module checksum. Cemu's documented `patch_*.asm` format supports PPC instruction replacement and code caves.

## Public-research boundary

The supplied Bilibili URL (`BV1XC4y1q74u`) could not be retrieved by the static web client and its three b23 download links were already known to return 404. It is not treated as source evidence. The project records public links in the README and proceeds from the local ARM/PPC assets above.

## Exact PPC dispatches and fail-closed assertions

All instruction words below are big-endian words from the immutable RPX text section. The installer verifies the RPX SHA-256 and every source/anchor word before copying a PPC pack; Cemu additionally gates the patch group with `moduleMatches = 0x348600a0`.

### Lobby restricted-mode override (Experimental)

The earlier branch, six-site substitution, full-home code-cave, 3DS-register-position `r9`, and resident-object accessor candidates all loaded in Cemu while the restricted three-option menu remained. They are superseded and are not gameplay success. The latest accessor run is especially conclusive: Cemu's log records module checksum `0x348600a0`, application of patch group `MH3G HD JP v96`, and activation of the Lobby leaf, while the screenshot still shows only deposit, withdrawal, and combine/sell.

The valid 3DS reference supplied for Port Tanzia changes `0x008EA6D0` from ARM `0xE3A02001` (`MOV r2, #1`) to `0xE3A02000` (`MOV r2, #0`). The complete extracted 3DS `.code` was reverse-LZSS decompressed to SHA-256 `3354687a7831b61dab19dd07619303de5c969523d4f35134aac38bcfb1759b77`. Disassembly proves that this is the third argument to ARM function `0x005DEC70`, not a menu count or UI factory selector. That function stores the argument as a mode byte and selects state value `3` when the mode equals `1`, otherwise value `6`.

The Wii U semantic counterpart is PPC function `0x021F0A8C`. It stores its third PPC argument (`r5`) at object offset `+0x6E12`, performs the same `mode == 1` comparison, and writes the same `3` versus `6` state values. There are exactly two direct PPC callers. The sibling complete-box path at `0x027995F8` passes `r5 = 0`; the Port Tanzia restricted path at `0x02799678` passes `r5 = 1`; both immediately call `0x021F0A8C`. This argument/data-flow match is the cross-architecture mapping that the old register-position guess lacked.

| Role | Address | Original big-endian word | Evidence |
| --- | --- | --- | --- |
| Store mode | `0x021f0ad0` | `0x9bfc6e12` | `stb r31, 0x6e12(r28)` stores the third argument |
| Mode test | `0x021f0af0` | `0x2c1f0001` | `cmpwi r31, 1` |
| Unrestricted value | `0x021f0af4` | `0x38000006` | Defaults to state value `6` |
| Restricted override | `0x021f0af8`, `0x021f0afc` | `bne +8`; `li r0, 3` | Mode `1` changes the state value to `3` |
| State store | `0x021f0b00` | `0xb01d000c` | Stores the selected state into the shared box state |
| Complete caller | `0x027995f8`, `0x02799600` | `li r5, 0`; `bl 0x021f0a8c` | Existing unrestricted call |
| Port caller | `0x02799678`, `0x02799680` | `li r5, 1`; `bl 0x021f0a8c` | Patch the mode argument only |

```asm
0x02799678 = li r5, 0
```

This does not replace a UI object, construct a different object, alter the physical chest model, or touch save data. It changes one existing Port interaction argument from restricted mode to the game's own unrestricted mode. The candidate is **Runtime Experimental**, default-off, and available only through explicit experimental opt-in until in-game evidence proves equipment/set/talisman actions, deposit/withdrawal, combine/sell, closing and reopening, and a clean restart.

### Quest supply/delivery -> home resource dispatch (Experimental)

| Menu source | Address | Original | Replacement | Destination |
| --- | --- | --- | --- | --- |
| Supply box | `0x021b0e90` | `0x300043f4` (`GUI\\quest\\box`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |
| Delivery box | `0x021b0f14` | `0x30004404` (`GUI\\quest\\cockpit\\que_delibox`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

The shared target anchors are `0x021bbf1c = 0x3c001002` and `0x021bbf28 = 0x300056f4`. These two sites are menu-resource dispatch arguments in the quest interaction flow, not model or save-data addresses. The dispatch substitution is deliberately **Runtime Experimental**, default excluded from installation, until isolated in-game testing proves that every required home-box action works and that quest state remains sound.

## Runtime validation gate

No Cemu process was launched for this research. To promote either box feature, record the exact manifest identity, Cemu version, title update, RPX SHA-256, module checksum, enabled pack set, and in-game result. Test the lobby and quest cases separately, then test a clean restart. Do not test the Experimental quest pack in multiplayer; the online recommendation remains 30 FPS only.
