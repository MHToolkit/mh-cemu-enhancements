[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #65“战斗体验改善器”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #65 "Combat Experience Enhancer"; only the pinned preimage sites below are replaced.

# 中文：把通用技能查询的首个比较改为自比较。
# English: Replace the first generic-skill comparison with a self-comparison.
0x02890ae4 = cmplw r8, r8
