[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #29“任何地方可用电阻弹”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #29 "Power Coating Usable Anywhere"; only the pinned preimage sites below are replaced.

# 中文：强制电阻弹场景可用性判定返回真。
# English: Force the Power Coating scene-availability test to return true.
0x02898fdc = li r3, 1
