[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：外部 3DS ARM“装备制造与强化无需材料”的 JP v96 PPC 精确调用族转换。
# English: Exact JP-v96 PPC call-family conversion of the external 3DS ARM "Craft and Upgrade Without Materials" cheat.

# 中文：源代码 0x0042A848 的单条仓库查询在 PPC 中被编译器展开为两条路径；两处均直接返回 99。
# English: The single source item-box query at 0x0042A848 is compiler-expanded into two PPC paths; both return 99 directly.
0x02182c30 = li r3, 99
0x02182c90 = li r3, 99

# 中文：源金手指附带生产全解锁；保留合法 ID 边界，只取消解锁位失败分支。
# English: The source cheat bundles production unlock; retain valid-ID bounds and remove only the unlock-bit failure branch.
0x02198fc8 = nop

# 中文：把合计材料数量函数的全部 25 个非豁免直接调用替换为 99。
# English: Replace all twenty-five non-exempt direct calls to the combined material-count routine with 99.
0x021c4014 = li r3, 99
0x021c4060 = li r3, 99
0x021c40b0 = li r3, 99
0x021cb7c8 = li r3, 99
0x021d25f0 = li r3, 99
0x021d48b4 = li r3, 99
0x021d4918 = li r3, 99
0x021d49fc = li r3, 99
0x021d4a80 = li r3, 99
0x021d80e0 = li r3, 99
0x021eca44 = li r3, 99
0x021eefec = li r3, 99
0x021ef95c = li r3, 99
0x021f79a8 = li r3, 99
0x02206d6c = li r3, 99
0x0220967c = li r3, 99
0x0221b2b4 = li r3, 99
0x0221bc38 = li r3, 99
0x0221c09c = li r3, 99
0x0221c44c = li r3, 99
0x0221c548 = li r3, 99
0x02226fb0 = li r3, 99
0x02228298 = li r3, 99
0x02238858 = li r3, 99
0x0269504c = li r3, 99

# 中文：0x021F74AC 是与 ARM 返回地址 0x005EC3A0 对应的唯一豁免调用，故意保持原样。
# English: 0x021F74AC is the sole exempt call corresponding to ARM return address 0x005EC3A0 and is intentionally left untouched.
