[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #7“HP 无限”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #7 "Infinite HP"; only the pinned preimage sites below are replaced.

# 中文：禁止普通当前 HP 写回。
# English: Suppress the normal current-HP writeback.
0x02865ff8 = nop
