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

### Lobby restricted-box selector redirect (Experimental)

The earlier branch, six-site substitution, full-home code-cave, and 3DS-informed `r9` candidates all loaded in Cemu while the restricted three-option menu remained. They are superseded and are not gameplay success. The valid 3DS reference supplied for Port Tanzia changes `0x008EA6D0` from ARM `0xE3A02001` (`MOV r2, #1`) to `0xE3A02000` (`MOV r2, #0`), but that ARM register cannot be mapped to a PPC register by position. The latest in-game screenshot proves that the PPC `li r9, 0` candidate also did not alter the menu.

The PPC comparison explains why: both the first restricted path and the complete home path pass `r9 = 1` into their shared initializer. It is not the menu-class selector. The actual UI factory dispatch uses its `r4` selector as a jump-table index: selector `0x07` enters the first 0x2a0-byte restricted constructor and selector `0x08` enters the alternate 0x2a0-byte restricted constructor. The complete home handler tests `r31 == 1` and then enters the 0x300-byte home constructor at `0x021bbef4`.

| Role | Address | Original big-endian word | Candidate evidence / replacement |
| --- | --- | --- | --- |
| First restricted selector | `0x021bb6c4` | `0x480003b4` | Selector `0x07` branches to `0x021bba78` |
| Alternate restricted selector | `0x021bb6c8` | `0x48000434` | Selector `0x08` branches to `0x021bbafc` |
| Restricted constructors | `0x021bba78`, `0x021bbafc` | `0x386002a0` | Both construct 0x2a0-byte restricted UI objects |
| Home guard | `0x021bbe54` | `0x281f0001` | Full home route requires `r31 == 1` |
| Home branch | `0x021bbe5c` | `0x41820098` | Required context branches to `0x021bbef4` |
| Home constructor | `0x021bbef4` | `0x38600300` | Constructs the 0x300-byte full home UI object |
| Home resource | `0x021bbf28` | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

```asm
0x021bb6c4 = b lobby_full_box_entry
0x021bb6c8 = b lobby_full_box_entry

.origin = codecave
lobby_full_box_entry:
li r31, 1
b 0x021bbef4
```

This redirects both verified restricted selectors to the existing complete home UI construction sequence; it does not change the physical chest model or save data. It is now **retracted**: the Cemu 2.6 macOS runtime applied it with code cave `0x01800000-0x01800008`, then crashed before gameplay with `SIGBUS` / `EXC_BAD_ACCESS` at guest `0x017ffffc`, in the `PPCRecompiler` thread. The code cave must not be reused. The next candidate requires a runtime GDB trace of the original dispatcher call context, then a non-code-cave patch only if that trace proves a safe source instruction.

### Quest supply/delivery -> home resource dispatch (Experimental)

| Menu source | Address | Original | Replacement | Destination |
| --- | --- | --- | --- | --- |
| Supply box | `0x021b0e90` | `0x300043f4` (`GUI\\quest\\box`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |
| Delivery box | `0x021b0f14` | `0x30004404` (`GUI\\quest\\cockpit\\que_delibox`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

The shared target anchors are `0x021bbf1c = 0x3c001002` and `0x021bbf28 = 0x300056f4`. These two sites are menu-resource dispatch arguments in the quest interaction flow, not model or save-data addresses. The dispatch substitution is deliberately **Runtime Experimental**, default excluded from installation, until isolated in-game testing proves that every required home-box action works and that quest state remains sound.

## Runtime validation gate

No Cemu process was launched for this research. To promote either box feature, record the exact manifest identity, Cemu version, title update, RPX SHA-256, module checksum, enabled pack set, and in-game result. Test the lobby and quest cases separately, then test a clean restart. Do not test the Experimental quest pack in multiplayer; the online recommendation remains 30 FPS only.
