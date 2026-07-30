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

### Lobby restricted box -> full home-box construction path (Experimental)

The first candidate patched only `0x021bba90` with a branch into the middle of the home path. The user’s in-game result showed that Cemu loaded and applied that pack while the restricted three-option menu remained. The static RCA is that the single branch skipped the full path's allocation size, allocator, constructor, and GUI-resource setup; it is superseded and must not be treated as gameplay success.

| Role | Address | Original big-endian word | Candidate replacement / matched home-path evidence |
| --- | --- | --- | --- |
| Allocation size | `0x021bba78` | `0x386002a0` (`li r3, 0x2a0`) | `li r3, 0x300`; anchor `0x021bbef4 = 0x38600300` |
| Allocation call | `0x021bba80` | `0x48500f55` (`bl 0x026bc9d4`, restricted allocator) | `bl 0x026fcf00`; home anchor `0x021bbefc = 0x48541005`; Cemu resolved word `0x48541481` |
| Constructor call | `0x021bba90` | `0x48501135` (`bl 0x026bcbc4`, restricted constructor) | `bl 0x026fd0f0`; home anchor `0x021bbf0c = 0x485411e5`; Cemu resolved word `0x48541661` |
| Stack constructor argument | `0x021bbaac` | `0x90a1000c` (`stw r5, 0xc(r1)`) | `stw r31, 0xc(r1)`; home anchor `0x021bbf2c = 0x93e1000c` |
| GUI resource | `0x021bbab0` | `0x30005664` (`GUI\\lobby\\sho_item`) | `addic r0, r0, 0x56f4`; home anchor `0x021bbf28 = 0x300056f4` for `GUI\\lobby\\myh_box2_n` |
| Register constructor argument | `0x021bbac4` | `0x7f0ac378` (`mr r10, r24`) | `lwz r10, 4(r27)`; home anchor `0x021bbf14 = 0x815b0004` |

At the common dispatcher call, this makes `r3`–`r10` and stack arguments `8(r1)` through `0x14(r1)` match the existing full-home path where they differ. Cemu's actual `PPCAssembler` accepted all six candidate instructions; `BRANCH_S26` relocation uses the patched instruction address, yielding the recorded final branch words above. The target is still interaction/UI construction, never a chest model or save address. This candidate is **Runtime Experimental**, default-off, until in-game evidence shows equipment, talismans, and item actions.

### Quest supply/delivery -> home resource dispatch (Experimental)

| Menu source | Address | Original | Replacement | Destination |
| --- | --- | --- | --- | --- |
| Supply box | `0x021b0e90` | `0x300043f4` (`GUI\\quest\\box`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |
| Delivery box | `0x021b0f14` | `0x30004404` (`GUI\\quest\\cockpit\\que_delibox`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

The shared target anchors are `0x021bbf1c = 0x3c001002` and `0x021bbf28 = 0x300056f4`. These two sites are menu-resource dispatch arguments in the quest interaction flow, not model or save-data addresses. The dispatch substitution is deliberately **Runtime Experimental**, default excluded from installation, until isolated in-game testing proves that every required home-box action works and that quest state remains sound.

## Runtime validation gate

No Cemu process was launched for this research. To promote either box feature, record the exact manifest identity, Cemu version, title update, RPX SHA-256, module checksum, enabled pack set, and in-game result. Test the lobby and quest cases separately, then test a clean restart. Do not test the Experimental quest pack in multiplayer; the online recommendation remains 30 FPS only.
