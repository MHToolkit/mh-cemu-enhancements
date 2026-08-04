[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #17“偷盗无效”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #17 "Theft Immunity"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x5B 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x5B to return true.
0x024d26f0 = li r3, 1

# 中文：强制效果 ID 0x5B 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x5B to return true.
0x02523154 = li r3, 1

# 中文：强制效果 ID 0x5B 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x5B to return true.
0x02523174 = li r3, 1
