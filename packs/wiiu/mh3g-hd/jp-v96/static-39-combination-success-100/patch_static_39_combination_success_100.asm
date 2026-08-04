[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #39“调和成功率 100%”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #39 "Combination Success 100%"; only the pinned preimage sites below are replaced.

# 中文：强制调和成功率效果查询返回真。
# English: Force the combination-success effect query to return true.
0x0203ade4 = li r3, 1
