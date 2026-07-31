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

The first candidate patched only `0x021bba90` with a branch into the middle of the home path. The second candidate copied six constructor-path instructions. Both were loaded and applied by Cemu while the restricted three-option menu remained. The deeper dispatcher trace identifies why: `0x021bb6c4` routes selector `0x07` to the restricted path, while the native full-home path first requires `r31 == 1` at `0x021bbe54`; the six-site candidate passed the caller's unknown `r31` through instead of establishing that full-home context. Both earlier candidates are superseded and are not gameplay success.

| Role | Address | Original big-endian word | Candidate evidence / replacement |
| --- | --- | --- | --- |
| Restricted selector entry | `0x021bba78` | `0x386002a0` (`li r3, 0x2a0`) | Branch to `lobby_full_box_entry` in Cemu’s code cave |
| Selector proof | `0x021bb6c4` | `0x480003b4` | Dispatcher selector `0x07` branches to `0x021bba78` |
| Full-path context guard | `0x021bbe54` | `0x281f0001` | `cmplwi r31, 1` |
| Full-path branch | `0x021bbe5c` | `0x41820098` | Branches to `0x021bbef4` only when `r31 == 1` |
| Full-box allocation | `0x021bbef4` | `0x38600300` | Existing full-home path target |
| Full-box allocation call | `0x021bbefc` | `0x48541005` | Existing full-home allocator |
| Full-box constructor call | `0x021bbf0c` | `0x485411e5` | Existing `uIDLobbyMyhBox` constructor |
| Full-box GUI resource | `0x021bbf28` | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

The replacement has one patched RPX word plus a Cemu code cave:

```asm
0x021bba78 = b lobby_full_box_entry
.origin = codecave
lobby_full_box_entry:
li r31, 1
b 0x021bbef4
```

Cemu reserves code-cave memory in `0x01800000..0x01bfffff`; both branches are within PPC `BRANCH_S26` range and are resolved by Cemu after the code-cave address is allocated. Its real `PPCAssembler` accepted the source branch, `li r31, 1`, and the branch back into `0x021bbef4`. The target remains interaction/UI construction, never a chest model or save address. This candidate is **Runtime Experimental**, default-off, until in-game evidence shows equipment, talismans, and item actions.

### Quest supply/delivery -> home resource dispatch (Experimental)

| Menu source | Address | Original | Replacement | Destination |
| --- | --- | --- | --- | --- |
| Supply box | `0x021b0e90` | `0x300043f4` (`GUI\\quest\\box`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |
| Delivery box | `0x021b0f14` | `0x30004404` (`GUI\\quest\\cockpit\\que_delibox`) | `0x300056f4` | `GUI\\lobby\\myh_box2_n` |

The shared target anchors are `0x021bbf1c = 0x3c001002` and `0x021bbf28 = 0x300056f4`. These two sites are menu-resource dispatch arguments in the quest interaction flow, not model or save-data addresses. The dispatch substitution is deliberately **Runtime Experimental**, default excluded from installation, until isolated in-game testing proves that every required home-box action works and that quest state remains sound.

## Runtime validation gate

No Cemu process was launched for this research. To promote either box feature, record the exact manifest identity, Cemu version, title update, RPX SHA-256, module checksum, enabled pack set, and in-game result. Test the lobby and quest cases separately, then test a clean restart. Do not test the Experimental quest pack in multiplayer; the online recommendation remains 30 FPS only.
