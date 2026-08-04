[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #40“最大调和数”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #40 "Maximum Combination Yield"; only the pinned preimage sites below are replaced.

# 中文：强制最大调和产量效果查询返回真。
# English: Force the maximum-combination-yield effect query to return true.
0x0203b2b8 = li r3, 1
