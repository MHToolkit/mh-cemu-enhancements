[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #37“耐力无限”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #37 "Infinite Stamina"; only the pinned preimage sites below are replaced.

# 中文：强制耐力条件帮助函数返回真。
# English: Force the stamina-condition helper to return true.
0x02863dfc = li r3, 1

# 中文：跳过低于上限分支，使耐力上限值始终写回。
# English: Skip the below-maximum branch so the maximum stamina value is always written back.
0x028665b0 = nop
