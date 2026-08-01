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

### Lobby restricted-object accessor redirect (Experimental)

The earlier branch, six-site substitution, full-home code-cave, and 3DS-informed `r9` candidates all loaded in Cemu while the restricted three-option menu remained. They are superseded and are not gameplay success. The valid 3DS reference supplied for Port Tanzia changes `0x008EA6D0` from ARM `0xE3A02001` (`MOV r2, #1`) to `0xE3A02000` (`MOV r2, #0`), but that ARM register cannot be mapped to a PPC register by position. The latest in-game screenshot proves that the PPC `li r9, 0` candidate also did not alter the menu.

The PPC comparison explains why: both the first restricted path and the complete home path pass `r9 = 1` into their shared initializer. It is not the menu-class selector. The factory selectors also run while `sID::IDLobby` initializes its resident UI objects, not when the player opens a box. Redirecting those factory branches changed the object layout and the dual-selector code-cave candidate crashed Cemu before gameplay.

The correct layer is the `sID::IDLobby` virtual accessor at `0x021baf70` (vtable entry `+0x4c`). Initialization creates the selector-`0x08` restricted object in slot `+0xb4`, the selector-`0x0e` complete-home object in slot `+0xa8`, and the alternate selector-`0x07` restricted object in slot `+0xc4`. When the accessor receives logical UI ID `0x17`, its only object-return instruction is `0x021baff4 = lwz r3, 0xb4(r3)`. The replacement changes only that D-form displacement to `+0xa8`.

| Role | Address | Original big-endian word | Evidence / replacement |
| --- | --- | --- | --- |
| Restricted slot `+0xb4` | `0x021b2af0`, `0x021b2b00` | `li r4, 0x08`; `stw r3, 0xb4(r31)` | Factory selector `0x08` is created once and stored |
| Complete-home slot `+0xa8` | `0x021b2bd0`, `0x021b2be0` | `li r4, 0x0e`; `stw r3, 0xa8(r31)` | Complete-home object is already resident |
| Alternate restricted slot `+0xc4` | `0x021b2c78`, `0x021b2c88` | `li r4, 0x07`; `stw r3, 0xc4(r31)` | Alternate restricted object remains untouched |
| Logical-ID guard | `0x021bafa4`, `0x021bafa8` | `cmplwi r4, 0x17`; `beq 0x021bafe4` | Isolates the requested lobby interaction path |
| Restricted-object return | `0x021baff4` | `0x806300b4` | Replace with `0x806300a8` (`lwz r3, 0xa8(r3)`) |
| Return anchor | `0x021baff8` | `0x4e800020` | Returns the selected resident object directly |

```asm
0x021baff4 = lwz r3, 0x00a8(r3)
```

This does not construct a different object, alter the physical chest model, or touch save data. It reuses the complete-home object that the unmodified game already created and changes only the object selected for logical UI ID `0x17`. The candidate is **Runtime Experimental**, default-off, and available only through explicit experimental opt-in until in-game evidence proves equipment, talismans, deposit/withdrawal, combine/sell, and clean restart behavior.

### Quest supply/delivery -> home resource dispatch (Experimental)

| Menu source | Address | Original | Replacement | Destination |
| --- | --- | --- | --- | --- |
| Supply box | `0x021b0e90` | `0x300043f4` (`GUI\\quest\\box`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |
| Delivery box | `0x021b0f14` | `0x30004404` (`GUI\\quest\\cockpit\\que_delibox`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

The shared target anchors are `0x021bbf1c = 0x3c001002` and `0x021bbf28 = 0x300056f4`. These two sites are menu-resource dispatch arguments in the quest interaction flow, not model or save-data addresses. The dispatch substitution is deliberately **Runtime Experimental**, default excluded from installation, until isolated in-game testing proves that every required home-box action works and that quest state remains sound.

## Runtime validation gate

No Cemu process was launched for this research. To promote either box feature, record the exact manifest identity, Cemu version, title update, RPX SHA-256, module checksum, enabled pack set, and in-game result. Test the lobby and quest cases separately, then test a clean restart. Do not test the Experimental quest pack in multiplayer; the online recommendation remains 30 FPS only.
