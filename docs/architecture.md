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
        quest-blue-supply-box-full-item-box-control/
        quest-red-blue-full-item-box-experimental/
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

Status records evidence maturity; `availability` independently controls whether the installer may deploy a pack. `available` entries may be selected subject to their status gate. `runtime-blocked` entries remain in the catalog as reproducible negative evidence, but selection fails closed even when `--include-experimental` is supplied.

状态用于记录证据成熟度；`availability` 独立决定安装器是否允许部署。`available` 条目仍需满足对应状态门槛；`runtime-blocked` 条目只作为可复核的失败证据留在 catalog，即使传入 `--include-experimental` 也会拒绝选择。

## Safety and compatibility / 安全与兼容

- The 30 FPS pack changes Cemu's per-pack `vsyncFrequency`; it does not write Cemu global settings.
- Box work targets interaction/menu dispatch classes, never save contents or a visible chest model.
- PPC patches may not install against a mismatching checksum or preimage/target anchor.
- The red quest-delivery candidate excludes the original blue branch, but repeated gameplay remained unusable; it is `runtime-blocked`.
- The independent blue control confirmed that the initializer alone cannot produce a usable menu. Its unconditional `0x02219DF0 = nop` bridge hot-loaded but blanked quest-board dialogue and still opened no item box, so it is also `runtime-blocked`.
- The combined red+blue candidate unifies both objects at the shared selector-0 path and replaces the original helper-call window with an inline conditional gate. Asynchronous GDB subsequently proved the complete native slot-6 lifecycle reaches a null lobby-GUI layout dereference at `0x0268AB84` in quest context. The source remains reproducible evidence, but installation fails closed as `runtime-blocked`.
- 红箱候选没有修改原版蓝箱分支，但多次实测仍不可用，因此标记为 `runtime-blocked`。
- 独立蓝箱对照证明，仅调用据点完整仓库初始化器不能产生可用菜单。它的无条件 `0x02219DF0 = nop` 调度桥虽然成功热加载，却导致任务看板对话框空白且仍不弹仓库，因此同样标记为 `runtime-blocked`。
- 红蓝统一候选让两个对象共同进入选择器 `0` 路径，并在原辅助函数窗口内实现条件门槛。后续异步 GDB 已证明完整原生槽 6 生命周期在任务场景会因大厅 GUI 布局为空而于 `0x0268AB84` 解引用崩溃。源码保留作可复现证据，但安装按 `runtime-blocked` 失败关闭。
- For online play, leave all item-box modification packs disabled. The 30 FPS pack is also default-off while its instability is unresolved.
