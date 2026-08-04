[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #5“锋利度不减”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #5 "Sharpness Never Decreases"; only the pinned preimage sites below are replaced.

# 中文：禁止普通锋利度递减写回。
# English: Suppress the normal sharpness-decrement writeback.
0x0285f100 = nop
