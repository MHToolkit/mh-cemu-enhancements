# Architecture / 架构

## Purpose / 目标

`mh-cemu-enhancements` is a local-first, multi-title catalog of Cemu enhancements. It packages only declarative Graphic Pack files, metadata, verification tooling, and documentation. It never modifies a game RPX on disk or the Cemu binary.

## Layout / 目录

```text
packs/
  wiiu/
    mh3g-hd/
      jp-v96/
        fps-lock-30/
        lobby-full-item-box/
        quest-delivery-full-item-box-experimental/
```

The platform, canonical title, region, and update/version are path components, not repository-level assumptions. A future `mh4u-hd`, non-Monster-Hunter title, or another region can add its own platform/title/version leaf without changing the public scripts or schemas.

## Trust gates / 信任门槛

1. **Catalog gate:** JSON manifests validate against the generic schema and match their directory identity.
2. **Cemu syntax gate:** each `rules.txt` has a compatible definition; each PPC pack has a `patch_*.asm` group with the exact Cemu module checksum.
3. **Reference gate:** a PPC pack must name every original instruction and destination anchor. `verify-reference` compares the supplied reference RPX SHA-256 and big-endian words before an install is permitted.
4. **Install gate:** install and uninstall copy/remove only the catalog-owned Cemu pack directories, make a timestamped backup, and are idempotent.
5. **Runtime gate:** only an in-game transcript can promote a pack from `Static Verified` or `Runtime Experimental` to `Runtime Verified`.

## Status vocabulary / 状态词汇

| Status | Meaning |
| --- | --- |
| `Static Verified` | Pack structure and static preimage/module evidence passed; no gameplay claim. |
| `Runtime Experimental` | The pack intentionally remains disabled by default and needs isolated gameplay validation. |
| `Runtime Verified` | A recorded in-game test proves the documented behavior for the exact manifest identity. |

## Safety and compatibility / 安全与兼容

- The 30 FPS pack changes Cemu's per-pack `vsyncFrequency`; it does not write Cemu global settings.
- Box work targets interaction/menu dispatch classes, never save contents or a visible chest model.
- PPC patches may not install against a mismatching checksum or preimage/target anchor.
- The red quest-delivery-box feature is Experimental and default-off; its blue supply-box sibling is outside the patch scope.
- For online play, leave both box packs disabled. The 30 FPS pack is also default-off while its instability is unresolved.
